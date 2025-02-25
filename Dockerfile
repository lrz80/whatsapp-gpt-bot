# Usa una imagen base de Python (o la que estés usando)
FROM python:3.10

# Instalar dependencias
RUN apt-get update && apt-get install -y wget curl unzip

# Descargar e instalar la versión más reciente de Chromium
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# Continúa con la instalación de dependencias y el código
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia el código de la aplicación
COPY . .

# Ejecuta la aplicación
CMD ["python", "app.py"]





