import os, random, threading, asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- CONFIG ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
DUENO_ID = 8650569384 
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

# --- WEB SERVER ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP 9.5 Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- LÓGICA DE ACCESO ---
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
        # El punto 2: Bienvenida pidiendo foto, nombre, edad y país
        msg = "🥳 *¡NUEVO MIEMBRO ADMITIDO!*\n\nBienvenido al grupo. Por favor preséntate enviando:\n📸 *Foto Real*\n👤 *Nombre*\n🎂 *Edad*\n🌎 *País*"
        await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=msg, parse_mode='Markdown')
    except: pass

# --- JUEGOS ---
async def j_juego(u: Update, c: ContextTypes.DEFAULT_TYPE):
    opciones = ["🔥 *RETO:* Confiesa algo.", "🤔 *ADIVINANZA:* ¿Qué es? (R: Un secreto)"]
    await u.message.reply_text(random.choice(opciones), parse_mode='Markdown')

# --- ARRANQUE RESILIENTE ---
async def main_bot():
    # Pausa inicial para que la instancia vieja muera en Telegram
    await asyncio.sleep(10)
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    app.add_handler(CommandHandler("juego", j_juego))
    
    async with app:
        await app.initialize()
        await app.start()
        print("🛡️ Angerona VIP 9.5 iniciada.")
        # drop_pending_updates=True es vital para quitar el error de Conflict
        await app.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main_bot())
    
