import os
import asyncio
import threading
import random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- ⚙️ CONFIGURACIÓN CRÍTICA ---
TOKEN = '8616684285:AAHQkeJfOVlv11o2M14bgwU1Q3UMzHpPjVE'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]
auditoria_secreta = [] 
warns_usuario = {}
total_baneados = 0 

# --- 🌐 SERVIDOR WEB (Obligatorio para Render) ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP 4.0 - Blindaje Activo", 200

def run_flask():
    # Render requiere bindear al puerto 10000 o el que asigne
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
    "🛡️ _Advertencias: 3 warns = BAN automático_"
)

# --- 🤖 LÓGICA DE INTERACCIÓN Y SEGURIDAD ---

async def enviar_reglas_job(context: ContextTypes.DEFAULT_TYPE):
    """Tarea programada cada 60 min."""
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
        await query.edit_message_text("✅ *ACCESO CONCEDIDO.*")
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
    elif random.random() < 0.10 and any(x in texto.lower() for x in ["bot", "angerona", "hola"]):
        resp = ["Los observo... 👀", "Pórtense bien. 🛡️", "Anotado en la auditoría. 📝"]
        await update.message.reply_text(random.choice(resp))

async def comando_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != DUENO_ID: return
    msg = f"📊 *STATS:* \n📩 Auditados: {len(auditoria_secreta)}\n⚠️ Warns: {len(warns_usuario)}\n🚫 Bans: {total_baneados}"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def comando_auditoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != DUENO_ID: return
    if not auditoria_secreta: return await update.message.reply_text("Vacía.")
    await update.message.reply_text("📋 *AUDITORÍA:*\n\n" + "\n".join(auditoria_secreta))

# --- 🚀 ARRANQUE DE ALTO RENDIMIENTO ---

def main():
    # Iniciar Flask en un hilo separado
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Crear la aplicación de forma síncrona para evitar errores de weakref
    application = Application.builder().token(TOKEN).build()
    
    # Configurar tareas programadas (Reglas cada 60 min)
    job_queue = application.job_queue
    job_queue.run_repeating(enviar_reglas_auto, interval=3600, first=10)
    
    # Handlers
    application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    application.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    application.add_handler(CommandHandler("stats", comando_stats))
    application.add_handler(CommandHandler("auditoria", comando_auditoria))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_seguridad))
    
    # Ejecución continua
    print("🛡️ Angerona 4.0 iniciada correctamente.")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
