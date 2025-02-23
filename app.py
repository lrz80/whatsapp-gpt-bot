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

# Inicializar cliente OpenAI
openai.api_key = OPENAI_API_KEY  # Asigna la API key correctamente

# Inicializar cliente de Twilio
client_twilio = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Conectar con SQLite
try:
    conn = sqlite3.connect("chatbot.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()
except sqlite3.Error as e:
    print(f"⚠️ Error conectando a SQLite: {e}")

@app.route("/", methods=["GET"])
def home():
    return "¡Servidor funcionando correctamente en Railway!"

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    from_number = request.values.get("From", "").strip()
    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    # Obtener historial de conversación
    historial = [{"role": "system", "content": "Eres un asistente de WhatsApp."}]
    cursor.execute("SELECT role, content FROM conversaciones WHERE user=? ORDER BY id ASC", (from_number,))
    historial += [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
    historial.append({"role": "user", "content": incoming_msg})

    try:
        respuesta_ai = openai.client.chat.completions.create(
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
