#!/bin/bash
set -e

echo "🧹 Eliminando migraciones antiguas..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "⚙️ Creando nuevas migraciones..."
python manage.py makemigrations --noinput || true

echo "🚀 Aplicando migraciones..."
python manage.py migrate --noinput || true

echo "✅ Build completado exitosamente"
