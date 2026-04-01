import os
import asyncio
import threading
import random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]
auditoria_secreta = [] 
warns_usuario = {}
total_baneados = 0 

# --- 🌐 WEB SERVER ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona Smart 3.1 Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 📜 REGLAS ---
REGLAS_TEXTO = (
    "📜🔥 *REGLAS OFICIALES – “VALIENDO MADRES”* 🔥📜\n\n"
    "1️⃣ 🚫 *Prohibido menores de edad*\n"
    "2️⃣ 🤝 *Respeto ante todo*\n"
    "3️⃣ 📵 *Nada de privados sin permiso*\n"
    "4️⃣ 🚫 *Cero contenido ilegal o enfermizo*\n"
    "5️⃣ 😂 *Aquí se viene a convivir*\n"
    "6️⃣ 🔥 *Se vale picar… pero no pasarse*\n\n"
    "⚠️ *PRESENTACIÓN OBLIGATORIA:* Foto, Nombre, Edad y País.\n"
    "🛡️ _Sistema de advertencias activo (3 warns = BAN)_"
)

# --- 🤖 LÓGICA ---
async def enviar_reglas_auto(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=f"⏰ *RECORDATORIO:* \n\n{REGLAS_TEXTO}", parse_mode='Markdown')
    except: pass

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    kbd = [[InlineKeyboardButton("✅ ACEPTO LAS REGLAS", callback_data=f"adm_{req.from_user.id}")]]
    try:
        await context.bot.send_message(chat_id=req.from_user.id, text=f"👋 ¡Hola! Confirma para entrar:\n\n{REGLAS_TEXTO}", reply_markup=InlineKeyboardMarkup(kbd), parse_mode='Markdown')
    except: pass

async def boton_aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = int(query.data.split("_")[1])
    try:
        await context.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=user_id)
        await query.edit_message_text("✅ *ACCESO CONCEDIDO.* ¡Ya puedes entrar!")
        bienvenida = (f"🥳 *¡BIENVENIDO/A!* 🥳\n\n{REGLAS_TEXTO}\n\n✨ *Presentación:* Foto, Nombre, Edad y País.")
        await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=bienvenida, parse_mode='Markdown')
    except: pass

async def monitor_seguridad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_baneados
    if not update.message or not update.message.text: return
    user = update.effective_user
    texto = update.message.text

    auditoria_secreta.append(f"👤 {user.first_name}: {texto}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    if any(p in texto.lower() for p in PALABRAS_PROHIBIDAS):
        await update.message.delete()
        warns_usuario[user.id] = warns_usuario.get(user.id, 0) + 1
        if warns_usuario[user.id] >= 3:
            await context.bot.ban_chat_member(chat_id=ID_GRUPO_FIJO, user_id=user.id)
            total_baneados += 1
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"🚫 *BAN:* {user.first_name} expulsado.")
        else:
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"⚠️ {user.first_name}, warn: {warns_usuario[user.id]}/3")
    elif random.random() < 0.10: # IA
        resp = ["Los observo... 👀", "Pórtense bien. 🛡️", "Anotado en la auditoría. 📝"]
        if any(x in texto.lower() for x in ["bot", "angerona", "hola"]):
            await update.message.reply_text(random.choice(resp))

async def comando_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != DUENO_ID: return
    msg = (f"📊 *STATS:* \n📩 Auditados: {len(auditoria_secreta)}\n⚠️ Warns: {len(warns_usuario)}\n🚫 Bans: {total_baneados}")
    await update.message.reply_text(msg, parse_mode='Markdown')

async def comando_auditoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != DUENO_ID: return
    await update.message.reply_text("📋 *AUDITORÍA:*\n\n" + "\n".join(auditoria_secreta), parse_mode='Markdown')

# --- 🚀 ARRANQUE ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Construcción correcta para activar JobQueue
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Programar reglas cada 60 min
    if app.job_queue:
        app.job_queue.run_repeating(enviar_reglas_auto, interval=3600, first=10)
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    app.add_handler(CommandHandler("stats", comando_stats))
    app.add_handler(CommandHandler("auditoria", comando_auditoria))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_seguridad))
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait() # Mantiene el bot vivo

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass
