# Usa una imagen base de Python (o la que estés usando)
FROM python:3.10

# Instalar dependencias
RUN apt-get update && apt-get install -y wget curl unzip

# Instalar Google Chrome en lugar de Chromium
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/google-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update && apt-get install -y google-chrome-stable

# Continúa con la instalación de dependencias y el código
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia el código de la aplicación
COPY . .

# Ejecuta la aplicación
CMD ["python", "app.py"]





