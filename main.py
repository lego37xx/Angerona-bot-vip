import os
import asyncio
from datetime import datetime
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler, ChatMemberHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAEYZ2xafcgnmvOMa9Co0NI9I83AT6qReVc'
DUENO_ID = 8650569384 
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"
WEBHOOK_URL = "https://angerona-bot-vip.onrender.com" # Tu URL de Render

auditoria_secreta = [] 
warns = {}
palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]

# --- 📜 REGLAS ---
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

# --- 🌐 SERVER FLASK CON WEBHOOK ---
app_flask = Flask(__name__)
bot_instance = Bot(TOKEN)
application = Application.builder().token(TOKEN).build()

@app_flask.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot_instance)
        await application.process_update(update)
    return 'OK', 200

@app_flask.route('/')
def index(): return "🛡️ Angerona Webhook Activo", 200

# --- 🛡️ LÓGICA DE ACCESO ---
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
        await query.edit_message_caption(caption="🚀 *ACCESO CONCEDIDO.*")
    except: pass

async def bienvenida_nueva(u: Update, c: ContextTypes.DEFAULT_TYPE):
    result = u.chat_member
    if result.new_chat_member.status == 'member' and result.old_chat_member.status != 'member':
        nombre = result.new_chat_member.user.first_name
        msg = f"🥳 *¡BIENVENIDO {nombre.upper()}!*\n\nPresentación obligatoria con Foto y Datos.\n\n⚠️ *Evita ser expulsado.*"
        await c.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=msg, parse_mode='Markdown')

# --- 🛠️ COMANDOS ---
async def c_reglas_al_grupo(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # Si escribes /reglas en el privado del bot, las manda AL GRUPO
    if u.effective_chat.type == 'private' and u.effective_user.id == DUENO_ID:
        await c.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=URL_LOGO, caption=REGLAS_TEXTO, parse_mode='Markdown')
        await u.message.reply_text("✅ Reglas enviadas al grupo exitosamente.")

async def c_auditoria(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id == DUENO_ID:
        if not auditoria_secreta: return await u.message.reply_text("Vacío.")
        await u.message.reply_text("\n".join(auditoria_secreta))

async def monitor_seguridad(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    user, texto = u.effective_user, u.message.text
    auditoria_secreta.append(f"[{datetime.now().strftime('%H:%M')}] 👤 {user.first_name}: {texto}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)
    if any(p in texto.lower() for p in palabras_prohibidas):
        await u.message.delete()

# --- 🚀 CONFIGURACIÓN FINAL ---
application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
application.add_handler(CallbackQueryHandler(boton_callback))
application.add_handler(ChatMemberHandler(bienvenida_nueva, ChatMemberHandler.CHAT_MEMBER))
application.add_handler(CommandHandler("reglas", c_reglas_al_grupo))
application.add_handler(CommandHandler("auditoria", c_auditoria))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_seguridad))

if __name__ == '__main__':
    # Configurar Webhook al arrancar
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(bot_instance.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}"))
    
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)
