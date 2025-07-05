"""Aplicación de demostración de Flask"""
import json
import os
import subprocess
import requests

from flask import Flask, render_template, render_template_string, url_for, redirect, flash, g
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, HiddenField, validators
import boto3

import config
import util

# Obtiene el documento de identidad de la instancia EC2.
def get_instance_document():
    """Obtiene el documento de identidad de la instancia EC2."""
    try:
        r = requests.get("http://169.254.169.254/latest/dynamic/instance-identity/document")
        if r.status_code == 401:
            token=(
                requests.put(
                    "http://169.254.169.254/latest/api/token", 
                    headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'}, 
                    verify=False, timeout=1
                )
            ).text
            r = requests.get(
                "http://169.254.169.254/latest/dynamic/instance-identity/document",
                headers={'X-aws-ec2-metadata-token': token}, timeout=1
            )
        r.raise_for_status()
        return r.json()
    except:
        print("Información de la instancia no disponible")
        return { "availabilityZone" : "us-fake-1a",  "instanceId" : "i-fakeabc" }


# Importa el módulo de base de datos adecuado según el modo.
if "DYNAMO_MODE" in os.environ:
    import database_dynamo as database
else:
    import database

# Inicializa la aplicación Flask.
application = Flask(__name__)
application.secret_key = config.FLASK_SECRET

# Obtiene información de la instancia.
doc = get_instance_document()
availablity_zone = doc["availabilityZone"]
instance_id = doc["instanceId"]

# Define las insignias de los empleados.
badges = {
    "apple" : "Usuario de Mac",
    "windows" : "Usuario de Windows",
    "linux" : "Usuario de Linux",
    "video-camera" : "Estrella de Contenido Digital",
    "trophy" : "Empleado del Mes",
    "camera" : "Fotógrafo",
    "plane" : "Viajero Frecuente",
    "paperclip" : "Aficionado a los Clips",
    "coffee" : "Experto en Café",
    "gamepad" : "Jugador",
    "bug" : "Solucionador de Errores",
    "umbrella" : "Fan de Seattle",
}

### Configuración de FlaskForm
class EmployeeForm(FlaskForm):
    """Clase de formulario flask_wtf"""
    employee_id = HiddenField()
    photo = FileField('image')
    full_name = StringField('Nombre Completo', [validators.InputRequired()])
    location = StringField('Ubicación', [validators.InputRequired()])
    job_title = StringField('Cargo', [validators.InputRequired()])
    badges = HiddenField('Insignias')

@application.before_request
def before_request():
    """Configura las variables globales a las que se hace referencia en las plantillas de Jinja."""
    g.availablity_zone = availablity_zone
    g.instance_id = instance_id

@application.route("/")
def home():
    """Pantalla de inicio"""
    s3_client = boto3.client('s3')
    employees = database.list_employees()
    if employees == 0:
        return render_template_string("""        
        {% extends "main.html" %}
        {% block head %}
        Directorio de Empleados de Flask - Inicio
        <a class="btn btn-primary float-right" href="{{ url_for('add') }}">Agregar</a>
        {% endblock %}
        """)
    else:
        for employee in employees:
            try:
                if "object_key" in employee and employee["object_key"]:
                    employee["signed_url"] = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': config.PHOTOS_BUCKET, 'Key': employee["object_key"]}
                    )
            except: 
                pass

    return render_template_string("""
        {% extends "main.html" %}
        {% block head %}
        Directorio de Empleados - Inicio
        <a class="btn btn-primary float-right" href="{{ url_for('add') }}">Agregar</a>
        {% endblock %}
        {% block body %}
            {%  if not employees %}<h4>Directorio Vacío</h4>{% endif %}

            <table class="table table-bordered">
              <tbody>
            {% for employee in employees %}
                <tr>
                  <td width="100">{% if employee.signed_url %}
                  <img width="50" src="{{employee.signed_url}}" /><br/>
                  {% endif %}
                  <a href="{{ url_for('delete', employee_id=employee.id) }}"><span class="fa fa-remove" aria-hidden="true"></span> eliminar</a>
                  </td>
                  <td><a href="{{ url_for('view', employee_id=employee.id) }}">{{employee.full_name}}</a>
                  {% for badge in badges %}
                  {% if badge in employee['badges'] %}
                  <i class="fa fa-{{badge}}" title="{{badges[badge]}}"></i>
                  {% endif %}
                  {% endfor %}
                  <br/>
                  <small>{{employee.location}}</small>
                  </td>
                </tr>
            {% endfor %}

              </tbody>
            </table>

        {% endblock %}
    """, employees=employees, badges=badges)

@application.route("/add")
def add():
    """Agrega un empleado."""
    form = EmployeeForm()
    return render_template("view-edit.html", form=form, badges=badges)

