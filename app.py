from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# Mensajes predefinidos
RESPUESTAS = {
    "hola": "¡Hola! Bienvenido a nuestro servicio de Indoor Cycling 🚴‍♂️. ¿En qué puedo ayudarte?",
    "horarios": "Nuestros horarios son de 6 AM a 10 PM, de lunes a sábado. 📅",
    "ubicacion": "Estamos ubicados en Av. Siempre Viva 123, Ciudad. 📍",
    "contacto": "Puedes llamarnos al +123456789 o escribirnos por WhatsApp. 📞",
}

# Función para buscar en la web información sobre Indoor Cycling
def buscar_informacion(pregunta):
    try:
        response = requests.get(f"https://www.google.com/search?q={pregunta}+Indoor+Cycling")
        return f"Encontré información en la web sobre tu pregunta: {response.url}"
    except:
        return "Lo siento, no pude encontrar información en la web en este momento."

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()
    
    # Revisamos si hay una respuesta predefinida
    for key in RESPUESTAS:
        if key in incoming_msg:
            resp.message(RESPUESTAS[key])
            return str(resp)

    # Si no hay respuesta predefinida, buscamos en la web
    respuesta = buscar_informacion(incoming_msg)
    resp.message(respuesta)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
