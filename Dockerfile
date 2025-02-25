FROM python:3.10-slim

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    curl wget unzip chromium \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar ChromeDriver manualmente
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver*

# Instalar librerías de Python
RUN pip install --no-cache-dir selenium flask
RUN pip install --no-cache-dir selenium flask requests
RUN pip install --no-cache-dir selenium flask requests openai
RUN pip install --no-cache-dir selenium flask requests openai twilio
RUN pip install --no-cache-dir selenium flask requests openai twilio webdriver-manager

# Configurar variables de entorno
ENV PATH="/usr/lib/chromium/:${PATH}"
ENV CHROMIUM_PATH="/usr/bin/chromium"

# Copiar el código del proyecto
WORKDIR /app
COPY . .

# Ejecutar el bot
CMD ["python", "app.py"]




