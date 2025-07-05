"""Capa de base de datos: la próxima vez, usa SQLAlchemy"""
import mysql.connector
import config

def list_employees():
    """Selecciona todos los empleados de la base de datos."""
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT id, object_key, full_name, location, job_title, badges
        FROM employee
        ORDER BY full_name desc""")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def load_employee(employee_id):
    """Selecciona un empleado de la base de datos."""
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT id, object_key, full_name, location, job_title, badges
        FROM employee
        WHERE id = %(emp)s;""", {'emp': employee_id})
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def add_employee(object_key, full_name, location, job_title, badges):
    """Agrega un empleado a la base de datos."""
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""INSERT INTO employee (object_key, full_name, location, job_title, badges)
     VALUES (%s, %s, %s, %s, %s);""", (object_key, full_name, location, job_title, badges))
    conn.commit()
    cursor.close()
    conn.close()

def update_employee(employee_id, object_key, full_name, location, job_title, badges):
    """Actualiza un empleado en la base de datos."""
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)


    if object_key:
        cursor.execute("""
            UPDATE employee SET
            object_key=%s, full_name=%s, location=%s, job_title=%s, badges=%s
            WHERE id = %s;
         """, (object_key, full_name, location, job_title, badges, employee_id))
    else:
        # Si no se proporciona una clave de objeto, no la actualices.
        cursor.execute("""
            UPDATE employee SET
            full_name=%s, location=%s, job_title=%s, badges=%s
            WHERE id = %s;
         """, (full_name, location, job_title, badges, employee_id))

    conn.commit()
    cursor.close()
    conn.close()

def delete_employee(employee_id):
    """Elimina un empleado."""
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM employee WHERE id = %(emp)s;""", {'emp': employee_id})
    conn.commit()
    cursor.close()
    conn.close()

def get_database_connection():
    """Crea una conexión a la base de datos."""
    conn = mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD,
                                   host=config.DATABASE_HOST,
                                   database=config.DATABASE_DB_NAME,
                                   port=config.DATABASE_PORT,
                                   use_pure=True) # see https://bugs.mysql.com/90585
    return conn
