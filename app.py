import os
from flask import Flask
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

port = int(os.environ.get("PORT", 5000))  # Puerto dinámico de Railway

# Mensajes predefinidos
RESPUESTAS = {
    "hola": "¡Hola! Bienvenido a Spinzone Indoor Cycling 🚴‍♂️. ¿En qué puedo ayudarte?",
    "horarios": "Nuestros horarios son: Cycling: Lunes a Jueves: 9am, 6:30pm y 7pm. Viernes: 9am y 7:30pm. Sabados y Domingos: 10am. Clases Funcionales: Lunes a Jueves: 10am y 5:30pm. Viernes: 10am. 📅",
    "ubicacion": "Estamos ubicados en 2175 Davenport Blvd Davenport Fl 33837. 📍",
    "contacto": "Puedes llamarnos al +8633171646 o escribirnos por WhatsApp. 📞",
    "precios": "Primera clase GRATIS, 4 Clases: $49.99, 8 clases $79.99, 12 clases $99.99, 16 clases $129.99, Paquete ilimitados: Solo Cycling o Funcionales $159.99 por mes o $139.99 por mes en autopay por 3 meses, Cycling+Funcionales: $175.99 por mes o $155.99 por mes en autopay por 3 meses."
}

# Función para buscar en la web información sobre Indoor Cycling
def buscar_informacion(pregunta):
    try:
        response = requests.get(f"https://www.instagram.com/spinzone_indoorcycling/")
        return f"Por supuesto! aca encontraras toda la informacion que necesites"
    except:
        return "Lo siento, no pude encontrar información en este momento."

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
    app.run(host="0.0.0.0", port=5000)
