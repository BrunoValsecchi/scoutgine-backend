from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import EstadisticasJugador, Jugador
from django.db import models
import json
import random
from django.views.decorators.csrf import csrf_exempt
import traceback

# Puedes poner esto como constantes en tu models.py o en un archivo utils.py

STATS_OFENSIVAS = [
    'goals', 'expected_goals_xg', 'shots', 'shots_on_target', 'assists',
    'expected_assists_xa', 'penalties_awarded', 'touches_in_opposition_box',
    'successful_dribbles', 'dribble_success'
]

STATS_DEFENSIVAS = [
    'saves', 'save_percentage', 'goals_conceded', 'goals_prevented', 'clean_sheets',
    'error_led_to_goal', 'high_claim', 'tackles_won', 'tackles_won_percentage',
    'interceptions', 'blocked', 'recoveries', 'possession_won_final_3rd',
    'dribbled_past', 'fouls_committed', 'yellow_cards', 'red_cards', 'aerial_duels_won',
    'aerial_duels_won_percentage', 'duels_won', 'duels_won_percentage', 'dispossessed'
]

STATS_CREACION = [
    'successful_passes', 'pass_accuracy_outfield', 'accurate_long_balls_outfield',
    'long_ball_accuracy_outfield', 'chances_created', 'successful_crosses',
    'cross_accuracy', 'touches', 'fouls_won'
]

STATS_ARQUERO = [
    'saves', 'save_percentage', 'goals_conceded', 'goals_prevented', 'clean_sheets',
    'error_led_to_goal', 'high_claim', 'pass_accuracy', 'accurate_long_balls',
    'long_ball_accuracy'
]

def grafico_jugador_view(request, jugador_id, estadistica):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    
    # Calcular estadísticas para las cards
    stat_value, promedio, percentil = calcular_estadisticas_cards(jugador, estadistica)
    
    datos_grafico = obtener_datos_estadistica(jugador, estadistica)
    
    context = {
        'jugador': jugador,
        'estadistica': estadistica,
        'datos_json': json.dumps(datos_grafico),
        'stat_value': stat_value,
        'promedio': promedio,
        'percentil': percentil,
    }
    return render(request, 'estadistica_jugador.html', context)

