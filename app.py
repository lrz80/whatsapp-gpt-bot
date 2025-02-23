import os
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = Flask(__name__)

# 🔑 Cargar claves de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# 📢 Verificar que las claves existen
if not all([OPENAI_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER]):
    raise ValueError("❌ ERROR: Faltan claves en las variables de entorno. Revisa Railway.")

# Inicializar clientes
openai.api_key = OPENAI_API_KEY
client_twilio = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/", methods=["GET"])
def home():
    return "🚀 ¡Servidor funcionando correctamente en Railway!"

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    """ Responde a mensajes de WhatsApp con GPT-4 """
    from_number = request.values.get("From", "").strip()
    incoming_msg = request.values.get("Body", "").strip()

    # 📢 DEBUG: Ver mensaje entrante
    print(f"📥 Mensaje recibido de {from_number}: {incoming_msg}")

    try:
        # 🔥 Obtener respuesta de GPT-4
        respuesta_ai = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": incoming_msg}]
        )
        respuesta_texto = respuesta_ai["choices"][0]["message"]["content"].strip()

        # 📤 Enviar respuesta a WhatsApp
        client_twilio.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=from_number,
            body=respuesta_texto
        )

        print(f"📤 Respuesta enviada a {from_number}: {respuesta_texto}")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        client_twilio.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=from_number,
            body="Lo siento, hubo un error al procesar tu mensaje. Inténtalo más tarde."
        )

    return "OK", 200

if __name__ == "__main__":
    from waitress import serve
    print("🚀 Servidor iniciando en http://0.0.0.0:5000")
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
