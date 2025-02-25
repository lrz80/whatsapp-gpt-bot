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

# Instalar Google Chrome estable
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libdbus-glib-1-2 \
    libgtk-3-0 \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*


# Continúa con la instalación de dependencias y el código
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia el código de la aplicación
COPY . .

# Ejecuta la aplicación
CMD ["python", "app.py"]





