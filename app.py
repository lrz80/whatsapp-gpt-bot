import os
import time
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

app = Flask(__name__)

# Mensajes predefinidos
RESPUESTAS = {
    "hola": "¡Hola! Bienvenido a Spinzone Indoor Cycling 🚴‍♂️. ¿En qué puedo ayudarte?",
    "horarios": "Nuestros horarios son: Cycling: Lunes a Jueves: 9am, 6:30pm y 7pm. Viernes: 9am y 7:30pm. Sabados y Domingos: 10am. Clases Funcionales: Lunes a Jueves: 10am y 5:30pm. Viernes: 10am. 📅",
    "ubicacion": "Estamos ubicados en 2175 Davenport Blvd Davenport Fl 33837. 📍",
    "contacto": "Puedes llamarnos al +8633171646 o escribirnos por WhatsApp. 📞",
    "precios": """Aca te comparto nuestra lista de precios: 
    Primera clase GRATIS, 4 Clases: $49.99, 8 clases $79.99, 12 clases $99.99, 16 clases $129.99, Paquete ilimitados: Solo Cycling o Funcionales $159.99 por mes o $139.99 por mes en autopay por 3 meses, Cycling+Funcionales: $175.99 por mes o $155.99 por mes en autopay por 3 meses.""",
    "informacion": """Gracias por tu interés en Spinzone Indoorcycling. Somos mucho más que una clase de spinning, ofrecemos una experiencia única que combina intensidad, música envolvente y motivación sin límites. 
    ¿Qué es el Indoor Cycling? El indoor cycling es un entrenamiento cardiovascular de alta energía que se realiza en bicicletas estáticas con resistencia ajustable. Nuestras clases están guiadas por instructores expertos y acompañadas de música motivadora, lo que te ayuda a mejorar tu resistencia, quemar calorías y fortalecer piernas y glúteos mientras disfrutas del ritmo y la energía del grupo. 
    ¿Qué son las Clases Funcionales? Además del indoor cycling, ofrecemos clases funcionales, entrenamientos diseñados para trabajar todo el cuerpo con ejercicios que mejoran la fuerza, resistencia y coordinación. Utilizamos una combinación de peso corporal, bandas, mancuernas y otros elementos para garantizar un entrenamiento completo y efectivo. 
    ¿Por qué elegir Spinzone? Clases dinámicas para todos los niveles. Entrenamiento guiado por instructores certificados. Ambiente motivador con música y energía inigualables. Equipos de última tecnología para un rendimiento óptimo. 
    ¿Dónde estamos ubicados? 2175 Davenport Blvd Davenport Fl 33837. 
    ¿Cómo reservar una clase? Puedes agendar tu clase fácilmente registrandote a través de nuestro sitio web  https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view o contactarnos por WhatsApp +18633171646. 
    Si tienes alguna otra pregunta, estaré encantado de ayudarte. ¡Esperamos verte pronto pedaleando y entrenando con nosotros!""",
    "no me deja seleccionar numero de bicicleta": """A veces, cuando es la primera reserva, el sistema asigna automaticamente una bicicleta. Para solucionar esto, te sugiero los siguientes pasos:
    Cancelar la reserva actual: Accede a nuestra App y ve a tus reservas. Selecciona la clase reservada. Elige la opcion CANCELAR.
    Reserva nuevamente seleccionando la bicicleta: Despues de cancelar, vuelve a la seccion de clases. Selecciona la clase. Pulsas el boton BOOK. Deberias de ver una lista con las bicicletas (Spots). Elige el numero de bicilceta que deseas.
    Si despues de intentar estos pasos aun tienes dificultades para seleccionar la bicicleta, por favor haznoslo saber escrbiendo al Whatsapp o llamando al numero +18633171646 y con gusto de asistiremos.""" 
    }

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    """ Maneja los mensajes entrantes de WhatsApp """
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()

    # 📌 Buscar la respuesta en RESPUESTAS o devolver mensaje por defecto
    respuesta = RESPUESTAS.get(incoming_msg, "Lo siento, no entiendo tu mensaje. Escríbenos 'ayuda' para más información. 🤖")

    print(f"📩 Mensaje recibido: {incoming_msg}")
    
    time.sleep(2)  # ⏳ Simula un pequeño retraso como si respondiera un humano
    
    msg = resp.message(respuesta)
    print(f"📤 Respuesta enviada: {respuesta}")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
