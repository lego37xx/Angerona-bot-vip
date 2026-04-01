import os
import asyncio
import threading
import random
import logging
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- ⚙️ CONFIGURACIÓN MAESTRA ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]
auditoria_secreta = [] 
warns_usuario = {}
total_baneados = 0 

# --- 🌐 SERVIDOR WEB (Render) ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP Inteligente Online", 200

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

# --- 🤖 INTELIGENCIA Y MODERACIÓN ---
async def responder_con_onda(update: Update, texto: str):
    respuestas = [
        "Sigan platicando, pero los estoy auditando... 👀",
        "¿Mucho desorden aquí? Recuerden quién manda. 🛡️",
        "Interesante... esto va directo a mi base de datos secreta. 📝",
        "Pórtense bien o sacamos el mazo del BAN. 🔨"
    ]
    if any(x in texto.lower() for x in ["bot", "angerona", "hola"]):
        await update.message.reply_text(random.choice(respuestas))

async def monitor_seguridad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_baneados
    if not update.message or not update.message.text: return
    user = update.effective_user
    texto = update.message.text

    # Registro en Auditoría Secreta
    log = f"👤 {user.first_name} ({user.id}): {texto}"
    auditoria_secreta.append(log)
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    # Filtro de palabras
    if any(p in texto.lower() for p in PALABRAS_PROHIBIDAS):
        await update.message.delete()
        warns_usuario[user.id] = warns_usuario.get(user.id, 0) + 1
        if warns_usuario[user.id] >= 3:
            await context.bot.ban_chat_member(chat_id=ID_GRUPO_FIJO, user_id=user.id)
            total_baneados += 1
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"🚫 *BAN:* {user.first_name} expulsado por 3 advertencias.")
        else:
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"⚠️ {user.first_name}, borré eso. Warn: {warns_usuario[user.id]}/3")
    else:
        # Probabilidad de interacción de IA
        if random.random() < 0.10: 
            await responder_con_onda(update, texto)

# --- 🏗️ ACCESO Y AUTOMATIZACIÓN ---
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

async def enviar_reglas_auto(context: ContextTypes.DEFAULT_TYPE):
    """Envía reglas cada 60 min."""
    try:
        await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=f"⏰ *RECORDATORIO:* \n\n{REGLAS_TEXTO}", parse_mode='Markdown')
    except: pass

# --- 🗝️ COMANDOS ---
async def comando_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != DUENO_ID: return
    msg = (f"📊 *STATS ANGERONA:*\n\n📩 Mensajes auditados: {len(auditoria_secreta)}\n"
           f"⚠️ Usuarios con warn: {len(warns_usuario)}\n🚫 Baneos totales: {total_baneados}")
    await update.message.reply_text(msg, parse_mode='Markdown')

async def comando_auditoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != DUENO_ID: return
    reporte = "📋 *AUDITORÍA:*\n\n" + "\n".join(auditoria_secreta)
    await update.message.reply_text(reporte[:4000], parse_mode='Markdown')

# --- 🚀 INICIO ---
if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Automatización 60 min (3600 seg)
    app.job_queue.run_repeating(enviar_reglas_auto, interval=3600, first=10)
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    app.add_handler(CommandHandler("stats", comando_stats))
    app.add_handler(CommandHandler("auditoria", comando_auditoria))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_seguridad))
    
    print("🛡️ Angerona Smart 3.0: Online")
    app.run_polling(drop_pending_updates=True)
    
