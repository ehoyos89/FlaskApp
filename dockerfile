# Etapa 1: Build - Instala dependencias y compila paquetes
# Usamos una imagen completa de Python para tener las herramientas de compilación
FROM python:3.12 as builder

# Variables de entorno para la compilación
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala dependencias del sistema necesarias para compilar mysqlclient
RUN apt-get update && apt-get install -y     build-essential

# Establece el directorio de trabajo
WORKDIR /app

# Instala las dependencias de Python en un entorno virtual
COPY requirements.txt .
RUN python -m venv /opt/venv
RUN /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---

# Etapa 2: Final - Crea la imagen de producción final
# Usamos una imagen slim de Python para reducir el tamaño
FROM python:3.12-slim

# Información del mantenedor
LABEL maintainer="erick.hoyos@outlook.com"
LABEL description="Imagen de Docker para aplicación de Python con dependencias"

# Variables de entorno para la ejecución
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=application.py \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    PORT=5000

# Crea un grupo y usuario no-root para mayor seguridad
RUN groupadd --system flaskgroup && useradd --system --gid flaskgroup --shell /bin/false flaskuser

# Establece el directorio de trabajo
WORKDIR /app

# Copia el entorno virtual con las dependencias desde la etapa de build
COPY --from=builder /opt/venv /opt/venv

# Copia el código de la aplicación
COPY . .

# Cambia la propiedad de los archivos al usuario no-root
RUN chown -R flaskuser:flaskgroup /app

# Cambia al usuario no-root
USER flaskuser

# Expone el puerto en el que correrá la aplicación
EXPOSE 5000

# Comando para iniciar la aplicación usando Gunicorn
# Inicia 4 workers, enlaza al puerto 5000 y establece un timeout de 120s
ENTRYPOINT [ "gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "--timeout=120", "application:application" ]
