import os
import openai
import unicodedata
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from langdetect import detect

openai.api_key = os.getenv("OPENAI_API_KEY")

# Definir respuestas predefinidas antes de usarla
PREDEFINED_RESPONSES = {
    "hola": "¡Hola! ¿En qué puedo ayudarte?",
    "buenas": "¡Hola! ¿En qué puedo ayudarte?",
    "buenas tardes": "¡Hola! ¿En qué puedo ayudarte?",
}

app = Flask(__name__)

def has_accent(word):
    normalized = unicodedata.normalize('NFD', word)
    return any(char in "́̀̈" for char in normalized)  # Detecta tildes, diéresis

def split_message(text, max_length=1600):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Mensajes predefinidos
RESPUESTAS = {
    ("hola", "buenas" "buenos días", "buenas tardes", "buenas noches"): "¡Hola! Bienvenido a Spinzone Indoor Cycling 🚴‍♂️. ¿En qué puedo ayudarte?",
    "horarios": """**Nuestros horarios son:**

    **Cycling:**
    Lunes a Jueves: 9am, 6:30pm y 7pm.
    Viernes: 9am y 7:30pm.
    Sabados y Domingos: 10am.

    **Clases Funcionales:**
    Lunes a Jueves: 10am y 5:30pm.
    Viernes: 10am. 📅""",
    "**Dónde estan ubicados o ubicacion?**": "Estamos ubicados en 2175 Davenport Blvd Davenport Fl 33837. 📍",
    "**numero de contacto o telefono**": "Puedes llamarnos al +8633171646 o escribirnos por WhatsApp. 📞",
    "**Cómo reservar una clase o clase gratis o quiero registrarme?**": "Puedes agendar tu clase fácilmente registrandote a través de nuestro sitio web  https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view o enviarnos:\nNombre.\nApellido.\nFecha de Nacimiento.\nNumero de Telefono\nEmail\nal WhatsApp +18633171646.",
    "**precios o membresias**": """Te comparto nuestra lista de precios:

    **Primera clase GRATIS**
    4 Clases: $49.99
    8 clases $79.99
    12 clases $99.99
    16 clases $129.99

    **Paquete ilimitados:** 
    Solo Cycling o Funcionales $159.99 por mes o $139.99 por mes en autopay por 3 meses
    Cycling+Funcionales: $175.99 por mes o $155.99 por mes en autopay por 3 meses.""",
    "informacion":[ 
        "Gracias por tu interés en Spinzone Indoorcycling. Somos mucho más que una clase de spinning, ofrecemos una experiencia única que combina intensidad, música envolvente y motivación sin límites.\n", 
        
        "**¿Qué es el Indoor Cycling?**\nEl indoor cycling es un entrenamiento cardiovascular de alta energía que se realiza en bicicletas estáticas con resistencia ajustable. Nuestras clases están guiadas por instructores expertos y acompañadas de música motivadora, lo que te ayuda a mejorar tu resistencia, quemar calorías y fortalecer piernas y glúteos mientras disfrutas del ritmo y la energía del grupo.\n", 
        
        "**¿Qué son las Clases Funcionales?**\nAdemás del indoor cycling, ofrecemos clases funcionales, entrenamientos diseñados para trabajar todo el cuerpo con ejercicios que mejoran la fuerza, resistencia y coordinación. Utilizamos una combinación de peso corporal, bandas, mancuernas y otros elementos para garantizar un entrenamiento completo y efectivo.\n", 
        
        "**¿Por qué elegir Spinzone?**\nClases dinámicas para todos los niveles.\nEntrenamiento guiado por instructores certificados.\nAmbiente motivador con música y energía inigualables.\nEquipos de última tecnología para un rendimiento óptimo.\n", 
        
        "Si tienes alguna otra pregunta, estaré encantado de ayudarte.\n¡Esperamos verte pronto pedaleando y entrenando con nosotros!",
    ],
    ("no me deja seleccionar numero de bicicleta", "bici", "spot"):
    "🛠 **Solución para seleccionar número de bicicleta**\n"  
    "🔹 A veces, cuando es la primera reserva, el sistema asigna automaticamente una bicicleta.\n"  
    "\n"
    "🔹 **Cancelar la reserva o reserva actual:**\n"  
    "- Accede a nuestra App y ve a tus reservas.\n"  
    "- Selecciona la clase y cancela la reserva.\n\n"  
    "\n"
    "🔹 **Reserva nuevamente seleccionando la bicicleta:**\n"  
    "- Vuelve a la sección de clases.\n"  
    "- Selecciona la bicicleta disponible y confirma tu reserva.\n"  
    "\n"
    "📲 Si después de intentar estos pasos aún tienes problemas, contáctanos por WhatsApp al **+18633171646**."
}

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.form.get("Body", "").strip().lower()
    response = MessagingResponse()
    
    # Si el mensaje está en respuestas predefinidas
    if incoming_msg in PREDEFINED_RESPONSES:
        response.message(PREDEFINED_RESPONSES[incoming_msg])
        return str(response)

    # Detectar idioma
    try:
        lang = detect(incoming_msg)
    except:
        lang = "unknown"
    
    # Generar respuesta con OpenAI
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": incoming_msg}]
        )
        bot_response = completion["choices"][0]["message"]["content"]
    except Exception as e:
        bot_response = "Lo siento, hubo un error procesando tu mensaje."

    # Dividir respuesta si es muy larga
    for msg in split_message(bot_response):
        response.message(msg)

    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto asignado por Railway
    app.run(host="0.0.0.0", port=port, debug=True)

