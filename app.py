from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import re

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes entrantes de WhatsApp"""
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()

    # 🔹 Buscar palabra clave dentro del mensaje usando regex
    respuesta = next((RESPUESTAS[key] for key in RESPUESTAS if re.search(rf"\b{key}\b", incoming_msg)), 
                     ["Lo siento, no entiendo tu mensaje. Escribe 'ayuda' para más información. 🆘"])

    # 🔸 Asegurar que la respuesta es un string
    if isinstance(respuesta, list):
        respuesta = "\n".join(respuesta)

    # 📩 Enviar respuesta en formato texto plano
    msg = resp.message(respuesta)
    
    print(f"📩 Respuesta enviada: {respuesta}")
    
    return str(resp)  # 💡 Convertir a string antes de retornar

# Mensajes predefinidos
RESPUESTAS = {
    "hola": "¡Hola! Bienvenido a Spinzone Indoor Cycling 🚴‍♂️. ¿En qué puedo ayudarte?",
    "horarios": """**Nuestros horarios son:**

    **Cycling:**
    Lunes a Jueves: 9am, 6:30pm y 7pm.
    Viernes: 9am y 7:30pm.
    Sabados y Domingos: 10am.

    **Clases Funcionales:**
    Lunes a Jueves: 10am y 5:30pm.
    Viernes: 10am. 📅""",
    "ubicacion": "Estamos ubicados en 2175 Davenport Blvd Davenport Fl 33837. 📍",
    "contacto": "Puedes llamarnos al +8633171646 o escribirnos por WhatsApp. 📞",
    "precios": """Aca te comparto nuestra lista de precios:

    **Primera clase GRATIS**
    4 Clases: $49.99
    8 clases $79.99
    12 clases $99.99
    16 clases $129.99

    **Paquete ilimitados:** 
    Solo Cycling o Funcionales $159.99 por mes o $139.99 por mes en autopay por 3 meses
    Cycling+Funcionales: $175.99 por mes o $155.99 por mes en autopay por 3 meses.""",
    "informacion":[ 
        "Gracias por tu interés en Spinzone Indoorcycling. Somos mucho más que una clase de spinning, ofrecemos una experiencia única que combina intensidad, música envolvente y motivación sin límites.", 
        
        "**¿Qué es el Indoor Cycling?**\nEl indoor cycling es un entrenamiento cardiovascular de alta energía que se realiza en bicicletas estáticas con resistencia ajustable. Nuestras clases están guiadas por instructores expertos y acompañadas de música motivadora, lo que te ayuda a mejorar tu resistencia, quemar calorías y fortalecer piernas y glúteos mientras disfrutas del ritmo y la energía del grupo.", 
        
        "**¿Qué son las Clases Funcionales?**\nAdemás del indoor cycling, ofrecemos clases funcionales, entrenamientos diseñados para trabajar todo el cuerpo con ejercicios que mejoran la fuerza, resistencia y coordinación. Utilizamos una combinación de peso corporal, bandas, mancuernas y otros elementos para garantizar un entrenamiento completo y efectivo.", 
        
        "**¿Por qué elegir Spinzone?**\nClases dinámicas para todos los niveles.\nEntrenamiento guiado por instructores certificados.\nAmbiente motivador con música y energía inigualables.\nEquipos de última tecnología para un rendimiento óptimo.",
        
        "**¿Dónde estamos ubicados?**\n2175 Davenport Blvd Davenport Fl 33837.", 
        
        "**¿Cómo reservar una clase?**\nPuedes agendar tu clase fácilmente registrandote a través de nuestro sitio web  https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view o enviarnos:\nNombre.\nApellido.\nFecha de Nacimiento.\nNumero de Telefono\nEmail\nal WhatsApp +18633171646.",
        
        "Si tienes alguna otra pregunta, estaré encantado de ayudarte.\n¡Esperamos verte pronto pedaleando y entrenando con nosotros!",
    ],
    "no me deja seleccionar numero de bicicleta":
    "🛠 **Solución para seleccionar número de bicicleta**\n"  
    "🔹 A veces, cuando es la primera reserva, el sistema asigna automaticamente una bicicleta.\n"  
    "\n"
    "🔹 **Cancelar la reserva actual:**\n"  
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
