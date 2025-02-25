# Usa una imagen base de Python (o la que estés usando)
FROM python:3.10

# Instala wget y unzip antes de descargar ChromeDriver
RUN apt-get update && apt-get install -y wget unzip

# Descarga y configura ChromeDriver
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/linux64/chromedriver-linux64.zip" \
    -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /usr/local/bin/chromedriver-linux64

# Continúa con la instalación de dependencias y el código
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia el código de la aplicación
COPY . .

# Ejecuta la aplicación
CMD ["python", "app.py"]





