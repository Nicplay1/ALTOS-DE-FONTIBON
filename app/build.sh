#!/bin/bash
set -e

echo "🚀 Instalando dependencias..."
pip install -r requirements.txt

echo "⚙️ Aplicando migraciones..."
python app/manage.py makemigrations
python app/manage.py migrate --noinput

echo "✅ Migraciones aplicadas correctamente."