def calcular_estadisticas_cards(jugador, estadistica):
    """
    Calcula las estadísticas para mostrar en las cards del hero:
    - Valor actual del jugador
    - Promedio de la liga
    - Percentil del jugador
    """
    
    # Mapeo de nombres de estadística a campos del modelo
    mapeo_estadisticas = {
        'Goles': 'goals',
        'Asistencias': 'assists',
        'Tiros al arco': 'shots_on_target',
        'Tiros totales': 'shots',
        'Goles esperados (xG)': 'expected_goals_xg',
        'Penales a favor': 'penalties_awarded',
        'Ocasiones claras falladas': 'big_chances_missed',
        'Goles concedidos': 'goals_conceded',
        'Vallas invictas': 'clean_sheets',
        'xG concedido': 'expected_goals_conceded_xgc',
        'Entradas exitosas': 'tackles_won',
        'Intercepciones': 'interceptions',
        'Despejes': 'blocked',
        'Recuperaciones último tercio': 'recoveries',
        'Atajadas': 'saves',
        'Pases precisos por partido': 'successful_passes',
        'Precisión de pases': 'pass_accuracy_outfield',
        'Pases largos precisos': 'accurate_long_balls_outfield',
        'Centros precisos': 'successful_crosses',
        'Ocasiones creadas': 'chances_created',
        'Toques en área rival': 'touches_in_opposition_box',
        'Tiros de esquina': 'corners_taken',
        'Rating': 'average_rating',
        'Posesión promedio': 'possession_percentage',
        'Toques totales': 'touches',
        'Duelos ganados': 'duels_won_percentage',
        'Duelos aéreos ganados': 'aerial_duels_won_percentage',
        'Faltas por partido': 'fouls_committed',
        'Tarjetas amarillas': 'yellow_cards',
        'Tarjetas rojas': 'red_cards',
    }
    
    campo_bd = mapeo_estadisticas.get(estadistica)
    
    if not campo_bd:
        return None, None, None
    
    try:
        # 1. Obtener valor actual del jugador
        stat_value = None
        try:
            jugador_stats = EstadisticasJugador.objects.get(jugador=jugador)
            stat_value = getattr(jugador_stats, campo_bd, None)
            if stat_value is not None:
                if isinstance(stat_value, float):
                    stat_value = round(stat_value, 2)
                else:
                    stat_value = int(stat_value)
        except EstadisticasJugador.DoesNotExist:
            pass
        
        # 2. Calcular promedio de la liga
        promedio = None
        try:
            stats_liga = EstadisticasJugador.objects.exclude(**{f'{campo_bd}__isnull': True})
            valores = [getattr(stat, campo_bd) for stat in stats_liga if getattr(stat, campo_bd) is not None]
            
            if valores:
                promedio = sum(valores) / len(valores)
                if isinstance(promedio, float):
                    promedio = round(promedio, 2)
                else:
                    promedio = int(promedio)
        except Exception as e:
            pass
        
        # 3. Calcular percentil
        percentil = None
        if stat_value is not None:
            try:
                stats_liga = EstadisticasJugador.objects.exclude(**{f'{campo_bd}__isnull': True})
                valores = [getattr(stat, campo_bd) for stat in stats_liga if getattr(stat, campo_bd) is not None]
                
                if valores:
                    valores_menores = [v for v in valores if v < stat_value]
                    percentil = round((len(valores_menores) / len(valores)) * 100, 1)
            except Exception as e:
                pass
        
        return stat_value, promedio, percentil
        
    except Exception as e:
        return None, None, None

def obtener_datos_estadistica(jugador, estadistica):
    mapeo_estadisticas = {
        'Goles': 'goals',
        'Asistencias': 'assists',
        'Tiros al arco': 'shots_on_target',
        'Tiros totales': 'shots',
        'Goles esperados (xG)': 'expected_goals_xg',
        'Penales a favor': 'penalties_awarded',
        'Ocasiones claras falladas': 'big_chances_missed',
        'Goles concedidos': 'goals_conceded',
        'Vallas invictas': 'clean_sheets',
        'xG concedido': 'expected_goals_conceded_xgc',
        'Entradas exitosas': 'tackles_won',
        'Intercepciones': 'interceptions',
        'Despejes': 'blocked',
        'Recuperaciones último tercio': 'recoveries',
        'Atajadas': 'saves',
        'Pases precisos por partido': 'successful_passes',
        'Precisión de pases': 'pass_accuracy_outfield',
        'Pases largos precisos': 'accurate_long_balls_outfield',
        'Centros precisos': 'successful_crosses',
        'Ocasiones creadas': 'chances_created',
        'Toques en área rival': 'touches_in_opposition_box',
        'Tiros de esquina': 'corners_taken',
        'Rating': 'average_rating',
        'Partidos jugados': 'appearances',
        'Minutos jugados': 'minutes_played',
        'Posesión promedio': 'possession_percentage',
        'Toques totales': 'touches',
        'Duelos ganados': 'duels_won_percentage',
        'Duelos aéreos ganados': 'aerial_duels_won_percentage',
        'Faltas por partido': 'fouls_committed',
        'Tarjetas amarillas': 'yellow_cards',
        'Tarjetas rojas': 'red_cards',
    }
    campo = mapeo_estadisticas.get(estadistica)
    if not campo:
        return {'labels': [], 'data': [], 'error': f'Estadística "{estadistica}" no encontrada'}
    stats_jugador = EstadisticasJugador.objects.filter(jugador=jugador).first()
    if stats_jugador and hasattr(stats_jugador, campo):
        valor_actual = getattr(stats_jugador, campo, 0)
        labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        data = generar_evolucion_ejemplo(valor_actual or 0, len(labels))
        return {
            'labels': labels,
            'data': data,
            'estadistica': estadistica,
            'jugador': jugador.nombre,
            'valor_actual': float(valor_actual) if valor_actual else 0,
            'error': None
        }
    else:
        return generar_datos_ejemplo(estadistica, jugador)

