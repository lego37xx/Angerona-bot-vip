import os
import asyncio
import threading
import random
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
total_baneados = 0 # Contador de baneos para /stats

# --- 🌐 SERVIDOR WEB (Render) ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP Inteligente Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 📜 REGLAS Y TEXTOS ---
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

# --- 🤖 INTELIGENCIA Y PERSONALIDAD ---
async def responder_con_onda(update: Update, texto: str):
    """Respuestas inteligentes y divertidas según el contexto."""
    texto = texto.lower()
    respuestas_random = [
        "Aquí mando yo, pero sigan en lo suyo... los observo. 👀",
        "¿Alguien dijo fiesta o solo están perdiendo el tiempo? 🥂",
        "Recuerden: la paciencia de Angerona es corta, las reglas son largas. 🛡️",
        "Interesante... sigan, estoy tomando notas para la auditoría. 📝"
    ]
    
    if "hola" in texto or "buen" in texto:
        await update.message.reply_text(f"👋 ¡Qué onda {update.effective_user.first_name}! No olvides presentarte si eres nuevo.")
    elif "bot" in texto or "angerona" in texto:
        await update.message.reply_text(random.choice(respuestas_random))
    elif "admin" in texto:
        await update.message.reply_text("¿El Admin? Es un tipo ocupado, mejor pórtense bien. 😎")

# --- 🛡️ FUNCIONES DE MODERACIÓN Y ACCESO ---

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    user = req.from_user
    kbd = [[InlineKeyboardButton("✅ ACEPTO LAS REGLAS", callback_data=f"adm_{user.id}")]]
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=f"👋 ¡Hola {user.first_name}! Para entrar a *{req.chat.title}*, confirma las reglas:\n\n{REGLAS_TEXTO}",
            reply_markup=InlineKeyboardMarkup(kbd),
            parse_mode='Markdown'
        )
    except: pass

async def boton_aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = int(query.data.split("_")[1])
    try:
        await context.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=user_id)
        await query.edit_message_text("✅ *ACCESO CONCEDIDO.* ¡Entra ya!", parse_mode='Markdown')
        
        bienvenida = (f"🥳 *¡BIENVENIDO/A A LA FAMILIA!* 🥳\n\n{REGLAS_TEXTO}\n\n"
                      "✨ *Envía tu presentación ahora (Foto, Nombre, Edad y País).*")
        await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=bienvenida, parse_mode='Markdown')
    except: pass

async def monitor_silencioso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_baneados
    if not update.message or not update.message.text: return
    user = update.effective_user
    texto = update.message.text
    
    # 1. Auditoría Secreta
    log = f"👤 {user.first_name} ({user.id}): {texto}"
    auditoria_secreta.append(log)
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    # 2. Filtro de Seguridad
    if any(p in texto.lower() for p in PALABRAS_PROHIBIDAS):
        await update.message.delete()
        warns_usuario[user.id] = warns_usuario.get(user.id, 0) + 1
        if warns_usuario[user.id] >= 3:
            await context.bot.ban_chat_member(chat_id=ID_GRUPO_FIJO, user_id=user.id)
            total_baneados += 1
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"🚫 *BAN:* {user.first_name} ha sido eliminado por sucio.")
        else:
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=f"⚠️ {user.first_name}, borré eso. Warn: {warns_usuario[user.id]}/3")
    else:
        # 3. Interacción Inteligente (Si no es comando ni palabra prohibida)
        if random.random() < 0.15: # 15% de probabilidad de que el bot comente algo
            await responder_con_onda(update, texto)

# --- ⏰ TAREAS AUTOMÁTICAS ---
async def enviar_reglas_auto(context: ContextTypes.DEFAULT_TYPE):
    """Envía las reglas cada 60 minutos al grupo."""
    try:
        await context.bot.send_photo(
            chat_id=ID_GRUPO_FIJO, 
            photo=URL_LOGO, 
            caption=f"⏰ *RECORDATORIO DE REGLAS:*\n\n{REGLAS_TEXTO}",
            parse_mode='Markdown'
        )
    except: pass

# --- 🗝️ COMANDOS EXCLUSIVOS ---

async def comando_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Estadísticas detalladas solo para el dueño."""
    if update.effective_user.id != DUENO_ID: return
    stats = (
        "📊 *REPORTE ESTRATÉGICO ANGERONA:*\n\n"
        f"📝 *Mensajes auditados:* {len(auditoria_secreta)}\n"
        f"⚠️ *Usuarios con advertencias:* {len(warns_usuario)}\n"
        f"🚫 *Total de baneos efectuados:* {total_baneados}\n"
        "🟢 *Estado del Sistema:* Operativo y en Stealth."
    )
    await update.message.reply_text(stats, parse_mode='Markdown')

async def comando_auditoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != DUENO_ID: return
    reporte = "📋 *AUDITORÍA PRIVADA:*\n\n" + "\n".join(auditoria_secreta)
    await update.message.reply_text(reporte[:4000], parse_mode='Markdown')

# --- 🚀 ARRANQUE ---

async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Automatización: Cada 3600 segundos (60 min)
    app.job_queue.run_repeating(enviar_reglas_auto, interval=3600, first=10)
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    app.add_handler(CommandHandler("stats", comando_stats))
    app.add_handler(CommandHandler("auditoria", comando_auditoria))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_silencioso))
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit): pass
