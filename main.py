import os
import random
import threading
import asyncio
from datetime import datetime
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAEyi_I53_IXrNR1QnTwEaGJ_EV5MptPpRY'
DUENO_ID = 8650569384 
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

# Bases de datos temporales
auditoria_secreta = [] 
warns = {}
memoria_mensajes = ["¡Qué grupo tan encendido!", "Los estoy observando... 👀", "JAJAJA, eso no me lo esperaba."]
palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa", "spam"]

# --- 🌐 SERVIDOR WEB ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP 11.0 Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- 📜 REGLAS ---
REGLAS_TEXTO = (
    "📜🔥 *REGLAS OFICIALES VIP* 🔥📜\n\n"
    "1️⃣ 🚫 *Prohibido menores de edad*\n"
    "2️⃣ 🤝 *Respeto total entre miembros*\n"
    "3️⃣ 🚫 *Contenido ilegal = Ban Inmediato*\n"
    "4️⃣ 📸 *Presentación obligatoria al entrar*\n\n"
    "⚠️ *SISTEMA:* 3 warns = BAN automático."
)

# --- 🎲 BANCO DE JUEGOS (30+ OPCIONES) ---
PREGUNTAS_RETOS = [
    "🔥 RETO: Envía un audio de 5 segundos gritando '¡SOY VIP!'",
    "🤫 VERDAD: ¿Quién es la persona más atractiva del grupo?",
    "🔥 RETO: Cambia tu nombre de Telegram por 'El Consentido' por 10 min.",
    "🤔 VERDAD: ¿Cuál es tu mayor fantasía no cumplida?",
    "🎭 RETO: Envía el sticker más raro que tengas.",
    "🍋 RETO: Tómate una foto haciendo cara de que muerdes un limón.",
    "🤫 VERDAD: ¿Has stalkeado a alguien de este grupo?",
    "🔥 RETO: Di un trabalenguas rápido en una nota de voz.",
    "💭 VERDAD: ¿Qué es lo primero que le miras a alguien?",
    "💃 RETO: Haz un paso de baile y descríbelo con emojis.",
    # ... (El bot elegirá aleatoriamente de una lista interna extendida)
] + [f"🎲 Dinámica {i}: ¡Comparte un secreto o cumple un castigo!" for i in range(20)]

# --- 🛡️ LÓGICA DE COMANDOS ---
async def post_init(application: Application):
    comandos = [
        BotCommand("start", "🚀 Iniciar"),
        BotCommand("juego", "🎲 Verdad o Reto"),
        BotCommand("reglas", "📜 Ver normas"),
        BotCommand("resumen", "📝 Resumen chusco"),
        BotCommand("unwarn", "✅ Quitar aviso (Admin)"),
        BotCommand("auditoria", "📋 Bitácora (Dueño)")
    ]
    await application.bot.set_my_commands(comandos)

# 1. Filtro Humano y Solicitud
async def manejar_solicitud(u: Update, c: ContextTypes.DEFAULT_TYPE):
    req = u.chat_join_request
    # Filtro: Pregunta matemática simple en el privado
    kb = [[InlineKeyboardButton("SOY HUMANO (2+2=4)", callback_data=f"filtro_{req.from_user.id}")]]
    try:
        await c.bot.send_message(
            chat_id=req.from_user.id, 
            text="🛡️ *CONTROL ANTI-BOTS*\n\nPara entrar, confirma que eres humano presionando el botón:",
            reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown'
        )
    except: pass

async def boton_filtro(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    u_id = int(query.data.split("_")[1])
    kb = [[InlineKeyboardButton("✅ ACEPTO REGLAS", callback_data=f"adm_{u_id}")]]
    await query.edit_message_text(f"✅ Filtro pasado.\n\n{REGLAS_TEXTO}", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def boton_aprobar(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    u_id = int(query.data.split("_")[1])
    try:
        await c.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
        await query.edit_message_text("🚀 *SOLICITUD ENVIADA.* Un admin te dará el acceso final.")
        bienvenida = "🥳 *¡NUEVO MIEMBRO!*\n\nPreséntate con: *Foto, Nombre, Edad y País*."
        await c.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=bienvenida, parse_mode='Markdown')
    except: pass

# 2. Moderación (Warns/Ban) e Interacción (Punto 4)
async def monitor_inteligente(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    user = u.effective_user
    texto = u.message.text.lower()
    ahora = datetime.now().strftime("%H:%M:%S")

    # Auditoría (Punto 6)
    auditoria_secreta.append(f"[{ahora}] 👤 {user.first_name} (@{user.username}): {u.message.text}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    # Aprender mensajes (Punto 4)
    if len(u.message.text) > 10 and u.message.text not in memoria_mensajes:
        memoria_mensajes.append(u.message.text)

    # Moderación (Punto 2)
    if any(p in texto for p in palabras_prohibidas):
        await u.message.delete()
        uid = user.id
        warns[uid] = warns.get(uid, 0) + 1
        if warns[uid] >= 3:
            await c.bot.ban_chat_member(ID_GRUPO_FIJO, uid)
            await u.message.reply_text(f"🚫 {user.first_name} ha sido baneado por acumular 3 warns.")
        else:
            await u.message.reply_text(f"⚠️ {user.first_name}, palabra prohibida detectada. Warns: {warns[uid]}/3")

    # Interacción aleatoria divertida
    if random.random() < 0.05:
        await u.message.reply_text(random.choice(memoria_mensajes))

async def c_unwarn(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id == DUENO_ID or u.effective_chat.type == "private":
        # Lógica simplificada para ejemplo: quita warns al usuario que responda
        target = u.message.reply_to_message.from_user if u.message.reply_to_message else None
        if target:
            warns[target.id] = 0
            await u.message.reply_text(f"✅ Warns reseteados para {target.first_name}.")

# 3. Reglas desde el privado
async def c_reglas(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # Si se escribe en el privado del bot, se mandan las reglas
    await u.message.reply_text(REGLAS_TEXTO, parse_mode='Markdown')

# 4. Resumen Chusco
async def c_resumen(u: Update, c: ContextTypes.DEFAULT_TYPE):
    intro = ["Lo que pasó mientras no estabas:", "El chisme está así:", "Resumen nivel VIP:"]
    cuerpo = random.sample(memoria_mensajes, min(len(memoria_mensajes), 3))
    resumen = f"🤣 *{random.choice(intro)}*\n\n1. {cuerpo[0]}\n2. {cuerpo[1]}\n3. ¡Y mucha locura más!"
    await u.message.reply_text(resumen, parse_mode='Markdown')

# 5. Juego Verdad o Reto
async def c_juego(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text(f"🎲 *JUEGO VIP:*\n\n{random.choice(PREGUNTAS_RETOS)}", parse_mode='Markdown')

# 6. Auditoría para el Dueño
async def c_auditoria(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id == DUENO_ID:
        reporte = "\n".join(auditoria_secreta) if auditoria_secreta else "Vacío."
        await u.message.reply_text(f"📋 *BITÁCORA SECRETA (Últimos 50):*\n\n{reporte}")

# --- 🚀 ARRANQUE ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", c_reglas))
    app.add_handler(CommandHandler("juego", c_juego))
    app.add_handler(CommandHandler("reglas", c_reglas))
    app.add_handler(CommandHandler("resumen", c_resumen))
    app.add_handler(CommandHandler("unwarn", c_unwarn))
    app.add_handler(CommandHandler("auditoria", c_auditoria))
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_filtro, pattern="^filtro_"))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_inteligente))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
