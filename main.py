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
memoria_mensajes = ["¡Este grupo tiene nivel!", "Puro relax.", "Se puso bueno el chisme.", "Eso fue épico."]
palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]

# --- 🌐 SERVIDOR WEB ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona 13.3 Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- 📜 REGLAS "VALIENDO MADRES" (RECUPERADAS) ---
REGLAS_TEXTO = (
    "📜🔥 *REGLAS OFICIALES – “VALIENDO MADRES”* 🔥📜\n\n"
    "1️⃣ 🚫 *Prohibido menores de edad*\n"
    "2️⃣ 🤝 *Respeto ante todo*\n"
    "3️⃣ 📳 *Nada de privados sin permiso*\n"
    "4️⃣ 🚫 *Cero contenido ilegal o enfermizo*\n"
    "5️⃣ 😂 *Aquí se viene a convivir*\n"
    "6️⃣ 🔥 *Se vale picar… pero no pasarse*\n\n"
    "⚠️ *PRESENTACIÓN OBLIGATORIA:*\n"
    "Foto, Nombre, Edad y País."
)

# --- 🎲 BANCO EXTENSO DE JUEGOS (+30 OPCIONES REINTEGRADAS) ---
LISTA_JUEGOS = [
    "🔥 RETO: Envía un audio de 5 segundos gritando '¡VALIENDO MADRES!'",
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
    "😈 RETO: Di algo 'sucio' al oído en un audio de 3 segundos.",
    "📸 RETO: Muestra tu última foto de la galería (sin trampas).",
    "📝 VERDAD: ¿Qué es lo que más te gusta de estar en este grupo?",
    "🃏 RETO: Elige a alguien del grupo y dile un piropo pesado.",
    "👣 RETO: Foto de tus pies o manos ahora mismo.",
    "🍺 RETO: Cuéntanos tu peor borrachera en un audio.",
    "💔 VERDAD: ¿Cuál ha sido tu peor cita?",
    "🤫 VERDAD: ¿Has stalkeado a alguien del grupo hoy?",
    "🎁 RETO: Dedica una canción a la última persona que escribió.",
    "🔥 RETO: Pon una frase picante en tu biografía de Telegram por 1 hora.",
    "🤔 VERDAD: ¿Qué harías si te quedas a solas con el admin?",
    "👄 RETO: Envía un sticker que represente tu estado de ánimo actual.",
    "🙈 VERDAD: ¿Cuál es tu placer culposo más extraño?",
    "🥂 RETO: Haz un brindis por el grupo en una nota de voz."
] + [f"🎲 Dinámica Especial: ¡Confiesa un secreto o cumple un castigo sorpresa!" for i in range(10)]

# --- 🛡️ COMANDOS ---
async def post_init(application: Application):
    comandos = [
        BotCommand("start", "🚀 Activar Sistema"),
        BotCommand("juego", "🎲 Verdad o Reto"),
        BotCommand("reglas", "📜 Publicar Reglas"),
        BotCommand("resumen", "📝 El Chisme Narrado"),
        BotCommand("auditoria", "📋 Bitácora (Dueño)"),
        BotCommand("unwarn", "✅ Quitar avisos (Responder a msg)")
    ]
    await application.bot.set_my_commands(comandos)

async def c_start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    try: await u.message.delete()
    except: pass
    await u.message.reply_text(f"🛡️ *SISTEMA ANGERONA ONLINE*\n\nHola *{u.effective_user.first_name}*, gestión lista.", parse_mode='Markdown')

