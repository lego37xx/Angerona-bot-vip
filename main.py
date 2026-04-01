import os
import logging
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHfSOA3yOtzAXlMfl0Exbhp6n2QyLMJzhc' 
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
NOMBRE_FOTO = 'logo.png'
PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]

REGLAS_TEXTO = (
    "📜🔥 *REGLAS OFICIALES – “VALIENDO MADRES”* 🔥📜\n\n"
    "1️⃣ 🚫 Prohibido menores de edad\n"
    "2️⃣ 🤝 Respeto ante todo\n"
    "3️⃣ 📵 Nada de privados sin permiso\n"
    "4️⃣ 🚫 Cero contenido ilegal o enfermizo\n"
    "5️⃣ 😂 Aquí se viene a convivir\n"
    "6️⃣ 🔥 Se vale picar… pero no pasarse\n\n"
    "⚠️ *PRESENTACIÓN OBLIGATORIA:* Foto, Nombre, Edad y País."
)

warns_usuario = {}
solicitudes_pendientes = {}

# --- 🌐 WEB SERVER ---
web_app = Flask('')
@web_app.route('/')
def home(): return "Angerona Activo. 🛡️"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 🛡️ FUNCIONES ---

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user = request.from_user
    solicitudes_pendientes[user.id] = request.chat.id
    keyboard = [[InlineKeyboardButton("✅ Iniciar Verificación", url=f"https://t.me/{(await context.bot.get_me()).username}?start=verificar")]]
    try:
        await context.bot.send_message(chat_id=user.id, text=f"🛡️ *ACCESO A VALIENDO MADRES*\n\nHola {user.first_name}, verifícate para entrar.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.args and context.args[0] == "verificar":
        if user.id in solicitudes_pendientes:
            await context.bot.approve_chat_join_request(chat_id=solicitudes_pendientes[user.id], user_id=user.id)
            await update.message.reply_text("✅ *Acceso Aprobado.*")
            del solicitudes_pendientes[user.id]
    else:
        try:
            with open(NOMBRE_FOTO, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=REGLAS_TEXTO, parse_mode='Markdown')
        except: await update.message.reply_text(REGLAS_TEXTO, parse_mode='Markdown')

async def enviar_reglas_periodicas(context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(NOMBRE_FOTO, 'rb') as photo:
            await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=photo, caption=REGLAS_TEXTO, parse_mode='Markdown')
        print("📅 Reglas enviadas.")
    except Exception as e: print(f"❌ Error: {e}")

# --- 🚀 INICIO ---

def main():
    # Inicialización limpia para evitar el error de 'Application'
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: None)) # Simplificado para test

    if application.job_queue:
        application.job_queue.run_repeating(enviar_reglas_periodicas, interval=60, first=10)
        print("✅ Reloj activo.")

    # El drop_pending_updates=True es clave para evitar conflictos de mensajes viejos
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    main()
