import os
import random
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
DUENO_ID = 8650569384 
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

memoria_conversacional = ["¡Hola!", "Los observo.", "Sigan con lo suyo."]
auditoria_secreta = [] 

# --- WEB SERVER ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- LÓGICA ---
async def monitor(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    text = u.message.text
    auditoria_secreta.append(f"👤 {u.effective_user.first_name}: {text}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)
    
    if random.random() < 0.10: # 10% de respuesta
        await u.message.reply_text(random.choice(memoria_conversacional))

async def c_auditoria(u, c):
    if u.effective_user.id == DUENO_ID:
        reporte = "📋 *AUDITORÍA:*\n" + "\n".join(auditoria_secreta[-20:])
        await u.message.reply_text(reporte, parse_mode='Markdown')

async def manejar_solicitud(u, c):
    kb = [[InlineKeyboardButton("✅ ACEPTO", callback_data=f"adm_{u.chat_join_request.from_user.id}")]]
    await c.bot.send_message(u.chat_join_request.from_user.id, "Acepta las reglas para entrar.", reply_markup=InlineKeyboardMarkup(kb))

async def boton_aprobar(u, c):
    uid = int(u.callback_query.data.split("_")[1])
    await c.bot.approve_chat_join_request(ID_GRUPO_FIJO, uid)
    await u.callback_query.edit_message_text("✅ Acceso concedido.")

# --- ARRANQUE ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Usamos la estructura estándar para evitar errores de hilos
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    app.add_handler(CommandHandler("auditoria", c_auditoria))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor))
    
    print("🛡️ Iniciando polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
    
