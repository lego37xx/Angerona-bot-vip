import os
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE' 
NOMBRE_FOTO = 'logo.png'
PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]

REGLAS_TEXTO = (
    "❤️ *¡BIENVENIDOS A VALIENDO MADRES!* ❤️\n\n"
    "Para la mejor convivencia, sigue estas **6 reglas de oro**:\n\n"
    "1️⃣ 🔞 *Solo adultos:* Sin excepciones.\n"
    "2️⃣ 🤝 *Respeto mutuo:* Cero dramas.\n"
    "3️⃣ 📵 *Nada de DM:* No escribas al privado sin permiso.\n"
    "4️⃣ 🚫 *Cero ilegalidad:* Prohibido contenido ilegal o estafas.\n"
    "5️⃣ 😂 *Diversión:* Venimos a pasarla bien.\n"
    "6️⃣ 🔥 *Límites:* Relajo con respeto.\n\n"
    "✨ *DINÁMICA:* Preséntate con **Foto, Nombre, Edad y País**."
)

solicitudes_pendientes = {}

# --- 🌐 WEB SERVER (Simple para Render) ---
web_app = Flask('')
@web_app.route('/')
def home(): return "Servidor Activo 🛡️"

# --- 🛡️ FUNCIONES DEL BOT ---

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user = request.from_user
    solicitudes_pendientes[user.id] = request.chat.id
    keyboard = [[InlineKeyboardButton("✅ ¡Verificarme!", url=f"https://t.me/{(await context.bot.get_me()).username}?start=verificar")]]
    try:
        await context.bot.send_message(
            chat_id=user.id, 
            text=f"👋 *¡Hola {user.first_name}!* Toca abajo para entrar al grupo. 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.args and context.args[0] == "verificar":
        if user.id in solicitudes_pendientes:
            await context.bot.approve_chat_join_request(chat_id=solicitudes_pendientes[user.id], user_id=user.id)
            await update.message.reply_text("✨ *¡Aprobado!* Ya puedes entrar. ¡No olvides presentarte! 🥳")
            del solicitudes_pendientes[user.id]
    else:
        await update.message.reply_text(REGLAS_TEXTO, parse_mode='Markdown')

async def bienvenida_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        bienvenida = (
            f"🥳 *¡BIENVENIDO/A, {member.first_name.upper()}!* 🥳\n\n"
            "Para quedarte, envíanos: 📸 *Foto* | 👤 *Nombre* | 🎂 *Edad* | 🌎 *País*"
        )
        try:
            with open(NOMBRE_FOTO, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=bienvenida, parse_mode='Markdown')
        except:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=bienvenida, parse_mode='Markdown')

async def filtro_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        if any(p in update.message.text.lower() for p in PALABRAS_PROHIBIDAS):
            await update.message.delete()

# --- 🚀 MOTOR ASÍNCRONO ---

async def run_bot():
    # Esta es la forma correcta de iniciar sin causar 'weak reference' en Render
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_grupo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtro_mensajes))

    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        # Mantiene el bot vivo sin bloquear el hilo principal de forma brusca
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    # Lanzamos el bot usando el bucle de eventos principal
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        pass
