import os
import subprocess

def install_chrome_and_driver():
    try:
        print("🚀 Instalando Chrome y ChromeDriver...")

        # Instalar dependencias necesarias
        subprocess.run("apt-get update && apt-get install -y wget curl unzip", shell=True, check=True)
        subprocess.run("apt-get install -y libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxrandr2 libxrender1", shell=True, check=True)

        # Descargar e instalar Google Chrome
        subprocess.run("curl -o /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", shell=True, check=True)
        subprocess.run("dpkg -i /tmp/chrome.deb || apt-get -fy install", shell=True, check=True)

        # Obtener la versión correcta de ChromeDriver
        chrome_version = subprocess.check_output("google-chrome --version | awk '{print $3}'", shell=True).decode("utf-8").strip()
        chromedriver_version = subprocess.check_output(f"curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}", shell=True).decode("utf-8").strip()

        # Descargar e instalar ChromeDriver
        subprocess.run(f"curl -o /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_linux64.zip", shell=True, check=True)
        subprocess.run("unzip /tmp/chromedriver.zip -d /usr/bin/", shell=True, check=True)
        subprocess.run("chmod +x /usr/bin/chromedriver", shell=True, check=True)

        print("✅ Chrome y ChromeDriver instalados correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando Chrome/ChromeDriver: {e}")

# Ejecutar instalación solo en Railway
if __name__ == "__main__":
    install_chrome_and_driver()

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
    from_number = request.values.get("From", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    # 🔹 Respuestas rápidas
    incoming_msg = request.values.get("Body", "").strip().lower()
    if "horarios" in incoming_msg:
        respuesta = "📅 Los horarios y reservas están aquí: https://app.glofox.com/..."
    elif "reservas" in incoming_msg:
        respuesta = "🎟 Reserva tu clase aquí: https://app.glofox.com/..."
    elif "precios" in incoming_msg:
        respuesta = "💲 Consulta precios y membresías aquí: https://app.glofox.com/..."
    elif "ubicación" in incoming_msg or "dirección" in incoming_msg:
        respuesta = "📍 Estamos ubicados en 2175 Davenport Blvd, Davenport FL 33837. ¡Te esperamos!"
    elif "teléfono" in incoming_msg or "contacto" in incoming_msg:
        respuesta = "📞 Nuestro número de contacto es +1 (863) 317-1646. Llámanos si necesitas más información."
    elif "sitio web" in incoming_msg or "página web" in incoming_msg:
        respuesta = "🌐 Puedes visitar nuestro sitio web aquí: https://spinzoneinc.com"
    elif "reservar clase" in incoming_msg:
        respuesta = "¡Claro! Estoy procesando tu reserva..."
    if "reservar_clase" in globals():  # Verifica si la función existe
        reservar_clase()  
    elif "hola" in incoming_msg or "buenas" in incoming_msg:
        respuesta = "¡Hola! Bienvenido a SpinZone. ¿En qué puedo ayudarte?"
    # Aquí puedes llamar a la función de reserva si es necesario
    else:
        respuesta = "Lo siento, no entendí tu mensaje. ¿Puedes reformularlo?"

    msg.body(respuesta)  # Enviar la respuesta al usuario

    # 🔹 Guardar historial de conversación
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
            respuesta = reservar_clase()
            msg.body(respuesta)
            return str(resp)

    except Exception as e:
        print(f"❌ ERROR: {e}")
        msg.body("Lo siento, hubo un error al procesar tu mensaje. Inténtalo más tarde.")

    return str(resp)

# 🔹 Automatización con Selenium para reservas en Glofox
def reservar_clase():
    try:
        # Reemplaza "TU_API_KEY" con la API Key de Browserless
        browserless_url = "wss://chrome.browserless.io?token=RpjC71GraniIGGbace2d072e1f4e476227bf2556b4"

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Conectar Selenium con Browserless
        driver = webdriver.Remote(
            command_executor=browserless_url,
            desired_capabilities=options.to_capabilities()
        )



        # 🔹 Abrir Glofox
        driver.get("https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view")
        time.sleep(3)

        # 🔹 Hacer clic en "Login/Register"
        driver.find_element(By.CSS_SELECTOR, "body > div.container > div:nth-child(2) > div > div > ul.header-options > li:nth-child(2)").click()
        time.sleep(2)

        # 🔹 Iniciar sesión (modificar con credenciales de prueba)
        driver.find_element(By.CSS_SELECTOR, "#login-register-modal input").send_keys("luisamazon80@gmail.com")
        driver.find_element(By.CSS_SELECTOR, "#login-register-modal input[type='password']").send_keys("L.r14066719")
        driver.find_element(By.CSS_SELECTOR, "#login-register-modal button").click()
        time.sleep(3)

        # 🔹 Comprar crédito gratuito
        driver.find_element(By.CSS_SELECTOR, "body > div.container > div.ng-scope > div:nth-child(4) > div.col.s12.m7.push-m1.col-padding > div > ul > li > button").click()
        time.sleep(2)

        # 🔹 Seleccionar fecha y hora de clase
        driver.find_element(By.CSS_SELECTOR, "body > div.container > div.ng-scope > div > div.slider > div.slider-wrapper > ul > li:nth-child(4) > span").click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "body > div.container > div.ng-scope > div > ul > li:nth-child(1) > button").click()
        time.sleep(2)

        print("✅ Reserva completada con éxito")
        driver.quit()

    except Exception as e:
        print(f"❌ ERROR AL RESERVAR: {e}")

if __name__ == "__main__":
    from waitress import serve
    PORT = int(os.environ.get("PORT", 5000))
    print(f"🚀 Servidor iniciando en http://0.0.0.0:{PORT}")
    serve(app, host="0.0.0.0", port=PORT)
