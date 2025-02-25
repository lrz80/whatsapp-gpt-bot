FROM python:3.10-slim

# Instalar dependencias
RUN apt-get update && apt-get install -y \
    curl unzip chromium \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar ChromeDriver manualmente
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip

# Instalar librerías de Python
RUN pip install --no-cache-dir selenium flask

# Configurar variables de entorno
ENV PATH="/usr/lib/chromium/:${PATH}"
ENV CHROMIUM_PATH="/usr/bin/chromium"

# Copiar el código del proyecto
WORKDIR /app
COPY . .

# Ejecutar el bot
CMD ["python", "app.py"]


