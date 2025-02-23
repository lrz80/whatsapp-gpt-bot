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

# Configurar API de OpenAI
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

    # 📌 Respuestas específicas de Spinzone Indoorcycling
    respuestas_rapidas = {
        "horarios": "Puedes ver los horarios y hacer reservas aquí: https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view",
        "reservas": "Para hacer una reserva, visita: https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view",
        "precios": "Los precios y planes de membresía los encuentras aquí: https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/memberships",
        "direccion": "Spinzone Indoorcycling está ubicado en **2175 Davenport Blvd Davenport Fl 33837**. ¡Te esperamos!",
        "telefono": "Puedes contactarnos al **+18633171646**.",
        "pagina web": "Visita nuestra página web aquí: **www.spinzoneic.com**.",
        "clases": "Consulta los horarios y disponibilidad de clases en: https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view"
    }

    # 🔍 Revisar si el mensaje es una pregunta frecuente
    for key, value in respuestas_rapidas.items():
        if key in incoming_msg:
            msg.body(value)
            return str(resp)

    # 👇 Si el mensaje no está en las preguntas frecuentes, usa OpenAI
    historial = [
        {"role": "system", "content": "Eres el asistente virtual de Spinzone Indoorcycling. Tu trabajo es responder preguntas sobre la empresa, incluyendo dirección, teléfono, página web, precios y reservas. No menciones que eres una IA. Siempre responde con información útil y clara."}
    ]

    cursor.execute("SELECT role, content FROM conversaciones WHERE user=? ORDER BY id ASC", (from_number,))
    historial += [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
    historial.append({"role": "user", "content": incoming_msg})

    try:
        respuesta_ai = openai.ChatCompletion.create(
            model="gpt-4",
            messages=historial
        )
        respuesta_ai["choices"][0]["message"]["content"].strip()

        # 📌 Guardar mensaje y respuesta en la base de datos
        cursor.execute("INSERT INTO conversaciones (user, role, content) VALUES (?, ?, ?)", (from_number, "user", incoming_msg))
        cursor.execute("INSERT INTO conversaciones (user, role, content) VALUES (?, ?, ?)", (from_number, "assistant", respuesta_texto))
        conn.commit()

        msg.body(respuesta_texto)  # Enviar respuesta a WhatsApp

    except Exception as e:
        print(f"❌ ERROR: {e}")
        msg.body("Lo siento, hubo un error al procesar tu mensaje. Inténtalo más tarde.")

    return str(resp)

    # Guardar historial en SQLite
    cursor.execute("SELECT role, content FROM conversaciones WHERE user=? ORDER BY id ASC", (from_number,))
    historial = [
    {"role": "system", "content": "Eres el asistente virtual de Spinzone Indoorcycling. Responde preguntas sobre horarios, precios y reservas como si fueras parte del equipo de la empresa.       No menciones que eres una inteligencia artificial."}
]

    cursor.execute("SELECT role, content FROM conversaciones WHERE user=? ORDER BY id ASC", (from_number,))
    historial += [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
    historial.append({"role": "user", "content": incoming_msg})

    try:
        client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)

        respuesta_ai = client_openai.chat.completions.create(
            model="gpt-4",
            messages=historial
        )
        # ✅ Acceder correctamente al contenido de la respuesta
        respuesta_texto = respuesta_ai.choices[0].message.content.strip()

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
