FROM python:3.10-slim

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    curl wget unzip chromium \
    && rm -rf /var/lib/apt/lists/*

# Instalar librerías de Python
RUN pip install --no-cache-dir selenium flask
RUN pip install --no-cache-dir selenium flask requests
RUN pip install --no-cache-dir selenium flask requests openai
RUN pip install --no-cache-dir selenium flask requests openai twilio
RUN pip install --no-cache-dir selenium flask requests openai twilio waitress
RUN pip install --no-cache-dir selenium flask requests openai twilio webdriver-manager

# Configurar variables de entorno
ENV PATH="/usr/lib/chromium/:${PATH}"
ENV CHROMIUM_PATH="/usr/bin/chromium"

# Copiar el código del proyecto
WORKDIR /app
COPY . .

# Ejecutar el bot
CMD ["python", "app.py"]




