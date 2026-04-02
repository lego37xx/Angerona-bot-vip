import os
import random
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler, CallbackQueryHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAHF7JAV66o2CIOpgUynYMLIyUo-TWX_0AA'
DUENO_ID = 8650569384 
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

memoria_neural = ["Interesante...", "Los observo.", "Bitácora actualizada."]
auditoria_secreta = [] 
warns_usuario = {}

# --- 🌐 SERVIDOR KEEP-ALIVE ---
web_app = Flask('')
@web_app.route('/')
def home(): return "🛡️ Angerona VIP 9.0 - Sistema Operativo", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 📜 REGLAS ---
REGLAS_TEXTO = (
    "📜🔥 *REGLAS OFICIALES VIP* 🔥📜\n\n"
    "1️⃣ 🚫 *Prohibido menores de edad*\n"
    "2️⃣ 🤝 *Respeto total entre miembros*\n"
    "3️⃣ 🚫 *Cero contenido ilegal*\n\n"
    "⚠️ *SISTEMA:* 3 warns = BAN automático."
)

# --- 🧠 INTELIGENCIA Y SEGURIDAD ---
async def monitor_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user = update.effective_user
    texto = update.message.text
    
    auditoria_secreta.append(f"👤 {user.first_name}: {texto}")
    if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)

    if any(p in texto.lower() for p in ["gore", "cp", "zoofilia"]):
        try: await update.message.delete()
        except: pass
        return

    if random.random() < 0.10:
        await update.message.reply_text(random.choice(memoria_neural))

# --- 🎲 JUEGOS ---
async def j_juego(u, c):
    opciones = ["🔥 *RETO:* Di algo atrevido.", "🤔 *ADIVINANZA:* ¿Qué tiene cuello pero no cabeza? (R: Una camisa)"]
    await u.message.reply_text(random.choice(opciones), parse_mode='Markdown')

# --- 🛡️ GESTIÓN DE ACCESO Y BIENVENIDA ---
async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    kbd = [[InlineKeyboardButton("✅ ACEPTO LAS REGLAS", callback_data=f"adm_{req.from_user.id}")]]
    try:
        await context.bot.send_message(
            chat_id=req.from_user.id, 
            text=f"👋 Hola. Para ser admitido en el grupo VIP, debes aceptar las normas:\n\n{REGLAS_TEXTO}", 
            reply_markup=InlineKeyboardMarkup(kbd), 
            parse_mode='Markdown'
        )
    except: pass

async def boton_aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    u_id = int(query.data.split("_")[1])
    user_obj = query.from_user # El usuario que aceptó las reglas

    try:
        # 1. Aprobar al usuario en el grupo
        await context.bot.approve_chat_join_request(chat_id=ID_GRUPO_FIJO, user_id=u_id)
        
        # 2. Confirmar en el privado del usuario
        await query.edit_message_text("✅ *ACCESO CONCEDIDO.* Ya puedes entrar al grupo.")
        
        # 3. Bienvenida formal en el grupo con solicitud de datos
        bienvenida = (
            f"🥳 *¡NUEVO MIEMBRO ADMITIDO!* 🥳\n\n"
            f"Bienvenido/a al círculo VIP. Para mantener tu lugar, preséntate ahora mismo enviando:\n\n"
            f"📸 *Foto Real*\n"
            f"👤 *Nombre*\n"
            f"🎂 *Edad*\n"
            f"🌎 *País*\n\n"
            f"⚠️ _Si no te presentas, el sistema podría considerar tu cuenta como inactiva._"
        )
        await context.bot.send_photo(
            chat_id=ID_GRUPO_FIJO, 
            photo=URL_LOGO, 
            caption=bienvenida, 
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error al aprobar: {e}")

# --- 🚀 ARRANQUE SEGURO ---
async def start_bot():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^adm_"))
    app.add_handler(CommandHandler("juego", j_juego))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_total))
    
    async with app:
        await app.initialize()
        await app.start()
        print("🛡️ Angerona 9.0: Polling activo con Bienvenida Automática.")
        await app.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit): pass
