"""
URL configuration for scoutgine project - API BACKEND ONLY
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def api_root(request):
    return JsonResponse({
        'message': 'ScoutGine API Backend',
        'version': '1.0',
        'status': 'active',
        'endpoints': {
            'ligas': '/ajax/ligas/',
            'equipos': '/ajax/equipos/',
            'jugadores': '/ajax/jugadores/',
            'stats_equipos': '/stats_equipos/',
            'stats_jugadores': '/stats_jugadores/',
            'recomendacion': '/ajax/recomendacion/',
            'comparacion': '/ajax/comparacion/',
            'equipo_detalle': '/equipo_detalle/<id>/',  # ✅ AGREGAR ESTA LÍNEA
        },
        'frontend_url': 'https://scoutgine-frontend.onrender.com'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api_root'),
    
    # ✅ RUTAS AJAX (van primero para evitar conflictos)
    path('ajax/', include('myapp.urls')),
    
    # ✅ RUTAS DE PÁGINAS (van después)
    path('', include('myapp.urls')),  # Para otras páginas HTML
]

# ✅ SERVIR ARCHIVOS ESTÁTICOS EN DESARROLLO
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)