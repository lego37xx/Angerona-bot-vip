import os
import random
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
DUENO_ID = 8650569384 # Identificador del propietario
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

# Memoria de sesión
memoria_conversacional = []
historial_mensajes = []
auditoria_secreta = [] # Almacena los últimos 50 mensajes
warns_usuario = {}

# --- 🌐 SERVIDOR WEB ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP 6.0 - Blindaje Total", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 📜 REGLAS ---
REGLAS_TEXTO = (
    "📜🔥 *REGLAS OFICIALES – PRIVADO* 🔥📜\n\n"
    "1️⃣ 🚫 *Prohibido menores de edad*\n"
    "2️⃣ 🤝 *Respeto y convivencia*\n"
    "3️⃣ 📵 *No Privados sin consentimiento*\n"
    "4️⃣ 🚫 *Cero contenido ilegal*\n"
    "5️⃣ 😂 *Diversión sin excesos*\n\n"
    "⚠️ *SISTEMA:* 3 warns = BAN automático."
)

# --- 🤖 LÓGICA DE AUDITORÍA, APRENDIZAJE Y SEGURIDAD ---
async def monitor_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user = update.effective_user
    texto = update.message.text
    t_low = texto.lower()

    # 1. AUDITORÍA SECRETA (Solo visible para ti vía comando)
    registro = f"👤 {user.first_name} ({user.id}): {texto}"
    auditoria_secreta.append(registro)
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    # 2. Registro para /resumen e Historial
    historial_mensajes.append(f"{user.first_name}: {texto}")
    if len(historial_mensajes) > 30: historial_mensajes.pop(0)

    # 3. Aprendizaje Neural
    if 15 < len(texto) < 100 and not texto.startswith('/'):
        if texto not in memoria_conversacional:
            memoria_conversacional.append(texto)

    # 4. Filtro de Seguridad (Warns/Ban)
    palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]
    if any(p in t_low for p in palabras_prohibidas):
        await update.message.delete()
        warns_usuario[user.id] = warns_usuario.get(user.id, 0) + 1
        conteo = warns_usuario[user.id]
        if conteo >= 3:
            await context.bot.ban_chat_member(chat_id=ID_GRUPO_FIJO, user_id=user.id)
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"🚫 *BAN:* {user.first_name} fuera por 3 advertencias.")
        else:
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"⚠️ *WARN {conteo}/3:* {user.first_name}, cuida tus palabras.")
        return

    # 5. Interacción Inteligente (15% probabilidad)
    if random.random() < 0.15:
        if "angerona" in t_low: resp = "Aquí estoy, vigilando en las sombras."
        else: resp = random.choice(memoria_conversacional) if memoria_conversacional else "Los leo..."
        await update.message.reply_text(resp)

# --- 🗝️ COMANDOS ---

async def comando_auditoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra los últimos 50 mensajes solo al dueño en privado."""
    if update.effective_user.id != DUENO_ID: return
    if not auditoria_secreta: return await update.message.reply_text("La bitácora está vacía.")
    
    reporte = "📋 *BITÁCORA DE AUDITORÍA (Últimos 50):*\n\n" + "\n".join(auditoria_secreta)
    # Telegram tiene un límite de 4096 caracteres por mensaje
    await update.message.reply_text(reporte[:4000], parse_mode='Markdown')

async def comando_unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resta un warn respondiendo al mensaje del usuario."""
    if not update.message.reply_to_message: return
    target = update.message.reply_to_message.from_user
    if target.id in warns_usuario and warns_usuario[target.id] > 0:
        warns_usuario[target.id] -= 1
        await update.message.reply_text(f"✅ Warn quitado a {target.first_name}. Total: {warns_usuario[target.id]}")

async def comando_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not historial_mensajes: return await update.message.reply_text("Sin datos.")
    temas = list(set([m.split(': ')[1][:30] + "..." for m in historial_mensajes if ': ' in m]))
    await update.message.reply_text(f"📝 *RESUMEN:* \n• " + "\n• ".join(temas[-5:]), parse_mode='Markdown')

# --- 🛡️ GESTIÓN DE ACCESO ---

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    kbd = [[InlineKeyboardButton("✅ ACEPTO LAS REGLAS", callback_data=f"adm_{req.from_user.id}")]]
    try:
        await context.bot.send_message(chat_id=req.from_user.id, text=f"👋 Hola. Acepta para entrar:\n\n{REGLAS_TEXTO}", reply_markup=InlineKeyboardMarkup(kbd), parse_mode='Markdown')
    except: pass

async def boton_aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    u_id = int(query.data.split("_")[1])
    try:
        await context.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
        await query.edit_message_text("✅ *ACCESO CONCEDIDO.*")
        await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption="🥳 ¡Bienvenido/a! Preséntate con Foto, Nombre y Edad.")
    except: pass

# --- 🚀 ARRANQUE ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    app.add_handler(CommandHandler("auditoria", comando_auditoria))
    app.add_handler(CommandHandler("resumen", comando_resumen))
    app.add_handler(CommandHandler("unwarn", comando_unwarn))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_total))
    
    print("🛡️ Angerona 6.0: Blindaje, Inteligencia y Auditoría Online.")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
