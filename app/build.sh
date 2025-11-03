#!/usr/bin/env bash
set -o errexit

echo "🚀 Instalando dependencias..."
pip install -r requirements.txt

echo "⚙️ Limpiando migraciones viejas..."
python manage.py migrate usuario zero --noinput
python manage.py migrate vigilante zero --noinput
python manage.py migrate residente zero --noinput
python manage.py migrate administrador zero --noinput

echo "🧩 Volviendo a crear migraciones..."
python manage.py makemigrations
python manage.py migrate --noinput

echo "✅ Migraciones aplicadas correctamente."