def generar_evolucion_ejemplo(valor_base, num_puntos):
    if not valor_base:
        valor_base = 1
    datos = []
    valor_actual = valor_base
    for i in range(num_puntos):
        variacion = random.uniform(-0.2, 0.2)
        valor_actual = max(0, valor_actual * (1 + variacion))
        if valor_base >= 10:
            datos.append(round(valor_actual, 1))
        else:
            datos.append(round(valor_actual, 2))
    return datos

def generar_datos_ejemplo(estadistica, jugador):
    import random
    labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    if 'Rating' in estadistica:
        data = [round(random.uniform(6.0, 8.5), 2) for _ in range(12)]
    elif 'Goles' in estadistica:
        data = [random.randint(0, 3) for _ in range(12)]
    elif 'Pases' in estadistica or 'precisos' in estadistica.lower():
        data = [round(random.uniform(20, 80), 1) for _ in range(12)]
    elif 'Precisión' in estadistica or '%' in estadistica:
        data = [round(random.uniform(60, 95), 1) for _ in range(12)]
    elif 'Tarjetas' in estadistica:
        data = [random.randint(0, 2) for _ in range(12)]
    else:
        data = [round(random.uniform(0, 15), 1) for _ in range(12)]
    return {
        'labels': labels,
        'data': data,
        'estadistica': estadistica,
        'jugador': jugador.nombre,
        'valor_actual': data[-1] if data else 0,
        'error': None,
        'es_ejemplo': True
    }

