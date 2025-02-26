import os
from waitress import serve
import subprocess
import requests
import time
import openai
import sqlite3
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from flask import Flask, request, jsonify
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import jsonify
import threading
from flask import Response
from reservar_clase import reservar_clase

app = Flask(__name__)

# 🔹 Cargar variables de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Asegurar que la API Key está definida
if OPENAI_API_KEY:
    client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    raise ValueError("⚠️ ERROR: La clave de API de OpenAI no está configurada correctamente.")

client_twilio = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# 🔹 Conectar con SQLite
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

@app.route("/", methods=["GET"])
def home():
    return "¡Servidor funcionando correctamente en Railway!"

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    data = request.form  # 📌 Cambiar de request.get_json() a request.form
    incoming_msg = data.get("Body", "").strip().lower()
    from_number = data.get("From", "")

    resp = MessagingResponse()  
    msg = resp.message()  # Asegura que msg esté definido

    print(f"📩 Mensaje recibido: {incoming_msg}")
    print(f"📲 Número de WhatsApp: {from_number}")

    # 🟢 Definir un valor por defecto para 'respuesta'
    respuesta = "Lo siento, no entendí tu mensaje."
    respuesta_texto = "Lo siento, no entendí tu mensaje."

    # Enviar respuesta rápida antes de iniciar Selenium
    if "reservar" in incoming_msg:
        threading.Thread(target=reservar_clase, args=()).start()  # Inicia la reserva en segundo plano
        print(f"📤 Respuesta enviada: {respuesta_texto}")
        return jsonify({"status": "success", "message": "⏳ Procesando tu reserva..."}), 200

    # Respuestas rápidas
    if "horarios" in incoming_msg:
        print(f"📤 Respuesta enviada: {respuesta_texto}")
        respuesta = "🕒 Los horarios y reservas están aquí: https://app.glofox.com/...", 200

    if "precios" in incoming_msg or "planes" in incoming_msg:
        print(f"📤 Respuesta enviada: {respuesta_texto}")
        return jsonify({"status": "success", "message": "💲 Consulta precios y membresías aquí: https://app.glofox.com/..."}), 200

    if "ubicación" in incoming_msg or "dirección" in incoming_msg:
        print(f"📤 Respuesta enviada: {respuesta_texto}")
        return jsonify({"status": "success", "message": "📍 Estamos ubicados en 2175 Davenport Blvd, Davenport FL 33837. ¡Te esperamos!..."}), 200

    if "teléfono" in incoming_msg or "contacto" in incoming_msg:
        print(f"📤 Respuesta enviada: {respuesta_texto}")
        return jsonify({"status": "success", "message": "📞 Nuestro número de contacto es +1 (863) 317-1646. Llámanos si necesitas más información..."}), 200
    
    if "sitio web" in incoming_msg or "página web" in incoming_msg:
        print(f"📤 Respuesta enviada: {respuesta_texto}")
        return jsonify({"status": "success", "message": "🌐 Puedes visitar nuestro sitio web aquí: https://spinzoneinc.com..."}), 200
    
    if "hola" in incoming_msg or "buenas" in incoming_msg:
        print(f"📤 Respuesta enviada: {respuesta_texto}")
        return jsonify({"status": "success", "message": " ¡Hola! Bienvenido a SpinZone. ¿En qué puedo ayudarte?..."}), 200
    
    elif "informacion" in incoming_msg or "más información" in incoming_msg:
        print(f"📤 Respuesta enviada: {respuesta_texto}")
        return jsonify({"status": "success", "message": "💲 Consulta precios y membresías aquí: https://app.glofox.com/..."}), 200

    # Aquí puedes llamar a la función de reserva si es necesario
    else:
        print(f"📤 Respuesta enviada: {respuesta_texto}")
        respuesta_texto = "Lo siento, no entendí tu mensaje."

    # 🔹 Guardar historial de conversación
    from_number = request.values.get("From", "").strip()
    cursor.execute("SELECT role, content FROM conversaciones WHERE user=? ORDER BY id ASC", (from_number,))
    historial = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
    historial.append({"role": "user", "content": incoming_msg})

    try:
        respuesta_ai = client_openai.chat.completions.create(
        model="gpt-4",
        messages=historial
    )

        # Verifica que el bot no diga que es una IA
        respuesta_texto = respuesta_ai.choices[0].message.content.strip()
        if "soy una inteligencia artificial" in respuesta_texto.lower():
            respuesta_texto = "Hola, ¿en qué puedo ayudarte?"



        # Guardar en la base de datos
        cursor.execute("INSERT INTO conversaciones (user, role, content) VALUES (?, ?, ?)", (from_number, "user", incoming_msg))
        cursor.execute("INSERT INTO conversaciones (user, role, content) VALUES (?, ?, ?)", (from_number, "assistant", respuesta_texto))
        conn.commit()

        msg.body(respuesta_texto)

        # 🔹 Si el usuario menciona "reservar clase", iniciar Selenium
        if "reservar clase" in incoming_msg.lower():
            respuesta_texto = reservar_clase()
            msg.body(respuesta)
            return str(resp)

    except Exception as e:
        print(f"❌ ERROR: {e}")
        msg.body("Lo siento, hubo un error al procesar tu mensaje. Inténtalo más tarde.")

    print(f"📤 Respuesta enviada: {respuesta}")

    # 📌 IMPORTANTE: Usar MessagingResponse() para que Twilio envíe la respuesta
    resp = MessagingResponse()
    resp.message(respuesta)

    return Response(resp.to_xml(), mimetype="application/xml")  # Responde en formato XML

