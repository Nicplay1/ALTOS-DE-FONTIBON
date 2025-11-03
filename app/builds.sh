#!/bin/bash

# 🔹 Salir si hay un error
set -e

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Ejecutando migraciones..."
python manage.py migrate

echo "🔥 Build completado."
