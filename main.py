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

auditoria_secreta = [] 
warns = {}
memoria_mensajes = ["¡Este grupo tiene nivel!", "Puro VIP aquí.", "Se puso bueno el chisme.", "JAJAJA eso fue épico."]
palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]

# --- 🌐 SERVIDOR WEB ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP 12.3 Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- 📜 REGLAS ---
REGLAS_TEXTO = (
    "📜🔥 *REGLAS OFICIALES VIP* 🔥📜\n\n"
    "1️⃣ 🚫 *Prohibido menores de edad.*\n"
    "2️⃣ 🤝 *Respeto total entre miembros.*\n"
    "3️⃣ 🚫 *Contenido ilegal = BAN INMEDIATO.*\n"
    "4️⃣ 📸 *Presentación obligatoria (Foto, Nombre, Edad, País).*\n\n"
    "⚠️ *SISTEMA:* 3 warns = Expulsión automática."
)

# --- 🎲 BANCO DE JUEGOS (30+ OPCIONES) ---
LISTA_JUEGOS = [
    "🔥 RETO: Envía un audio de 5 segundos gritando '¡SOY VIP!'",
    "🤫 VERDAD: ¿Quién te parece más atractivo/a del grupo?",
    "🔥 RETO: Cambia tu nombre a 'El Consentido' por 10 minutos.",
    "🤔 VERDAD: ¿Cuál es tu mayor fantasía no cumplida?",
    "🎭 RETO: Envía el sticker más atrevido que tengas.",
    "🤫 VERDAD: ¿Alguna vez te han pillado en algo prohibido?",
    "🔥 RETO: Di un trabalenguas difícil en nota de voz.",
    "💭 VERDAD: ¿Qué es lo primero que miras en una foto?",
    "💃 RETO: Describe tu outfit de hoy con solo 3 emojis.",
    "🍋 RETO: Tómate una selfie fingiendo que muerdes un limón.",
    "📱 RETO: Captura de pantalla de tu última búsqueda en Google.",
    "🎤 RETO: Canta 10 segundos de tu canción favorita.",
    "😈 RETO: Di algo 'sucio' al oído de un audio de 3 segundos."
] + [f"🎲 Dinámica: ¡Confiesa un secreto o cumple un castigo sorpresa!" for i in range(15)]

# --- 🛡️ FUNCIONES ---
async def post_init(application: Application):
    comandos = [
        BotCommand("start", "🚀 Activar Sistema"),
        BotCommand("juego", "🎲 Verdad o Reto"),
        BotCommand("reglas", "📜 Publicar Reglas"),
        BotCommand("resumen", "📝 El Chisme Narrado"),
        BotCommand("auditoria", "📋 Bitácora (Dueño)")
    ]
    await application.bot.set_my_commands(comandos)

async def c_start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    try: await u.message.delete()
    except: pass
    await u.message.reply_text(f"🛡️ *¡SISTEMA ONLINE!*\n\nHola *{u.effective_user.first_name}*, estoy listo. Usa el menú para interactuar.", parse_mode='Markdown')

