# Directorio de Empleados (Aplicación Flask)

Esta es una aplicación web de demostración construida con Flask que sirve como un directorio de empleados. Permite a los usuarios realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para gestionar la información de los empleados, incluyendo sus fotos y credenciales.

## Características Principales

- **Gestión de Empleados:** Permite listar, agregar, editar y eliminar empleados del directorio.
- **Fotos de Empleados:** Sube, redimensiona y muestra las fotos de los empleados. Las imágenes se almacenan de forma segura en un bucket de Amazon S3.
- **Asignación de Credenciales (Badges):** Asigna credenciales visuales a los empleados para destacar sus habilidades o logros (por ejemplo, "Usuario de Linux", "Fotógrafo", "Jugador").
- **Doble Soporte de Base de Datos:** La aplicación puede funcionar con **MySQL** o **Amazon DynamoDB**, configurable a través de variables de entorno.
- **Información de la Instancia EC2:** Muestra metadatos de la instancia EC2 donde se ejecuta la aplicación, como el ID de la instancia y la zona de disponibilidad.
- **Prueba de Estrés de CPU:** Incluye una función para realizar pruebas de estrés en la CPU del servidor, útil para demostraciones y monitorización.

## Requisitos Previos

- Python 3.x
- Pip (manejador de paquetes de Python)
- Un servidor de base de datos **MySQL** O una tabla en **Amazon DynamoDB**.
- Un bucket de **Amazon S3** para el almacenamiento de fotos.
- Credenciales de AWS configuradas en el entorno donde se ejecuta la aplicación (si se usa DynamoDB o S3).

## Instalación y Configuración

Sigue estos pasos para configurar y ejecutar la aplicación en tu entorno local o en un servidor.

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd <directorio-del-proyecto>
```

### 2. Instalar Dependencias

Instala todas las librerías de Python necesarias:

```bash
pip install -r requirements.txt
```

### 3. Configuración de la Base de Datos

Puedes elegir entre MySQL o DynamoDB.

#### Opción A: Usar MySQL

1.  **Crear la Base de Datos y la Tabla:** Ejecuta el script `database_create_tables.sql` en tu servidor MySQL para crear la base de datos `flaskdb` y la tabla `employee`.

    ```sql
    CREATE DATABASE IF NOT EXISTS flaskdb;
    USE flaskdb;

    CREATE TABLE IF NOT EXISTS employee (
      id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
      object_key NVARCHAR(80),
      full_name NVARCHAR(200) NOT NULL,
      location NVARCHAR(200) NOT NULL,
      job_title NVARCHAR(200) NOT NULL,
      badges NVARCHAR(200) NOT NULL,
      created_datetime DATETIME DEFAULT NOW()
    );
    ```

2.  **Configurar Variables de Entorno para MySQL:**
    No establezcas la variable `DYNAMO_MODE`. En su lugar, define las siguientes variables para la conexión a MySQL:

    ```bash
    export DATABASE_HOST="tu_host_mysql"
    export DATABASE_USER="tu_usuario_mysql"
    export DATABASE_PASSWORD="tu_contraseña_mysql"
    export DATABASE_DB_NAME="flaskdb"
    ```

#### Opción B: Usar Amazon DynamoDB

1.  **Crear la Tabla en DynamoDB:**
    - Ve a la consola de Amazon DynamoDB.
    - Crea una nueva tabla con el nombre `Employees`.
    - Define la clave de partición (Partition Key) como `id` de tipo `String`.
    - No se necesita una clave de ordenación (Sort Key).

2.  **Configurar Variable de Entorno para DynamoDB:**
    Establece la siguiente variable de entorno para activar el modo DynamoDB:

    ```bash
    export DYNAMO_MODE=on
    ```

### 4. Configuración del Bucket de Amazon S3

La aplicación necesita un bucket de S3 para almacenar las fotos de los empleados.

1.  Crea un bucket en Amazon S3.
2.  Asegúrate de que los permisos del bucket permitan a la aplicación (a través de su rol de IAM) realizar acciones `PutObject` y `GetObject`.
3.  Establece la siguiente variable de entorno:

    ```bash
    export PHOTOS_BUCKET="tu-nombre-de-bucket-s3"
    ```

### 5. Configuración de la Clave Secreta de Flask

Flask requiere una clave secreta para gestionar las sesiones de forma segura.

```bash
export FLASK_SECRET="una-clave-secreta-muy-segura"
```

## Cómo Ejecutar la Aplicación

Una vez que hayas configurado las variables de entorno para la base de datos y S3, puedes iniciar la aplicación con el servidor de desarrollo de Flask:

```bash
flask run
```

Por defecto, la aplicación estará disponible en `http://127.0.0.1:5000`.

Para ejecutarla en un puerto o host específico (por ejemplo, para que sea accesible en tu red local):

```bash
flask run --host=0.0.0.0 --port=8080
```

## Uso de la Aplicación

- **Página Principal:** Muestra una lista de todos los empleados con su foto y nombre. Desde aquí puedes eliminar empleados o hacer clic en su nombre para ver más detalles.
- **Agregar Empleado:** Haz clic en el botón "Add" para ir al formulario de creación de un nuevo empleado.
- **Editar Empleado:** En la página de vista de un empleado, haz clic en "Edit" para modificar su información.
- **Asignar Credenciales (Badges):** En el formulario de edición/creación, puedes seleccionar una o más credenciales para el empleado.
- **Página de Información:** El enlace "Info" en la barra de navegación te lleva a una página que muestra los metadatos de la instancia EC2 y te da opciones para realizar una prueba de estrés de CPU.

## Detalles Técnicos

- **Backend:** Flask
- **Frontend:** Jinja2 templates con HTML y Bootstrap para el estilo.
- **Base de Datos:** `mysql-connector-python` para MySQL y `boto3` para DynamoDB.
- **Almacenamiento de Archivos:** `boto3` para la integración con Amazon S3.
- **Procesamiento de Imágenes:** La librería `Pillow` se utiliza para redimensionar las imágenes antes de subirlas a S3.
