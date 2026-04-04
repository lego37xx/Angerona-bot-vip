import os
import telebot
import threading
import time
from datetime import datetime
from flask import Flask, request

# --- ⚙️ CONFIGURACIÓN (MANTENIDA) ---
TOKEN = '8616684285:AAEYZ2xafcgnmvOMa9Co0NI9I83AT6qReVc'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

# --- 🕒 CONFIGURACIÓN DE SEGURIDAD ---
TIEMPO_GRACIA = 600  # 10 minutos en segundos
usuarios_en_espera = {} # Diccionario para rastrear la presentación
auditoria_secreta = []
palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- 📜 REGLAS "VALIENDO MADRES" (MANTENIDAS) ---
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

# --- ⚖️ LÓGICA DE AUTO-BANEO ---
def ejecutar_juicio_angerona(user_id, nombre):
    """ Función que espera 10 min y banea si no hubo presentación """
    time.sleep(TIEMPO_GRACIA)
    
    # Si después de 10 min el usuario sigue marcado como False (no presentado)
    if user_id in usuarios_en_espera and not usuarios_en_espera[user_id]:
        try:
            bot.ban_chat_member(ID_GRUPO_FIJO, user_id)
            bot.unban_chat_member(ID_GRUPO_FIJO, user_id) # Permite reingreso futuro
            
            # Mensaje en el grupo (Justificación del bot)
            bot.send_message(
                ID_GRUPO_FIJO, 
                f"⚠️ *AVISO:* El usuario *{nombre}* fue expulsado por Angerona.\nMotivo: No se presentó en el tiempo límite de 10 minutos.",
                parse_mode='Markdown'
            )
            # Limpieza
            del usuarios_en_espera[user_id]
        except:
            pass

# --- 🛡️ FILTRO DE ACCESO (MANTENIDO + ACTIVADOR DE TIMER) ---
@bot.chat_join_request_handler()
def manejar_solicitud(req):
    markup = telebot.types.InlineKeyboardMarkup()
    boton = telebot.types.InlineKeyboardButton(text="🤝 ACEPTAR REGLAS Y ENTRAR", callback_data=f"ok_{req.from_user.id}")
    markup.add(boton)
    try:
        bot.send_photo(req.from_user.id, URL_LOGO, caption=REGLAS_TEXTO, reply_markup=markup, parse_mode='Markdown')
    except: pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('ok_'))
def boton_callback(call):
    user_id = int(call.data.split("_")[1])
    nombre = call.from_user.first_name
    try:
        bot.approve_chat_join_request(ID_GRUPO_FIJO, user_id)
        bot.edit_message_caption(
            caption="🚀 *ACCESO CONCEDIDO.* Tienes 10 min para presentarte en el grupo.", 
            chat_id=call.from_user.id, 
            message_id=call.message.message_id, 
            parse_mode='Markdown'
        )
        
        # INICIAR RELOJ DE EXPULSIÓN
        usuarios_en_espera[user_id] = False
        threading.Thread(target=ejecutar_juicio_angerona, args=(user_id, nombre), daemon=True).start()
    except:
        bot.answer_callback_query(call.id, "Ya eres miembro.")

# --- 🥳 BIENVENIDA (MANTENIDA) ---
@bot.message_handler(content_types=['new_chat_members'])
def bienvenida(m):
    for user in m.new_chat_members:
        msg = (f"🥳 *¡BIENVENIDO {user.first_name.upper()}!*\n\n"
               "Preséntate ahora con Foto Real, Nombre, Edad y País.\n"
               "⚠️ *Tienes 10 minutos antes de ser expulsado.*")
        bot.send_photo(ID_GRUPO_FIJO, URL_LOGO, caption=msg, parse_mode='Markdown')

# --- 🛠️ COMANDOS Y SEGURIDAD (MANTENIDOS) ---
@bot.message_handler(commands=['reglas'])
def enviar_reglas(m):
    if m.chat.type == 'private' and m.from_user.id == DUENO_ID:
        bot.send_photo(ID_GRUPO_FIJO, URL_LOGO, caption=REGLAS_TEXTO, parse_mode='Markdown')
        bot.reply_to(m, "✅ Reglas enviadas al grupo.")

@bot.message_handler(commands=['auditoria'])
def ver_auditoria(m):
    if m.from_user.id == DUENO_ID:
        res = "\n".join(auditoria_secreta) if auditoria_secreta else "Vacío."
        bot.reply_to(m, f"📋 *AUDITORÍA:*\n{res}")

@bot.message_handler(func=lambda m: True)
def monitor_y_deteccion(m):
    if m.chat.id == ID_GRUPO_FIJO:
        # SI ESCRIBE, MARCAR COMO PRESENTADO
        if m.from_user.id in usuarios_en_espera:
            usuarios_en_espera[m.from_user.id] = True
        
        # Auditoría y Filtro de palabras
        auditoria_secreta.append(f"👤 {m.from_user.first_name}: {m.text}")
        if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)
        if any(p in (m.text or "").lower() for p in palabras_prohibidas):
            bot.delete_message(m.chat.id, m.message_id)

# --- 🌐 WEBHOOK (MANTENIDO) ---
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://angerona-bot-vip.onrender.com/" + TOKEN)
    return "🛡️ Angerona 14.0 - Auto-Baneo Activo", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))
            
