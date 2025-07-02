from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Posicion, Equipo, EstadisticasEquipo, Jugador
import json
import random
# import numpy as np
from .estadistica_jugador import grafico_jugador_view
from .comparacion import GRUPOS_STATS, GRUPOS_STATS_EQUIPOS, GRUPOS_STATS_JUGADORES# ============================================================================
# VISTAS PRINCIPALES
# ============================================================================

def home(request):
    return render(request, "index.html")

def grafico(request):
    return render(request, "grafico.html")

def menu(request):
    return render(request, "menu.html")

def equipo(request):
    """Página principal de equipos"""
    try:
        from .equipo import equipo as equipo_func
        return equipo_func(request)
    except Exception as e:
        return render(request, "equipo.html", {'error': str(e)})

def equipo_detalle(request, equipo_id):
    """Vista para mostrar un equipo individual"""
    try:
        equipo = get_object_or_404(Equipo, id=equipo_id)
        context = {
            'equipo': equipo,
            'equipo_id': equipo_id,
            'page_title': f'{equipo.nombre} | ScoutGine'
        }
        return render(request, 'equipo_detalle.html', context)
    except Exception as e:
        print(f"❌ Error en equipo_detalle: {e}")
        context = {
            'error': f'Error cargando equipo: {str(e)}',
            'equipo_id': equipo_id,
            'page_title': 'Error | ScoutGine'
        }
        return render(request, 'equipo_detalle.html', context)

def ligas(request):
    from .ligas import ligas as ligas_func
    return ligas_func(request)


def comparacion(request):
    # ✅ Usar la función de comparacion.py en lugar de duplicar lógica
    from .comparacion import comparacion as comparacion_func
    return comparacion_func(request)


def stats_jugadores(request):
    """Vista para estadísticas de jugadores - delegada a helper"""
    from .api_helpers import stats_jugadores_wrapper
    return stats_jugadores_wrapper(request)

def jugadores(request):
    from .jugadores import jugadores as jugadores_func
    return jugadores_func(request)

def jugador_detalle(request, jugador_id):
    from .detalle_jugador import jugador_detalle as jugador_detalle_func
    return jugador_detalle_func(request, jugador_id)

def posiciones(request):
    from .posiciones import posiciones as posiciones_func
    return posiciones_func(request)
def grafico_jugador(request, jugador_id, estadistica):
    # Tu lógica aquí
    pass
def buscar(request):
    from .buscar import buscar as buscar_func
    return buscar_func(request)

def index(request):
    from .index import index as index_func
    return index_func(request)
def jugador_detalle(request, jugador_id):
    from .detalle_jugador import jugador_detalle as jugador_detalle_func
    return jugador_detalle_func(request, jugador_id)
# ============================================================================
# API ENDPOINTS
# ============================================================================

def posiciones_api(request):
    """API para obtener datos de posiciones"""
    torneos = {
        'apertura_a': Posicion.objects.filter(torneo_id=34),
        'apertura_b': Posicion.objects.filter(torneo_id=49),
        'clausura_a': Posicion.objects.filter(torneo_id=4),
        'clausura_b': Posicion.objects.filter(torneo_id=19)
    }
    
    data = {key: list(torneo.values()) for key, torneo in torneos.items()}
    return JsonResponse(data)

# ============================================================================
# GRÁFICOS DE ESTADÍSTICAS
# ============================================================================

def grafico_equipo(request, equipo_id, stat_name=None, estadistica=None):
    """Vista para mostrar gráfico de estadística de equipo"""
    try:
        # Usar el parámetro correcto
        stat_to_use = stat_name or estadistica
        
        print(f"🎯 grafico_equipo llamado con equipo_id={equipo_id}, stat={stat_to_use}")
        
        if not stat_to_use:
            return JsonResponse({
                'error': 'Estadística no especificada',
                'status': 'error'
            }, status=400)
        
        # Verificar que el equipo existe
        try:
            equipo = Equipo.objects.get(id=equipo_id)
        except Equipo.DoesNotExist:
            return JsonResponse({
                'error': f'Equipo con ID {equipo_id} no encontrado',
                'status': 'error'
            }, status=404)
        
        # ✅ USAR EL TEMPLATE CORRECTO: estadistica_detalle.html
        return render(request, 'estadistica_detalle.html', {
            'equipo_id': equipo_id,
            'equipo_nombre': equipo.nombre,
            'stat_name': stat_to_use,
            'page_title': f'{stat_to_use} - {equipo.nombre}'
        })
        
    except Exception as e:
        print(f"❌ Error general en grafico_equipo: {e}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'status': 'error'
        }, status=500)
