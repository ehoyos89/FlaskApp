"""Configuración centralizada"""
import os

# Bucket de S3 para las fotos de los empleados.
PHOTOS_BUCKET = os.environ['PHOTOS_BUCKET']
# Clave secreta de Flask para la aplicación.
FLASK_SECRET = os.environ['FLASK_SECRET']
# Puerto de la base de datos.
DATABASE_PORT = 3306

# Host de la base de datos.
DATABASE_HOST = os.environ['DATABASE_HOST']
# Usuario de la base de datos.
DATABASE_USER = os.environ['DATABASE_USER']
# Contraseña de la base de datos.
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
# Nombre de la base de datos.
DATABASE_DB_NAME = os.environ['DATABASE_DB_NAME']
