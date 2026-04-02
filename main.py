import os
import random
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- ⚙️ CONFIGURACIÓN DESDE ENTORNO ---
TOKEN = os.environ.get("BOT_TOKEN", "TU_TOKEN_AQUÍ_SI_NO_USAS_VARIABLES")
DUENO_ID = 8650569384 
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

# --- 🌐 SERVIDOR WEB ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP Operativa", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 🗝️ COMANDOS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ *Angerona VIP Online*\n\nEsperando solicitudes de acceso...", parse_mode='Markdown')

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    kbd = [[InlineKeyboardButton("✅ ACEPTO LAS REGLAS", callback_data=f"adm_{req.from_user.id}")]]
    await context.bot.send_message(chat_id=req.from_user.id, text="Bienvenido. Acepta las reglas para entrar.", reply_markup=InlineKeyboardMarkup(kbd))

async def boton_aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    u_id = int(query.data.split("_")[1])
    try:
        await context.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
        await query.edit_message_text("✅ Acceso concedido.")
        bienvenida = "🥳 *¡NUEVO MIEMBRO!*\n\nPreséntate con: *Foto, Nombre, Edad y País*."
        await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=bienvenida, parse_mode='Markdown')
    except: pass

# --- 🚀 ARRANQUE TOTAL ---
async def start_bot():
    # Evita el conflicto esperando a que la red se estabilice
    await asyncio.sleep(2)
    
    app = Application.builder().token(TOKEN).build()
    
    # Handlers fundamentales
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    
    async with app:
        await app.initialize()
        await app.start()
        print("🛡️ Bot iniciado con nuevo Token.")
        # drop_pending_updates limpia los mensajes viejos que causan errores
        await app.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit): pass
    
