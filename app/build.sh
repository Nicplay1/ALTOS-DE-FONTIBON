#!/usr/bin/env bash
#!/usr/bin/env bash
set -o errexit

echo "🚀 Instalando dependencias..."
pip install -r requirements.txt

echo "📂 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "📦 Aplicando migraciones..."
python manage.py migrate --noinput

echo "📦 Cargando datos iniciales..."
python manage.py init_datos || true

echo "✅ Deploy completado."




#!/usr/bin/env bash
#set -o errexit

#echo "🚀 Instalando dependencias..."
#pip install -r requirements.txt

#echo "⚙️ Aplicando migraciones nuevas..."
#python manage.py makemigrations --noinput
#python manage.py migrate --noinput

#echo "📂 Recolectando archivos estáticos..."
#python manage.py collectstatic --noinput

#echo "📦 Cargando datos iniciales si faltan..."
#python manage.py init_datos || true

#echo "✅ Base de datos actualizada sin eliminar datos."
