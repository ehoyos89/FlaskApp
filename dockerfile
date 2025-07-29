# Usar imagen de tamaño reducido
FROM python:3.14.0rc1-alpine3.22

# Información del mantenedor
LABEL maintainer="erick.hoyos@outlook.com"
LABEL description="Imagen de Docker para aplicación de Python con dependencias"

# Establecer variables de entorno (solo no sensibles)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=application.py \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    PORT=5000

# Crear usuario no-root para seguridad
#RUN groupadd -r flaskgroup && useradd -r -g flaskgroup flaskuser
RUN addgroup -S flaskgroup && adduser -S -G flaskgroup flaskuser


# Instalar dependencias del sistema necesarias para MySQL
RUN apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    pkgconfig

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Cambiar ownership de los archivos al usuario no-root
RUN chown -R flaskuser:flaskgroup /app

# Cambiar al usuario no-root
USER flaskuser

# Exponer el puerto
EXPOSE 5000

ENTRYPOINT [ "python", "application.py" ]