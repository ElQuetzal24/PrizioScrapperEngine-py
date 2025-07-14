# Imagen base ligera con Python 3.11
FROM python:3.11-slim

# Evitar interacción en instalación de paquetes
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema necesarias para Playwright y ODBC
RUN apt-get update && \
    apt-get install -y curl gnupg apt-transport-https software-properties-common && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y \
        msodbcsql17 \
        unixodbc-dev \
        gcc g++ \
        libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
        libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libxshmfence1 \
        libx11-xcb1 libgtk-3-0 libxss1 libnss3 libdrm2 \
        build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar navegadores para Playwright
RUN playwright install --with-deps

# Variables de entorno (si se requieren adicionales)
ENV PYTHONUNBUFFERED=1

# Comando de ejecución (ajustable según el entrypoint)
CMD ["python", "entrypoint.py"]
