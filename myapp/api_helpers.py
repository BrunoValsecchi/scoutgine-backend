from django.http import JsonResponse
from django.utils import timezone

def api_status(request):
    """Endpoint simple para verificar conexión"""
    return JsonResponse({
        'status': 'connected',
        'message': 'Backend funcionando correctamente',
        'timestamp': str(timezone.now())
    })

def stats_jugadores_wrapper(request):
    """Wrapper para stats de jugadores usando funciones existentes"""
    try:
        from .models import EstadisticasJugador, Jugador
        
        # Obtener datos usando el modelo existente
        total_jugadores = Jugador.objects.count()
        total_stats = EstadisticasJugador.objects.count()
        
        print(f"📊 Stats Jugadores: {total_jugadores} jugadores, {total_stats} estadísticas")
        
        if total_stats == 0:
            return JsonResponse({
                'goleadores': [],
                'asistencias': [],
                'tarjetas_amarillas': [],
                'tarjetas_rojas': [],
                'message': 'No hay estadísticas de jugadores en la base de datos',
                'status': 'success'
            })
        
        # Obtener estadísticas usando el modelo existente
        stats_jugadores = EstadisticasJugador.objects.select_related('jugador', 'jugador__equipo').all()
        
        # Preparar datos para rankings - SOLO CAMPOS QUE EXISTEN
        jugadores_data = []
        
        for stat in stats_jugadores:
            if stat.jugador:
                jugador_info = {
                    'nombre': stat.jugador.nombre,
                    'equipo': stat.jugador.equipo.nombre if stat.jugador.equipo else 'Sin equipo',
                    'goles': stat.goals or 0,
                    'asistencias': stat.assists or 0,
                    'amarillas': stat.yellow_cards or 0,
                    'rojas': stat.red_cards or 0,
                }
                
                # ✅ ELIMINÉ REFERENCIA A 'partidos' y 'minutos' - NO EXISTEN
                jugadores_data.append(jugador_info)
        
        # Crear rankings - SIN partidos NI minutos
        goleadores = sorted(jugadores_data, key=lambda x: x['goles'], reverse=True)[:20]
        asistencias = sorted(jugadores_data, key=lambda x: x['asistencias'], reverse=True)[:20]
        tarjetas_amarillas = sorted(jugadores_data, key=lambda x: x['amarillas'], reverse=True)[:20]
        tarjetas_rojas = sorted(jugadores_data, key=lambda x: x['rojas'], reverse=True)[:20]
        
        print(f"✅ Procesados {len(jugadores_data)} jugadores")
        
        return JsonResponse({
            'goleadores': goleadores,
            'asistencias': asistencias,
            'tarjetas_amarillas': tarjetas_amarillas,
            'tarjetas_rojas': tarjetas_rojas,
            'total_jugadores': len(jugadores_data),
            'status': 'success'
        })
        
    except Exception as e:
        print(f"❌ Error en stats_jugadores: {e}")
        return JsonResponse({
            'goleadores': [],
            'asistencias': [],
            'tarjetas_amarillas': [],
            'tarjetas_rojas': [],
            'error': str(e),
            'status': 'error'
        }, status=500)