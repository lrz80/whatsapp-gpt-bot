from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/")
def home():
    return "¡Servidor funcionando correctamente en Railway!"

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    from_number = request.values.get("From", "").strip()  # Número del usuario
    incoming_msg = request.values.get("Body", "").strip().lower()  # Mensaje recibido

    resp = MessagingResponse()
    msg = resp.message()

    # Respuesta básica para probar
    msg.body(f"Recibí tu mensaje: {incoming_msg}")

    return str(resp)

if __name__ == "__main__":
    from waitress import serve
    import os
    print("🚀 Servidor iniciando en http://0.0.0.0:5000")
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

