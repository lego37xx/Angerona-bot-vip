import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ CONFIGURACIÓN CRÍTICA ---
TOKEN = '8616684285:AAH4NBmcFs-ZTnUvIRhLMkahBcf49i0tBDUMzn6L1k'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
NOMBRE_FOTO = 'logo.png'
PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]

# Diccionario para advertencias {user_id: cantidad_warns}
warns_usuario = {}

# --- 🚀 SERVIDOR PARA RENDER ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "Angerona está patrullando con éxito. 🛡️"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 🛡️ FUNCIONES DEL BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bienvenida profesional"""
    mensaje = (
        "🛡️ *¡Hola! Soy Angerona, la guardiana de este grupo* 🛡️\n\n"
        "Para mantener la seguridad, envía tu **presentación**:\n"
        "📸 *Foto*\n"
        "👤 *Nombre*\n"
        "🎂 *Edad*\n"
        "🌎 *País*\n\n"
        "⚠️ _Si no cumples las reglas, tomaré medidas._"
    )
    try:
        with open(NOMBRE_FOTO, 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=mensaje, parse_mode='Markdown')
    except:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje, parse_mode='Markdown')

async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /unwarn - Solo para el dueño"""
    if update.effective_user.id != DUENO_ID:
        return

    # Si respondes a un mensaje de alguien: /unwarn
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        warns_usuario[target_user.id] = 0
        await update.message.reply_text(f"✅ *Advertencias limpiadas* para {target_user.first_name}. ¡Estás libre!")
    else:
        # Si lo usas tú solo, te limpia a ti mismo
        warns_usuario[update.effective_user.id] = 0
        await update.message.reply_text("✅ *Tus advertencias han sido borradas*, Luis. ¡Limpio!")

async def filtro_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Vigila palabras prohibidas y aplica warns llamativos"""
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    texto = update.message.text.lower()

    if any(palabra in texto for palabra in PALABRAS_PROHIBIDAS):
        user_id = user.id
        warns_usuario[user_id] = warns_usuario.get(user_id, 0) + 1
        count = warns_usuario[user_id]
        
        if count >= 3:
            await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
            await update.message.reply_text(f"🚫 *USUARIO ELIMINADO*\n\n{user.first_name} ha sido baneado por acumular 3 advertencias.")
        else:
            # Mensaje de advertencia más visual
            aviso = (
                f"⚠️ *¡ADVERTENCIA PARA {user.first_name.upper()}!* ⚠️\n\n"
                f"Has usado una palabra prohibida. Esto no está permitido.\n"
                f"🚩 Contador: *{count}/3*\n\n"
                f" _Al llegar a 3 serás expulsado automáticamente._"
            )
            await update.message.reply_text(aviso, parse_mode='Markdown')
        
        await update.message.delete()

# --- 🕹️ EJECUCIÓN ---

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("unwarn", unwarn)) # NUEVO COMANDO
    
    # Filtro
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtro_mensajes))
    
    application.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    main()
    
