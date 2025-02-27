from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import re
from unidecode import unidecode

app = Flask(__name__)

def normalizar_texto(texto):
    return unidecode(texto.lower())  # Convierte a minúsculas y elimina acentos

def enviar_respuesta(resp, mensaje):
    """Divide y envía mensajes largos en partes más cortas para evitar el límite de Twilio."""
    limite = 1500  # Máximo seguro antes de 1600 caracteres
    partes = [mensaje[i:i+limite] for i in range(0, len(mensaje), limite)]
    
    for parte in partes:
        resp.message(str(parte))  # Envía cada parte como un mensaje separado

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes entrantes de WhatsApp"""
    incoming_msg = normalizar_texto(request.values.get("Body", "").strip())  
    print(f"Mensaje recibido (normalizado): {incoming_msg}")  # Debug

    resp = MessagingResponse()

    incoming_msg = normalizar_texto(incoming_msg)  # Convierte a minúsculas y quita acentos

    # 🔹 Normalizar claves del diccionario RESPUESTAS
    RESPUESTAS_NORMALIZADAS = {normalizar_texto(k): v for k, v in RESPUESTAS.items()}

    print(f"Palabras clave disponibles: {list(RESPUESTAS_NORMALIZADAS.keys())}")  

    respuesta = None  
    for claves, resp in RESPUESTAS.items():  
        if isinstance(claves, tuple):  # Si la clave es una tupla (lista de palabras)  
            if any(re.search(rf"\b{re.escape(key)}\b", incoming_msg) for key in claves):  
                respuesta = resp  
                break  
        else:  # Si la clave es una sola palabra  
            if re.search(rf"\b{re.escape(claves)}\b", incoming_msg):  
                respuesta = resp  
                break  

    if respuesta is None:  
        respuesta = "Lo siento, no entiendo tu mensaje. Escribe 'ayuda' para más información."  

    print(f"Respuesta encontrada: {respuesta}")  # Debug  

    # 📩 Enviar respuesta
    if isinstance(respuesta, (list, tuple)): 
        respuesta = "\n".join(respuesta)  # Convierte lista/tupla en string

    enviar_respuesta(resp, respuesta)  # Envía la respuesta final


    print(f"📩 Respuesta enviada: {respuesta}")

    return str(resp)  

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
    ("**no me deja seleccionar numero de bicicleta**", "bici"):
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
