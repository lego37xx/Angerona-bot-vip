import os, threading, time, logging
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler, ChatJoinRequestHandler

# --- CONFIGURACIÓN ---
TOKEN = '8616684285:AAEF271duWSPV0-UfJ9rK4rUdI6UQz1-Zxg'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233 
NOMBRE_FOTO = 'logo.png' 
PALABRAS_PROHIBIDAS = ["gore", "cp", "zoofilia", "estafa", "hacker", "spam"]

# Diccionario para rastrear advertencias {user_id: cantidad_warns}
warns_usuario = {}

# --- 🚀 SERVIDOR PARA RENDER ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "🛡️ Angerona Online - Sistema de Seguridad Activo", 200

def run_web():
    # Render usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def start_keep_alive():
    threading.Thread(target=run_web, daemon=True).start()

# --- ⏰ REGLAS ACTUALIZADAS ---
async def enviar_reglas(context: ContextTypes.DEFAULT_TYPE):
    mensaje_reglas = (
        "📜🔥 **REGLAS OFICIALES – “VALIENDO MADRES”** 🔥📜\n\n"
        "1️⃣ 🚫 **Prohibido menores de edad**\n"
        "2️⃣ 🤝 **Respeto ante todo**\n"
        "3️⃣ 📵 **Nada de privados sin permiso**\n"
        "4️⃣ 🚫 **Cero contenido ilegal o enfermizo**\n"
        "5️⃣ 🔞 **No venta de contenido (Only, etc.)**\n"
        "6️⃣ 😂 **Aquí se viene a convivir**\n"
        "7️⃣ 🔥 **Se vale picar… pero no pasarse**\n\n"
        "⚠️ **SISTEMA DE ADVERTENCIAS:**\n"
        "Si incumples las reglas recibirás un warn. Al **3er warn** serás baneado automáticamente por Angerona. 🛡️"
    )
    try:
        if os.path.exists(NOMBRE_FOTO):
            with open(NOMBRE_FOTO, 'rb') as f:
                await context.bot.send_photo(chat_id=ID_GRUPO_FIJO, photo=f, caption=mensaje_reglas, parse_mode=constants.ParseMode.MARKDOWN)
        else:
            await context.bot.send_message(chat_id=ID_GRUPO_FIJO, text=mensaje_reglas, parse_mode=constants.ParseMode.MARKDOWN)
    except: pass

# --- 🛡️ SEGURIDAD Y BAN AUTOMÁTICO ---
async def filtro_seguridad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    texto = update.message.text.lower()

    if any(p in texto for p in PALABRAS_PROHIBIDAS):
        try:
            await update.message.delete()
            
            # Gestionar Warns
            warns_usuario[user_id] = warns_usuario.get(user_id, 0) + 1
            conteo = warns_usuario[user_id]

            if conteo >= 3:
                await context.bot.ban_chat_member(chat_id=ID_GRUPO_FIJO, user_id=user_id)
                await context.bot.send_message(
                    chat_id=ID_GRUPO_FIJO, 
                    text=f"🚫 **BAN DIRECTO:** {user_name} ha sido expulsado tras acumular 3 advertencias."
                )
                warns_usuario[user_id] = 0 # Reset
            else:
                await context.bot.send_message(
                    chat_id=ID_GRUPO_FIJO, 
                    text=f"⚠️ **ADVERTENCIA {conteo}/3:** {user_name}, tu mensaje fue eliminado por incumplir las reglas. A la tercera serás baneado. 🛡️"
                )
        except Exception as e:
            print(f"Error en filtro: {e}")

# --- ACCESO Y BIENVENIDA CON PRESENTACIÓN ---
async def manejar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    kbd = [[InlineKeyboardButton("✅ ACEPTO LAS REGLAS", callback_data=f"apr_{req.chat.id}_{req.from_user.id}")]]
    try:
        await context.bot.send_message(chat_id=req.from_user.id, text=f"👋 ¡Hola! Confirma para entrar a **{req.chat.title}**:", reply_markup=InlineKeyboardMarkup(kbd))
    except: pass

async def boton_aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data.split("_")
    try:
        await context.bot.approve_chat_join_request(chat_id=int(d[1]), user_id=int(d[2]))
        await q.edit_message_text("✅ **¡ACCESO CONCEDIDO!** Ya puedes entrar.")
        
        # Bienvenida con solicitud de datos
        presentacion = (
            f"🎊 **¡BIENVENIDO(A) AL DESMADRE!** 🎊\n\n"
            f"Hola {q.from_user.mention_markdown_v2()}, acabas de pasar el filtro de seguridad\. "
            f"Para permanecer en el grupo, **debes presentarte** con los siguientes datos:\n\n"
            f"📸 **Foto:** Una imagen visible (diferente a la de tu perfil)\.\n"
            f"👤 **Nombre:**\n"
            f"🎂 **Edad:**\n"
            f"🌎 **País:**\n\n"
            f"🛡️ _¡Si no cumples con las reglas o la presentación, Angerona tomará medidas\!_"
        )
        # Puedes subir una imagen llamada 'bienvenida.png' a tu proyecto para que se vea mejor
        await context.bot.send_message(chat_id=int(d[1]), text=presentacion, parse_mode='MarkdownV2')
    except: pass

# --- INICIO ---
if __name__ == '__main__':
    start_keep_alive()
    while True:
        try:
            app = ApplicationBuilder().token(TOKEN).build()
            app.job_queue.run_repeating(enviar_reglas, interval=1200, first=10)
            app.add_handler(ChatJoinRequestHandler(manejar_solicitud))
            app.add_handler(CallbackQueryHandler(boton_aprobar, pattern="^apr_"))
            app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), filtro_seguridad))
            
            print("🛡️ Angerona Actualizada: Sistema de Ban y Presentación listo.")
            app.run_polling(drop_pending_updates=True)
        except Exception as e:
            print(f"🔄 Error: {e}. Reiniciando...")
            time.sleep(5)
            
