#!/bin/bash
echo "🚀 Building with cache optimization..."

# Use pip cache to speed up builds
pip install --upgrade pip
pip install --cache-dir=/tmp/pip-cache -r requirements.txt

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Build completed!"