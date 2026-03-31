import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ CONFIGURACIÓN CRÍTICA ---
TOKEN = '8616684285:AAEF271duWSPV0-UfJ9rK4rUdI6UQz1-Zxg'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233  # Tu grupo VIP
NOMBRE_FOTO = 'logo.png'
PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]

# Diccionario para rastrear advertencias {user_id: cantidad_warns}
warns_usuario = {}

# --- 🚀 SERVIDOR PARA RENDER ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "Angerona está viva y patrullando. 🛡️"

# --- 🛡️ FUNCIONES DEL BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Bienvenida con reglas"""
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
        # Intenta enviar con la foto si existe
        with open(NOMBRE_FOTO, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=mensaje_bienvenida,
                parse_mode='Markdown'
            )
    except Exception as e:
        # Si falla la foto, envía solo el texto
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
            # BAN AUTOMÁTICO AL TERCER WARN
            await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
            await update.message.reply_text(f"🚫 *{user.first_name}* ha sido baneado tras 3 advertencias.")
        else:
            await update.message.reply_text(
                f"⚠️ *¡Atención {user.first_name}!* Has usado una palabra prohibida.\n"
                f"Advertencia: *{count}/3*. Al llegar a 3 serás expulsado."
            )
        
        # Borra el mensaje prohibido
        await update.message.delete()

# --- 🕹️ EJECUCIÓN PRINCIPAL ---

def main():
    # Crear la aplicación con el Token
    application = Application.builder().token(TOKEN).build()

    # Añadir manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    
    # Añadir filtro de mensajes (vigilancia 24/7)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtro_mensajes))

    # Iniciar el bot (Render usará el webhook o polling según la carga)
    print("Iniciando patrullaje de Angerona...")
    application.run_polling()

if __name__ == '__main__':
    # Esto permite que Flask corra en un hilo separado si fuera necesario, 
    # pero para Render usaremos el polling directo por ahora.
    main()
            
