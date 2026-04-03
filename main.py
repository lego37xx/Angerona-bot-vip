import os
import telebot # Librería síncrona
from flask import Flask, request

# --- ⚙️ CONFIGURACIÓN ---
TOKEN = '8616684285:AAEYZ2xafcgnmvOMa9Co0NI9I83AT6qReVc'
DUENO_ID = 8650569384
ID_GRUPO_FIJO = -1003519088233
URL_LOGO = "https://raw.githubusercontent.com/lego37xx/Angerona-bot-vip/main/logo.png"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

auditoria_secreta = []
warns = {}
palabras_prohibidas = ["gore", "cp", "zoofilia", "estafa"]

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

# --- 🛡️ FUNCIÓN PRINCIPAL: FILTRO DE ACCESO ---
@bot.chat_join_request_handler()
def manejar_solicitud(req):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("🤝 ACEPTAR REGLAS Y ENTRAR", callback_data=f"a_{req.from_user.id}"))
    try:
        # Envía reglas por privado al usuario
        bot.send_photo(req.from_user.id, URL_LOGO, caption=REGLAS_TEXTO, reply_markup=kb, parse_mode='Markdown')
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('a_'))
def boton_callback(call):
    u_id = int(call.data.split("_")[1])
    try:
        # Aprobación inmediata
        bot.approve_chat_join_request(ID_GRUPO_FIJO, u_id)
        bot.edit_message_caption("🚀 *¡ACCESO CONCEDIDO!* Ya puedes entrar al grupo.", call.from_user.id, call.message.message_id, parse_mode='Markdown')
    except:
        bot.answer_callback_query(call.id, "Error al aprobar o ya eres miembro.")

# --- 🥳 BIENVENIDA AL GRUPO ---
@bot.message_handler(content_types=['new_chat_members'])
def bienvenida(m):
    for user in m.new_chat_members:
        msg = (f"🥳 *¡BIENVENIDO {user.first_name.upper()}!*\n\n"
               "Presentación obligatoria con:\n📸 *Foto Real*\n👤 *Nombre y Edad*\n🌎 *País*\n\n"
               "⚠️ *Evita la expulsión cumpliendo las reglas.*")
        bot.send_photo(ID_GRUPO_FIJO, URL_LOGO, caption=msg, parse_mode='Markdown')

# --- 🛠️ COMANDOS ADMINISTRATIVOS ---
@bot.message_handler(commands=['reglas'])
def enviar_reglas(m):
    # Si le escribes /reglas en privado, las manda al grupo
    if m.chat.type == 'private' and m.from_user.id == DUENO_ID:
        bot.send_photo(ID_GRUPO_FIJO, URL_LOGO, caption=REGLAS_TEXTO, parse_mode='Markdown')
        bot.reply_to(m, "✅ Reglas publicadas en el grupo.")

@bot.message_handler(commands=['auditoria'])
def ver_auditoria(m):
    if m.from_user.id == DUENO_ID:
        res = "\n".join(auditoria_secreta) if auditoria_secreta else "Historial vacío."
        bot.reply_to(m, f"📋 *AUDITORÍA SECRETA:*\n\n{res}")

@bot.message_handler(commands=['unwarn'])
def reset_warns(m):
    if m.from_user.id == DUENO_ID and m.reply_to_message:
        target_id = m.reply_to_message.from_user.id
        warns[target_id] = 0
        bot.reply_to(m, "✅ Advertencias reseteadas.")

# --- 📋 MONITOR DE SEGURIDAD ---
@bot.message_handler(func=lambda m: True)
def monitor(m):
    if m.chat.id == ID_GRUPO_FIJO:
        # Auditoría últimos 50
        auditoria_secreta.append(f"👤 {m.from_user.first_name}: {m.text}")
        if len(auditoria_secreta) > 50: auditoria_secreta.pop(0)
        
        # Filtro palabras
        if any(p in (m.text or "").lower() for p in palabras_prohibidas):
            bot.delete_message(m.chat.id, m.message_id)

# --- 🌐 WEBHOOK Y SERVER ---
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://angerona-bot-vip.onrender.com/" + TOKEN)
    return "🛡️ Angerona Status: ONLINE", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))
    