# --- Radar AJAX endpoint ---
def ajax_radar_jugador(request):
    jugador_id = request.GET.get('jugador_id')
    grupo = request.GET.get('grupo', 'ofensivos')
    posicion = request.GET.get('posicion')

    if not jugador_id:
        return JsonResponse({'success': False, 'error': 'Faltan jugador_id'})

    try:
        jugador = Jugador.objects.get(id=jugador_id)
        jugador_stats = EstadisticasJugador.objects.get(jugador_id=jugador_id)
    except (Jugador.DoesNotExist, EstadisticasJugador.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Jugador no encontrado'})

    # ✅ USAR POSICIONES DEL CAMPO jugador.posicion
    # El campo posicion puede tener múltiples posiciones separadas por comas
    posiciones_raw = jugador.posicion or "CB"
    posiciones_jugador = [p.strip() for p in posiciones_raw.split(',') if p.strip()]
    
    # Si no se especifica posición, usar la primera del jugador
    if not posicion or posicion not in posiciones_jugador:
        posicion = posiciones_jugador[0]

    GRUPOS = {
        'ofensivos': STATS_OFENSIVAS,
        'defensivos': STATS_DEFENSIVAS,
        'creacion': STATS_CREACION,
        'arquero': STATS_ARQUERO,
    }
    campos = GRUPOS.get(grupo, STATS_OFENSIVAS)
    labels_nombres = [campo.replace('_', ' ').capitalize() for campo in campos]

    percentiles_jugador = []

    def calcular_percentil(valores, valor_jugador):
        if not valores or valor_jugador is None:
            return 50
        valores_menores = sum(1 for v in valores if v < valor_jugador)
        return round(100 * (valores_menores / len(valores)))

    for campo in campos:
        # Solo jugadores con esa posición (en cualquier parte de la cadena)
        jugadores_misma_pos = Jugador.objects.filter(posicion__icontains=posicion)
        stats_misma_pos = EstadisticasJugador.objects.filter(jugador__in=jugadores_misma_pos).exclude(**{f"{campo}__isnull": True})
        valores = list(stats_misma_pos.values_list(campo, flat=True))
        valor_jugador = getattr(jugador_stats, campo, None)
        percentil = calcular_percentil(valores, valor_jugador)
        percentiles_jugador.append(percentil)

    percentiles_promedio = [50 for _ in campos]

    return JsonResponse({
        'success': True,
        'labels': labels_nombres,
        'max': 100,
        'jugador': percentiles_jugador,
        'promedio': percentiles_promedio,
        'posicion': posicion,
        'posiciones_jugador': posiciones_jugador,  # ✅ POSICIONES DE LA TABLA JUGADOR
    })

# --- Ranking, Evolución, Percentil AJAX endpoints ---
def ajax_ranking_jugadores(request):
    stat = request.GET.get('stat')
    if not stat:
        return JsonResponse({'success': False, 'error': 'Falta estadística'})
    jugadores = EstadisticasJugador.objects.exclude(**{f"{stat}__isnull": True}).select_related('jugador')
    top = sorted(jugadores, key=lambda j: getattr(j, stat, 0), reverse=True)[:10]
    data = [{
        'nombre': j.jugador.nombre,
        'equipo': j.jugador.equipo.nombre if j.jugador.equipo else '',
        'valor': getattr(j, stat, 0)
    } for j in top]
    return JsonResponse({'success': True, 'ranking': data})

def ajax_evolucion_jugador(request):
    jugador_id = request.GET.get('jugador_id')
    stat = request.GET.get('stat')
    if not jugador_id or not stat:
        return JsonResponse({'success': False, 'error': 'Faltan datos'})
    try:
        est = EstadisticasJugador.objects.get(jugador_id=jugador_id)
        base = getattr(est, stat, 0)
        evolucion = [round(base * (1 + random.uniform(-0.15, 0.15)), 2) for _ in range(6)]
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]
        return JsonResponse({'success': True, 'labels': meses, 'data': evolucion})
    except EstadisticasJugador.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Jugador no encontrado'})

def ajax_percentil_jugador(request):
    jugador_id = request.GET.get('jugador_id')
    stat = request.GET.get('stat')
    if not jugador_id or not stat:
        return JsonResponse({'success': False, 'error': 'Faltan datos'})
    jugadores = EstadisticasJugador.objects.exclude(**{f"{stat}__isnull": True})
    valores = sorted([getattr(j, stat, 0) for j in jugadores])
    try:
        est = EstadisticasJugador.objects.get(jugador_id=jugador_id)
        valor = getattr(est, stat, 0)
    except EstadisticasJugador.DoesNotExist:
        valor = 0
    percentiles = [25, 50, 75, 90]
    valores_percentiles = [valores[int(len(valores)*p/100)] if valores else 0 for p in percentiles]
    return JsonResponse({
        'success': True,
        'percentiles': percentiles,
        'valores_percentiles': valores_percentiles,
        'valor_jugador': valor
    })

def calcular_percentil(valores, valor):
    """Calcula el percentil de un valor en una lista de valores."""
    if not valores or valor is None:
        return 0
    valores = sorted(valores)
    below = sum(1 for v in valores if v < valor)
    percentil = below / len(valores) * 100
    return int(round(percentil))