# 🔹 Automatización con Selenium para reservas en Glofox
def whatsapp_reply():

    try:
        print("🔄 Iniciando Selenium...")

        # Configurar opciones de Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.binary_location = "/usr/bin/google-chrome"

        # Iniciar WebDriver con las opciones configuradas
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Abrir la página de reserva
        driver.get("https://app.glofox.com/")  # Reemplaza con la URL real
        print("🌍 Página cargada:", driver.title)

        # Esperar a que cargue el formulario de login
        print("⌛ Esperando que cargue el formulario de login...")
        elemento = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#login"))  # Verifica el selector
        )
        elemento.click()
        print("✅ Elemento encontrado y clickeado")

        # ✅ Abrir Glofox
        driver.get("https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view")
        time.sleep(3)

        # ✅ Hacer clic en "Login/Register"
        driver.find_element(By.CSS_SELECTOR, "#login-register-modal input").send_keys("luisamazon80@gmail.com")
        driver.find_element(By.CSS_SELECTOR, "#login-register-modal input[type='password']").send_keys("L.r14066719")
        driver.find_element(By.CSS_SELECTOR, "#login-register-modal button").click()
        time.sleep(3)

        # ✅ Comprar crédito gratuito (si aplica)
        driver.find_element(By.CSS_SELECTOR, "body > div.container > div.ng-scope > div:nth-child(4) > div.col.s12.m7.push-m1...").click()
        time.sleep(2)

        # ✅ Seleccionar fecha y hora de clase
        driver.find_element(By.CSS_SELECTOR, "body > div.container > div.ng-scope > div.slider > div.slider-wrapper > ul...").click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "body > div.container > div.ng-scope > div > ul > li:nth-child(1) > button").click()
        time.sleep(2)

        print("✅ Reserva completada con éxito")
        driver.quit()  # Siempre cerrar el navegador
        return "✅ Tu clase ha sido reservada con éxito."
    
    except Exception as e:
        print(f"❌ ERROR AL RESERVAR: {e}")  
        driver.quit()  # Asegurar cierre del navegador en caso de error
        return f"❌ Error al reservar: {e}"
    
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)

