from django.urls import path
from . import views
from .ligas import ligas
from .statsequipo import stats_equipos
from .estadistica_jugador import (
    ajax_radar_jugador,
    ajax_ranking_jugadores,
    ajax_evolucion_jugador,
    ajax_percentil_jugador,
    ajax_grafico_dispersion_jugador,
    api_jugador_posiciones,
    ajax_boxplot_jugador,
    ajax_jugador_estadistica
)
from . import statsjugadores

urlpatterns = [
    # ✅ PÁGINAS PRINCIPALES
    path('equipo_detalle/<int:equipo_id>/', views.equipo_detalle, name='equipo_detalle_page'),
    path('ligas/', ligas, name='ligas'),
    path('stats-equipos/', stats_equipos, name='stats_equipos'),
    path('stats-jugadores/', statsjugadores.stats_jugadores, name='stats_jugadores'),
    path('menu/', views.menu, name='menu'),
    path('equipo/', views.equipo, name='equipo'),
    path('comparacion/', views.comparacion, name='comparacion'),
    path('recomendacion/', views.recomendacion, name='recomendacion'),
    path('jugador/<int:jugador_id>/', views.jugador_detalle, name='jugador_detalle'),
    
    # ✅ APIS AJAX ESPECÍFICAS (DEBEN IR ANTES QUE LAS GENÉRICAS)
    path('ajax/equipos/', views.ajax_equipos, name='ajax_equipos'),
    path('ajax/equipo/<int:equipo_id>/info/', views.ajax_equipo_info, name='ajax_equipo_info'),
    path('ajax/equipo/<int:equipo_id>/plantilla/', views.ajax_equipo_plantilla, name='ajax_equipo_plantilla'),
    path('ajax/equipo/<int:equipo_id>/estadisticas/', views.ajax_equipo_estadisticas, name='ajax_equipo_estadisticas'),
    path('ajax/equipo/<int:equipo_id>/jugadores/', views.ajax_equipo_jugadores, name='ajax_equipo_jugadores'),  # ✅ NUEVA
    path('ajax/recomendar-jugadores/', views.ajax_recomendar_jugadores, name='ajax_recomendar_jugadores'),
    path('ajax/grafico-dispersion/', views.ajax_grafico_dispersion, name='ajax_grafico_dispersion'),
    path('ajax/analisis-correlacion/', views.ajax_analisis_correlacion, name='ajax_analisis_correlacion'),
    path('ajax/radar-equipo/', views.ajax_radar_equipo, name='ajax_radar_equipo'),
    path('ajax/boxplot-estadistica/', views.ajax_boxplot_estadistica, name='ajax_boxplot_estadistica'),
    path('ajax/radar-jugador/', ajax_radar_jugador, name='ajax_radar_jugador'),
    path('ajax/ranking-jugadores/', ajax_ranking_jugadores, name='ajax_ranking_jugadores'),
    path('ajax/evolucion-jugador/', ajax_evolucion_jugador, name='ajax_evolucion_jugador'),
    path('ajax/percentil-jugador/', ajax_percentil_jugador, name='ajax_percentil_jugador'),
    path('ajax/grafico-dispersion-jugador/', ajax_grafico_dispersion_jugador, name='ajax_grafico_dispersion_jugador'),
    path('ajax/boxplot-jugador/', ajax_boxplot_jugador, name='ajax_boxplot_jugador'),
    path('api/jugador/<int:jugador_id>/posiciones/', api_jugador_posiciones, name='api_jugador_posiciones'),

    # ✅ OTRAS PÁGINAS Y APIS
    path('grafico/', views.grafico, name='grafico'),
    path('jugador/<int:jugador_id>/grafico/<str:estadistica>/', views.grafico_jugador_view, name='grafico_jugador'),
    
    # ✅ RUTAS GENÉRICAS AL FINAL
    path('ajax/equipo/<int:equipo_id>/estadistica/<str:estadistica>/', views.ajax_equipo_estadistica_detalle, name='ajax_equipo_estadistica_detalle'),
    path('grafico-equipo/<int:equipo_id>/<str:stat_name>/', views.grafico_equipo, name='grafico_equipo_stat'),

    # ✅ RUTAS PARA COMPARACIÓN
    path('ajax/comparar-equipos/', views.ajax_comparar_equipos, name='ajax_comparar_equipos'),
    path('ajax/comparar-jugadores/', views.ajax_comparar_jugadores, name='ajax_comparar_jugadores'),
    
    # ✅ RUTAS PARA COMPARACIÓN COMPLETA (ESTADÍSTICAS)
    path('ajax/comparar-equipos-completo/', views.ajax_comparar_equipos_completo, name='ajax_comparar_equipos_completo'),
    path('ajax/comparar-jugadores-completo/', views.ajax_comparar_jugadores_completo, name='ajax_comparar_jugadores_completo'),
    
    # ✅ RUTAS PARA GRUPOS DE ESTADÍSTICAS
    path('ajax/grupos-stats-equipos/', views.ajax_grupos_stats_equipos, name='ajax_grupos_stats_equipos'),
    path('ajax/grupos-stats-jugadores/', views.ajax_grupos_stats_jugadores, name='ajax_grupos_stats_jugadores'),
    path('ajax/jugador/<int:jugador_id>/estadistica/<str:estadistica>/', ajax_jugador_estadistica, name='ajax_jugador_estadistica'),
]
