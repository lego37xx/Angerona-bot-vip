import os
import asyncio
import threading
from datetime import datetime
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler, ChatMemberHandler

# --- ⚙️ CONFIGURACIÓN ---
# Token actualizado por el usuario
TOKEN = '8616684285:AAEYZ2xafcgnmvOMa9Co0NI9I83AT6qReVc'
DUENO_ID = 8650569384 
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

auditoria_secreta = [] 
warns = {}
palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]

# --- 🌐 SERVIDOR WEB (Para Render) ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona Protocolo Base - Online", 200

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

# --- 🛡️ GESTIÓN DE ACCESO (UN SOLO CLIC) ---
async def manejar_solicitud(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.chat_join_request.from_user
    kb = [[InlineKeyboardButton("🤝 ACEPTAR REGLAS Y ENTRAR", callback_data=f"a_{user.id}")]]
    try:
        # Envía las reglas al privado del usuario que solicita entrar
        await c.bot.send_photo(chat_id=user.id, photo=URL_LOGO, caption=REGLAS_TEXTO, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    except: pass

async def boton_callback(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    u_id = int(query.data.split("_")[1])
    try:
        # El bot aprueba la solicitud
        await c.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
        await query.edit_message_caption(caption="🚀 *ACCESO CONCEDIDO.* ¡Bienvenido al grupo!")
    except:
        await query.edit_message_caption(caption="✅ Solicitud procesada.")

async def bienvenida_nueva(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # Detecta entrada al grupo (sea por el bot o manual)
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

# --- 📋 SEGURIDAD Y AUDITORÍA ---
async def monitor_seguridad(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    user, texto = u.effective_user, u.message.text
    
    # Registro en Auditoría (Solo últimos 50 mensajes)
    ahora = datetime.now().strftime("%H:%M")
    auditoria_secreta.append(f"[{ahora}] 👤 {user.first_name}: {texto}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    # Filtro de Palabras Prohibidas
    if any(p in texto.lower() for p in palabras_prohibidas):
        await u.message.delete()
        uid = user.id
        warns[uid] = warns.get(uid, 0) + 1
        if warns[uid] >= 3:
            await c.bot.ban_chat_member(ID_GRUPO_FIJO, uid)
            await c.bot.send_message(ID_GRUPO_FIJO, f"🚫 {user.first_name} expulsado por acumular 3 advertencias.")
        else:
            await u.message.reply_text(f"⚠️ {user.first_name}, aviso {warns[uid]}/3 por lenguaje no permitido.")

# --- 🛠️ COMANDOS ---
async def c_unwarn(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # Resetea advertencias al responder a un mensaje
    if u.effective_user.id == DUENO_ID and u.message.reply_to_message:
        target_id = u.message.reply_to_message.from_user.id
        warns[target_id] = 0
        await u.message.reply_text("✅ Advertencias reseteadas.")

async def c_reglas_privado(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # Solo responde por chat privado con el bot
    if u.message.chat.type == 'private':
        await c.bot.send_photo(chat_id=u.effective_user.id, photo=URL_LOGO, caption=REGLAS_TEXTO, parse_mode='Markdown')

async def c_auditoria(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # Solo para el dueño
    if u.effective_user.id == DUENO_ID:
        if not auditoria_secreta:
            return await u.message.reply_text("Historial de mensajes vacío.")
        await u.message.reply_text("📋 *AUDITORÍA ÚLTIMOS 50 MSJS:*\n\n" + "\n".join(auditoria_secreta), parse_mode='Markdown')

# --- 🚀 ARRANQUE ---
async def main():
    # Pausa inicial de seguridad para evitar Conflict
    await asyncio.sleep(5) 
    
    threading.Thread(target=run_flask, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    
    # Handlers de Entrada
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_callback))
    app.add_handler(ChatMemberHandler(bienvenida_nueva, ChatMemberHandler.CHAT_MEMBER))
    
    # Comandos Administrativos
    app.add_handler(CommandHandler("reglas", c_reglas_privado))
    app.add_handler(CommandHandler("auditoria", c_auditoria))
    app.add_handler(CommandHandler("unwarn", c_unwarn))
    app.add_handler(CommandHandler("start", lambda u, c: None)) # No responde nada al usuario
    
    # Monitor de Seguridad
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_seguridad))
    
    await app.initialize(); await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    # Mantener el script vivo
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
    