def generar_graficos_completos(equipo, estadistica, valor_equipo, equipos_nombres, equipos_valores, estadisticas_obj):
    """Genera todos los gráficos para la estadística"""
    from pyecharts.charts import Bar, Line, Gauge
    from pyecharts import options as opts
    
    # Determinar color según tipo
    if 'goles' in estadistica.lower() or 'tiros' in estadistica.lower():
        color = "#ff6b6b"
    elif 'defens' in estadistica.lower() or 'vallas' in estadistica.lower():
        color = "#4ecdc4"
    elif 'pases' in estadistica.lower() or 'posesión' in estadistica.lower():
        color = "#45b7d1"
    else:
        color = "#67aaff"
    
    graficos = {}
    
    # 1. RANKING TOP 10
    try:
        top_equipos = sorted(zip(equipos_nombres, equipos_valores), key=lambda x: x[1], reverse=True)[:10]
        nombres_top = [nombre for nombre, _ in top_equipos]
        valores_top = [valor for _, valor in top_equipos]
        
        ranking_chart = (
            Bar(init_opts=opts.InitOpts(width="100%", height="350px", theme="dark"))
            .add_xaxis(nombres_top)
            .add_yaxis("", valores_top, color=color)
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"🏆 Top 10 - {estadistica}",
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(color="#e3e6ee", font_size=14)
                ),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45, color="#a6b6d9")),
                yaxis_opts=opts.AxisOpts(name=estadistica, name_textstyle_opts=opts.TextStyleOpts(color="#a6b6d9"))
            )
        )
        graficos['ranking_chart'] = mark_safe(ranking_chart.render_embed())
    except:
        pass
    
    # 2. EVOLUCIÓN TEMPORAL
    try:
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]
        evolucion = []
        base = valor_equipo
        
        for _ in range(6):
            variacion = random.uniform(-0.1, 0.1)
            nuevo_valor = base * (1 + variacion)
            evolucion.append(round(nuevo_valor, 2))
            base = nuevo_valor
        
        promedio_liga = sum(equipos_valores) / len(equipos_valores)
        
        evolucion_chart = (
            Line(init_opts=opts.InitOpts(width="100%", height="350px", theme="dark"))
            .add_xaxis(meses)
            .add_yaxis(f"{equipo.nombre}", evolucion, color=color, is_smooth=True)
            .add_yaxis("Promedio Liga", [promedio_liga] * 6, color="#666666", is_smooth=True)
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"📈 Evolución - {estadistica}",
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(color="#e3e6ee", font_size=14)
                )
            )
        )
        graficos['evolucion_chart'] = mark_safe(evolucion_chart.render_embed())
    except:
        pass
    
    # 3. PERCENTILES
    try:
        # Calcular percentiles con Python nativo
        def calcular_percentil(valores_ordenados, percentil):
            """Calcula percentil usando Python nativo"""
            if not valores_ordenados:
                return 0
            n = len(valores_ordenados)
            k = (percentil / 100) * (n - 1)
            f = int(k)
            c = k - f
            if f == n - 1:
                return valores_ordenados[f]
            return valores_ordenados[f] * (1 - c) + valores_ordenados[f + 1] * c
        
        # Asegurar que equipos_valores está ordenado
        equipos_valores_ordenados = sorted(equipos_valores)
        
        # Calcular quartiles
        q1 = calcular_percentil(equipos_valores_ordenados, 25)
        q2 = calcular_percentil(equipos_valores_ordenados, 50)
        q3 = calcular_percentil(equipos_valores_ordenados, 75)
        
        percentil_chart = (
            Bar(init_opts=opts.InitOpts(width="100%", height="350px", theme="dark"))
            .add_xaxis(["Q1", "Mediana", "Q3"])
            .add_yaxis("Liga", [q1, q2, q3], color="#95a5a6")
            .add_yaxis(equipo.nombre, [valor_equipo] * 3, color=color)
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"🎯 Distribución - {estadistica}",
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(color="#e3e6ee", font_size=14)
                )
            )
        )
        graficos['percentil_chart'] = mark_safe(percentil_chart.render_embed())
    except:
        pass
    
    # 4. ANÁLISIS CONTEXTUAL
    try:
        categorias = ["Últimos 5", "Casa", "Visitante", "1ª Mitad", "2ª Mitad"]
        datos_simulados = [valor_equipo * (1 + random.uniform(-0.2, 0.2)) for _ in categorias]
        promedio_liga = sum(equipos_valores) / len(equipos_valores)
        
        barras_chart = (
            Bar(init_opts=opts.InitOpts(width="100%", height="350px", theme="dark"))
            .add_xaxis(categorias)
            .add_yaxis(f"{equipo.nombre}", datos_simulados, color=color)
            .add_yaxis("Promedio Liga", [promedio_liga] * len(categorias), color="#666666")
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"📊 Análisis Contextual - {estadistica}",
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(color="#e3e6ee", font_size=14)
                ),
                legend_opts=opts.LegendOpts(pos_top="10%")
            )
        )
        graficos['barras_chart'] = mark_safe(barras_chart.render_embed())
    except:
        pass
    
    # 5. MEDIDOR DE RENDIMIENTO
    try:
        valores_ordenados = sorted(equipos_valores, reverse=True)
        try:
            posicion = valores_ordenados.index(valor_equipo)
            percentil = ((len(valores_ordenados) - posicion) / len(valores_ordenados)) * 100
        except ValueError:
            percentil = 50
        
        gauge_chart = (
            Gauge(init_opts=opts.InitOpts(width="100%", height="350px", theme="dark"))
            .add(
                "",
                [("Rendimiento", round(percentil, 1))],
                radius="70%",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(
                        color=[(0.3, "#ff6b6b"), (0.7, "#ffd700"), (1, "#4ecdc4")], width=20
                    )
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"🎯 Percentil - {estadistica}",
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(color="#e3e6ee", font_size=14)
                )
            )
        )
        graficos['gauge_chart'] = mark_safe(gauge_chart.render_embed())
    except:
        pass
    
    # 6. COMPARACIÓN CON RIVALES
    try:
        # Equipos similares (±30% del valor)
        equipos_similares = []
        for nombre, valor in zip(equipos_nombres, equipos_valores):
            if abs(valor - valor_equipo) <= valor_equipo * 0.3:
                equipos_similares.append((nombre, valor))
        
        equipos_similares = equipos_similares[:5]
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]
        
        comparacion_chart = Line(init_opts=opts.InitOpts(width="100%", height="350px", theme="dark"))
        comparacion_chart.add_xaxis(meses)
        
        # Equipo principal
        tendencia = [valor_equipo * (1 + random.uniform(-0.1, 0.1)) for _ in range(6)]
        comparacion_chart.add_yaxis(f"{equipo.nombre} ⭐", tendencia, color=color, is_smooth=True, symbol_size=8)
        
        # Rivales
        colores = ["#ff6b6b", "#4ecdc4", "#ffd700", "#95a5a6"]
        for i, (nombre_rival, valor_rival) in enumerate(equipos_similares[:4]):
            if nombre_rival != (equipo.nombre_corto or equipo.nombre[:15]):
                tendencia_rival = [valor_rival * (1 + random.uniform(-0.1, 0.1)) for _ in range(6)]
                comparacion_chart.add_yaxis(
                    nombre_rival, tendencia_rival, 
                    color=colores[i % len(colores)], is_smooth=True, symbol_size=6
                )
        
        comparacion_chart.set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"📈 vs Rivales Directos",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(color="#e3e6ee", font_size=14)
            ),
            legend_opts=opts.LegendOpts(pos_top="12%")
        )
        graficos['comparacion_chart'] = mark_safe(comparacion_chart.render_embed())
    except:
        pass
    
    return graficos

# ============================================================================
# AJAX ENDPOINTS
# ============================================================================

