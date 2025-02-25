# Usa una imagen base de Python
FROM python:3.10-slim

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    chromium

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


