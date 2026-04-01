import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE' 
NOMBRE_FOTO = 'logo.png'
# Lista de palabras para moderación básica
PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]

# Las 6 reglas oficiales con tono cálido
REGLAS_TEXTO = (
    "❤️ *¡BIENVENIDOS A VALIENDO MADRES!* ❤️\n\n"
    "Para que todos disfrutemos al máximo, sigue estas **6 reglas de oro**:\n\n"
    "1️⃣ 🔞 *Solo adultos:* Grupo exclusivo para mayores de edad.\n"
    "2️⃣ 🤝 *Respeto mutuo:* Sin insultos ni dramas innecesarios.\n"
    "3️⃣ 📵 *Nada de DM:* Prohibido escribir al privado sin permiso.\n"
    "4️⃣ 🚫 *Cero ilegalidad:* Prohibido gore, cp, zoofilia o estafas.\n"
    "5️⃣ 😂 *Diversión:* Venimos a convivir y pasarla increíble.\n"
    "6️⃣ 🔥 *Límites:* Se vale el relajo, pero con respeto.\n\n"
    "✨ *DINÁMICA DE ENTRADA:* ✨\n"
    "Es obligatorio presentarte con: **Foto, Nombre, Edad y País**."
)

solicitudes_pendientes = {}

# --- 🌐 WEB SERVER (Obligatorio para Render) ---
web_app = Flask('')
@web_app.route('/')
def home(): return "Servidor Angerona Activo 🛡️"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 🛡️ FUNCIONES DEL BOT ---

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la petición de entrada al grupo."""
    request = update.chat_join_request
    user = request.from_user
    solicitudes_pendientes[user.id] = request.chat.id
    
    keyboard = [[InlineKeyboardButton("✅ ¡Verificarme ahora!", url=f"https://t.me/{(await context.bot.get_me()).username}?start=verificar")]]
    
    try:
        await context.bot.send_message(
            chat_id=user.id, 
            text=f"👋 *¡Hola {user.first_name}!*\n\nPara entrar al grupo, solo toca el botón de abajo y confírmame que vienes con buena vibra. 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesos del comando /start."""
    user = update.effective_user
    if context.args and context.args[0] == "verificar":
        if user.id in solicitudes_pendientes:
            await context.bot.approve_chat_join_request(chat_id=solicitudes_pendientes[user.id], user_id=user.id)
            await update.message.reply_text("✨ *¡Acceso aprobado!* Corre al grupo y preséntate con la banda. 🥳")
            del solicitudes_pendientes[user.id]
    else:
        await update.message.reply_text(REGLAS_TEXTO, parse_mode='Markdown')

async def bienvenida_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje cuando el usuario entra oficialmente."""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        
        bienvenida = (
            f"🥳 *¡BIENVENIDO/A A LA FAMILIA, {member.first_name.upper()}!* 🥳\n\n"
            "¡Qué alegría que ya estés aquí! Para no ser removido, por favor envíanos:\n\n"
            "📸 *Foto* | 👤 *Nombre* | 🎂 *Edad* | 🌎 *País*\n\n"
            "¡Disfruta mucho del grupo! ✨"
        )
        try:
            with open(NOMBRE_FOTO, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=bienvenida, parse_mode='Markdown')
        except:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=bienvenida, parse_mode='Markdown')

async def filtro_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elimina palabras prohibidas automáticamente."""
    if update.message and update.message.text:
        if any(p in update.message.text.lower() for p in PALABRAS_PROHIBIDAS):
            await update.message.delete()

# --- 🚀 MOTOR ---

def main():
    # USAMOS APPLICATIONBUILDER SIN JOB_QUEUE PARA EVITAR ERRORES DE MEMORIA
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_grupo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtro_mensajes))

    print("🤖 Angerona modo estabilidad iniciado...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    main()
