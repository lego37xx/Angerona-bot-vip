import os
import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatJoinRequestHandler

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAH4NBmcFs-ZTnUvIRhLMkahBcf49i0tBDUMzn6L1k'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
NOMBRE_FOTO = 'logo.png'
PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]

# Diccionario temporal para guardar quién pidió entrar {user_id: chat_id}
solicitudes_pendientes = {}

web_app = Flask('')
@web_app.route('/')
def home(): return "Angerona: Portería Automática Activa. 🛡️"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 🛡️ FUNCIONES ---

async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la solicitud y manda el botón de verificación al privado"""
    request = update.chat_join_request
    user = request.from_user
    chat_id = request.chat.id
    
    # Guardamos la solicitud en memoria
    solicitudes_pendientes[user.id] = chat_id
    
    keyboard = [[InlineKeyboardButton("✅ Verificarme para Entrar", url=f"https://t.me/{(await context.bot.get_me()).username}?start=verificar")]]
    
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=(
                f"🛡️ *SISTEMA DE SEGURIDAD ANGERONA*\n\n"
                f"Hola {user.first_name}, has solicitado entrar al grupo.\n"
                "Para ser aceptado automáticamente, toca el botón de abajo y dale a 'Iniciar'."
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except:
        # Si tiene el privado cerrado, no podemos enviarle el link
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la verificación y aprueba al usuario"""
    user = update.effective_user
    args = context.args
    
    if args and args[0] == "verificar":
        if user.id in solicitudes_pendientes:
            group_id = solicitudes_pendientes[user.id]
            try:
                # --- 🔑 ACCIÓN MAESTRA: EL BOT APRUEBA AL USUARIO ---
                await context.bot.approve_chat_join_request(chat_id=group_id, user_id=user.id)
                
                await update.message.reply_text("✅ *¡Verificado!* He aprobado tu solicitud. Ya puedes entrar al grupo.")
                
                # Limpiamos de memoria
                del solicitudes_pendientes[user.id]
                
            except Exception as e:
                await update.message.reply_text("❌ Hubo un error al aprobarte. Avisa a un administrador.")
        else:
            await update.message.reply_text("ℹ️ No tienes solicitudes pendientes o ya fuiste aprobado.")
    else:
        # Mensaje de reglas normal
        mensaje_reglas = "🛡️ *REGLAS DEL GRUPO*\n\n📸 Foto\n👤 Nombre\n🎂 Edad\n🌎 País\n\n_Presentación obligatoria al entrar._"
        try:
            with open(NOMBRE_FOTO, 'rb') as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=mensaje_reglas, parse_mode='Markdown')
        except:
            await update.message.reply_text(mensaje_reglas, parse_mode='Markdown')

async def bienvenida_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saludo automático cuando el usuario entra tras ser aprobado"""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        
        await update.message.reply_text(
            f"🎊 ¡Bienvenido {member.first_name}! Angerona te ha permitido el acceso.\n\n"
            "⚠️ *TIENES 5 MINUTOS* para enviar tu presentación completa (Foto, Nombre, Edad, País) o serás removido.",
            parse_mode='Markdown'
        )

async def enviar_reglas_periodicas(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text="📢 *REGLAS:* La presentación es obligatoria para permanecer.", parse_mode='Markdown')

async def filtro_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user = update.effective_user
    if any(p in update.message.text.lower() for p in PALABRAS_PROHIBIDAS):
        warns_usuario[user.id] = warns_usuario.get(user.id, 0) + 1
        if warns_usuario[user.id] >= 3:
            await context.bot.ban_chat_member(ID_GRUPO_FIJO, user.id)
            await update.message.reply_text(f"🚫 {user.first_name} baneado.")
        else:
            await update.message.reply_text(f"⚠️ {user.first_name}, palabra prohibida ({warns_usuario[user.id]}/3)")
        await update.message.delete()

# --- 🕹️ EJECUCIÓN ---

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(ChatJoinRequestHandler(manejar_solicitud))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_grupo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filtro_mensajes))
    
    if application.job_queue:
        application.job_queue.run_repeating(enviar_reglas_periodicas, interval=21600, first=10)

    application.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    main()
            
