import os
import random
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
DUENO_ID = 8650569384 
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

# Memoria de sesión
memoria_conversacional = ["Interesante...", "Los observo.", "Sigan platicando.", "Bitácora actualizada."]
historial_mensajes = []
auditoria_secreta = [] 
warns_usuario = {}

# --- 🌐 SERVIDOR WEB (Keep-Alive) ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP 8.0 - Sistema de Control Total", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 📜 REGLAS ---
REGLAS_TEXTO = (
    "📜🔥 *REGLAS OFICIALES – PRIVADO* 🔥📜\n\n"
    "1️⃣ 🚫 *Prohibido menores de edad*\n"
    "2️⃣ 🤝 *Respeto y convivencia*\n"
    "3️⃣ 📵 *Privados bajo advertencia*\n"
    "4️⃣ 🚫 *Cero contenido ilegal*\n"
    "5️⃣ 😂 *Diversión sin excesos*\n\n"
    "⚠️ *SISTEMA:* 3 warns = BAN automático."
)

# --- 🤖 LÓGICA DE AUDITORÍA Y SEGURIDAD ---
async def monitor_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user = update.effective_user
    texto = update.message.text
    t_low = texto.lower()

    # Auditoría Secreta (Últimos 50)
    auditoria_secreta.append(f"👤 {user.first_name} ({user.id}): {texto}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    # Historial para /resumen (Últimos 30)
    historial_mensajes.append(f"{user.first_name}: {texto}")
    if len(historial_mensajes) > 30: historial_mensajes.pop(0)

    # Aprendizaje Neural
    if 15 < len(texto) < 100 and not texto.startswith('/'):
        if texto not in memoria_conversacional:
            memoria_conversacional.append(texto)
            if len(memoria_conversacional) > 100: memoria_conversacional.pop(0)

    # Filtro de Seguridad
    palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]
    if any(p in t_low for p in palabras_prohibidas):
        try: await update.message.delete()
        except: pass
        warns_usuario[user.id] = warns_usuario.get(user.id, 0) + 1
        if warns_usuario[user.id] >= 3:
            await context.bot.ban_chat_member(chat_id=ID_GRUPO_FIJO, user_id=user.id)
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"🚫 *BAN:* {user.first_name} expulsado por 3 advertencias.")
        else:
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"⚠️ *WARN {warns_usuario[user.id]}/3:* {user.first_name}, cuida tus palabras.")
        return

    # Interacción Aleatoria (15%)
    if random.random() < 0.15:
        await update.message.reply_text(random.choice(memoria_conversacional))

# --- 🎲 MÓDULO DE JUEGOS ---
async def j_adivinanza(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lista = ["🤔 *ADIVINANZA:* ¿Qué es lo que se hace más grande cuanto más le quitas? \n(R: Un hoyo)",
             "🤔 *ADIVINANZA:* Poso en el agua y no me mojo, poso en el fuego y no me quemo. \n(R: La sombra)"]
    await update.message.reply_text(random.choice(lista), parse_mode='Markdown')

async def j_verdad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    preg = ["🤫 *VERDAD:* ¿Qué es lo más vergonzoso que has hecho en una cita?",
            "🤫 *VERDAD:* ¿Cuál es tu mayor fantasía no cumplida?"]
    await update.message.reply_text(random.choice(preg), parse_mode='Markdown')

async def j_reto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    retos = ["🔥 *RETO:* Envía un audio de 10 segundos cantando algo.",
             "🔥 *RETO:* Confiesa quién te gusta del grupo."]
    await update.message.reply_text(random.choice(retos), parse_mode='Markdown')

async def j_picante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hot = ["🌶️ *PICANTE:* Describe tu última noche usando solo 3 emojis.",
           "🌶️ *PICANTE:* ¿Lugar más extraño donde has tenido un encuentro íntimo?"]
    await update.message.reply_text(random.choice(hot), parse_mode='Markdown')

# --- 🗝️ COMANDOS DE ADMINISTRACIÓN ---
async def c_auditoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != DUENO_ID: return
    if not auditoria_secreta: return await update.message.reply_text("Bitácora vacía.")
    await update.message.reply_text("📋 *AUDITORÍA:*\n\n" + "\n".join(auditoria_secreta), parse_mode='Markdown')

async def c_unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return
    target = update.message.reply_to_message.from_user
    if target.id in warns_usuario and warns_usuario[target.id] > 0:
        warns_usuario[target.id] -= 1
        await update.message.reply_text(f"✅ Se quitó 1 warn a {target.first_name}.")

async def c_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not historial_mensajes: return await update.message.reply_text("Sin datos.")
    temas = list(set([m.split(': ')[1][:30] + "..." for m in historial_mensajes if ': ' in m]))
    await update.message.reply_text(f"📝 *RESUMEN RECIENTE:* \n• " + "\n• ".join(temas[-5:]), parse_mode='Markdown')

# --- 🛡️ GESTIÓN DE ACCESO ---
async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    kbd = [[InlineKeyboardButton("✅ ACEPTO LAS REGLAS", callback_data=f"adm_{req.from_user.id}")]]
    try: await context.bot.send_message(chat_id=req.from_user.id, text=f"👋 Hola. Lee y acepta:\n\n{REGLAS_TEXTO}", reply_markup=InlineKeyboardMarkup(kbd), parse_mode='Markdown')
    except: pass

async def boton_aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; u_id = int(query.data.split("_")[1])
    try:
        await context.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
        await query.edit_message_text("✅ *ACCESO CONCEDIDO.*")
        await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption="🥳 ¡Bienvenido/a! Preséntate ahora.")
    except: pass

# --- 🚀 ARRANQUE TOTAL (Solución al Event Loop) ---
async def iniciar_bot():
    app = Application.builder().token(TOKEN).build()
    
    # Handlers Acceso
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    
    # Handlers Juegos
    app.add_handler(CommandHandler("adivinanza", j_adivinanza))
    app.add_handler(CommandHandler("verdad", j_verdad))
    app.add_handler(CommandHandler("reto", j_reto))
    app.add_handler(CommandHandler("picante", j_picante))
    
    # Handlers Admin/Info
    app.add_handler(CommandHandler("auditoria", c_auditoria))
    app.add_handler(CommandHandler("resumen", c_resumen))
    app.add_handler(CommandHandler("unwarn", c_unwarn))
    
    # Monitor Neural
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_total))
    
    async with app:
        await app.initialize()
        await app.start()
        print("🛡️ Angerona 8.0 activa. Polling iniciado.")
        await app.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(iniciar_bot())
    except (KeyboardInterrupt, SystemExit): pass
