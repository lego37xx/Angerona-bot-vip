import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE' 
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

solicitudes_pendientes = {}

# --- 🌐 WEB SERVER ---
web_app = Flask('')
@web_app.route('/')
def home(): return "Angerona Online 🛡️"

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
        await context.bot.send_message(chat_id=user.id, text=f"🛡️ Hola {user.first_name}, verifícate para entrar.", reply_markup=InlineKeyboardMarkup(keyboard))
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.args and context.args[0] == "verificar":
        if user.id in solicitudes_pendientes:
            await context.bot.approve_chat_join_request(chat_id=solicitudes_pendientes[user.id], user_id=user.id)
            await update.message.reply_text("✅ *Acceso aprobado.*")
            del solicitudes_pendientes[user.id]
    else:
        await update.message.reply_text(REGLAS_TEXTO, parse_mode='Markdown')

async def bienvenida_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        mensaje = (
            f"✨ *¡BIENVENIDO/A, {member.first_name.upper()}!* ✨\n\n"
            "Envía tu **presentación formal** para evitar ser removido:\n"
            "📸 *Foto* | 👤 *Nombre* | 🎂 *Edad* | 🌎 *País*"
        )
        try:
            with open(NOMBRE_FOTO, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=mensaje, parse_mode='Markdown')
        except:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje, parse_mode='Markdown')

async def enviar_reglas_callback(context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(NOMBRE_FOTO, 'rb') as photo:
            await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=photo, caption=REGLAS_TEXTO, parse_mode='Markdown')
    except:
        await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=REGLAS_TEXTO, parse_mode='Markdown')

async def activar_reloj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando manual para activar las reglas cada 2 horas sin crashear el inicio."""
    if update.effective_user.id == 8650569384: # Solo tú puedes activarlo
        context.job_queue.run_repeating(enviar_reglas_callback, interval=7200, first=10)
        await update.message.reply_text("✅ *Reloj de reglas activado correctamente.*")

async def filtro_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        if any(p in update.message.text.lower() for p in PALABRAS_PROHIBIDAS):
            await update.message.delete()

# --- 🚀 MOTOR ---

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reloj", activar_reloj)) # NUEVO COMANDO
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_grupo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtro_mensajes))

    print("🤖 Angerona
