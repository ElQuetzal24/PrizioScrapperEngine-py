FROM python:3.11-bullseye

WORKDIR /app

# Instalar dependencias de sistema necesarias
RUN apt-get update && \
    apt-get install -y curl gnupg unixodbc-dev gcc g++ && \
    apt-get remove -y libodbc2 libodbcinst2 unixodbc-common || true && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar navegadores de Playwright
RUN playwright install --with-deps

# Ejecutar el script principal
CMD ["python", "entrypoint.py"]
