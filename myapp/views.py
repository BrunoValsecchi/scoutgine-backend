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

@csrf_exempt
def ajax_grupos_stats_equipos(request):
    """API para obtener grupos de estadísticas de equipos"""
    try:
        from .statsequipo import obtener_grupos_stats_equipos
        grupos = obtener_grupos_stats_equipos()
        return JsonResponse(grupos)
    except Exception as e:
        print(f"❌ Error en ajax_grupos_stats_equipos: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def ajax_grupos_stats_jugadores(request):
    """API para obtener grupos de estadísticas de jugadores"""
    try:
        from .statsjugadores import obtener_grupos_stats_jugadores
        grupos = obtener_grupos_stats_jugadores()
        return JsonResponse(grupos)
    except Exception as e:
        print(f"❌ Error en ajax_grupos_stats_jugadores: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# ✅ TAMBIÉN COMPLETA LA FUNCIÓN QUE ESTÁ INCOMPLETA
@csrf_exempt
def ajax_comparar_jugadores_completo(request):
    """API para comparar jugadores con TODAS las estadísticas"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        jugador1_id = data.get('jugador1_id')
        jugador2_id = data.get('jugador2_id')
        
        if not jugador1_id or not jugador2_id:
            return JsonResponse({'error': 'IDs de jugadores requeridos'}, status=400)
        
        # Importar la función desde comparacion.py
        from .comparacion import comparar_jugadores_completo
        resultado = comparar_jugadores_completo(jugador1_id, jugador2_id)
        
        return JsonResponse(resultado)
        
    except Exception as e:
        print(f"❌ Error en ajax_comparar_jugadores_completo: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def ajax_comparar_equipos_completo(request):
    """API para comparar equipos con TODAS las estadísticas"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        equipo1_id = data.get('equipo1_id')
        equipo2_id = data.get('equipo2_id')
        
        if not equipo1_id or not equipo2_id:
            return JsonResponse({'error': 'IDs de equipos requeridos'}, status=400)
        
        # Importar la función desde comparacion.py
        from .comparacion import comparar_equipos_completo
        resultado = comparar_equipos_completo(equipo1_id, equipo2_id)
        
        return JsonResponse(resultado)
        
    except Exception as e:
        print(f"❌ Error en ajax_comparar_equipos_completo: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def ajax_equipo_jugadores(request, equipo_id):
    """API para obtener jugadores de un equipo específico"""
    try:
        equipo = get_object_or_404(Equipo, id=equipo_id)
        
        # Obtener jugadores del equipo
        jugadores = Jugador.objects.filter(equipo=equipo).order_by('nombre')
        
        jugadores_data = []
        for jugador in jugadores:
            jugadores_data.append({
                'id': jugador.id,
                'nombre': jugador.nombre,
                'posicion': jugador.posicion or 'POS',
                'edad': jugador.edad or 0,
                'dorsal': jugador.dorsal or 0,
                'pais': jugador.pais or 'País no especificado'
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
        print(f"❌ Error en ajax_equipo_jugadores: {e}")
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

@csrf_exempt
def ajax_comparar_equipos(request):
    """API para comparar dos equipos por grupo específico"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        equipo1_id = data.get('equipo1_id')
        equipo2_id = data.get('equipo2_id')
        grupo = data.get('grupo', 'ofensivo')
        
        if not equipo1_id or not equipo2_id:
            return JsonResponse({'error': 'IDs de equipos requeridos'}, status=400)
        
        # Importar la función desde comparacion.py
        from .comparacion import comparar_equipos
        resultado = comparar_equipos(equipo1_id, equipo2_id, grupo)
        
        return JsonResponse(resultado)
        
    except Exception as e:
        print(f"❌ Error en ajax_comparar_equipos: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def ajax_comparar_jugadores(request):
    """API para comparar dos jugadores por grupo específico"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        jugador1_id = data.get('jugador1_id')
        jugador2_id = data.get('jugador2_id')
        grupo = data.get('grupo', 'ofensivo')
        
        if not jugador1_id or not jugador2_id:
            return JsonResponse({'error': 'IDs de jugadores requeridos'}, status=400)
        
        # Importar la función desde comparacion.py
        from .comparacion import comparar_jugadores
        resultado = comparar_jugadores(jugador1_id, jugador2_id, grupo)
        
        return JsonResponse(resultado)
        
    except Exception as e:
        print(f"❌ Error en ajax_comparar_jugadores: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)