import os
import sqlite3
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = Flask(__name__)

# Cargar variables de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Inicializar cliente OpenAI correctamente
openai.api_key = OPENAI_API_KEY

# Inicializar cliente de Twilio
client_twilio = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Conectar con SQLite
conn = sqlite3.connect("chatbot.db", check_same_thread=False)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        role TEXT,
        content TEXT
    )
""")
conn.commit()

@app.route("/", methods=["GET"])
def home():
    return "¡Servidor funcionando correctamente en Railway!"

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    from_number = request.values.get("From", "").strip()
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    # Base de respuestas personalizadas para Spinzone Indoorcycling
    respuestas_personalizadas = {
        "hola": "¡Hola! 🚴‍♂️ Bienvenido a *Spinzone Indoorcycling*. ¿En qué puedo ayudarte?",
        "reserva": "Puedes hacer tu reserva aquí: [🔗 Reservas y horarios](https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view)",
        "precio": "Consulta nuestros planes y precios aquí: [💰 Planes y precios](https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/memberships)",
        "horario": "Nuestros horarios de clases están disponibles aquí: [📆 Ver horarios](https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view)",
        "direccion": "📍 Nos encontramos en Spinzone Indoorcycling, ¡te esperamos para una sesión increíble!",
        "clases": "En *Spinzone Indoorcycling* ofrecemos clases de indoor cycling para todos los niveles. ¿Te gustaría más información?",
        "instructor": "Contamos con instructores certificados que te guiarán en cada sesión. ¡Ven a conocernos!"
    }

    # Verifica si el mensaje coincide con una pregunta frecuente
    for clave, respuesta in respuestas_personalizadas.items():
        if clave in incoming_msg:
            msg.body(respuesta)
            return str(resp)

    # Si no es un mensaje predefinido, usa OpenAI para responder
    historial = [{"role": "user", "content": incoming_msg}]
    
    try:
    respuesta_ai = openai.ChatCompletion.create(
        model="gpt-4",
        messages=historial
    )
    respuesta_texto = respuesta_ai["choices"][0]["message"]["content"].strip()

    # Guardar mensaje y respuesta en SQLite
    cursor.execute("INSERT INTO conversaciones (user, role, content) VALUES (?, ?, ?)", (from_number, "user", incoming_msg))
    cursor.execute("INSERT INTO conversaciones (user, role, content) VALUES (?, ?, ?)", (from_number, "assistant", respuesta_texto))
    conn.commit()

    msg.body(respuesta_texto)  # Enviar respuesta a WhatsApp

except Exception as e:
    print(f"❌ ERROR: {e}")
    msg.body("Lo siento, hubo un error al procesar tu mensaje. Inténtalo más tarde.")

    return str(resp)

if __name__ == "__main__":
    from waitress import serve
    PORT = int(os.environ.get("PORT", 5000))
    print(f"🚀 Servidor iniciando en http://0.0.0.0:{PORT}")
    serve(app, host="0.0.0.0", port=PORT)
