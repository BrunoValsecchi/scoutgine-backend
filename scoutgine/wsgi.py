"""
WSGI config for scoutgine project.
Compatible with Vercel deployment.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Configurar Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scoutgine.settings")

# Inicializar aplicación Django
try:
    application = get_wsgi_application()
except Exception as e:
    print(f"Error initializing Django application: {e}")
    raise

# Variables requeridas por Vercel
app = application
handler = application

# Para compatibilidad con diferentes runtimes
def lambda_handler(event, context):
    """Handler para AWS Lambda/Vercel Functions"""
    return application(event, context)