def ajax_grafico_dispersion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            equipo_id = data.get('equipo_id')
            stat_principal = data.get('stat_principal')
            stat_comparacion = data.get('stat_comparacion', 'Rating')
            
            print(f"🔍 AJAX Dispersión - Principal: {stat_principal}, Comparación: {stat_comparacion}")
            
            # MAPEO COMPLETO DE ESTADÍSTICAS
            STAT_MAPPING = {
                'Rating': 'fotmob_rating',
                'Goles por partido': 'goals_per_match',
                'Goles concedidos por partido': 'goals_conceded_per_match',
                'Posesión promedio': 'average_possession',
                'Vallas invictas': 'clean_sheets',
                'Goles esperados (xG)': 'expected_goals_xg',
                'Tiros al arco por partido': 'shots_on_target_per_match',
                'Ocasiones claras': 'big_chances',
                'Ocasiones claras falladas': 'big_chances_missed',
                'xG concedido': 'xg_concedido',
                'Intercepciones por partido': 'interceptions_per_match',
                'Entradas exitosas por partido': 'successful_tackles_per_match',
                'Despejes por partido': 'clearances_per_match',
                'Atajadas por partido': 'saves_per_match',
                'Faltas por partido': 'fouls_per_match',
                'Tarjetas amarillas': 'yellow_cards',
                'Tarjetas rojas': 'red_cards',
                'Pases precisos por partido': 'accurate_passes_per_match',
                'Pases largos precisos por partido': 'accurate_long_balls_per_match',
                'Centros precisos por partido': 'accurate_crosses_per_match',
                'Toques en el área rival': 'touches_in_opposition_box',
                'Tiros de esquina': 'corners',
                'Recuperaciones en el último tercio': 'possession_won_final_3rd_per_match',
                'Penales a favor': 'penalties_awarded',
            }
            
            field_principal = STAT_MAPPING.get(stat_principal)
            field_comparacion = STAT_MAPPING.get(stat_comparacion)
            
            print(f"🔍 Fields - Principal: {field_principal}, Comparación: {field_comparacion}")
            
            if not field_principal:
                return JsonResponse({
                    'success': False, 
                    'error': f'Estadística principal no válida: {stat_principal}'
                })
                
            if not field_comparacion:
                return JsonResponse({
                    'success': False, 
                    'error': f'Estadística de comparación no válida: {stat_comparacion}'
                })
            
            # Obtener datos de todos los equipos
            equipos_data = []
            todos_equipos = EstadisticasEquipo.objects.select_related('equipo').all()
            
            print(f"🔍 Total equipos en BD: {todos_equipos.count()}")
            
            for eq_stat in todos_equipos:
                val_principal = getattr(eq_stat, field_principal, None)
                val_comparacion = getattr(eq_stat, field_comparacion, None)
                
                if val_principal is not None and val_comparacion is not None:
                    try:
                        equipos_data.append({
                            'nombre': eq_stat.equipo.nombre_corto or eq_stat.equipo.nombre[:15],
                            'stat_principal': float(val_principal),
                            'stat_comparacion': float(val_comparacion),
                            'es_actual': eq_stat.equipo.id == int(equipo_id)
                        })
                    except (ValueError, TypeError):
                        continue
            
            print(f"🔍 Equipos con datos válidos: {len(equipos_data)}")
            
            if not equipos_data:
                return JsonResponse({
                    'success': False, 
                    'error': f'No se encontraron datos para {stat_principal} vs {stat_comparacion}'
                })
            
            # Calcular promedios
            promedio_principal = sum(eq['stat_principal'] for eq in equipos_data) / len(equipos_data)
            promedio_comparacion = sum(eq['stat_comparacion'] for eq in equipos_data) / len(equipos_data)
            
            print(f"✅ Dispersión exitosa: {len(equipos_data)} equipos")
            
            return JsonResponse({
                'success': True,
                'chart_data': {
                    'equipos': equipos_data,
                    'promedio_principal': round(promedio_principal, 2),
                    'promedio_comparacion': round(promedio_comparacion, 2)
                }
            })
            
        except Exception as e:
            print(f"❌ Error AJAX dispersión: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@require_POST  
def ajax_analisis_correlacion(request):
    """Vista AJAX para análisis de correlación"""
    try:
        # Datos simulados
        correlaciones = [
            {'stat': 'Victorias', 'correlacion': 0.75},
            {'stat': 'Goles Favor', 'correlacion': 0.68},
            {'stat': 'Posesión', 'correlacion': 0.45},
            {'stat': 'Goles Contra', 'correlacion': -0.62},
            {'stat': 'Tarjetas', 'correlacion': -0.23}
        ]
        
        return JsonResponse({'success': True, 'correlaciones': correlaciones})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_stats_data(stat_name, equipo_id=None):
    STAT_MAPPING = {
        'Rating': 'fotmob_rating',
        'Goles por partido': 'goals_per_match',
        'Goles concedidos por partido': 'goals_conceded_per_match',
        'Posesión promedio': 'average_possession',
        'Vallas invictas': 'clean_sheets',
        'Goles esperados (xG)': 'expected_goals_xg',
        'Tiros al arco por partido': 'shots_on_target_per_match',
        'Ocasiones claras': 'big_chances',
        'Ocasiones claras falladas': 'big_chances_missed',
        'xG concedido': 'xg_concedido',
        'Intercepciones por partido': 'interceptions_per_match',
        'Entradas exitosas por partido': 'successful_tackles_per_match',
        'Despejes por partido': 'clearances_per_match',
        'Atajadas por partido': 'saves_per_match',
        'Faltas por partido': 'fouls_per_match',
        'Tarjetas amarillas': 'yellow_cards',
        'Tarjetas rojas': 'red_cards',
        'Pases precisos por partido': 'accurate_passes_per_match',
        'Pases largos precisos por partido': 'accurate_long_balls_per_match',
        'Centros precisos por partido': 'accurate_crosses_per_match',
        'Toques en el área rival': 'touches_in_opposition_box',
        'Tiros de esquina': 'corners',
        'Recuperaciones en el último tercio': 'possession_won_final_3rd_per_match',
        'Penales a favor': 'penalties_awarded',
    }
    field_name = STAT_MAPPING.get(stat_name)
    if not field_name:
        return [], None

    equipos_stats = EstadisticasEquipo.objects.select_related('equipo').exclude(**{f"{field_name}__isnull": True})
    equipos_valores = []
    valor_equipo = None
    for eq_stat in equipos_stats:
        valor = getattr(eq_stat, field_name, None)
        if valor is not None:
            equipos_valores.append(float(valor))
            if equipo_id and str(eq_stat.equipo.id) == str(equipo_id):
                valor_equipo = float(valor)
    return equipos_valores, valor_equipo
def ajax_boxplot_estadistica(request):
    stat_id = request.GET.get('stat_id')
    equipo_id = request.GET.get('equipo_id')
    equipos_valores, valor_equipo = get_stats_data(stat_id, equipo_id)
    
    if not equipos_valores:
        return JsonResponse({'success': False, 'error': 'Sin datos'})
    
    # Calcular percentiles con Python nativo
    def calcular_percentil(valores_ordenados, percentil):
        """Calcula percentil usando Python nativo"""
        if not valores_ordenados:
            return 0
        n = len(valores_ordenados)
        k = (percentil / 100) * (n - 1)
        f = int(k)
        c = k - f
        if f == n - 1:
            return valores_ordenados[f]
        return valores_ordenados[f] * (1 - c) + valores_ordenados[f + 1] * c
    
    # Asegurar que equipos_valores está ordenado
    equipos_valores_ordenados = sorted(equipos_valores)
    
    # Calcular quartiles
    q1 = calcular_percentil(equipos_valores_ordenados, 25)
    q2 = calcular_percentil(equipos_valores_ordenados, 50)
    q3 = calcular_percentil(equipos_valores_ordenados, 75)
    
    # Boxplot: min, Q1, median, Q3, max
    box = [min(equipos_valores), q1, q2, q3, max(equipos_valores)]
    
    return JsonResponse({
        'success': True,
        'stat': stat_id,
        'box': box,
        'valores': equipos_valores,
        'valor_equipo': valor_equipo,
    })

def estadistica_jugador(request, jugador_id, estadistica):
    try:
        jugador = get_object_or_404(Jugador, id=jugador_id)
        
        # Obtener el valor actual del jugador para esta estadística
        stat_value = None
        if hasattr(jugador, estadistica):
            stat_value = getattr(jugador, estadistica)
            # Formatear el valor si es necesario
            if stat_value is not None:
                if isinstance(stat_value, float):
                    stat_value = round(stat_value, 2)
        
        # Calcular promedio de la liga para esta estadística
        promedio = None
        if hasattr(Jugador, estadistica):
            valores = Jugador.objects.exclude(**{f'{estadistica}__isnull': True}).values_list(estadistica, flat=True)
            if valores:
                promedio = round(sum(valores) / len(valores), 2)
        
        # Calcular percentil
        percentil = None
        if stat_value is not None:
            valores = list(Jugador.objects.exclude(**{f'{estadistica}__isnull': True}).values_list(estadistica, flat=True))
            if valores:
                valores_menores = [v for v in valores if v < stat_value]
                percentil = round((len(valores_menores) / len(valores)) * 100, 1)
        
        # Obtener posiciones para selectores
        posiciones = Jugador.objects.values_list('posicion', flat=True).distinct()
        posiciones = [p for p in posiciones if p]
        
        context = {
            'jugador': jugador,
            'estadistica': estadistica,
            'stat_value': stat_value,
            'promedio': promedio,
            'percentil': percentil,
            'posiciones': posiciones,
        }
        
        return render(request, 'estadistica_jugador.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar estadística: {str(e)}')
        return redirect('jugador_detalle', jugador_id=jugador_id)
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .recomendacion import (
    recomendar_jugadores_por_perfil, 
    obtener_perfiles_disponibles,
    PERFILES_JUGADORES
)
from .models import Equipo

def recomendacion(request):
    """Página principal de recomendación de jugadores"""
    perfiles = obtener_perfiles_disponibles()
    
    context = {
        'perfiles': perfiles,
        'title': 'Recomendación de Jugadores por Perfil',
        'equipos': Equipo.objects.all().order_by('nombre')
    }
    
    return render(request, 'recomendacion.html', context)


def ajax_recomendar_jugadores(request):
    """AJAX para obtener recomendaciones"""
    perfil = request.GET.get('perfil')
    limite = int(request.GET.get('limite', 10))
    equipo_excluir = request.GET.get('equipo_excluir')
    
    if not perfil or perfil not in PERFILES_JUGADORES:
        return JsonResponse({'error': 'Perfil no válido'}, status=400)
    
    equipo_excluir_id = None
    if equipo_excluir and equipo_excluir.isdigit():
        equipo_excluir_id = int(equipo_excluir)
    
    try:
        recomendaciones = recomendar_jugadores_por_perfil(
            perfil, limite, equipo_excluir_id
        )
        
        # Formatear respuesta para JSON
        jugadores_json = []
        for rec in recomendaciones:
            jugador = rec['jugador']
            jugadores_json.append({
                'id': jugador.id,
                'nombre': jugador.nombre,
                'posicion': jugador.posicion,
                'equipo': jugador.equipo.nombre if jugador.equipo else 'Sin equipo',
                'equipo_logo': jugador.equipo.logo if jugador.equipo and jugador.equipo.logo else None,
                'edad': jugador.edad,
                'pais': jugador.pais,
                'puntuacion': rec['puntuacion'],
                'perfil': rec['perfil'],
                'descripcion_perfil': rec['descripcion_perfil'],
                'stats_destacadas': rec['stats_destacadas']
            })
        
        return JsonResponse({
            'jugadores': jugadores_json,
            'total': len(jugadores_json),
            'perfil_info': {
                'nombre': perfil,
                'descripcion': PERFILES_JUGADORES[perfil]['descripcion']
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def ajax_equipos(request):
    """API para obtener lista de equipos en formato JSON"""
    try:
        equipos_bd = Equipo.objects.all().order_by('nombre')
        equipos = []
        for equipo_bd in equipos_bd:
            equipos.append({
                'id': equipo_bd.id,
                'nombre': equipo_bd.nombre,
                'nombre_corto': equipo_bd.nombre_corto or equipo_bd.nombre[:15],
                'logo': equipo_bd.logo if equipo_bd.logo else None,
                'liga': equipo_bd.liga
            })
        return JsonResponse({
            'equipos': equipos,
            'total_equipos': len(equipos),
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def ajax_equipo_detalle(request, equipo_id):
    """API para obtener detalle de un equipo específico"""
    try:
        equipo = Equipo.objects.get(id=equipo_id)
        
        # Obtener estadísticas del equipo
        estadisticas_obj = EstadisticasEquipo.objects.filter(equipo=equipo).first()
        
        # Obtener posición en tabla (simulado)
        posicion = 1  # Aquí puedes calcular la posición real
        puntos = 45   # Aquí puedes calcular los puntos reales
        
        equipo_data = {
            'id': equipo.id,
            'nombre': equipo.nombre,
            'nombre_corto': equipo.nombre_corto,
            'logo': equipo.logo,
            'liga': equipo.liga,
            'posicion': posicion,
            'puntos': puntos,
            'rating': estadisticas_obj.fotmob_rating if estadisticas_obj else None,
            'goles_promedio': estadisticas_obj.goals_per_match if estadisticas_obj else None,
            'goles_concedidos_promedio': estadisticas_obj.goals_conceded_per_match if estadisticas_obj else None,
            'posesion_promedio': estadisticas_obj.average_possession if estadisticas_obj else None,
            'vallas_invictas': estadisticas_obj.clean_sheets if estadisticas_obj else None,
            'tiros_arco_promedio': estadisticas_obj.shots_on_target_per_match if estadisticas_obj else None,
            'pases_precisos_promedio': estadisticas_obj.accurate_passes_per_match if estadisticas_obj else None,
            'faltas_promedio': estadisticas_obj.fouls_per_match if estadisticas_obj else None,
        }
        
        return JsonResponse({
            'equipo': equipo_data,
            'status': 'success'
        })
        
    except Equipo.DoesNotExist:
        return JsonResponse({
            'error': 'Equipo no encontrado',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def ajax_equipo_plantilla(request, equipo_id):
    """API para obtener la plantilla de un equipo"""
    try:
        equipo = get_object_or_404(Equipo, id=equipo_id)
        
        # Obtener jugadores ordenados por posición
        orden_posiciones = [
            "GK", "CB", "RB", "LB", "DM", "CM", "LM", "RM", "AM", "LW", "RW", "ST"
        ]
        
        jugadores = Jugador.objects.filter(equipo=equipo)
        
        def orden_jugador(j):
            pos = (j.posicion or "").split(",")[0].strip().upper()
            try:
                idx = orden_posiciones.index(pos)
            except ValueError:
                idx = len(orden_posiciones)
            return idx, j.nombre.lower()
        
        jugadores_ordenados = sorted(jugadores, key=orden_jugador)
        
        jugadores_data = []
        for jugador in jugadores_ordenados:
            jugadores_data.append({
                'id': jugador.id,
                'nombre': jugador.nombre,
                'posicion': jugador.posicion,
                'edad': jugador.edad,
                'dorsal': jugador.dorsal,
                'pais': jugador.pais,
                'altura': jugador.altura,
                'valor': jugador.valor
            })
        
        return JsonResponse({
            'jugadores': jugadores_data,
            'total_jugadores': len(jugadores_data),
            'equipo': {
                'id': equipo.id,
                'nombre': equipo.nombre
            },
            'status': 'success'
        })
        
    except Equipo.DoesNotExist:
        return JsonResponse({
            'error': 'Equipo no encontrado',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def ajax_equipo_estadisticas(request, equipo_id):
    """API para obtener estadísticas detalladas de un equipo"""
    try:
        equipo = get_object_or_404(Equipo, id=equipo_id)
        estadisticas_obj = EstadisticasEquipo.objects.filter(equipo=equipo).first()
        
        if not estadisticas_obj:
            return JsonResponse({
                'error': 'No hay estadísticas disponibles para este equipo',
                'status': 'error'
            }, status=404)
        
        # Traducciones de campos
        traducciones = {
            'fotmob_rating': 'Rating FotMob',
            'goals_per_match': 'Goles por partido',
            'goals_conceded_per_match': 'Goles concedidos por partido',
            'average_possession': 'Posesión promedio',
            'clean_sheets': 'Vallas invictas',
            'expected_goals_xg': 'Goles esperados (xG)',
            'shots_on_target_per_match': 'Tiros al arco por partido',
            'big_chances': 'Ocasiones claras',
            'big_chances_missed': 'Ocasiones claras falladas',
            'accurate_passes_per_match': 'Pases precisos por partido',
            'penalties_awarded': 'Penales a favor',
            'touches_in_opposition_box': 'Toques en área rival',
            'corners': 'Tiros de esquina',
            'interceptions_per_match': 'Intercepciones por partido',
            'successful_tackles_per_match': 'Entradas exitosas por partido'
        }
        
        estadisticas = {}
        exclude = ['id', 'equipo']
        
        for field in estadisticas_obj._meta.fields:
            name = field.name
            if name not in exclude:
                value = getattr(estadisticas_obj, name)
                if value is not None:
                    label = traducciones.get(name, name.replace("_", " ").capitalize())
                    estadisticas[label] = value
        
        return JsonResponse({
            'estadisticas': estadisticas,
            'equipo': {
                'id': equipo.id,
                'nombre': equipo.nombre
            },
            'status': 'success'
        })
        
    except Equipo.DoesNotExist:
        return JsonResponse({
            'error': 'Equipo no encontrado',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def equipo_detalle_view(request, equipo_id):
    """Vista HTML para mostrar la página de detalle de un equipo"""
    try:
        equipo = get_object_or_404(Equipo, id=equipo_id)
        context = {
            'equipo': equipo,
            'equipo_id': equipo_id,
            'page_title': f'{equipo.nombre} | ScoutGine'
        }
        return render(request, 'equipo_detalle.html', context)
    except Exception as e:
        context = {
            'error': f'Error cargando equipo: {str(e)}',
            'equipo_id': equipo_id,
            'page_title': 'Error | ScoutGine'
        }
        return render(request, 'equipo_detalle.html', context)

def ajax_equipo_info(request, equipo_id):
    """API para obtener información básica de un equipo"""
    try:
        equipo = get_object_or_404(Equipo, id=equipo_id)
        
        equipo_data = {
            'id': equipo.id,
            'nombre': equipo.nombre,
            'nombre_corto': equipo.nombre_corto or equipo.nombre[:15],
            'liga': equipo.liga,
            'logo': equipo.logo if equipo.logo else None,
        }
        
        return JsonResponse({
            'equipo': equipo_data,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"❌ Error en ajax_equipo_info: {e}")
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def ajax_equipo_estadistica_detalle(request, equipo_id, estadistica):
    """API para obtener detalle de una estadística específica de un equipo"""
    try:
        if not equipo_id or not estadistica:
            return JsonResponse({
                'error': 'Parámetros de URL faltantes. Se requiere equipo y estadística.',
                'status': 'error'
            }, status=400)
        
        equipo = get_object_or_404(Equipo, id=equipo_id)
        
        # Mapeo de estadísticas
        STAT_MAPPING = {
            'rating': 'fotmob_rating',
            'goles': 'goals_per_match',
            'goles-concedidos': 'goals_conceded_per_match',
            'posesion': 'average_possession',
            'vallas-invictas': 'clean_sheets',
            'xg': 'expected_goals_xg',
            'tiros-arco': 'shots_on_target_per_match',
            'ocasiones-claras': 'big_chances',
            'pases-precisos': 'accurate_passes_per_match',
            'intercepciones': 'interceptions_per_match',
            'entradas-exitosas': 'successful_tackles_per_match'
        }
        
        field_name = STAT_MAPPING.get(estadistica.lower())
        if not field_name:
            return JsonResponse({
                'error': f'Estadística "{estadistica}" no reconocida',
                'status': 'error'
            }, status=400)
        
        # Obtener estadísticas del equipo
        estadisticas_obj = EstadisticasEquipo.objects.filter(equipo=equipo).first()
        if not estadisticas_obj:
            return JsonResponse({
                'error': 'No hay estadísticas disponibles para este equipo',
                'status': 'error'
            }, status=404)
        
        valor_equipo = getattr(estadisticas_obj, field_name, None)
        if valor_equipo is None:
            return JsonResponse({
                'error': f'No hay datos para la estadística "{estadistica}"',
                'status': 'error'
            }, status=404)
        
        # Obtener datos de todos los equipos para comparación
        todos_equipos = EstadisticasEquipo.objects.select_related('equipo').exclude(**{f"{field_name}__isnull": True})
        
        equipos_data = []
        valores_liga = []
        
        for eq_stat in todos_equipos:
            valor = getattr(eq_stat, field_name, None)
            if valor is not None:
                try:
                    valor_float = float(valor)
                    valores_liga.append(valor_float)
                    equipos_data.append({
                        'nombre': eq_stat.equipo.nombre_corto or eq_stat.equipo.nombre[:15],
                        'valor': valor_float,
                        'es_actual': eq_stat.equipo.id == int(equipo_id)
                    })
                except (ValueError, TypeError):
                    continue
        
        # Calcular estadísticas de la liga
        if valores_liga:
            promedio_liga = sum(valores_liga) / len(valores_liga)
            valores_ordenados = sorted(valores_liga, reverse=True)
            try:
                posicion = valores_ordenados.index(float(valor_equipo)) + 1
            except ValueError:
                posicion = None
        else:
            promedio_liga = None
            posicion = None
        
        return JsonResponse({
            'estadistica': {
                'nombre': estadistica,
                'valor_equipo': float(valor_equipo),
                'promedio_liga': round(promedio_liga, 2) if promedio_liga else None,
                'posicion_liga': posicion,
                'total_equipos': len(valores_liga)
            },
            'equipos_comparacion': equipos_data[:10],  # Top 10
            'equipo': {
                'id': equipo.id,
                'nombre': equipo.nombre
            },
            'status': 'success'
        })
        
    except Equipo.DoesNotExist:
        return JsonResponse({
            'error': 'Equipo no encontrado',
            'status': 'error'
        }, status=404)
    except Exception as e:
        print(f"❌ Error en ajax_equipo_estadistica_detalle: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def ajax_grupos_stats_equipos(request):
    """API para obtener grupos de estadísticas de equipos"""
    try:
        grupos = {
            "ofensivo": {
                "nombre": "Ofensivo",
                "estadisticas": [
                    {"key": "goals_per_match", "label": "Goles por partido"},
                    {"key": "expected_goals_xg", "label": "Goles esperados (xG)"},
                    {"key": "shots_on_target_per_match", "label": "Tiros al arco por partido"},
                    {"key": "big_chances", "label": "Ocasiones claras"},
                    {"key": "big_chances_missed", "label": "Ocasiones claras erradas"},
                    {"key": "touches_in_opposition_box", "label": "Toques en área rival"},
                    {"key": "penalties_awarded", "label": "Penales a favor"},
                    {"key": "corners", "label": "Tiros de esquina"}
                ]
            },
            "creacion": {
                "nombre": "Creación",
                "estadisticas": [
                    {"key": "average_possession", "label": "Posesión promedio"},
                    {"key": "accurate_passes_per_match", "label": "Pases precisos por partido"},
                    {"key": "accurate_long_balls_per_match", "label": "Pases largos precisos por partido"},
                    {"key": "accurate_crosses_per_match", "label": "Centros precisos por partido"}
                ]
            },
            "defensivo": {
                "nombre": "Defensivo", 
                "estadisticas": [
                    {"key": "goals_conceded_per_match", "label": "Goles concedidos por partido"},
                    {"key": "xg_concedido", "label": "xG concedidos"},
                    {"key": "clean_sheets", "label": "Vallas invictas"},
                    {"key": "interceptions_per_match", "label": "Intercepciones por partido"},
                    {"key": "successful_tackles_per_match", "label": "Entradas exitosas por partido"},
                    {"key": "clearances_per_match", "label": "Despejes por partido"},
                    {"key": "possession_won_final_3rd_per_match", "label": "Posesión ganada tercio final"},
                    {"key": "saves_per_match", "label": "Atajadas por partido"}
                ]
            },
            "general": {
                "nombre": "General",
                "estadisticas": [
                    {"key": "fotmob_rating", "label": "Rating FotMob"},
                    {"key": "fouls_per_match", "label": "Faltas por partido"},
                    {"key": "yellow_cards", "label": "Tarjetas amarillas"},
                    {"key": "red_cards", "label": "Tarjetas rojas"}
                ]
            }
        }
        return JsonResponse(grupos)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def ajax_grupos_stats_jugadores(request):
    """API para obtener grupos de estadísticas de jugadores"""
    try:
        grupos = {
            "arquero": {
                "nombre": "Arquero",
                "estadisticas": [
                    {"key": "saves", "label": "Atajadas"},
                    {"key": "save_percentage", "label": "% de atajadas"},
                    {"key": "goals_conceded", "label": "Goles concedidos"},
                    {"key": "goals_prevented", "label": "Goles evitados"},
                    {"key": "clean_sheets", "label": "Vallas invictas"},
                    {"key": "error_led_to_goal", "label": "Errores que llevaron a gol"},
                    {"key": "high_claim", "label": "Salidas altas"},
                    {"key": "pass_accuracy", "label": "Precisión de pases"},
                    {"key": "accurate_long_balls", "label": "Pases largos precisos"},
                    {"key": "long_ball_accuracy", "label": "% precisión pases largos"}
                ]
            },
            "ofensivo": {
                "nombre": "Ofensivo",
                "estadisticas": [
                    {"key": "goals", "label": "Goles"},
                    {"key": "expected_goals_xg", "label": "Goles esperados (xG)"},
                    {"key": "xg_on_target_xgot", "label": "xG al arco"},
                    {"key": "non_penalty_xg", "label": "xG sin penales"},
                    {"key": "shots", "label": "Tiros"},
                    {"key": "shots_on_target", "label": "Tiros al arco"},
                    {"key": "touches_in_opposition_box", "label": "Toques en área rival"},
                    {"key": "successful_dribbles", "label": "Regates exitosos"},
                    {"key": "dribble_success", "label": "% éxito en regates"}
                ]
            },
            "creacion": {
                "nombre": "Creación",
                "estadisticas": [
                    {"key": "assists", "label": "Asistencias"},
                    {"key": "expected_assists_xa", "label": "Asistencias esperadas (xA)"},
                    {"key": "successful_passes", "label": "Pases exitosos"},
                    {"key": "pass_accuracy_outfield", "label": "% precisión pases"},
                    {"key": "accurate_long_balls_outfield", "label": "Pases largos precisos"},
                    {"key": "long_ball_accuracy_outfield", "label": "% precisión pases largos"},
                    {"key": "chances_created", "label": "Ocasiones creadas"},
                    {"key": "successful_crosses", "label": "Centros exitosos"},
                    {"key": "cross_accuracy", "label": "% precisión centros"},
                    {"key": "touches", "label": "Toques"}
                ]
            },
            "defensivo": {
                "nombre": "Defensivo",
                "estadisticas": [
                    {"key": "tackles_won", "label": "Entradas ganadas"},
                    {"key": "tackles_won_percentage", "label": "% entradas ganadas"},
                    {"key": "duels_won", "label": "Duelos ganados"},
                    {"key": "duels_won_percentage", "label": "% duelos ganados"},
                    {"key": "aerial_duels_won", "label": "Duelos aéreos ganados"},
                    {"key": "aerial_duels_won_percentage", "label": "% duelos aéreos ganados"},
                    {"key": "interceptions", "label": "Intercepciones"},
                    {"key": "blocked", "label": "Bloqueos"},
                    {"key": "recoveries", "label": "Recuperaciones"},
                    {"key": "possession_won_final_3rd", "label": "Posesión ganada tercio final"}
                ]
            },
            "general": {
                "nombre": "General",
                "estadisticas": [
                    {"key": "fouls_won", "label": "Faltas recibidas"},
                    {"key": "fouls_committed", "label": "Faltas cometidas"},
                    {"key": "penalties_awarded", "label": "Penales conseguidos"},
                    {"key": "yellow_cards", "label": "Tarjetas amarillas"},
                    {"key": "red_cards", "label": "Tarjetas rojas"},
                    {"key": "dispossessed", "label": "Desposesiones"},
                    {"key": "dribbled_past", "label": "Regateado"}
                ]
            }
        }
        return JsonResponse(grupos)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def ajax_equipo_jugadores(request, equipo_id):
    """API para obtener jugadores de un equipo específico"""
    try:
        equipo = get_object_or_404(Equipo, id=equipo_id)
        jugadores = Jugador.objects.filter(equipo=equipo).order_by('nombre')
        
        jugadores_data = []
        for jugador in jugadores:
            jugadores_data.append({
                'id': jugador.id,
                'nombre': jugador.nombre,
                'posicion': jugador.posicion or 'N/A',
                'edad': jugador.edad,
                'equipo': jugador.equipo.nombre if jugador.equipo else 'Sin equipo'
            })
        
        return JsonResponse({
            'jugadores': jugadores_data,
            'total': len(jugadores_data),
            'equipo': {
                'id': equipo.id,
                'nombre': equipo.nombre
            },
            'status': 'success'
        })
        
    except Equipo.DoesNotExist:
        return JsonResponse({
            'error': 'Equipo no encontrado',
            'status': 'error'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

@csrf_exempt
def ajax_comparar_equipos(request):
    """API para comparar dos equipos con estadísticas reales"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        equipo1_id = data.get('equipo1_id')
        equipo2_id = data.get('equipo2_id')
        grupo = data.get('grupo')
        
        # Obtener equipos
        equipo1 = get_object_or_404(Equipo, id=equipo1_id)
        equipo2 = get_object_or_404(Equipo, id=equipo2_id)
        
        # Obtener estadísticas
        stats1 = EstadisticasEquipo.objects.filter(equipo=equipo1).first()
        stats2 = EstadisticasEquipo.objects.filter(equipo=equipo2).first()
        
        if not stats1 or not stats2:
            return JsonResponse({
                'error': 'No hay estadísticas disponibles para uno o ambos equipos',
                'status': 'error'
            }, status=404)
        
        # ✅ MAPEO ACTUALIZADO CON LOS GRUPOS CORRECTOS
        grupos_mapping = {
            "ofensivo": ["goals_per_match", "expected_goals_xg", "shots_on_target_per_match", "big_chances", "touches_in_opposition_box"],
            "creacion": ["accurate_passes_per_match", "accurate_long_balls_per_match", "accurate_crosses_per_match", "average_possession"],
            "defensivo": ["goals_conceded_per_match", "clean_sheets", "interceptions_per_match", "successful_tackles_per_match", "saves_per_match"],
            "general": ["fotmob_rating", "fouls_per_match", "yellow_cards", "red_cards"]
        }
        
        estadisticas_grupo = grupos_mapping.get(grupo, [])
        if not estadisticas_grupo:
            return JsonResponse({
                'error': f'Grupo "{grupo}" no reconocido',
                'status': 'error'
            }, status=400)
        
        # Construir respuesta
        estadisticas = []
        valores_equipo1 = []
        valores_equipo2 = []
        
        for stat_key in estadisticas_grupo:
            valor1 = getattr(stats1, stat_key, 0) or 0
            valor2 = getattr(stats2, stat_key, 0) or 0
            
            # Manejar valores de texto como average_possession
            if isinstance(valor1, str):
                try:
                    valor1 = float(valor1.replace('%', ''))
                except:
                    valor1 = 0
            if isinstance(valor2, str):
                try:
                    valor2 = float(valor2.replace('%', ''))
                except:
                    valor2 = 0
            
            estadisticas.append({
                'nombre': stat_key.replace('_', ' ').replace('per match', '').title(),
                'max_valor': max(float(valor1), float(valor2), 10)
            })
            
            valores_equipo1.append(float(valor1))
            valores_equipo2.append(float(valor2))
        
        return JsonResponse({
            'equipo1': {
                'id': equipo1.id,
                'nombre': equipo1.nombre,
                'liga': equipo1.liga
            },
            'equipo2': {
                'id': equipo2.id,
                'nombre': equipo2.nombre,
                'liga': equipo2.liga
            },
            'estadisticas': estadisticas,
            'valores_equipo1': valores_equipo1,
            'valores_equipo2': valores_equipo2,
            'grupo': grupo,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error en ajax_comparar_equipos: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def ajax_comparar_jugadores(request):
    """API para comparar dos jugadores con estadísticas reales"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        jugador1_id = data.get('jugador1_id')
        jugador2_id = data.get('jugador2_id')
        grupo = data.get('grupo')
        
        if not jugador1_id or not jugador2_id or not grupo:
            return JsonResponse({
                'error': 'Faltan parámetros requeridos: jugador1_id, jugador2_id, grupo',
                'status': 'error'
            }, status=400)
        
        # Obtener jugadores
        jugador1 = get_object_or_404(Jugador, id=jugador1_id)
        jugador2 = get_object_or_404(Jugador, id=jugador2_id)
        
        # Obtener estadísticas
        from .models import EstadisticasJugador
        stats1 = EstadisticasJugador.objects.filter(jugador=jugador1).first()
        stats2 = EstadisticasJugador.objects.filter(jugador=jugador2).first()
        
        if not stats1 or not stats2:
            return JsonResponse({
                'error': 'No hay estadísticas disponibles para uno o ambos jugadores',
                'status': 'error'
            }, status=404)
        
        # ✅ MAPEO COMPLETO CON LOS 5 GRUPOS
        grupos_mapping = {
            "arquero": [
                "saves", "save_percentage", "goals_conceded", "goals_prevented", 
                "clean_sheets", "error_led_to_goal", "high_claim", "pass_accuracy"
            ],
            "ofensivo": [
                "goals", "expected_goals_xg", "shots", "shots_on_target", 
                "touches_in_opposition_box", "successful_dribbles", "dribble_success"
            ],
            "creacion": [
                "assists", "expected_assists_xa", "successful_passes", "pass_accuracy_outfield", 
                "chances_created", "successful_crosses", "cross_accuracy", "touches"
            ],
            "defensivo": [
                "tackles_won", "tackles_won_percentage", "duels_won", "duels_won_percentage",
                "aerial_duels_won", "interceptions", "blocked", "recoveries"
            ],
            "general": [
                "fouls_won", "fouls_committed", "yellow_cards", "red_cards", 
                "dispossessed", "dribbled_past"
            ]
        }
        
        estadisticas_grupo = grupos_mapping.get(grupo, [])
        if not estadisticas_grupo:
            return JsonResponse({
                'error': f'Grupo "{grupo}" no reconocido. Grupos disponibles: {list(grupos_mapping.keys())}',
                'status': 'error'
            }, status=400)
        
        # Construir respuesta con estadísticas reales
        estadisticas = []
        valores_jugador1 = []
        valores_jugador2 = []
        
        # Diccionario de traducciones para nombres más legibles
        traducciones = {
            'saves': 'Atajadas',
            'save_percentage': '% Atajadas',
            'goals_conceded': 'Goles Concedidos',
            'goals_prevented': 'Goles Evitados',
            'clean_sheets': 'Vallas Invictas',
            'pass_accuracy': '% Pases Precisos',
            'goals': 'Goles',
            'expected_goals_xg': 'xG',
            'shots': 'Tiros',
            'shots_on_target': 'Tiros al Arco',
            'touches_in_opposition_box': 'Toques Área Rival',
            'successful_dribbles': 'Regates Exitosos',
            'dribble_success': '% Regates',
            'assists': 'Asistencias',
            'expected_assists_xa': 'xA',
            'successful_passes': 'Pases Exitosos',
            'pass_accuracy_outfield': '% Pases Campo',
            'chances_created': 'Ocasiones Creadas',
            'successful_crosses': 'Centros Exitosos',
            'cross_accuracy': '% Centros',
            'touches': 'Toques',
            'tackles_won': 'Entradas Ganadas',
            'tackles_won_percentage': '% Entradas',
            'duels_won': 'Duelos Ganados',
            'duels_won_percentage': '% Duelos',
            'aerial_duels_won': 'Duelos Aéreos',
            'interceptions': 'Intercepciones',
            'blocked': 'Bloqueos',
            'recoveries': 'Recuperaciones',
            'fouls_won': 'Faltas Recibidas',
            'fouls_committed': 'Faltas Cometidas',
            'yellow_cards': 'Tarjetas Amarillas',
            'red_cards': 'Tarjetas Rojas',
            'dispossessed': 'Desposesiones',
            'dribbled_past': 'Regateado'
        }
        
        for stat_key in estadisticas_grupo:
            valor1 = getattr(stats1, stat_key, 0) or 0
            valor2 = getattr(stats2, stat_key, 0) or 0
            
            # Convertir a float y manejar valores nulos
            try:
                valor1 = float(valor1)
            except (ValueError, TypeError):
                valor1 = 0.0
                
            try:
                valor2 = float(valor2)
            except (ValueError, TypeError):
                valor2 = 0.0
            
            # Usar traducción si existe, sino formatear el nombre
            nombre_stat = traducciones.get(stat_key, stat_key.replace('_', ' ').title())
            
            estadisticas.append({
                'nombre': nombre_stat,
                'max_valor': max(valor1, valor2, 10)  # Valor máximo para escala del gráfico
            })
            
            valores_jugador1.append(valor1)
            valores_jugador2.append(valor2)
        
        return JsonResponse({
            'jugador1': {
                'id': jugador1.id,
                'nombre': jugador1.nombre,
                'equipo': jugador1.equipo.nombre if jugador1.equipo else 'Sin equipo',
                'posicion': jugador1.posicion or 'N/A',
                'edad': jugador1.edad,
                'pais': jugador1.pais
            },
            'jugador2': {
                'id': jugador2.id,
                'nombre': jugador2.nombre,
                'equipo': jugador2.equipo.nombre if jugador2.equipo else 'Sin equipo',
                'posicion': jugador2.posicion or 'N/A',
                'edad': jugador2.edad,
                'pais': jugador2.pais
            },
            'estadisticas': estadisticas,
            'valores_jugador1': valores_jugador1,
            'valores_jugador2': valores_jugador2,
            'grupo': grupo,
            'total_estadisticas': len(estadisticas),
            'status': 'success'
        })
        
    except Jugador.DoesNotExist:
        return JsonResponse({
            'error': 'Uno o ambos jugadores no encontrados',
            'status': 'error'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON inválido en el cuerpo de la petición',
            'status': 'error'
        }, status=400)
    except Exception as e:
        print(f"❌ Error en ajax_comparar_jugadores: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'Error interno del servidor: {str(e)}',
            'status': 'error'
        }, status=500)

@csrf_exempt
def ajax_comparar_equipos_completo(request):
    """API para obtener TODAS las estadísticas de dos equipos de una vez"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        equipo1_id = data.get('equipo1_id')
        equipo2_id = data.get('equipo2_id')
        
        if not equipo1_id or not equipo2_id:
            return JsonResponse({
                'error': 'IDs de equipos requeridos',
                'status': 'error'
            }, status=400)
        
        # Obtener equipos
        try:
            equipo1 = Equipo.objects.get(id=equipo1_id)
            equipo2 = Equipo.objects.get(id=equipo2_id)
        except Equipo.DoesNotExist:
            return JsonResponse({
                'error': 'Uno o ambos equipos no encontrados',
                'status': 'error'
            }, status=404)
        
        # Obtener estadísticas
        try:
            stats1 = EstadisticasEquipo.objects.filter(equipo=equipo1).first()
            stats2 = EstadisticasEquipo.objects.filter(equipo=equipo2).first()
        except Exception as e:
            return JsonResponse({
                'error': f'Error obteniendo estadísticas: {str(e)}',
                'status': 'error'
            }, status=500)
        
        if not stats1 or not stats2:
            return JsonResponse({
                'error': 'No hay estadísticas disponibles para uno o ambos equipos',
                'status': 'error'
            }, status=404)
        
        # ✅ TODOS LOS GRUPOS DE ESTADÍSTICAS
        grupos_mapping = {
            "ofensivo": {
                "nombre": "Estadísticas Ofensivas",
                "icono": "bx-target-lock",
                "stats": ["goals_per_match", "expected_goals_xg", "shots_on_target_per_match", "big_chances", "touches_in_opposition_box"]
            },
            "creacion": {
                "nombre": "Creación de Juego", 
                "icono": "bx-network-chart",
                "stats": ["accurate_passes_per_match", "accurate_long_balls_per_match", "accurate_crosses_per_match", "average_possession"]
            },
            "defensivo": {
                "nombre": "Estadísticas Defensivas",
                "icono": "bx-shield-alt-2", 
                "stats": ["goals_conceded_per_match", "clean_sheets", "interceptions_per_match", "successful_tackles_per_match", "saves_per_match"]
            },
            "general": {
                "nombre": "Estadísticas Generales",
                "icono": "bx-stats",
                "stats": ["fotmob_rating", "fouls_per_match", "yellow_cards", "red_cards"]
            }
        }
        
        # ✅ MAPEO DE NOMBRES LEGIBLES
        nombres_stats = {
            "goals_per_match": "Goles por Partido",
            "expected_goals_xg": "xG (Goles Esperados)",
            "shots_on_target_per_match": "Tiros al Arco p/P",
            "big_chances": "Grandes Oportunidades",
            "touches_in_opposition_box": "Toques en Área Rival",
            "accurate_passes_per_match": "Pases Precisos p/P",
            "accurate_long_balls_per_match": "Pases Largos Precisos p/P", 
            "accurate_crosses_per_match": "Centros Precisos p/P",
            "average_possession": "Posesión Promedio (%)",
            "goals_conceded_per_match": "Goles Recibidos p/P",
            "clean_sheets": "Portería a Cero",
            "interceptions_per_match": "Intercepciones p/P",
            "successful_tackles_per_match": "Tackles Exitosos p/P",
            "saves_per_match": "Atajadas p/P",
            "fotmob_rating": "Rating FotMob",
            "fouls_per_match": "Faltas p/P",
            "yellow_cards": "Tarjetas Amarillas", 
            "red_cards": "Tarjetas Rojas"
        }
        
        # ✅ FUNCIÓN SEGURA PARA OBTENER LIGA
        def get_liga_nombre(equipo):
            try:
                if hasattr(equipo, 'liga') and equipo.liga:
                    # Si liga es un objeto, obtener su nombre
                    if hasattr(equipo.liga, 'nombre'):
                        return equipo.liga.nombre
                    # Si liga es un string directamente
                    else:
                        return str(equipo.liga)
                else:
                    return 'Liga N/A'
            except Exception as e:
                print(f"⚠️ Error obteniendo liga de {equipo.nombre}: {str(e)}")
                return 'Liga N/A'
        
        # ✅ PROCESAR TODOS LOS GRUPOS
        resultado = {
            'equipo1': {
                'nombre': str(equipo1.nombre) if hasattr(equipo1, 'nombre') else 'Equipo 1',
                'liga': get_liga_nombre(equipo1)
            },
            'equipo2': {
                'nombre': str(equipo2.nombre) if hasattr(equipo2, 'nombre') else 'Equipo 2',
                'liga': get_liga_nombre(equipo2)
            },
            'grupos': {}
        }
        
        for grupo_key, grupo_info in grupos_mapping.items():
            estadisticas_grupo = []
            valores_equipo1 = []
            valores_equipo2 = []
            
            for stat_field in grupo_info["stats"]:
                try:
                    # Obtener valores de forma segura
                    valor1 = getattr(stats1, stat_field, 0)
                    valor2 = getattr(stats2, stat_field, 0)
                    
                    # Convertir a float de forma segura
                    valor1 = float(valor1) if valor1 is not None else 0.0
                    valor2 = float(valor2) if valor2 is not None else 0.0
                    
                    estadisticas_grupo.append({
                        'nombre': nombres_stats.get(stat_field, stat_field.replace('_', ' ').title()),
                        'campo': stat_field
                    })
                    valores_equipo1.append(valor1)
                    valores_equipo2.append(valor2)
                    
                except Exception as e:
                    print(f"⚠️ Error procesando {stat_field}: {str(e)}")
                    # Continuar con valores por defecto
                    estadisticas_grupo.append({
                        'nombre': nombres_stats.get(stat_field, stat_field.replace('_', ' ').title()),
                        'campo': stat_field
                    })
                    valores_equipo1.append(0.0)
                    valores_equipo2.append(0.0)
            
            resultado['grupos'][grupo_key] = {
                'nombre': grupo_info["nombre"],
                'icono': grupo_info["icono"],
                'estadisticas': estadisticas_grupo,
                'valores_equipo1': valores_equipo1,
                'valores_equipo2': valores_equipo2
            }
        
        return JsonResponse(resultado)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Datos JSON inválidos',
            'status': 'error'
        }, status=400)
    except Exception as e:
        print(f"❌ Error en ajax_comparar_equipos_completo: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'Error interno del servidor: {str(e)}',
            'status': 'error'
        }, status=500)

@csrf_exempt
def ajax_comparar_jugadores_completo(request):
    """API para obtener TODAS las estadísticas de dos jugadores de una vez"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        jugador1_id = data.get('jugador1_id')
        jugador2_id = data.get('jugador2_id')
        
        if not jugador1_id or not jugador2_id:
            return JsonResponse({
                'error': 'IDs de jugadores requeridos',
                'status': 'error'
            }, status=400)
        
        # Obtener jugadores
        try:
            jugador1 = Jugador.objects.get(id=jugador1_id)
            jugador2 = Jugador.objects.get(id=jugador2_id)
        except Jugador.DoesNotExist:
            return JsonResponse({
                'error': 'Uno o ambos jugadores no encontrados',
                'status': 'error'
            }, status=404)
        
        # Obtener estadísticas
        try:
            stats1 = EstadisticasJugador.objects.filter(jugador=jugador1).first()
            stats2 = EstadisticasJugador.objects.filter(jugador=jugador2).first()
        except Exception as e:
            return JsonResponse({
                'error': f'Error obteniendo estadísticas: {str(e)}',
                'status': 'error'
            }, status=500)
        
        if not stats1 or not stats2:
            return JsonResponse({
                'error': 'No hay estadísticas disponibles para uno o ambos jugadores',
                'status': 'error'
            }, status=404)
        
        # ✅ GRUPOS BÁSICOS PARA EMPEZAR
        grupos_mapping = {
            "general": {
                "nombre": "Estadísticas Generales",
                "icono": "bx-stats",
                "stats": ["goals", "assists", "yellow_cards", "red_cards", "minutes_played"]
            },
            "ofensivo": {
                "nombre": "Estadísticas Ofensivas", 
                "icono": "bx-target-lock",
                "stats": ["goals", "assists", "shots_on_target", "big_chances_scored", "penalty_goals"]
            }
        }
        
        # ✅ MAPEO DE NOMBRES LEGIBLES BÁSICO
        nombres_stats = {
            "goals": "Goles",
            "assists": "Asistencias",
            "yellow_cards": "Tarjetas Amarillas",
            "red_cards": "Tarjetas Rojas", 
            "minutes_played": "Minutos Jugados",
            "shots_on_target": "Tiros al Arco",
            "big_chances_scored": "Grandes Oportunidades Anotadas",
            "penalty_goals": "Goles de Penal"
        }
        
        # ✅ FUNCIÓN SEGURA PARA OBTENER EQUIPO
        def get_equipo_nombre(jugador):
            try:
                if hasattr(jugador, 'equipo') and jugador.equipo:
                    if hasattr(jugador.equipo, 'nombre'):
                        return jugador.equipo.nombre
                    else:
                        return str(jugador.equipo)
                else:
                    return 'Sin Equipo'
            except Exception as e:
                print(f"⚠️ Error obteniendo equipo de {jugador.nombre}: {str(e)}")
                return 'Sin Equipo'
        
        # ✅ PROCESAR TODOS LOS GRUPOS
        resultado = {
            'jugador1': {
                'nombre': str(jugador1.nombre) if hasattr(jugador1, 'nombre') else 'Jugador 1',
                'equipo': get_equipo_nombre(jugador1),
                'posicion': str(jugador1.posicion) if hasattr(jugador1, 'posicion') and jugador1.posicion else 'N/A',
                'edad': int(jugador1.edad) if hasattr(jugador1, 'edad') and jugador1.edad else 0,
                'pais': str(jugador1.pais) if hasattr(jugador1, 'pais') and jugador1.pais else 'N/A'
            },
            'jugador2': {
                'nombre': str(jugador2.nombre) if hasattr(jugador2, 'nombre') else 'Jugador 2',
                'equipo': get_equipo_nombre(jugador2),
                'posicion': str(jugador2.posicion) if hasattr(jugador2, 'posicion') and jugador2.posicion else 'N/A',
                'edad': int(jugador2.edad) if hasattr(jugador2, 'edad') and jugador2.edad else 0,
                'pais': str(jugador2.pais) if hasattr(jugador2, 'pais') and jugador2.pais else 'N/A'
            },
            'grupos': {}
        }
        
        for grupo_key, grupo_info in grupos_mapping.items():
            estadisticas_grupo = []
            valores_jugador1 = []
            valores_jugador2 = []
            
            for stat_field in grupo_info["stats"]:
                try:
                    # Obtener valores de forma segura
                    valor1 = getattr(stats1, stat_field, 0)
                    valor2 = getattr(stats2, stat_field, 0)
                    
                    # Convertir a float de forma segura
                    valor1 = float(valor1) if valor1 is not None else 0.0
                    valor2 = float(valor2) if valor2 is not None else 0.0
                    
                    estadisticas_grupo.append({
                        'nombre': nombres_stats.get(stat_field, stat_field.replace('_', ' ').title()),
                        'campo': stat_field
                    })
                    valores_jugador1.append(valor1)
                    valores_jugador2.append(valor2)
                    
                except Exception as e:
                    print(f"⚠️ Error procesando {stat_field}: {str(e)}")
                    # Continuar con valores por defecto
                    estadisticas_grupo.append({
                        'nombre': nombres_stats.get(stat_field, stat_field.replace('_', ' ').title()),
                        'campo': stat_field
                    })
                    valores_jugador1.append(0.0)
                    valores_jugador2.append(0.0)
            
            resultado['grupos'][grupo_key] = {
                'nombre': grupo_info["nombre"],
                'icono': grupo_info["icono"],
                'estadisticas': estadisticas_grupo,
                'valores_jugador1': valores_jugador1,
                'valores_jugador2': valores_jugador2
            }
        
        return JsonResponse(resultado)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Datos JSON inválidos',
            'status': 'error'
        }, status=400)
    except Exception as e:
        print(f"❌ Error en ajax_comparar_jugadores_completo: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'Error interno del servidor: {str(e)}',
            'status': 'error'
        }, status=500)