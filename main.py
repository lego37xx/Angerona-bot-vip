import os
import random
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
DUENO_ID = 8650569384 

# Servidor para que Render no mate el proceso
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# Lógica básica de respuesta
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        if random.random() < 0.10: # 10% de probabilidad
            await update.message.reply_text("Sistema Angerona activo y observando.")

# Arranque principal
async def main_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    
    async with app:
        await app.initialize()
        await app.start()
        print("🛡️ Bot iniciado con éxito.")
        await app.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(main_bot())
    except KeyboardInterrupt:
        pass
            
