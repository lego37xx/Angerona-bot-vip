import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE' 
NOMBRE_FOTO = 'logo.png'
PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]

# Restauración de las 6 reglas originales con tono cálido
REGLAS_TEXTO = (
    "❤️ *¡BIENVENIDOS A VALIENDO MADRES!* ❤️\n\n"
    "Estamos muy felices de tenerte en nuestra familia. Para mantener el mejor ambiente, por favor sigue nuestras **6 reglas de oro**:\n\n"
    "1️⃣ 🔞 *Solo adultos:* Estrictamente prohibido menores de edad.\n"
    "2️⃣ 🤝 *Respeto total:* Tratamos a los demás como queremos ser tratados.\n"
    "3️⃣ 📵 *Privados prohibidos:* No contactes a nadie por DM sin su consentimiento previo.\n"
    "4️⃣ 🚫 *Cero ilegalidad:* Nada de contenido gore, infantil, zoofilia o estafas.\n"
    "5️⃣ 😂 *Buena vibra:* Venimos a convivir, reír y pasar un buen rato.\n"
    "6️⃣ 🔥 *Límites claros:* Se vale el relajo, pero sin pasarse de la raya.\n\n"
    "✨ *DINÁMICA DE ENTRADA:* ✨\n"
    "Es obligatorio presentarte enviando: **Foto, Nombre, Edad y País**. ¡Queremos darte la bienvenida como te mereces!"
)

solicitudes_pendientes = {}

# --- 🌐 WEB SERVER ---
web_app = Flask('')
@web_app.route('/')
def home(): return "Angerona Online 🛡️"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 🛡️ FUNCIONES DE GESTIÓN ---

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Primer contacto: El bot le habla al usuario que pidió unirse."""
    request = update.chat_join_request
    user = request.from_user
    solicitudes_pendientes[user.id] = request.chat.id
    keyboard = [[InlineKeyboardButton("✅ ¡Verificarme ahora!", url=f"https://t.me/{(await context.bot.get_me()).username}?start=verificar")]]
    
    mensaje_privado = (
        f"👋 *¡Hola {user.first_name}! Qué gusto saludarte.*\n\n"
        "Para mantener nuestro grupo seguro y divertido, solo necesitamos una pequeña verificación. "
        "¡Toca el botón de abajo y nos vemos en el grupo! 👇"
    )
    try:
        await context.bot.send_message(chat_id=user.id, text=mensaje_privado, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Proceso de aprobación y visualización de reglas."""
    user = update.effective_user
    if context.args and context.args[0] == "verificar":
        if user.id in solicitudes_pendientes:
            await context.bot.approve_chat_join_request(chat_id=solicitudes_pendientes[user.id], user_id=user.id)
            await update.message.reply_text("✨ *¡Felicidades!* Tu acceso ha sido aprobado. Corre al grupo y preséntate. 🥳")
            del solicitudes_pendientes[user.id]
    else:
        # Si alguien escribe /start solo por ver las reglas
        await update.message.reply_text(REGLAS_TEXTO, parse_mode='Markdown')

async def bienvenida_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje cálido cuando el usuario entra oficialmente al chat."""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        
        bienvenida_calida = (
            f"🥳 *¡TENEMOS NUEVO MIEMBRO: {member.first_name.upper()}!* 🥳\n\n"
            "¡Qué alegría que ya estés dentro de **Valiendo Madres**! Para empezar con toda la actitud y que no te saquen, "
            "por favor envíanos tu **presentación formal**:\n\n"
            "📸 *Tu mejor Foto*\n"
            "👤 *Tu Nombre*\n"
            "🎂 *Tu Edad*\n"
            "🌎 *Tu País*\n\n"
            "¡Siéntete como en casa y disfruta del desmadre! ✨"
        )
        try:
            with open(NOMBRE_FOTO, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=bienvenida_calida, parse_mode='Markdown')
        except:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=bienvenida_calida, parse_mode='Markdown')

async def filtro_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Moderación automática de palabras prohibidas."""
    if update.message and update.message.text:
        if any(p in update.message.text.lower() for p in PALABRAS_PROHIBIDAS):
            await update.message.delete()

# --- 🚀 MOTOR ---

def main():
    # Application sin job_queue para evitar el crasheo en Render
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_grupo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtro_mensajes))

    print("🤖 Angerona Online: Servicio restaurado y amigable.")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    main()
