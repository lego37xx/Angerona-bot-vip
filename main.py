import os
import threading
import random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]
auditoria_secreta = [] 
warns_usuario = {}
total_baneados = 0 

# --- 🌐 SERVIDOR WEB ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP Inteligente - Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 📜 REGLAS ---
REGLAS_TEXTO = (
    "📜🔥 *REGLAS OFICIALES – “VALIENDO MADRES”* 🔥📜\n\n"
    "1️⃣ 🚫 *Prohibido menores de edad*\n"
    "2️⃣ 🤝 *Respeto ante todo*\n"
    "3️⃣ 📵 *Nada de privados sin permiso*\n"
    "4️⃣ 🚫 *Cero contenido ilegal*\n"
    "5️⃣ 😂 *Aquí se viene a convivir*\n"
    "6️⃣ 🔥 *Se vale picar… pero no pasarse*\n\n"
    "⚠️ *PRESENTACIÓN OBLIGATORIA:* Foto, Nombre, Edad y País.\n"
    "🛡️ _Advertencias: 3 warns = BAN_"
)

# --- 🤖 CEREBRO DE INTERACCIÓN ---
async def inteligencia_angerona(update: Update, texto: str):
    """Lógica de respuesta basada en personalidad."""
    t = texto.lower()
    
    # Diccionario de reacciones
    if any(x in t for x in ["hola", "buen", "onda"]):
        resp = [f"¿Qué onda {update.effective_user.first_name}? Pórtense bien.", "Hola. Sigan en lo suyo, yo vigilo. 👀", "¡Qué tal! No olviden las reglas."]
    elif any(x in t for x in ["bot", "angerona"]):
        resp = ["¿Me llamaron? Estoy ocupada auditando mensajes. 📝", "Aquí estoy. No se pasen de listos.", "Angerona siempre escucha. 🛡️"]
    elif "admin" in t or "dueño" in t:
        resp = ["El Ingeniero está al mando, yo solo ejecuto. 😎", "No molesten al Admin, para eso estoy yo."]
    else:
        # Respuestas aleatorias para dar vida al chat
        resp = ["Interesante... sigan, los leo. 👀", "Recuerden que la auditoría no duerme.", "Anotando esto en mi bitácora secreta. 📋"]

    await update.message.reply_text(random.choice(resp))

# --- 🛡️ MODERACIÓN Y ACCESO ---
async def monitor_seguridad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_baneados
    if not update.message or not update.message.text: return
    user = update.effective_user
    texto = update.message.text

    # Auditoría
    auditoria_secreta.append(f"👤 {user.first_name}: {texto}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    # Filtro de palabras
    if any(p in texto.lower() for p in PALABRAS_PROHIBIDAS):
        await update.message.delete()
        warns_usuario[user.id] = warns_usuario.get(user.id, 0) + 1
        if warns_usuario[user.id] >= 3:
            await context.bot.ban_chat_member(chat_id=ID_GRUPO_FIJO, user_id=user.id)
            total_baneados += 1
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"🚫 *BAN:* {user.first_name} acumuló 3 advertencias.")
        else:
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"⚠️ {user.first_name}, warn: {warns_usuario[user.id]}/3")
    
    # Probabilidad de interacción (15%) si mencionan al bot o palabras clave
    elif random.random() < 0.15:
        await inteligencia_angerona(update, texto)

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    kbd = [[InlineKeyboardButton("✅ ACEPTO LAS REGLAS", callback_data=f"adm_{req.from_user.id}")]]
    try:
        await context.bot.send_message(chat_id=req.from_user.id, text=f"👋 ¡Hola! Confirma para entrar:\n\n{REGLAS_TEXTO}", reply_markup=InlineKeyboardMarkup(kbd), parse_mode='Markdown')
    except: pass

async def boton_aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = int(query.data.split("_")[1])
    try:
        await context.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=user_id)
        await query.edit_message_text("✅ *ACCESO CONCEDIDO.*")
        bienvenida = f"🥳 *¡BIENVENIDO/A!* 🥳\n\n{REGLAS_TEXTO}\n\n✨ *Presentación:* Foto, Nombre, Edad y País."
        await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=bienvenida, parse_mode='Markdown')
    except: pass

# --- 🗝️ COMANDOS MANUALES (Privado) ---
async def comando_reglas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía las reglas al grupo cuando tú lo decidas."""
    if update.effective_user.id != DUENO_ID: return
    await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=f"📢 *MENSAJE DEL ADMIN:*\n\n{REGLAS_TEXTO}", parse_mode='Markdown')
    await update.message.reply_text("✅ Reglas enviadas al grupo.")

async def comando_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != DUENO_ID: return
    msg = f"📊 *STATS:* \n📩 Auditados: {len(auditoria_secreta)}\n⚠️ Warns: {len(warns_usuario)}\n🚫 Bans: {total_baneados}"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def comando_auditoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != DUENO_ID: return
    if not auditoria_secreta: return await update.message.reply_text("Vacía.")
    await update.message.reply_text("📋 *AUDITORÍA:*\n\n" + "\n".join(auditoria_secreta))

# --- 🚀 ARRANQUE ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    application.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    
    # Comandos
    application.add_handler(CommandHandler("reglas", comando_reglas))
    application.add_handler(CommandHandler("stats", comando_stats))
    application.add_handler(CommandHandler("auditoria", comando_auditoria))
    
    # Monitor de mensajes e Inteligencia
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_seguridad))
    
    print("🛡️ Angerona Smart: Online")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
    
