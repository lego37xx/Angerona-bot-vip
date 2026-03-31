import os
import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAFBtFppXJZJrQJ7LAjqMF9yYDYPb_ePKxk' 
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
NOMBRE_FOTO = 'logo.png'
PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]

warns_usuario = {}
solicitudes_pendientes = {}

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
        # Reglas manuales con foto
        texto = (
            "📜🔥 *REGLAS OFICIALES – “VALIENDO MADRES”* 🔥📜\n\n"
            "1️⃣ 🚫 Prohibido menores de edad\n"
            "2️⃣ 🤝 Respeto ante todo\n"
            "3️⃣ 📵 Nada de privados sin permiso\n"
            "4️⃣ 🚫 Cero contenido ilegal o enfermizo\n"
            "5️⃣ 😂 Aquí se viene a convivir\n"
            "6️⃣ 🔥 Se vale picar… pero no pasarse\n\n"
            "⚠️ *Presentación obligatoria:* Foto, Nombre, Edad y País."
        )
        try:
            with open(NOMBRE_FOTO, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=texto, parse_mode='Markdown')
        except: await update.message.reply_text(texto, parse_mode='Markdown')

async def bienvenida_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        
        bienvenida_texto = (
            f"✨ *¡BIENVENIDO/A A LA FAMILIA, {member.first_name.upper()}!* ✨\n\n"
            "Es un gusto tenerte en **Valiendo Madres**. Para mantener tu lugar, "
            "envía tu **presentación formal** ahora mismo:\n\n"
            "📸 *Foto Real*\n"
            "👤 *Tu Nombre*\n"
            "🎂 *Tu Edad*\n"
            "🌎 *Tu País*\n\n"
            "¡Pásatela chingón! 🤝"
        )
        try:
            with open(NOMBRE_FOTO, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=bienvenida_texto, parse_mode='Markdown')
        except: await update.message.reply_text(bienvenida_texto, parse_mode='Markdown')

async def enviar_reglas_periodicas(context: ContextTypes.DEFAULT_TYPE):
    reglas_texto = (
        "📜🔥 *REGLAS OFICIALES – “VALIENDO MADRES”* 🔥📜\n\n"
        "1️⃣ 🚫 Prohibido menores de edad\n"
        "2️⃣ 🤝 Respeto ante todo\n"
        "3️⃣ 📵 Nada de privados sin permiso\n"
        "4️⃣ 🚫 Cero contenido ilegal o enfermizo\n"
        "5️⃣ 😂 Aquí se viene a convivir\n"
        "6️⃣ 🔥 Se vale picar… pero no pasarse\n\n"
        "📢 *RECORDATORIO:* No olvides enviar tu presentación para no ser removido."
    )
    try:
        with open(NOMBRE_FOTO, 'rb') as photo:
            await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=photo, caption=reglas_texto, parse_mode='Markdown')
    except: await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=reglas_texto, parse_mode='Markdown')

async def filtro_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Inmunidad Admins
    member = await context.bot.get_chat_member(chat_id, user.id)
    if member.status in ['administrator', 'creator'] or user.id == DUENO_ID: return

    if any(p in update.message.text.lower() for p in PALABRAS_PROHIBIDAS):
        warns_usuario[user.id] = warns_usuario.get(user.id, 0) + 1
        count = warns_usuario[user.id]
        await update.message.delete()
        if count >= 3:
            await context.bot.ban_chat_member(chat_id, user.id)
            await context.bot.send_message(chat_id=chat_id, text=f"🚫 *{user.first_name}* ha sido removido por romper las reglas de convivencia.")
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ {user.first_name}, esa palabra no va aquí. Advertencia: *{count}/3*")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_grupo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtro_mensajes))
    
    # --- ⏰ REGLAS CADA 2 HORAS ---
    if application.job_queue:
        application.job_queue.run_repeating(enviar_reglas_periodicas, interval=7200, first=10)

    application.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    main()