def ajax_grafico_dispersion_jugador(request):
    """
    Devuelve datos para scatter plot de jugadores según dos estadísticas, filtrando por posición.
    """
    jugador_id = request.GET.get('jugador_id')
    stat_x = request.GET.get('stat_x', 'pass_accuracy_outfield')
    stat_y = request.GET.get('stat_y', 'saves')
    posicion = request.GET.get('posicion', 'CB')

    if not jugador_id:
        return JsonResponse({'success': False, 'error': 'Falta jugador_id'})

    try:
        jugador = Jugador.objects.get(id=jugador_id)
        
        # ✅ OBTENER POSICIONES DE LA TABLA JUGADOR
        posiciones_raw = jugador.posicion or "CB"
        posiciones_jugador = [p.strip() for p in posiciones_raw.split(',') if p.strip()]
        
        # Si no se especifica posición, usar la primera del jugador
        if not posicion or posicion not in posiciones_jugador:
            posicion = posiciones_jugador[0]
        
        # ✅ FUNCIÓN PARA FILTRAR JUGADORES POR POSICIÓN DE LA TABLA JUGADOR
        def jugadores_con_posicion(pos):
            return Jugador.objects.filter(
                models.Q(posicion__icontains=pos) |
                models.Q(posicion__startswith=pos) |
                models.Q(posicion__endswith=pos) |
                models.Q(posicion__exact=pos)
            )
        
        # Obtener jugadores con la misma posición
        jugadores_posicion = jugadores_con_posicion(posicion)
        jugadores_ids = list(jugadores_posicion.values_list('id', flat=True))
        
        if not jugadores_ids:
            return JsonResponse({'success': False, 'error': f'No hay jugadores en posición {posicion}'})
        
        # Mapear estadísticas a campos de BD
        stat_x_bd = obtener_campo_estadistica(stat_x) or stat_x
        stat_y_bd = obtener_campo_estadistica(stat_y) or stat_y
        
        # ✅ FILTRAR ESTADÍSTICAS POR LOS IDs DE JUGADORES CON ESA POSICIÓN
        stats_qs = EstadisticasJugador.objects.filter(
            jugador_id__in=jugadores_ids
        ).exclude(**{f"{stat_x_bd}__isnull": True}).exclude(**{f"{stat_y_bd}__isnull": True}).select_related('jugador')
        
        # Si no hay datos después del filtro, usar todos los registros (incluyendo 0s)
        if stats_qs.count() == 0:
            print("⚠️ No hay datos después de filtrar nulls, usando todos los registros...")
            stats_qs = EstadisticasJugador.objects.filter(
                jugador_id__in=jugadores_ids
            ).select_related('jugador')
        
        # Procesar datos para el gráfico
        data = []
        jugador_actual = None
        
        for stat in stats_qs:
            x_val = getattr(stat, stat_x_bd, 0) or 0
            y_val = getattr(stat, stat_y_bd, 0) or 0
            
            punto = {
                'nombre': stat.jugador.nombre,
                'x': float(x_val),
                'y': float(y_val),
                'jugador_id': stat.jugador.id
            }
            
            data.append(punto)
            
            if stat.jugador.id == int(jugador_id):
                jugador_actual = punto
        
        # Obtener opciones para el eje Y
        campos_numericos = obtener_campos_numericos_estadisticas()
        opciones_y = [{'value': campo, 'label': campo.replace('_', ' ').title()} for campo in campos_numericos]
        
        return JsonResponse({
            'success': True,
            'data': data,
            'stat_x': stat_x_bd,
            'stat_y': stat_y_bd,
            'campos_y': campos_numericos,
            'opciones_y': opciones_y,
            'jugador_actual': jugador_actual,
            'posicion': posicion,
            'posiciones_jugador': posiciones_jugador,  # ✅ POSICIONES DE LA TABLA JUGADOR
            'total_jugadores': len(data),
            'debug_info': {
                'stat_x_original': stat_x,
                'stat_x_traducido': stat_x_bd,
                'stat_y': stat_y,
                'stat_y_traducido': stat_y_bd,
                'posicion': posicion,
                'jugadores_en_posicion': len(jugadores_ids),
                'stats_con_datos': stats_qs.count(),
                'puntos_validos': len(data)
            }
        })
        
    except Jugador.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Jugador no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error: {str(e)}'})

