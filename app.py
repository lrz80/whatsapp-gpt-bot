from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import asyncio
from googletrans import Translator
from langdetect import detect
from unidecode import unidecode

app = Flask(__name__)

def traducir_texto(texto, idioma_destino):
    """Traduce el texto al idioma deseado de forma síncrona."""
    traductor = Translator()
    traduccion = traductor.translate(texto, dest=idioma_destino)
    return traduccion.text  # Asegura que devuelve el texto directamente

# Función para detectar el idioma
def detectar_idioma(texto):
    try:
        return detect(texto)
    except:
        return "es"  # Si hay error, por defecto español

# Normalizar texto (minúsculas y sin acentos)
def normalizar_texto(texto):
    return unidecode(texto.lower())

# Función para dividir mensajes largos
def enviar_respuesta(resp, mensaje):
    """Divide y envía mensajes largos para evitar el límite de Twilio."""
    limite = 1500  # Máximo seguro antes de 1600 caracteres
    partes = [mensaje[i:i+limite] for i in range(0, len(mensaje), limite)]
    for parte in partes:
        resp.message(str(parte))  # Envía cada parte como mensaje separado

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
# Definir RESPUESTAS_NORMALIZADAS antes de usarla
RESPUESTAS_NORMALIZADAS = {k: v for k, v in RESPUESTAS.items()}

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes entrantes de WhatsApp de forma síncrona."""
    global RESPUESTAS_NORMALIZADAS
    incoming_msg = request.values.get("Body", "").strip()
    idioma_detectado = detectar_idioma(incoming_msg)
    incoming_msg = normalizar_texto(incoming_msg)

    resp = MessagingResponse()
    respuesta = RESPUESTAS_NORMALIZADAS.get(incoming_msg, "Lo siento, no entiendo tu mensaje.")
    respuesta = traducir_texto(respuesta, idioma_detectado)  # Traducción en modo síncrono

    # Normalizar claves del diccionario RESPUESTAS
    RESPUESTAS_NORMALIZADAS = {}
    for claves, valor in RESPUESTAS.items():
        if isinstance(claves, tuple):  # Si la clave es una tupla (varias palabras)
            for palabra in claves:
                RESPUESTAS_NORMALIZADAS[normalizar_texto(palabra)] = valor
        else:  # Si es una clave única
            RESPUESTAS_NORMALIZADAS[normalizar_texto(claves)] = valor

    # Buscar palabra clave en el mensaje
    respuesta = next((RESPUESTAS_NORMALIZADAS[key] for key in RESPUESTAS_NORMALIZADAS if key in incoming_msg), "Lo siento, no entiendo tu mensaje.")

    # Traducir la respuesta al idioma detectado
    respuesta = traducir_texto(respuesta, idioma_detectado)  # ✅ Versión síncrona

    # Enviar la respuesta
    enviar_respuesta(resp, respuesta)

    print(f"📩 Respuesta enviada: {respuesta}")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
