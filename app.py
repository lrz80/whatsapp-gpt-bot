import os
import time
import openai
import sqlite3
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

# 🔹 Respuestas rápidas
FAQS = {
    "horarios": "📅 Los horarios y reservas están aquí: https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view",
    "reservas": "🔹 Reserva tu clase aquí: https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/classes-day-view",
    "precios": "💰 Consulta precios y membresías aquí: https://app.glofox.com/portal/#/branch/6499ecc2ba29ef91ae07e461/memberships",
    "direccion": if "ubicación" in incoming_msg.lower():
    msg.body("📍 Estamos ubicados en 2175 Davenport Blvd Davenport Fl 33837. ¡Te esperamos!"),
    "telefono": if "teléfono" in incoming_msg.lower():
    msg.body("📞 Nuestro número de contacto es +1 (863) 317-1646. ¡Llámanos si necesitas más información!"),
    "pagina web": if "sitio web" in incoming_msg.lower():
        msg.body("🌐 Puedes visitar nuestro sitio web aquí: https://spinzoneic.com"),
    "reservar": if "reservar clase" in incoming_msg.lower():
        msg.body("¡Claro! Estoy procesando tu reserva...")
        respuesta = reservar_clase()
        msg.body(respuesta)"    
}

@app.route("/", methods=["GET"])
def home():
    return "¡Servidor funcionando correctamente en Railway!"

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    from_number = request.values.get("From", "").strip()
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    # 🔹 Respuestas rápidas
    for key, value in FAQS.items():
        if key in incoming_msg:
            msg.body(value)
            return str(resp)

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
            respuesta_texto = "Soy el asistente virtual de SpinZone, ¿en qué puedo ayudarte?"

        respuesta_texto = respuesta_ai.choices[0].message.content.strip()


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
        # Configurar WebDriver
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)

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
