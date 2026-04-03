import os
import asyncio
import threading
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
palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]

# --- 🌐 SERVIDOR WEB ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona Protocolo Base Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 📜 REGLAS OFICIALES ---
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

# --- 🛡️ GESTIÓN DE ACCESO ---
async def manejar_solicitud(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.chat_join_request.from_user
    kb = [[InlineKeyboardButton("🤝 ACEPTAR REGLAS Y ENTRAR", callback_data=f"a_{user.id}")]]
    try:
        await c.bot.send_photo(chat_id=user.id, photo=URL_LOGO, caption=REGLAS_TEXTO, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    except: pass

async def boton_callback(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    u_id = int(query.data.split("_")[1])
    try:
        await c.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
        await query.edit_message_caption(caption="🚀 *ACCESO CONCEDIDO.* ¡Bienvenido al grupo!")
    except:
        await query.edit_message_caption(caption="✅ Solicitud procesada correctamente.")

async def bienvenida_nueva(u: Update, c: ContextTypes.DEFAULT_TYPE):
    result = u.chat_member
    if result.new_chat_member.status in ['member'] and result.old_chat_member.status not in ['member']:
        nombre = result.new_chat_member.user.first_name
        msg = (
            f"🥳 *¡BIENVENIDO {nombre.upper()}!*\n\n"
            f"Ya estás en “VALIENDO MADRES”. Preséntate ahora con:\n"
            f"📸 *Foto Real*\n👤 *Nombre*\n🎂 *Edad*\n🌎 *País*\n\n"
            f"⚠️ *Evita ser expulsado cumpliendo con tu presentación.*"
        )
        await c.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=msg, parse_mode='Markdown')

# --- 📋 AUDITORÍA Y SEGURIDAD ---
async def monitor_seguridad(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    user, texto = u.effective_user, u.message.text
    
    # Auditoría (Últimos 50)
    ahora = datetime.now().strftime("%H:%M")
    auditoria_secreta.append(f"[{ahora}] 👤 {user.first_name}: {texto}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    # Filtro de Palabras
    if any(p in texto.lower() for p in palabras_prohibidas):
        await u.message.delete()
        uid = user.id
        warns[uid] = warns.get(uid, 0) + 1
        if warns[uid] >= 3:
            await c.bot.ban_chat_member(ID_GRUPO_FIJO, uid)
            await c.bot.send_message(ID_GRUPO_FIJO, f"🚫 {user.first_name} expulsado por 3 warns.")
        else:
            await u.message.reply_text(f"⚠️ {user.first_name}, aviso {warns[uid]}/3.")

# --- 🛠️ COMANDOS ADMINISTRATIVOS ---
async def c_unwarn(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id == DUENO_ID and u.message.reply_to_message:
        target_id = u.message.reply_to_message.from_user.id
        warns[target_id] = 0
        await u.message.reply_text("✅ Advertencias reseteadas para el usuario.")

async def c_reglas_privado(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # Solo envía reglas si se le escribe por privado al bot
    if u.message.chat.type == 'private':
        await c.bot.send_photo(chat_id=u.effective_user.id, photo=URL_LOGO, caption=REGLAS_TEXTO, parse_mode='Markdown')

async def c_auditoria(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id == DUENO_ID:
        if not auditoria_secreta:
            return await u.message.reply_text("Historial vacío.")
        await u.message.reply_text("\n".join(auditoria_secreta))

# --- 🚀 ARRANQUE ---
async def main():
    await asyncio.sleep(5) # Pausa de seguridad
    threading.Thread(target=run_flask, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    
    # Handlers de Acceso
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_callback))
    app.add_handler(ChatMemberHandler(bienvenida_nueva, ChatMemberHandler.CHAT_MEMBER))
    
    # Comandos
    app.add_handler(CommandHandler("reglas", c_reglas_privado))
    app.add_handler(CommandHandler("auditoria", c_auditoria))
    app.add_handler(CommandHandler("unwarn", c_unwarn))
    app.add_handler(CommandHandler("start", lambda u, c: None)) # Silencioso
    
    # Monitor
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_seguridad))
    
    await app.initialize(); await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
