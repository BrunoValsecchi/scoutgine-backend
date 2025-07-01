"""
URL configuration for scoutgine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # AJAX APIs - MANTENER CON PREFIJO
    path('ajax/', include('myapp.urls')),
    
    # FRONTEND PAGES - SERVIDAS POR WHITENOISE
    path('', TemplateView.as_view(template_name='index.html'), name='frontend_home'),
    path('menu/', TemplateView.as_view(template_name='menu.html'), name='frontend_menu'),
    path('ligas/', TemplateView.as_view(template_name='ligas.html'), name='frontend_ligas'),
    path('recomendacion/', TemplateView.as_view(template_name='recomendacion.html'), name='frontend_recomendacion'),
    path('comparacion/', TemplateView.as_view(template_name='comparacion.html'), name='frontend_comparacion'),
    path('equipo/', TemplateView.as_view(template_name='equipo.html'), name='frontend_equipo'),
    path('grafico/', TemplateView.as_view(template_name='grafico.html'), name='frontend_grafico'),
]
