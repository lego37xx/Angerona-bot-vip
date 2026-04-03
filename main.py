import os
import telebot
from flask import Flask, request

# --- ⚙️ CONFIGURACIÓN (SIN CAMBIOS) ---
TOKEN = '8616684285:AAEYZ2xafcgnmvOMa9Co0NI9I83AT6qReVc'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- 📜 REGLAS (SIN CAMBIOS) ---
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

# --- 🛡️ ARREGLO ESPECÍFICO DEL BOTÓN ---
@bot.chat_join_request_handler()
def manejar_solicitud(req):
    # Definición ultra-estable del botón
    markup = telebot.types.InlineKeyboardMarkup()
    # Usamos un callback corto para evitar errores de longitud
    boton = telebot.types.InlineKeyboardButton(
        text="🤝 ACEPTAR REGLAS Y ENTRAR", 
        callback_data=f"ok_{req.from_user.id}"
    )
    markup.add(boton)
    
    try:
        # Enviamos foto + texto + el botón corregido
        bot.send_photo(
            chat_id=req.from_user.id, 
            photo=URL_LOGO, 
            caption=REGLAS_TEXTO, 
            reply_markup=markup, 
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error al enviar botón: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('ok_'))
def boton_callback(call):
    user_id = int(call.data.split("_")[1])
    try:
        # Aprobación técnica en el grupo
        bot.approve_chat_join_request(ID_GRUPO_FIJO, user_id)
        # Feedback visual para el usuario
        bot.edit_message_caption(
            caption="🚀 *¡ACCESO CONCEDIDO!* Entra al grupo ahora.", 
            chat_id=call.from_user.id, 
            message_id=call.message.message_id, 
            parse_mode='Markdown'
        )
    except:
        bot.answer_callback_query(call.id, "Ya eres miembro.")

# --- 🥳 BIENVENIDA (SIN CAMBIOS) ---
@bot.message_handler(content_types=['new_chat_members'])
def bienvenida(m):
    for user in m.new_chat_members:
        msg = (f"🥳 *¡BIENVENIDO {user.first_name.upper()}!*\n\n"
               "Preséntate ahora con Foto Real, Nombre, Edad y País.\n"
               "⚠️ *Evita ser expulsado.*")
        bot.send_photo(ID_GRUPO_FIJO, URL_LOGO, caption=msg, parse_mode='Markdown')

# --- 🛠️ COMANDOS (SIN CAMBIOS) ---
@bot.message_handler(commands=['reglas'])
def enviar_reglas(m):
    if m.chat.type == 'private' and m.from_user.id == DUENO_ID:
        bot.send_photo(ID_GRUPO_FIJO, URL_LOGO, caption=REGLAS_TEXTO, parse_mode='Markdown')
        bot.reply_to(m, "✅ Reglas publicadas en el grupo.")

# --- 🌐 WEBHOOK (SIN CAMBIOS) ---
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://angerona-bot-vip.onrender.com/" + TOKEN)
    return "🛡️ Angerona Activa", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))
