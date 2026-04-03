import os
import random
import threading
import asyncio
from datetime import datetime
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler, ChatMemberHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAEyi_I53_IXrNR1QnTwEaGJ_EV5MptPpRY'
DUENO_ID = 8650569384 
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

auditoria_secreta = [] 
warns = {}
memoria_mensajes = ["¡Este grupo tiene nivel!", "Puro relax.", "Se puso bueno el chisme."]
palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]

# --- 🌐 SERVIDOR WEB ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona 13.5 Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- 📜 REGLAS "VALIENDO MADRES" ---
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

# --- 🎲 BANCO DE JUEGOS REINTEGRADO (+30) ---
LISTA_JUEGOS = [
    "🔥 RETO: Envía un audio gritando '¡VALIENDO MADRES!'",
    "🤫 VERDAD: ¿Quién te parece más atractivo/a del grupo?",
    "🔥 RETO: Cambia tu nombre a 'El Consentido' por 10 minutos.",
    "🤔 VERDAD: ¿Cuál es tu mayor fantasía no cumplida?",
    "🎭 RETO: Envía el sticker más atrevido que tengas.",
    "🤫 VERDAD: ¿Alguna vez te han pillado en algo prohibido?",
    "🔥 RETO: Di un trabalenguas difícil en nota de voz.",
    "💭 VERDAD: ¿Qué es lo primero que miras en una foto?",
    "💃 RETO: Describe tu outfit de hoy con solo 3 emojis.",
    "📸 RETO: Muestra tu última foto de la galería.",
    "🍺 RETO: Cuéntanos tu peor borrachera en un audio.",
    "💔 VERDAD: ¿Cuál ha sido tu peor cita?",
    "🤫 VERDAD: ¿Has stalkeado a alguien del grupo hoy?",
    "🙈 VERDAD: ¿Cuál es tu placer culposo más extraño?",
    "🎁 RETO: Dedica una canción a la última persona que escribió."
] + [f"🎲 Dinámica: ¡Confiesa un secreto o cumple un castigo sorpresa!" for i in range(16)]

# --- 🛡️ FUNCIÓN DE BIENVENIDA ---
async def enviar_bienvenida_oficial(bot, user_name):
    bienvenida = (
        f"🥳 *¡BIENVENIDO {user_name.upper()}!*\n\n"
        f"Ya estás dentro de “VALIENDO MADRES”. Preséntate ahora con:\n\n"
        f"📸 *Foto Real*\n👤 *Nombre*\n🎂 *Edad*\n🌎 *País*\n\n"
        f"⚠️ *Evita ser expulsado cumpliendo con tu presentación.*"
    )
    await bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=bienvenida, parse_mode='Markdown')

# --- 🛡️ MANEJO DE ENTRADAS (UN SOLO BOTÓN) ---
async def manejar_solicitud(u: Update, c: ContextTypes.DEFAULT_TYPE):
    req = u.chat_join_request
    # Enviamos directamente las reglas con el botón de entrada final
    kb = [[InlineKeyboardButton("🤝 ACEPTAR REGLAS Y ENTRAR", callback_data=f"a_{req.from_user.id}")]]
    try:
        await c.bot.send_photo(
            chat_id=req.from_user.id, 
            photo=URL_LOGO, 
            caption=f"🛡️ *CONTROL DE ACCESO VIP*\n\n{REGLAS_TEXTO}", 
            reply_markup=InlineKeyboardMarkup(kb), 
            parse_mode='Markdown'
        )
    except: pass

async def boton_callback(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    data = query.data.split("_")
    action, u_id = data[0], int(data[1])

    if action == "a": 
        try:
            # Aprobación inmediata por el bot
            await c.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
            await query.edit_message_caption(caption="🚀 *¡BIENVENIDO!* Ya eres miembro. Entra al grupo ahora.", parse_mode='Markdown')
            await query.answer("¡Acceso concedido!")
        except Exception as e:
            # Si falla la aprobación automática, el mensaje es discreto
            await query.edit_message_caption(caption="✅ Solicitud procesada. Revisa el grupo en unos momentos.", parse_mode='Markdown')

async def detectar_nuevo_miembro(u: Update, c: ContextTypes.DEFAULT_TYPE):
    """Detecta la entrada (automática o manual) y lanza la bienvenida"""
    result = u.chat_member
    if result.new_chat_member.status in ['member', 'administrator'] and result.old_chat_member.status not in ['member', 'administrator']:
        user_name = result.new_chat_member.user.first_name
        await enviar_bienvenida_oficial(c.bot, user_name)

# --- 🛡️ COMANDOS Y MONITOR ---
async def c_resumen(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if len(memoria_mensajes) < 3: return
    frases = random.sample(memoria_mensajes, 3)
    historia = (
        f"📖 *LA HISTORIA DEL GRUPO:* \n\n"
        f"Resulta que hoy soltaron: *'{frases[0]}'* "
        f"y luego alguien dijo *'{frases[1]}'* "
        f"mientras otros decían *'{frases[2]}'*... "
        f"\n\n¡Por eso y por más, aquí siempre vale madres! 😂🔥"
    )
    await u.message.reply_text(historia, parse_mode='Markdown')

async def monitor_inteligente(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    user, texto = u.effective_user, u.message.text
    auditoria_secreta.append(f"[{datetime.now().strftime('%H:%M')}] 👤 {user.first_name}: {texto}")
    if any(p in texto.lower() for p in palabras_prohibidas): await u.message.delete()
    if len(texto) > 10: memoria_mensajes.append(texto)

# --- 🚀 ARRANQUE ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", lambda u, c: u.message.delete()))
    app.add_handler(CommandHandler("juego", lambda u, c: u.message.reply_text(f"🎲 *JUEGO:* {random.choice(LISTA_JUEGOS)}", parse_mode='Markdown')))
    app.add_handler(CommandHandler("resumen", c_resumen))
    app.add_handler(CommandHandler("auditoria", lambda u, c: u.message.reply_text("\n".join(auditoria_secreta[-20:])) if u.effective_user.id == DUENO_ID else None))
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_callback))
    app.add_handler(ChatMemberHandler(detectar_nuevo_miembro, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_inteligente))
    
    await app.initialize(); await app.start(); await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
                         