def ajax_boxplot_jugador(request):
    """
    Devuelve datos para boxplot de una estadística específica de jugadores.
    """
    jugador_id = request.GET.get('jugador_id')
    estadistica = request.GET.get('estadistica')
    posicion = request.GET.get('posicion')

    if not jugador_id or not estadistica:
        return JsonResponse({'success': False, 'error': 'Faltan parámetros'})

    try:
        jugador = Jugador.objects.get(id=jugador_id)
        
        # ✅ OBTENER POSICIONES DE LA TABLA JUGADOR
        posiciones_raw = jugador.posicion or "CB"
        posiciones_jugador = [p.strip() for p in posiciones_raw.split(',') if p.strip()]
        
        # Si no se especifica posición, usar la primera del jugador
        if not posicion or posicion not in posiciones_jugador:
            posicion = posiciones_jugador[0]
        
        # ✅ FUNCIÓN PARA FILTRAR JUGADORES POR POSICIÓN DE LA TABLA JUGADOR
        def jugadores_con_posicion(pos):
            return Jugador.objects.filter(
                models.Q(posicion__icontains=pos) |  # Contiene la posición
                models.Q(posicion__startswith=pos) |  # Empieza con la posición
                models.Q(posicion__endswith=pos) |    # Termina con la posición
                models.Q(posicion__exact=pos)         # Es exactamente la posición
            )
        
        # Obtener jugadores con la misma posición
        jugadores_posicion = jugadores_con_posicion(posicion)
        jugadores_ids = list(jugadores_posicion.values_list('id', flat=True))
        
        if not jugadores_ids:
            return JsonResponse({'success': False, 'error': f'No hay jugadores en posición {posicion}'})
        
        # Mapear nombre de estadística a campo de BD
        campo_bd = obtener_campo_estadistica(estadistica)
        if not campo_bd:
            return JsonResponse({'success': False, 'error': 'Estadística no válida'})
        
        # ✅ FILTRAR ESTADÍSTICAS POR LOS IDs DE JUGADORES CON ESA POSICIÓN
        stats_qs = EstadisticasJugador.objects.filter(
            jugador_id__in=jugadores_ids  # ← USAR jugador_id__in
        ).exclude(**{f"{campo_bd}__isnull": True})
        
        # Obtener valores para el boxplot
        valores = list(stats_qs.values_list(campo_bd, flat=True))
        
        if len(valores) < 5:
            return JsonResponse({'success': False, 'error': f'No hay suficientes datos para {posicion}'})
        
        # Calcular estadísticas del boxplot
        valores.sort()
        n = len(valores)
        q1 = valores[n // 4]
        median = valores[n // 2]
        q3 = valores[3 * n // 4]
        iqr = q3 - q1
        lower_whisker = max(min(valores), q1 - 1.5 * iqr)
        upper_whisker = min(max(valores), q3 + 1.5 * iqr)
        
        # Obtener valor del jugador actual
        try:
            jugador_stat = EstadisticasJugador.objects.get(jugador_id=jugador_id)
            valor_jugador = getattr(jugador_stat, campo_bd, None)
        except EstadisticasJugador.DoesNotExist:
            valor_jugador = None
        
        return JsonResponse({
            'success': True,
            'stat': estadistica,
            'posicion': posicion,
            'posiciones_jugador': posiciones_jugador,  # ✅ POSICIONES DE LA TABLA JUGADOR
            'box': [lower_whisker, q1, median, q3, upper_whisker],
            'valor_jugador': valor_jugador,
            'total_jugadores': len(valores),
            'jugador_nombre': jugador.nombre
        })
        
    except Jugador.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Jugador no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error: {str(e)}'})

@csrf_exempt
def ajax_jugador_estadistica(request, jugador_id, estadistica):
    try:
        jugador = get_object_or_404(Jugador, id=jugador_id)
        equipo = jugador.equipo if hasattr(jugador, 'equipo') else None

        stat_value, promedio, percentil = calcular_estadisticas_cards(jugador, estadistica)
        datos_grafico = obtener_datos_estadistica(jugador, estadistica)

        return JsonResponse({
            'jugador': {
                'id': jugador.id,
                'nombre': jugador.nombre,
                'dorsal': getattr(jugador, 'dorsal', None),
                'foto': getattr(jugador, 'foto', None),
                'posicion': getattr(jugador, 'posicion', None),
                'posicion_secundaria': getattr(jugador, 'posicion_secundaria', None),
            },
            'equipo': {
                'id': equipo.id if equipo else None,
                'nombre': equipo.nombre if equipo else None,
                'logo': equipo.logo if equipo else None
            } if equipo else None,
            'estadistica': estadistica,
            'estadisticas_hero': {
                'valor_actual': stat_value,
                'promedio_liga': promedio,
                'percentil': percentil
            },
            'datos_grafico': datos_grafico
        })
    except Exception as e:
        return JsonResponse({'error': f'{str(e)}', 'traceback': traceback.format_exc()}, status=500)

def api_jugador_posiciones(request, jugador_id):
    """Devuelve las posiciones de un jugador"""
    try:
        jugador = Jugador.objects.get(id=jugador_id)
        posiciones = [p.strip() for p in jugador.posicion.split(',')]
        return JsonResponse({'success': True, 'posiciones': posiciones})
    except Jugador.DoesNotExist:
        return JsonResponse({'success': False, 'posiciones': []})

def jugadores_con_posicion(posicion):
    """
    Devuelve un queryset de jugadores que tienen la posición dada,
    considerando variantes como 'RB', 'RB,CB', 'CB,RB', 'RB / CB', etc.
    """
    from django.db.models import Q
    # Quitar espacios y buscar coincidencias
    return Jugador.objects.filter(
        Q(posicion__iexact=posicion) |
        Q(posicion__istartswith=posicion + ',') |
        Q(posicion__iendswith=',' + posicion) |
        Q(posicion__icontains=',' + posicion + ',') |
        Q(posicion__icontains=posicion + ' /') |
        Q(posicion__icontains='/ ' + posicion) |
        Q(posicion__icontains='/' + posicion + '/') |
        Q(posicion__icontains=posicion)
    )

def obtener_campo_estadistica(nombre_estadistica):
    """Mapea nombres de estadísticas a campos de la base de datos"""
    mapeo = {
        'Precisión de pases': 'pass_accuracy_outfield',
        'pass_accuracy_outfield': 'pass_accuracy_outfield',
        'Goles': 'goals',
        'goals': 'goals',
        'Asistencias': 'assists',
        'assists': 'assists',
        'Intercepciones': 'interceptions',
        'interceptions': 'interceptions',
        'Entradas exitosos': 'tackles_won',
        'tackles_won': 'tackles_won',
        'Atajadas': 'saves',
        'saves': 'saves',
        'Tiros al arco': 'shots_on_target',
        'shots_on_target': 'shots_on_target',
        'Rating': 'average_rating',
        'average_rating': 'average_rating',
        'Partidos jugados': 'appearances',
        'appearances': 'appearances',
        'Minutos jugados': 'minutes_played',
        'minutes_played': 'minutes_played',
        'expected_goals_xg': 'expected_goals_xg',
        'expected_assists_xa': 'expected_assists_xa',
        'accurate_long_balls': 'accurate_long_balls',
    }
    return mapeo.get(nombre_estadistica, None)

def obtener_campos_numericos_estadisticas():
    """Devuelve una lista de campos numéricos disponibles"""
    from django.apps import apps
    
    EstadisticasJugador = apps.get_model('myapp', 'EstadisticasJugador')
    campos_numericos = []
    
    for field in EstadisticasJugador._meta.get_fields():
        if field.get_internal_type() in ['FloatField', 'IntegerField', 'DecimalField']:
            campos_numericos.append(field.name)
    
    return campos_numericos

