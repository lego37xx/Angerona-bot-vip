import os
import random
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get("BOT_TOKEN", "8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE")
DUENO_ID = 8650569384 
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

# --- WEB SERVER ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- COMANDOS Y LÓGICA ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ *SISTEMA ANGERONA ONLINE*\n\nEstoy listo para gestionar los accesos VIP.", parse_mode='Markdown')

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    kb = [[InlineKeyboardButton("✅ ACEPTO LAS REGLAS", callback_data=f"adm_{req.from_user.id}")]]
    await context.bot.send_message(chat_id=req.from_user.id, text="🔥 *BIENVENIDO AL VIP*\nAcepta las reglas para entrar.", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def boton_aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    u_id = int(query.data.split("_")[1])
    try:
        await context.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
        await query.edit_message_text("✅ *ACCESO CONCEDIDO.*")
        msg = "🥳 *¡NUEVO MIEMBRO ADMITIDO!*\n\nBienvenido al grupo. Por favor preséntate enviando:\n📸 *Foto Real*\n👤 *Nombre*\n🎂 *Edad*\n🌎 *País*"
        await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=msg, parse_mode='Markdown')
    except: pass

# --- ARRANQUE ---
async def main():
    # 1. Iniciar Flask en un hilo separado
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. Configurar el Bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    
    # 3. Iniciar Polling
    print("🛡️ Iniciando Angerona VIP...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    # Mantener vivo el loop
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
                            