# --- 📝 RESUMEN (REAJUSTADO) ---
async def c_resumen(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if len(memoria_mensajes) < 3: return await u.message.reply_text("Poco chisme aún.")
    frases = random.sample(memoria_mensajes, 3)
    historia = (
        f"📖 *LA HISTORIA DEL GRUPO:* \n\n"
        f"Resulta que hoy el grupo amaneció intenso cuando alguien soltó: *'{frases[0]}'* "
        f"y de repente otro respondió que *'{frases[1]}'* "
        f"mientras todos cerraban con que *'{frases[2]}'*... "
        f"\n\n¡Por eso y por más, aquí siempre vale madres! 😂🔥"
    )
    await u.message.reply_text(historia, parse_mode='Markdown')

# --- 🛡️ ACCESO Y ACEPTACIÓN ---
async def manejar_solicitud(u: Update, c: ContextTypes.DEFAULT_TYPE):
    req = u.chat_join_request
    kb = [[InlineKeyboardButton("✅ CONFIRMAR HUMANO", callback_data=f"f_{req.from_user.id}")]]
    try:
        await c.bot.send_message(chat_id=req.from_user.id, text="🛡️ *CONTROL DE ACCESO*\nConfirma que no eres un bot:", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    except: pass

async def boton_callback(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    data = query.data.split("_")
    action, u_id = data[0], int(data[1])

    if action == "f": 
        kb = [[InlineKeyboardButton("🤝 ACEPTAR REGLAS Y ENTRAR", callback_data=f"a_{u_id}")]]
        await c.bot.send_photo(chat_id=u_id, photo=URL_LOGO, caption=f"✅ Filtro superado.\n\n{REGLAS_TEXTO}", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        await query.answer()
        await query.edit_message_text("✅ Humano confirmado. Acepta las reglas abajo.")

    elif action == "a": 
        try:
            await c.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
            await query.edit_message_text("🚀 *¡BIENVENIDO!* Ya estás dentro. Ve al grupo.")
            
            bienvenida = (
                f"🥳 *¡BIENVENIDO {query.from_user.first_name.upper()}!*\n\n"
                f"Ya estás dentro de “VALIENDO MADRES”. Preséntate ahora con:\n\n"
                f"📸 *Foto Real*\n👤 *Nombre*\n🎂 *Edad*\n🌎 *País*\n\n"
                f"⚠️ *Evita ser expulsado cumpliendo con tu presentación.*"
            )
            await c.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=bienvenida, parse_mode='Markdown')
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}")

# --- 📋 AUDITORÍA Y MONITOR (REINTEGRADO) ---
async def monitor_inteligente(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    user, texto, ahora = u.effective_user, u.message.text, datetime.now().strftime("%H:%M:%S")
    
    # Auditoría Secreta
    auditoria_secreta.append(f"[{ahora}] 👤 {user.first_name}: {texto}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    # Filtro de palabras y Warns
    if any(p in texto.lower() for p in palabras_prohibidas):
        await u.message.delete()
        uid = user.id
        warns[uid] = warns.get(uid, 0) + 1
        if warns[uid] >= 3:
            await c.bot.ban_chat_member(ID_GRUPO_FIJO, uid)
            await c.bot.send_message(ID_GRUPO_FIJO, f"🚫 {user.first_name} expulsado por acumular 3 advertencias.")
        else:
            await u.message.reply_text(f"⚠️ {user.first_name}, aviso {warns[uid]}/3 por lenguaje prohibido.")
        return

    # Memoria para el resumen
    if len(texto) > 10 and texto not in memoria_mensajes:
        memoria_mensajes.append(texto)
        if len(memoria_mensajes) > 80: memoria_mensajes.pop(0)
    
    # Interacción aleatoria
    if random.random() < 0.04:
        await u.message.reply_text(f"Oye {user.first_name}, anotado para el chisme... 😏")

# --- 🚀 ARRANQUE ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", c_start))
    app.add_handler(CommandHandler("reglas", lambda u, c: c.bot.send_photo(ID_GRUPO_FIJO, URL_LOGO, REGLAS_TEXTO) if u.effective_user.id == DUENO_ID else None))
    app.add_handler(CommandHandler("juego", lambda u, c: u.message.reply_text(f"🎲 *JUEGO:* {random.choice(LISTA_JUEGOS)}", parse_mode='Markdown')))
    app.add_handler(CommandHandler("resumen", c_resumen))
    app.add_handler(CommandHandler("auditoria", lambda u, c: u.message.reply_text("\n".join(auditoria_secreta)) if u.effective_user.id == DUENO_ID else None))
    app.add_handler(CommandHandler("unwarn", lambda u, c: (warns.update({u.message.reply_to_message.from_user.id: 0}) or u.message.reply_text("✅ Reset de advertencias.")) if u.effective_user.id == DUENO_ID and u.message.reply_to_message else None))
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_inteligente))
    
    await app.initialize(); await app.start(); await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
