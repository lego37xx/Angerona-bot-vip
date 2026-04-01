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
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 🛡️ LÓGICA DEL BOT ---

REGLAS_OFICIALES = (
    "📜🔥 *REGLAS OFICIALES – “VALIENDO MADRES”* 🔥📜\n\n"
    "1️⃣ 🚫 *Prohibido menores de edad*\n"
    "2️⃣ 🤝 *Respeto ante todo*\n"
    "3️⃣ 📵 *Nada de privados sin permiso*\n"
    "4️⃣ 🚫 *Cero contenido ilegal o enfermizo*\n"
    "5️⃣ 😂 *Aquí se viene a convivir*\n"
    "6️⃣ 🔥 *Se vale picar… pero no pasarse*\n\n"
    "⚠️ *PRESENTACIÓN OBLIGATORIA:* Foto, Nombre, Edad y País."
)

solicitudes_pendientes = {}

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user = request.from_user
    solicitudes_pendientes[user.id] = request.chat.id
    keyboard = [[InlineKeyboardButton("✅ ¡Verificarme!", url=f"https://t.me/{(await context.bot.get_me()).username}?start=verificar")]]
    
    try:
        await context.bot.send_message(
            chat_id=user.id, 
            text=f"👋 *¡Hola {user.first_name}!* \n\nPara entrar al grupo, toca el botón de abajo. 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.args and context.args[0] == "verificar":
        if user.id in solicitudes_pendientes:
            await context.bot.approve_chat_join_request(chat_id=solicitudes_pendientes[user.id], user_id=user.id)
            await update.message.reply_text("✨ *¡Aprobado!* Ya puedes entrar al grupo. ¡No olvides presentarte! 🥳")
            del solicitudes_pendientes[user.id]
    else:
        await update.message.reply_text(REGLAS_OFICIALES, parse_mode='Markdown')

async def bienvenida_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        
        texto_bienvenida = (
            f"🥳 *¡BIENVENIDO/A A LA FAMILIA, {member.first_name.upper()}!* 🥳\n\n"
            f"{REGLAS_OFICIALES}\n\n"
            "✨ *¡Queremos conocerte! Envía tu presentación ahora mismo.*"
        )
        try:
            with open(NOMBRE_FOTO, 'rb') as f:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f, caption=texto_bienvenida, parse_mode='Markdown')
        except:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=texto_bienvenida, parse_mode='Markdown')

# --- 🚀 EJECUCIÓN ---

async def run_bot():
    # Application sin job_queue para evitar el crasheo "weak reference"
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_grupo))
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    # Iniciamos Flask primero para que Render de el "Live" rápido
    threading.Thread(target=run_flask, daemon=True).start()
    
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        pass