@application.route("/edit/<employee_id>")
def edit(employee_id):
    """Edita un empleado."""
    s3_client = boto3.client('s3')
    employee = database.load_employee(employee_id)
    signed_url = None
    if "object_key" in employee and employee["object_key"]:
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.PHOTOS_BUCKET, 'Key': employee["object_key"]}
        )

    form = EmployeeForm()
    form.employee_id.data = employee['id']
    form.full_name.data = employee['full_name']
    form.location.data = employee['location']
    form.job_title.data = employee['job_title']
    if 'badges' in employee:
        form.badges.data = employee['badges']

    return render_template("view-edit.html", form=form, badges=badges, signed_url=signed_url)

@application.route("/save", methods=['POST'])
def save():
    """Guarda un empleado."""
    form = EmployeeForm()
    s3_client = boto3.client('s3')
    key = None
    if form.validate_on_submit():
        if form.photo.data:
            image_bytes = util.resize_image(form.photo.data, (120, 160))
            if image_bytes:
                try:
                    # Guarda la imagen en S3.
                    prefix = "employee_pic/"
                    key = prefix + util.random_hex_bytes(8) + '.png'
                    s3_client.put_object(
                        Bucket=config.PHOTOS_BUCKET,
                        Key=key,
                        Body=image_bytes,
                        ContentType='image/png'
                    )
                except:
                    pass
        
        if form.employee_id.data:
            database.update_employee(
                form.employee_id.data,
                key,
                form.full_name.data,
                form.location.data,
                form.job_title.data,
                form.badges.data)
        else:
            database.add_employee(
                key,
                form.full_name.data,
                form.location.data,
                form.job_title.data,
                form.badges.data)
        flash("¡Guardado!")
        return redirect(url_for("home"))
    else:
        return "El formulario no se pudo validar"

@application.route("/employee/<employee_id>")
def view(employee_id):
    """Muestra un empleado."""
    s3_client = boto3.client('s3')
    employee = database.load_employee(employee_id)
    if "object_key" in employee and employee["object_key"]:
        try:
            employee["signed_url"] = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': config.PHOTOS_BUCKET, 'Key': employee["object_key"]}
            )
        except:
            pass
    form = EmployeeForm()

    return render_template_string("""
        {% extends "main.html" %}
        {% block head %}
            {{employee.full_name}}
            <a class="btn btn-primary float-right" href="{{ url_for("edit", employee_id=employee.id) }}">Editar</a>
            <a class="btn btn-primary float-right" href="{{ url_for('home') }}">Inicio</a>
        {% endblock %}
        {% block body %}

  <div class="row">
    <div class="col-md-4">
        {% if employee.signed_url %}
        <img alt="Mugshot" src="{{ employee.signed_url }}" />
        {% endif %}
    </div>

    <div class="col-md-8">
      <div class="form-group row">
        <label class="col-sm-2">{{form.location.label}}</label>
        <div class="col-sm-10">
        {{employee.location}}
        </div>
      </div>
      <div class="form-group row">
        <label class="col-sm-2">{{form.job_title.label}}</label>
        <div class="col-sm-10">
        {{employee.job_title}}
        </div>
      </div>
      {% for badge in badges %}
      <div class="form-check">
        {% if badge in employee['badges'] %}
        <span class="badge badge-primary"><i class="fa fa-{{badge}}"></i> {{badges[badge]}}</span>
        {% endif %}
      </div>
      {% endfor %}
      &nbsp;
    </div>
  </div>
</form>
        {% endblock %}
    """, form=form, employee=employee, badges=badges)

@application.route("/delete/<employee_id>")
def delete(employee_id):
    """Ruta para eliminar a un empleado."""
    database.delete_employee(employee_id)
    flash("¡Eliminado!")
    return redirect(url_for("home"))

@application.route("/info")
def info():
    """Ruta de información del servidor web."""
    return render_template_string("""
            {% extends "main.html" %}
            {% block head %}
                Información de la Instancia EC2
            {% endblock %}
            {% block body %}
            <b>ID de la Instancia</b>: {{g.instance_id}} <br/>
            <b>Zona de Disponibilidad</b>: {{g.availablity_zone}} <br/>
            <hr/>
            <small>Tiempo de stress al CPU:
            <a href="{{ url_for('stress', seconds=60) }}">1 min</a>,
            <a href="{{ url_for('stress', seconds=300) }}">5 min</a>,
            <a href="{{ url_for('stress', seconds=600) }}">10 min</a>
            </small>
            {% endblock %}""")

@application.route("/info/stress_cpu/<seconds>")
def stress(seconds):
    """Maximiza el uso de la CPU."""
    flash("Aplicando stress al CPU")
    subprocess.Popen(["stress", "--cpu", "8", "--timeout", seconds])
    return redirect(url_for("info"))

if __name__ == "__main__":
    application.run(debug=True)
