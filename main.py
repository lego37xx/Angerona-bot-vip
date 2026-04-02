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

# --- 🌐 SERVER ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP 12.9 Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- 📜 REGLAS ---
REGLAS_TEXTO = (
    "📜🔥 *REGLAS OFICIALES VIP* 🔥📜\n\n"
    "1️⃣ 🚫 *Prohibido menores de edad.*\n"
    "2️⃣ 🤝 *Respeto total entre miembros.*\n"
    "3️⃣ 🚫 *Contenido ilegal = BAN INMEDIATO.*\n"
    "4️⃣ 📸 *Presentación obligatoria.*\n\n"
    "⚠️ *SISTEMA:* 3 warns = Expulsión."
)

# --- 🎲 JUEGOS (MANTENIENDO TODOS) ---
LISTA_JUEGOS = [f"🎲 Dinámica: ¡Confiesa un secreto o cumple un castigo!" for i in range(25)]

# --- 🛡️ LÓGICA DE ENTRADA (REVISADA) ---

async def manejar_solicitud(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.chat_join_request.from_user
    kb = [[InlineKeyboardButton("✅ CONFIRMAR HUMANO", callback_data=f"f_{user.id}")]]
    try:
        await c.bot.send_message(chat_id=user.id, text="🛡️ *ACCESO VIP*\nConfirma que eres humano:", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    except: pass

async def boton_callback(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    data = query.data.split("_")
    action, u_id = data[0], int(data[1])

    if action == "f":
        kb = [[InlineKeyboardButton("🤝 ACEPTAR REGLAS Y ENTRAR", callback_data=f"a_{u_id}")]]
        await c.bot.send_photo(chat_id=u_id, photo=URL_LOGO, caption=REGLAS_TEXTO, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        await query.answer()

    elif action == "a":
        try:
            # INTENTO DE APROBACIÓN
            res = await c.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
            print(f"✅ Aprobación exitosa para {u_id}: {res}")
            
            await query.edit_message_text("🚀 *SOLICITUD APROBADA.* Entra al grupo.")
            
            bienvenida = f"🥳 *¡BIENVENIDO {query.from_user.first_name.upper()}!*\n\nPreséntate con Foto, Nombre y Edad."
            await c.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=bienvenida, parse_mode='Markdown')
        except Exception as e:
            print(f"❌ ERROR CRÍTICO AL APROBAR: {e}")
            await query.edit_message_text(f"⚠️ Error: El bot no tiene permiso para unirte automáticamente. Avisa al Ing. Luis.")

# --- 📝 RESTO DE FUNCIONES (MANTENIDAS) ---
async def c_resumen(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if len(memoria_mensajes) < 2: return
    puntos = random.sample(memoria_mensajes, 2)
    historia = f"📖 *HISTORIA:* Empezaron con *'{puntos[0]}'* y terminaron en *'{puntos[1]}'*... ¡Locura total!"
    await u.message.reply_text(historia, parse_mode='Markdown')

async def monitor_inteligente(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    user, texto = u.effective_user, u.message.text
    auditoria_secreta.append(f"[{datetime.now().strftime('%H:%M')}] 👤 {user.first_name}: {texto}")
    if len(texto) > 10: memoria_mensajes.append(texto)
    if any(p in texto.lower() for p in palabras_prohibidas): await u.message.delete()

# --- 🚀 ARRANQUE ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", lambda u, c: u.message.delete()))
    app.add_handler(CommandHandler("resumen", c_resumen))
    app.add_handler(CommandHandler("juego", lambda u, c: u.message.reply_text(f"🎲 {random.choice(LISTA_JUEGOS)}")))
    app.add_handler(CommandHandler("reglas", lambda u, c: c.bot.send_photo(ID_GRUPO_FIJO, URL_LOGO, REGLAS_TEXTO) if u.effective_user.id == DUENO_ID else None))
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_inteligente))
    
    await app.initialize(); await app.start(); await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
