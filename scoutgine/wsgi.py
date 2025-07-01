"""
WSGI config for scoutgine project.
Compatible with Vercel deployment.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scoutgine.settings')

application = get_wsgi_application()

# Variables requeridas por Vercel
app = application
handler = application

# Para compatibilidad con diferentes runtimes
def lambda_handler(event, context):
    """Handler para AWS Lambda/Vercel Functions"""
    return application(event, context)
