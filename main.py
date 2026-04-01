import os
import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
NOMBRE_FOTO = 'logo.png'  # Asegúrate de que el archivo se llame así en GitHub

# --- 🌐 WEB SERVER (Para que Render marque "Live" al instante) ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "Angerona Bot Online 🛡️", 200

def run_flask():
    # Render asigna el puerto automáticamente, por defecto 10000
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 📜 TEXTOS OFICIALES ---
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

# --- 🛡️ FUNCIONES DEL BOT ---

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la solicitud de unión y envía link de verificación al privado."""
    request = update.chat_join_request
    user = request.from_user
    solicitudes_pendientes[user.id] = request.chat.id
    
    keyboard = [[InlineKeyboardButton("✅ ¡Verificarme!", url=f"https://t.me/{(await context.bot.get_me()).username}?start=verificar")]]
    
    try:
        await context.bot.send_message(
            chat_id=user.id, 
            text=f"👋 *¡Hola {user.first_name}!* \n\nPara entrar al grupo, toca el botón de abajo para verificar que no eres un bot. 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except:
        pass # El usuario tiene el privado cerrado

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start y la aprobación de usuarios."""
    user = update.effective_user
    if context.args and context.args[0] == "verificar":
        if user.id in solicitudes_pendientes:
            await context.bot.approve_chat_join_request(chat_id=solicitudes_pendientes[user.id], user_id=user.id)
            await update.message.reply_text("✨ *¡Aprobado!* Ya puedes entrar al grupo. ¡No olvides presentarte con la banda! 🥳")
            del solicitudes_pendientes[user.id]
    else:
        await update.message.reply_text(REGLAS_OFICIALES, parse_mode='Markdown')

async def bienvenida_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía el logo y las reglas cuando alguien entra oficialmente al grupo."""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        
        texto_bienvenida = (
            f"🥳 *¡BIENVENIDO/A A LA FAMILIA, {member.first_name.upper()}!* 🥳\n\n"
            f"{REGLAS_OFICIALES}\n\n"
            "✨ *¡Queremos conocerte! Envía tu presentación ahora mismo.*"
        )
        
        try:
            # Intentamos enviar el logo con el texto
            with open(NOMBRE_FOTO, 'rb') as f:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id, 
                    photo=f, 
                    caption=texto_bienvenida, 
                    parse_mode='Markdown'
                )
        except Exception as e:
            # Si falla la foto (ej. no está en el repo), mandamos solo el texto
            print(f"Error al enviar foto: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=texto_bienvenida, 
                parse_mode='Markdown'
            )

# --- 🚀 MOTOR ASÍNCRONO ---

async def run_bot():
    # Application sin job_queue para evitar errores de memoria 'weak reference'
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_grupo))
    
    async with app:
        await app.initialize()
        await app.start()
        print("🤖 Bot Angerona iniciado y listo.")
        await app.updater.start_polling(drop_pending_updates=True)
        # Mantenemos el bucle vivo
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    # 1. Lanzamos Flask en un hilo aparte para que Render detecte el puerto 10000
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. Corremos el bot en el bucle principal asíncrono
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        pass
