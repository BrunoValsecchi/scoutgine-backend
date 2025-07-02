import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Posicion, Torneo, Equipo

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def ligas(request):
    print("🔥 VISTA LIGAS LLAMADA")  # ← DEBUG
    logger.debug('Vista ligas llamada')
    
    try:
        # ✅ VERIFICAR QUE HAY DATOS
        total_torneos = Torneo.objects.count()
        total_posiciones = Posicion.objects.count()
        total_equipos = Equipo.objects.count()
        
        print(f"📊 DB Info: {total_torneos} torneos, {total_posiciones} posiciones, {total_equipos} equipos")
        
        if total_torneos == 0:
            return JsonResponse({
                'torneos': {},
                'message': 'No hay torneos en la base de datos',
                'total_torneos': 0,
                'status': 'success'
            })
        
        # Agrupar por nombre y zona
        torneos = Torneo.objects.all().order_by('nombre', 'zona')[:10]  # ← LIMITAR PARA DEBUG
        zonas_dict = {}
        
        for torneo in torneos:
            print(f"🏆 Procesando torneo: {torneo.nombre} - Zona: {torneo.zona}")
            
            key = f"{torneo.nombre} - {torneo.zona}" if torneo.zona else torneo.nombre
            if key not in zonas_dict:
                zonas_dict[key] = {
                    'nombre': torneo.nombre,
                    'zona': torneo.zona,
                    'posiciones': []
                }
            
            posiciones = Posicion.objects.filter(torneo=torneo).select_related('equipo').order_by('posicion')[:20]  # ← LIMITAR
            for pos in posiciones:
                equipo_nombre = pos.equipo.nombre if pos.equipo else 'Sin equipo'
                zonas_dict[key]['posiciones'].append({
                    'posicion': pos.posicion,
                    'equipo': equipo_nombre,
                    'pj': pos.partidos_jugados or 0,
                    'pg': pos.partidos_ganados or 0,
                    'pe': pos.partidos_empatados or 0,
                    'pp': pos.partidos_perdidos or 0,
                    'gf': pos.goles_a_favor or 0,
                    'gc': pos.goles_en_contra or 0,
                })
        
        print(f"✅ Procesados {len(zonas_dict)} grupos de torneos")
        
        # ✅ RESPUESTA SIMPLE PARA DEBUG
        response_data = {
            'torneos': zonas_dict,
            'total_torneos': len(zonas_dict),
            'db_stats': {
                'torneos': total_torneos,
                'posiciones': total_posiciones,
                'equipos': total_equipos
            },
            'status': 'success'
        }
        
        print("🚀 Enviando respuesta JSON")
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ ERROR EN LIGAS: {e}")
        print(f"📝 Traceback: {error_detail}")
        
        logger.error(f'Error en vista ligas: {e}')
        
        return JsonResponse({
            'torneos': {},
            'error': str(e),
            'traceback': error_detail if settings.DEBUG else None,
            'status': 'error'
        }, status=500)

def ligas_api(request):
    try:
        apertura_a = list(Posicion.objects.filter(
            torneo_id=34
        ).select_related('equipo').order_by('posicion').values(
            'posicion', 'equipo__nombre', 'partidos_jugados',
            'partidos_ganados', 'partidos_empatados', 'partidos_perdidos',
            'goles_a_favor', 'goles_en_contra'
        ))
        
        
        # Procesar datos para API
        for item in apertura_a:
            item['dif'] = item['goles_a_favor'] - item['goles_en_contra']
            item['pts'] = (item['partidos_ganados'] * 3) + item['partidos_empatados']
        
        data = {
            'apertura_a': apertura_a,
            'status': 'success'
        }
        
        return JsonResponse(data)
        for zona_key, zona in zonas_dict.items():
            for pos in zona['posiciones']:
                print(f"  - {pos['equipo']}")
    except Exception as e:
        logger.error(f'Error in ligas_api: {e}')
        return JsonResponse({'error': str(e)}, status=500)

