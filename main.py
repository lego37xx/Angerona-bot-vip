import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ CONFIGURACIÓN CRÍTICA ---
TOKEN = '8616684285:AAFyPoA2cKvB1lDVONjH49iOtBDUMzn6L1k'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
NOMBRE_FOTO = 'logo.png'
PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]

# Diccionario para advertencias
warns_usuario = {}

# --- 🚀 SERVIDOR PARA ENGAÑAR A RENDER ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "Angerona está patrullando con éxito. 🛡️"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 🛡️ FUNCIONES DEL BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Bienvenida"""
    mensaje_bienvenida = (
        "🛡️ *¡Hola! Soy Angerona, la guardiana de este grupo* 🛡️\n\n"
        "Para mantener la seguridad, por favor envía tu **presentación**:\n"
        "📸 *Foto*\n"
        "👤 *Nombre*\n"
        "🎂 *Edad*\n"
        "🌎 *País*\n\n"
        "⚠️ _Si no cumples con las reglas o la presentación, tomaré medidas._"
    )
    
    try:
        with open(NOMBRE_FOTO, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=mensaje_bienvenida,
                parse_mode='Markdown'
            )
    except:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=mensaje_bienvenida,
            parse_mode='Markdown'
        )

async def filtro_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Vigila palabras prohibidas y aplica warns"""
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
            await update.message.reply_text(f"🚫 *{user.first_name}* baneado tras 3 advertencias.")
        else:
            await update.message.reply_text(
                f"⚠️ *¡Atención {user.first_name}!* Palabra prohibida.\n"
                f"Advertencia: *{count}/3*."
            )
        await update.message.delete()

# --- 🕹️ EJECUCIÓN ---

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtro_mensajes))
    
    print("Iniciando Angerona...")
    application.run_polling()

if __name__ == '__main__':
    # Arranca el servidor web en segundo plano para que Render esté feliz
    threading.Thread(target=run_flask, daemon=True).start()
    # Arranca el bot
    main()
        
