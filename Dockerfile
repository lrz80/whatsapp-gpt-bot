# Usa una imagen base con Python
FROM python:3.10-slim

# Instala dependencias
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    chromium \
    chromium-driver

# Especificar la versión de ChromeDriver compatible con Google Chrome
ENV CHROMEDRIVER_VERSION=133.0.6943.126

# Descargar e instalar ChromeDriver manualmente
RUN wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Establecer Chrome como la ruta predeterminada del navegador
ENV CHROME_BIN=/usr/bin/chromium

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]


