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
memoria_mensajes = ["¡Este grupo tiene nivel!", "Puro VIP aquí.", "Se puso bueno el chisme."]
palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]

# --- 🌐 SERVIDOR WEB ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP 11.5 Online", 200

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

# --- 🎲 JUEGOS (30+ PREGUNTAS) ---
PREGUNTAS_RETOS = [
    "🔥 RETO: Envía un audio de 5 segundos gritando '¡SOY VIP!'",
    "🤫 VERDAD: ¿Quién te parece más interesante del grupo?",
    "🔥 RETO: Cambia tu nombre a 'El Consentido' por 10 minutos.",
    "🤔 VERDAD: ¿Cuál es tu mayor fantasía?",
    "🎭 RETO: Envía el sticker más atrevido que tengas.",
    "🤫 VERDAD: ¿Alguna vez te han pillado haciendo algo prohibido?",
    "🔥 RETO: Di un trabalenguas difícil en nota de voz.",
    "💭 VERDAD: ¿Qué es lo primero que miras en una foto?",
    "💃 RETO: Describe tu outfit actual con solo 3 emojis.",
    "🍋 RETO: Tómate una selfie fingiendo que muerdes un limón."
] + [f"🎲 Dinámica {i}: ¡Confiesa un secreto o cumple un castigo!" for i in range(20)]

# --- 🛡️ FUNCIONES ---
async def post_init(application: Application):
    comandos = [
        BotCommand("start", "🚀 Iniciar"),
        BotCommand("juego", "🎲 Verdad o Reto"),
        BotCommand("reglas", "📜 Publicar reglas (Admin)"),
        BotCommand("resumen", "📝 Resumen chusco"),
        BotCommand("auditoria", "📋 Bitácora (Solo Dueño)")
    ]
    await application.bot.set_my_commands(comandos)

async def c_reglas(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # Corrección: Envía el logo con las reglas al grupo si el admin lo pide
    if u.effective_user.id == DUENO_ID:
        await c.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=REGLAS_TEXTO, parse_mode='Markdown')
        if u.effective_chat.type == "private":
            await u.message.reply_text("✅ Reglas publicadas en el grupo.")
    else:
        await u.message.reply_text("⚠️ Solo el administrador puede ejecutar este comando.")

async def manejar_solicitud(u: Update, c: ContextTypes.DEFAULT_TYPE):
    req = u.chat_join_request
    kb = [[InlineKeyboardButton("🤖 SOY HUMANO (Confirmar)", callback_data=f"filtro_{req.from_user.id}")]]
    try:
        await c.bot.send_message(chat_id=req.from_user.id, text="🛡️ *FILTRO ANTI-BOTS*\nPresiona para continuar:", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    except: pass

async def boton_filtro(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    u_id = int(query.data.split("_")[1])
    # Envía reglas y logo en el privado tras el filtro
    await c.bot.send_photo(chat_id=u_id, photo=URL_LOGO, caption=f"✅ Filtro superado.\n\n{REGLAS_TEXTO}", parse_mode='Markdown')
    await query.edit_message_text("👍 Gracias. Un administrador revisará tu perfil.")

async def monitor_inteligente(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    user, texto = u.effective_user, u.message.text
    ahora = datetime.now().strftime("%H:%M:%S")

    auditoria_secreta.append(f"[{ahora}] 👤 {user.first_name}: {texto}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    if any(p in texto.lower() for p in palabras_prohibidas):
        await u.message.delete()
        uid = user.id
        warns[uid] = warns.get(uid, 0) + 1
        if warns[uid] >= 3:
            await c.bot.ban_chat_member(ID_GRUPO_FIJO, uid)
            await c.bot.send_message(ID_GRUPO_FIJO, f"🚫 {user.first_name} baneado por 3 warns.")
        else:
            await u.message.reply_text(f"⚠️ {user.first_name}, aviso {warns[uid]}/3 por palabra prohibida.")

    if len(texto) > 15 and texto not in memoria_mensajes:
        memoria_mensajes.append(texto)
        if len(memoria_mensajes) > 100: memoria_mensajes.pop(0)

async def c_resumen(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if len(memoria_mensajes) < 3:
        return await u.message.reply_text("Aún no tengo suficiente chisme para un resumen.")
    puntos = random.sample(memoria_mensajes, 3)
    res = f"🤣 *RESUMEN CHUSCO DEL MOMENTO:*\n\n1️⃣ {puntos[0]}\n2️⃣ {puntos[1]}\n3️⃣ {puntos[2]}\n\n¡Sigan con el desmadre! 🔥"
    await u.message.reply_text(res, parse_mode='Markdown')

async def c_auditoria(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id == DUENO_ID:
        reporte = "\n".join(auditoria_secreta) if auditoria_secreta else "Vacío."
        await u.message.reply_text(f"📋 *AUDITORÍA (Dueño):*\n\n{reporte}")

# --- 🚀 ARRANQUE ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("reglas", c_reglas))
    app.add_handler(CommandHandler("juego", lambda u, c: u.message.reply_text(f"🎲 *JUEGO:* {random.choice(PREGUNTAS_RETOS)}", parse_mode='Markdown')))
    app.add_handler(CommandHandler("resumen", c_resumen))
    app.add_handler(CommandHandler("auditoria", c_auditoria))
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_filtro, pattern="^filtro_"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_inteligente))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
