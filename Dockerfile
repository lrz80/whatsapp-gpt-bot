# Usa una imagen base de Python
FROM python:3.10-slim

# Instalar dependencias
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Instalar ChromeDriver compatible con Chromium 133
RUN wget -q "https://chromedriver.storage.googleapis.com/133.0.6943.126/chromedriver_linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip


# Definir variables de entorno para Selenium y Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="/root/.local/bin:$PATH"

# Instalar WebDriver Manager y dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]


