import os
import logging
import threading
import time
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

# --- 🌐 WEB SERVER PARA RENDER ---
web_app = Flask('')
@web_app.route('/')
def home(): return "Angerona: Valiendo Madres VIP Activo. 🛡️"

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
        await context.bot.send_message(
            chat_id=user.id,
            text=f"🛡️ *ACCESO A VALIENDO MADRES*\n\nHola {user.first_name}, para entrar al grupo VIP debes verificar que eres humano.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    if args and args[0] == "verificar":
        if user.id in solicitudes_pendientes:
            await context.bot.approve_chat_join_request(chat_id=solicitudes_pendientes[user.id], user_id=user.id)
            await update.message.reply_text("✅ *Acceso Aprobado.* ¡Ya puedes entrar a Valiendo Madres!")
            del solicitudes_pendientes[user.id]
    else:
        try:
            with open(NOMBRE_FOTO, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=REGLAS_TEXTO, parse_mode='Markdown')
        except: await update.message.reply_text(REGLAS_TEXTO, parse_mode='Markdown')

async def bienvenida_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        bienvenida = (
            f"✨ *¡BIENVENIDO/A A LA FAMILIA, {member.first_name.upper()}!* ✨\n\n"
            "Es un gusto tenerte en **Valiendo Madres**. Envía tu **presentación formal**:\n"
            "📸 Foto | 👤 Nombre | 🎂 Edad | 🌎 País\n\n¡Pásatela chingón! 🤝"
        )
        try:
            with open(NOMBRE_FOTO, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=bienvenida, parse_mode='Markdown')
        except: await update.message.reply_text(bienvenida, parse_mode='Markdown')

async def enviar_reglas_periodicas(context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(NOMBRE_FOTO, 'rb') as photo:
            await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=photo, caption=REGLAS_TEXTO, parse_mode='Markdown')
            print("📅 Reglas automáticas enviadas con éxito.")
    except Exception as e:
        print(f"❌ Error en JobQueue: {e}")
        await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=REGLAS_TEXTO, parse_mode='Markdown')

async def filtro_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status in ['administrator', 'creator'] or user.id == DUENO_ID: return
    except: pass

    if any(p in update.message.text.lower() for p in PALABRAS_PROHIBIDAS):
        warns_usuario[user.id] = warns_usuario.get(user.id, 0) + 1
        count = warns_usuario[user.id]
        await update.message.delete()
        if count >= 3:
            await context.bot.ban_chat_member(chat_id, user.id)
            await context.bot.send_message(chat_id=chat_id, text=f"🚫 *{user.first_name}* ha sido removido por acumular 3 advertencias.")
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ {user.first_name}, esa palabra está prohibida. Advertencia: *{count}/3*")

# --- 🚀 INICIALIZACIÓN ---

def main():
    # Construcción robusta de la aplicación
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_grupo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtro_mensajes))
    
    # Configurar el reloj (JobQueue) antes de arrancar
    if application.job_queue:
        # Probaremos con 60 segundos para confirmar el éxito de inmediato
        application.job_queue.run_repeating(enviar_reglas_periodicas, interval=60, first=10)
        print("✅ JobQueue activo: El motor de reglas ha iniciado.")

    # Iniciar bot limpiando actualizaciones pendientes
    print("🤖 Angerona en guardia permanente...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # Lanzar servidor Flask en hilo separado
    threading.Thread(target=run_flask, daemon=True).start()
    # Pausa técnica de seguridad
    time.sleep(2)
    main()
