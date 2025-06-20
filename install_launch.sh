#!/bin/bash -ex
#yum -y install python3 mysql
#pip3 install -r requirements.txt
#amazon-linux-extras install epel
#yum -y install stress
#export PHOTOS_BUCKET=${SUB_PHOTOS_BUCKET}
#export DATABASE_HOST=${SUB_DATABASE_HOST}
#export DATABASE_USER=${SUB_DATABASE_USER}
#export DATABASE_PASSWORD=${SUB_DATABASE_PASSWORD}
#export DATABASE_DB_NAME=employees
#cat database_create_tables.sql | \
#mysql -h $$DATABASE_HOST -u $$DATABASE_USER -p$$DATABASE_PASSWORD
#FLASK_APP=application.py /usr/local/bin/flask run --host=0.0.0.0 --port=80


echo "🔄 Activando entorno virtual..."
source venv/bin/activate

echo "🔧 Configurando variables de entorno..."
export PHOTOS_BUCKET="local-photos-bucket"
export DATABASE_HOST="localhost"
export DATABASE_USER="flask_user"  # o "root" si prefieres usar root
export DATABASE_PASSWORD="Cloud-1027"
export DATABASE_DB_NAME="employees"
export FLASK_ENV=development
export FLASK_DEBUG=1

echo "🔍 Probando conexión a MySQL..."
mysql -u $DATABASE_USER -p$DATABASE_PASSWORD -h $DATABASE_HOST -e "USE $DATABASE_DB_NAME; SELECT COUNT(*) as 'Total empleados' FROM employee;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Conexión a MySQL exitosa"
    echo "🚀 Iniciando aplicación Flask..."
    flask --app application.py run --host=0.0.0.0 --port=5000
else
    echo "❌ Error: No se puede conectar a MySQL"
    echo "💡 Verifica que MySQL esté ejecutándose: sudo systemctl status mysqld"
    echo "💡 Verifica las credenciales en las variables de entorno"
fi