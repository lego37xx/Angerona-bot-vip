import os
import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
NOMBRE_FOTO = 'logo.png'

# --- 🌐 WEB SERVER (Prioridad para Render) ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "Angerona Online 🛡️", 200

def run_flask():
    # Render usa el puerto 10000 por defecto si no detecta PORT
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 🛡️ LÓGICA DEL BOT ---

REGLAS_TEXTO = (
    "❤️ *¡BIENVENIDOS A VALIENDO MADRES!* ❤️\n\n"
    "Normas de nuestra familia:\n"
    "1️⃣ 🔞 Solo adultos.\n"
    "2️⃣ 🤝 Respeto total.\n"
    "3️⃣ 📵 Nada de DM sin permiso.\n"
    "4️⃣ 🚫 Cero contenido ilegal.\n"
    "5️⃣ 😂 Buena vibra.\n"
    "6️⃣ 🔥 Relajo con respeto.\n\n"
    "✨ *DINÁMICA:* Preséntate con **Foto, Nombre, Edad y País**."
)

solicitudes_pendientes = {}

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user = request.from_user
    solicitudes_pendientes[user.id] = request.chat.id
    keyboard = [[InlineKeyboardButton("✅ ¡Verificarme!", url=f"https://t.me/{(await context.bot.get_me()).username}?start=verificar")]]
    try:
        await context.bot.send_message(chat_id=user.id, text=f"👋 ¡Hola {user.first_name}! Toca abajo para entrar.", reply_markup=InlineKeyboardMarkup(keyboard))
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.args and context.args[0] == "verificar":
        if user.id in solicitudes_pendientes:
            await context.bot.approve_chat_join_request(chat_id=solicitudes_pendientes[user.id], user_id=user.id)
            await update.message.reply_text("✨ ¡Aprobado! Ya puedes entrar al grupo.")
            del solicitudes_pendientes[user.id]
    else:
        await update.message.reply_text(REGLAS_TEXTO, parse_mode='Markdown')

async def bienvenida_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        bienvenida = f"🥳 ¡BIENVENIDO/A, {member.first_name.upper()}! Presentación: Foto, Nombre, Edad y País."
        try:
            with open(NOMBRE_FOTO, 'rb') as f:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f, caption=bienvenida)
        except:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=bienvenida)

# --- 🚀 EJECUCIÓN ---

async def run_bot():
    # Build sin job_queue para evitar el TypeError de weak reference
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_grupo))
    
    async with app:
        await app.initialize()
        await app.start()
        print("🤖 Bot iniciado correctamente.")
        await app.updater.start_polling(drop_pending_updates=True)
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    # 1. Iniciamos Flask en un hilo separado INMEDIATAMENTE
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    
    # 2. Iniciamos el bot
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        pass
    