# --- 📝 FUNCIÓN DE RESUMEN NARRATIVO (PUNTO 4 MEJORADO) ---
async def c_resumen(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if len(memoria_mensajes) < 3:
        return await u.message.reply_text("Todavía no hay suficiente chisme para armar una historia.")
    
    frases = random.sample(memoria_mensajes, 3)
    conectores_inicio = ["Resulta que hoy el grupo amaneció intenso,", "No me lo van a creer, pero todo empezó cuando", "El ambiente se puso pesado porque"]
    conectores_medio = [" y luego alguien soltó que", ", justo después de que dijeron que", ", mientras el otro gritaba que"]
    conectores_final = [" y para cerrar con broche de oro,", " pero al final lo más loco fue cuando", " total que acabaron diciendo que"]

    historia = (
        f"📖 *LA HISTORIA DEL GRUPO:* \n\n"
        f"{random.choice(conectores_inicio)} *'{frases[0]}'* "
        f"{random.choice(conectores_medio)} *'{frases[1]}'* "
        f"{random.choice(conectores_final)} *'{frases[2]}'*... "
        f"¡En fin, este VIP es pura locura! 😂🔥"
    )
    await u.message.reply_text(historia, parse_mode='Markdown')

async def c_reglas(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id == DUENO_ID:
        await c.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=REGLAS_TEXTO, parse_mode='Markdown')
    else:
        await c.bot.send_photo(chat_id=u.effective_user.id, photo=URL_LOGO, caption=REGLAS_TEXTO, parse_mode='Markdown')

async def manejar_solicitud(u: Update, c: ContextTypes.DEFAULT_TYPE):
    req = u.chat_join_request
    kb = [[InlineKeyboardButton("✅ CONFIRMAR HUMANO", callback_data=f"filtro_{req.from_user.id}")]]
    try:
        await c.bot.send_message(chat_id=req.from_user.id, text="🛡️ *CONTROL DE ACCESO VIP*\nConfirma que no eres un bot:", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    except: pass

async def boton_filtro(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    u_id = int(query.data.split("_")[1])
    await c.bot.send_photo(chat_id=u_id, photo=URL_LOGO, caption=f"✅ Filtro pasado.\n\n{REGLAS_TEXTO}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤝 SOLICITAR ENTRADA", callback_data=f"adm_{u_id}")]]), parse_mode='Markdown')
    await query.edit_message_text("Filtro superado. Revisa el mensaje de abajo.")

async def boton_aprobar(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    u_id = int(query.data.split("_")[1])
    try:
        await c.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
        await query.edit_message_text("🚀 *SOLICITUD PROCESADA.*")
        bienvenida = f"🥳 *¡BIENVENIDO {query.from_user.first_name.upper()}!*\n\nPreséntate con:\n📸 *Foto Real*\n👤 *Nombre*\n🎂 *Edad*\n🌎 *País*"
        await c.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=bienvenida, parse_mode='Markdown')
    except: pass

async def monitor_inteligente(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    user, texto, ahora = u.effective_user, u.message.text, datetime.now().strftime("%H:%M:%S")

    auditoria_secreta.append(f"[{ahora}] 👤 {user.first_name}: {texto}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    if any(p in texto.lower() for p in palabras_prohibidas):
        await u.message.delete()
        uid = user.id
        warns[uid] = warns.get(uid, 0) + 1
        if warns[uid] >= 3:
            await c.bot.ban_chat_member(ID_GRUPO_FIJO, uid)
            await c.bot.send_message(ID_GRUPO_FIJO, f"🚫 {user.first_name} expulsado.")
        else:
            await u.message.reply_text(f"⚠️ {user.first_name}, aviso {warns[uid]}/3.")

    if len(texto) > 10 and texto not in memoria_mensajes:
        memoria_mensajes.append(texto)
        if len(memoria_mensajes) > 80: memoria_mensajes.pop(0)
    
    # Interacción aleatoria (Punto 4)
    if random.random() < 0.05:
        await u.message.reply_text(f"Oye {user.first_name}, me guardaré eso de '{texto}' para el resumen de mañana... 😏")

# --- 🚀 ARRANQUE ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", c_start))
    app.add_handler(CommandHandler("reglas", c_reglas))
    app.add_handler(CommandHandler("juego", lambda u, c: u.message.reply_text(f"🎲 *JUEGO:* {random.choice(LISTA_JUEGOS)}", parse_mode='Markdown')))
    app.add_handler(CommandHandler("resumen", c_resumen))
    app.add_handler(CommandHandler("auditoria", lambda u, c: u.message.reply_text("\n".join(auditoria_secreta)) if u.effective_user.id == DUENO_ID else None))
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_filtro, pattern="^filtro_"))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_inteligente))
    await app.initialize(); await app.start(); await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
