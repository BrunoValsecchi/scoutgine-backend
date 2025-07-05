from django.shortcuts import render
from django.http import JsonResponse
from .models import EstadisticasEquipo

def stats_equipos(request):
    """Vista para estadísticas de equipos"""
    print("🔄 stats_equipos ejecutado")
    
    # ✅ DETECCIÓN JSON PARA LIGAS.JS (AL INICIO)
    if (request.path.endswith('/ajax/stats-equipos/') or 
        request.GET.get('ajax') == '1' or 
        request.headers.get('Content-Type') == 'application/json' or
        'ajax' in request.path.lower()):
        
        print("📊 Petición JSON detectada - Devolviendo datos para ligas.js")
        
        try:
            equipos_stats = EstadisticasEquipo.objects.select_related('equipo').all()
            
            # ✅ FUNCIÓN HELPER PARA PROCESAR CADA ESTADÍSTICA
            def procesar_estadistica(campo_modelo, clave_retorno):
                equipos_data = []
                for eq_stat in equipos_stats:
                    if eq_stat.equipo and hasattr(eq_stat, campo_modelo):
                        valor = getattr(eq_stat, campo_modelo, None)
                        if valor and str(valor) != '0' and str(valor) != '0.0':
                            try:
                                valor_str = str(valor).replace('%', '').replace(',', '.')
                                valor_num = float(valor_str)
                                if valor_num > 0:
                                    obj = {
                                        'equipo': eq_stat.equipo.nombre,
                                        'valor': valor_num,
                                        clave_retorno: valor_num
                                    }
                                    equipos_data.append(obj)
                            except (ValueError, TypeError):
                                continue
                return equipos_data
            
            # ✅ PROCESAR TODAS LAS 22 ESTADÍSTICAS
            
            # 1. RATING FOTMOB
            rating = procesar_estadistica('fotmob_rating', 'rating')
            rating.sort(key=lambda x: x['valor'], reverse=True)
            
            # 2. GOLES POR PARTIDO
            goles_favor = procesar_estadistica('goals_per_match', 'gf')
            goles_favor.sort(key=lambda x: x['valor'], reverse=True)
            
            # 3. GOLES RECIBIDOS POR PARTIDO
            goles_contra = procesar_estadistica('goals_conceded_per_match', 'gc')
            goles_contra.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            # 4. POSESIÓN PROMEDIO
            posesion = procesar_estadistica('average_possession', 'posesion')
            posesion.sort(key=lambda x: x['valor'], reverse=True)
            
            # 5. VALLAS INVICTAS
            vallas_invictas = procesar_estadistica('clean_sheets', 'vallas_invictas')
            vallas_invictas.sort(key=lambda x: x['valor'], reverse=True)
            
            # 6. GOLES ESPERADOS (xG)
            goles_esperados = procesar_estadistica('expected_goals_xg', 'goles_esperados')
            goles_esperados.sort(key=lambda x: x['valor'], reverse=True)
            
            # 7. TIROS AL ARCO POR PARTIDO
            tiros_al_arco = procesar_estadistica('shots_on_target_per_match', 'tiros_al_arco')
            tiros_al_arco.sort(key=lambda x: x['valor'], reverse=True)
            
            # 8. GRANDES OPORTUNIDADES
            grandes_oportunidades = procesar_estadistica('big_chances', 'grandes_oportunidades')
            grandes_oportunidades.sort(key=lambda x: x['valor'], reverse=True)
            
            # 9. GRANDES OPORTUNIDADES PERDIDAS
            grandes_oportunidades_perdidas = procesar_estadistica('big_chances_missed', 'grandes_oportunidades_perdidas')
            grandes_oportunidades_perdidas.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            # 10. PENALES A FAVOR
            penales_favor = procesar_estadistica('penalties_awarded', 'penales_favor')
            penales_favor.sort(key=lambda x: x['valor'], reverse=True)
            
            # 11. TOQUES EN ÁREA RIVAL
            toques_area_rival = procesar_estadistica('touches_in_opposition_box', 'toques_area_rival')
            toques_area_rival.sort(key=lambda x: x['valor'], reverse=True)
            
            # 12. CÓRNERS
            corners = procesar_estadistica('corners', 'corners')
            corners.sort(key=lambda x: x['valor'], reverse=True)
            
            # 13. PASES PRECISOS POR PARTIDO
            pases_precisos = procesar_estadistica('accurate_passes_per_match', 'pases_precisos')
            pases_precisos.sort(key=lambda x: x['valor'], reverse=True)
            
            # 14. PASES LARGOS PRECISOS POR PARTIDO
            pases_largos_precisos = procesar_estadistica('accurate_long_balls_per_match', 'pases_largos_precisos')
            pases_largos_precisos.sort(key=lambda x: x['valor'], reverse=True)
            
            # 15. CENTROS PRECISOS POR PARTIDO
            centros_precisos = procesar_estadistica('accurate_crosses_per_match', 'centros_precisos')
            centros_precisos.sort(key=lambda x: x['valor'], reverse=True)
            
            # 16. xG CONCEDIDOS
            xg_concedidos = procesar_estadistica('xg_conceded', 'xg_concedidos')
            xg_concedidos.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            # 17. INTERCEPCIONES POR PARTIDO
            intercepciones = procesar_estadistica('interceptions_per_match', 'intercepciones')
            intercepciones.sort(key=lambda x: x['valor'], reverse=True)
            
            # 18. TACKLES EXITOSOS POR PARTIDO
            tackles_exitosos = procesar_estadistica('successful_tackles_per_match', 'tackles_exitosos')
            tackles_exitosos.sort(key=lambda x: x['valor'], reverse=True)
            
            # 19. DESPEJES POR PARTIDO
            despejes = procesar_estadistica('clearances_per_match', 'despejes')
            despejes.sort(key=lambda x: x['valor'], reverse=True)
            
            # 20. RECUPERACIONES EN CAMPO RIVAL
            recuperaciones_campo_rival = procesar_estadistica('possession_won_final_3rd_per_match', 'recuperaciones_campo_rival')
            recuperaciones_campo_rival.sort(key=lambda x: x['valor'], reverse=True)
            
            # 21. ATAJADAS POR PARTIDO
            atajadas = procesar_estadistica('saves_per_match', 'atajadas')
            atajadas.sort(key=lambda x: x['valor'], reverse=True)
            
            # 22. FALTAS POR PARTIDO
            faltas = procesar_estadistica('fouls_per_match', 'faltas')
            faltas.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            # 23. TARJETAS AMARILLAS
            tarjetas_amarillas = procesar_estadistica('yellow_cards', 'tarjetas_amarillas')
            tarjetas_amarillas.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            # 24. TARJETAS ROJAS
            tarjetas_rojas = procesar_estadistica('red_cards', 'tarjetas_rojas')
            tarjetas_rojas.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            print(f"✅ JSON: Procesados {len(equipos_stats)} equipos")
            print(f"📊 Rankings generados (Top 5 por cada estadística):")
            print(f"   ⭐ Rating: {len(rating)} equipos")
            print(f"   ⚽ Goles favor: {len(goles_favor)} equipos")
            print(f"   🛡️ Goles contra: {len(goles_contra)} equipos")
            print(f"   🏀 Posesión: {len(posesion)} equipos")
            print(f"   🥅 Vallas: {len(vallas_invictas)} equipos")
            print(f"   📈 xG: {len(goles_esperados)} equipos")
            print(f"   🎯 Tiros: {len(tiros_al_arco)} equipos")
            print(f"   💫 Grandes oport.: {len(grandes_oportunidades)} equipos")
            print(f"   📋 Pases precisos: {len(pases_precisos)} equipos")
            print(f"   ⚔️ Tackles: {len(tackles_exitosos)} equipos")
            
            # ✅ DEVOLVER TODAS LAS 22 ESTADÍSTICAS
            return JsonResponse({
                # Generales (5)
                'rating': rating[:15],
                'goles_favor': goles_favor[:15],
                'goles_contra': goles_contra[:15],
                'posesion': posesion[:15],
                'vallas_invictas': vallas_invictas[:15],
                
                # Ataque (7)
                'goles_esperados': goles_esperados[:15],
                'tiros_al_arco': tiros_al_arco[:15],
                'grandes_oportunidades': grandes_oportunidades[:15],
                'grandes_oportunidades_perdidas': grandes_oportunidades_perdidas[:15],
                'penales_favor': penales_favor[:15],
                'toques_area_rival': toques_area_rival[:15],
                'corners': corners[:15],
                
                # Pases (3)
                'pases_precisos': pases_precisos[:15],
                'pases_largos_precisos': pases_largos_precisos[:15],
                'centros_precisos': centros_precisos[:15],
                
                # Defensa (6)
                'xg_concedidos': xg_concedidos[:15],
                'intercepciones': intercepciones[:15],
                'tackles_exitosos': tackles_exitosos[:15],
                'despejes': despejes[:15],
                'recuperaciones_campo_rival': recuperaciones_campo_rival[:15],
                'atajadas': atajadas[:15],
                
                # Disciplina (3)
                'faltas': faltas[:15],
                'tarjetas_amarillas': tarjetas_amarillas[:15],
                'tarjetas_rojas': tarjetas_rojas[:15],
                
                'total_equipos': len(equipos_stats),
                'status': 'success'
            })
            
        except Exception as e:
            print(f"❌ Error en JSON stats equipos: {e}")
            import traceback
            traceback.print_exc()
            
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    # ✅ SI ES PETICIÓN AJAX (Vista Completa)
    if request.GET.get('format') == 'json':
        estadistica = request.GET.get('estadistica')
        print(f"📊 Petición AJAX para: {estadistica}")
        
        if not estadistica:
            return JsonResponse({"error": "No se especificó estadística"})
        
        # ✅ SOLO LAS ESTADÍSTICAS ESPECIFICADAS
        campos = {
            # Generales (5)
            'fotmob_rating': 'Rating FotMob',
            'goals_per_match': 'Goles por partido',
            'goals_conceded_per_match': 'Goles recibidos por partido',
            'average_possession': 'Posesión promedio (%)',
            'clean_sheets': 'Vallas invictas',
            
            # Ataque (7)
            'expected_goals_xg': 'Goles esperados (xG)',
            'shots_on_target_per_match': 'Tiros al arco por partido',
            'big_chances': 'Grandes oportunidades',
            'big_chances_missed': 'Grandes oportunidades perdidas',
            'penalties_awarded': 'Penales a favor',
            'touches_in_opposition_box': 'Toques en área rival',
            'corners': 'Córners',
            
            # Pases (3)
            'accurate_passes_per_match': 'Pases precisos por partido',
            'accurate_long_balls_per_match': 'Pases largos precisos por partido',
            'accurate_crosses_per_match': 'Centros precisos por partido',
            
            # Defensa (7)
            'xg_concedidos': 'xG concedidos',
            'interceptions_per_match': 'Intercepciones por partido',
            'successful_tackles_per_match': 'Tackles exitosos por partido',
            'clearances_per_match': 'Despejes por partido',
            'possession_won_final_3rd_per_match': 'Recuperaciones en campo rival',
            'saves_per_match': 'Atajadas por partido',
            
            # Disciplina (3)
            'fouls_per_match': 'Faltas por partido',
            'yellow_cards': 'Tarjetas amarillas',
            'red_cards': 'Tarjetas rojas',
        }
        
        if estadistica not in campos:
            return JsonResponse({"error": f"Campo {estadistica} no válido. Disponibles: {list(campos.keys())}"})
        
        try:
            equipos_stats = EstadisticasEquipo.objects.select_related('equipo').all()
            equipos_lista = []
            
            for eq_stat in equipos_stats:
                valor = getattr(eq_stat, estadistica, None)
                
                if valor is not None and valor != '' and str(valor) != '0' and str(valor) != '0.0':
                    try:
                        if isinstance(valor, str):
                            valor_numerico = float(valor.replace('%', '').replace(',', '.'))
                        else:
                            valor_numerico = float(valor)
                        
                        if valor_numerico > 0:
                            if "possession" in estadistica:
                                formato = f"{valor_numerico:.1f}%"
                            elif estadistica in ['yellow_cards', 'red_cards', 'clean_sheets', 'big_chances', 
                                               'big_chances_missed', 'penalties_awarded', 'touches_in_opposition_box', 
                                               'corners', 'interceptions_per_match']:
                                formato = f"{int(valor_numerico)}"
                            else:
                                formato = f"{valor_numerico:.1f}"
                            
                            equipos_lista.append({
                                'nombre': eq_stat.equipo.nombre,
                                'valor': valor_numerico,
                                'valor_formatted': formato
                            })
                    except (ValueError, TypeError) as e:
                        print(f"⚠️ Error procesando {eq_stat.equipo.nombre} - {estadistica}: {valor} -> {e}")
                        continue
            
            # Ordenar
            stats_ascendentes = ['goals_conceded_per_match', 'xg_conceded', 'fouls_per_match', 
                               'yellow_cards', 'red_cards', 'big_chances_missed']
            reverse_order = estadistica not in stats_ascendentes
            
            equipos_lista.sort(key=lambda x: x['valor'], reverse=reverse_order)
            
            print(f"✅ AJAX: {estadistica} -> {len(equipos_lista)} equipos con datos válidos")
            if equipos_lista:
                print("🥇 Top 3:", [f'{eq["nombre"]}: {eq["valor_formatted"]}' for eq in equipos_lista[:3]])
            
            return JsonResponse({
                'equipos': equipos_lista,
                'label': campos[estadistica],
                'total': len(equipos_lista)
            })
            
        except Exception as e:
            print(f"❌ Error AJAX: {e}")
            return JsonResponse({"error": str(e)})
    
    # ✅ VISTA NORMAL (Vista Resumen) - SOLO ESTADÍSTICAS ESPECIFICADAS
    print("🏠 Generando Vista Resumen con TOP 3")
    
    campos_resumen = {
        # Generales (5)
        'fotmob_rating': 'Rating FotMob',
        'goals_per_match': 'Goles por partido',
        'goals_conceded_per_match': 'Goles recibidos por partido',
        'average_possession': 'Posesión promedio (%)',
        'clean_sheets': 'Vallas invictas',
        
        # Ataque (7)
        'expected_goals_xg': 'Goles esperados (xG)',
        'shots_on_target_per_match': 'Tiros al arco por partido',
        'big_chances': 'Grandes oportunidades',
        'big_chances_missed': 'Grandes oportunidades perdidas',
        'penales_awarded': 'Penales a favor',
       
        'corners': 'Córners',
        
        # Pases (3)
        'accurate_passes_per_match': 'Pases precisos por partido',
        'accurate_long_balls_per_match': 'Pases largos precisos por partido',
        'accurate_crosses_per_match': 'Centros precisos por partido',
        
        # Defensa (7)
        'xg_concedidos': 'xG concedidos',
        'interceptions_per_match': 'Intercepciones por partido',
        'successful_tackles_per_match': 'Tackles exitosos por partido',
        'clearances_per_match': 'Despejes por partido',
        'possession_won_final_3rd_per_match': 'Recuperaciones en campo rival',
        'saves_per_match': 'Atajadas por partido',
        
        # Disciplina (3)
        'fouls_per_match': 'Faltas por partido',
        'yellow_cards': 'Tarjetas amarillas',
        'red_cards': 'Tarjetas rojas',
    }
    
    top3_por_estadistica = {}
    
    for campo, label in campos_resumen.items():
        print(f"🔍 Procesando campo: {campo} ({label})")
        
        try:
            equipos_stats = EstadisticasEquipo.objects.select_related('equipo').all()
            equipos_con_datos = []
            
            for eq_stat in equipos_stats:
                valor = getattr(eq_stat, campo, None)
                
                if valor is not None and valor != '' and str(valor) != '0' and str(valor) != '0.0':
                    try:
                        if isinstance(valor, str):
                            valor_numerico = float(valor.replace('%', '').replace(',', '.'))
                        else:
                            valor_numerico = float(valor)
                        
                        if valor_numerico > 0:
                            if "possession" in campo:
                                formato = f"{valor_numerico:.1f}%"
                            elif campo in ['clean_sheets']:
                                formato = f"{int(valor_numerico)}"
                            else:
                                formato = f"{valor_numerico:.1f}"
                            
                            equipos_con_datos.append({
                                'nombre': eq_stat.equipo.nombre,
                                'valor': formato,
                                'valor_numerico': valor_numerico
                            })
                    except (ValueError, TypeError):
                        continue
            
            equipos_con_datos.sort(key=lambda x: x['valor_numerico'], reverse=True)
            top3 = equipos_con_datos[:3]
            
            print(f"✅ {label}: {len(top3)} equipos en top 3")
            for i, equipo in enumerate(top3):
                print(f"  {i+1}. {equipo['nombre']}: {equipo['valor']}")
            
            top3_por_estadistica[label] = top3
            
        except Exception as e:
            print(f"❌ Error en {label}: {e}")
            top3_por_estadistica[label] = []
    
    print(f"🎯 Total estadísticas procesadas: {len(top3_por_estadistica)}")
    
    context = {
        "top3_por_estadistica": top3_por_estadistica
    }
    
    print("📄 Renderizando template con context")
    
    return render(request, "partials/statsequipo.html", context)


def obtener_stats_resumen():
    """Función auxiliar para obtener TOP 3 por estadística (para usar en otras vistas)"""
    print("🔄 obtener_stats_resumen ejecutado")
    
    # ✅ SOLO LAS ESTADÍSTICAS ESPECIFICADAS
    campos = {
        # Generales (5)
        'fotmob_rating': 'Rating FotMob',
        'goals_per_match': 'Goles por partido',
        'goals_conceded_per_match': 'Goles recibidos por partido',
        'average_possession': 'Posesión promedio (%)',
        'clean_sheets': 'Vallas invictas',
        
        # Ataque (7)
        'expected_goals_xg': 'Goles esperados (xG)',
        'shots_on_target_per_match': 'Tiros al arco por partido',
        'big_chances': 'Grandes oportunidades',
        'big_chances_missed': 'Grandes oportunidades perdidas',
        'penalties_awarded': 'Penales a favor',
        'touches_in_opposition_box': 'Toques en área rival',
        'corners': 'Córners',
        
        # Pases (3)
        'accurate_passes_per_match': 'Pases precisos por partido',
        'accurate_long_balls_per_match': 'Pases largos precisos por partido',
        'accurate_crosses_per_match': 'Centros precisos por partido',
        
        # Defensa (7)
        'xg_concedidos': 'xG concedidos',
        'interceptions_per_match': 'Intercepciones por partido',
        'successful_tackles_per_match': 'Tackles exitosos por partido',
        'clearances_per_match': 'Despejes por partido',
        'possession_won_final_3rd_per_match': 'Recuperaciones en campo rival',
        'saves_per_match': 'Atajadas por partido',
        
        # Disciplina (3)
        'fouls_per_match': 'Faltas por partido',
        'yellow_cards': 'Tarjetas amarillas',
        'red_cards': 'Tarjetas rojas',
    }
    
    top3_por_estadistica = {}
    
    for campo, label in campos.items():
        try:
            equipos_stats = EstadisticasEquipo.objects.select_related('equipo').all()
            equipos_con_datos = []
            
            for eq_stat in equipos_stats:
                valor = getattr(eq_stat, campo, None)
                
                if valor is not None and valor != '' and str(valor) != '0' and str(valor) != '0.0':
                    try:
                        if isinstance(valor, str):
                            valor_numerico = float(valor.replace('%', '').replace(',', '.'))
                        else:
                            valor_numerico = float(valor)
                        
                        if valor_numerico > 0:
                            if "possession" in campo:
                                formato = f"{valor_numerico:.1f}%"
                            elif campo in ['clean_sheets']:
                                formato = f"{int(valor_numerico)}"
                            else:
                                formato = f"{valor_numerico:.1f}"
                            
                            equipos_con_datos.append({
                                'nombre': eq_stat.equipo.nombre,
                                'valor': formato,
                                'valor_numerico': valor_numerico
                            })
                    except (ValueError, TypeError):
                        continue
            
            equipos_con_datos.sort(key=lambda x: x['valor_numerico'], reverse=True)
            top3 = equipos_con_datos[:3]
            
            top3_por_estadistica[label] = top3
            
        except Exception as e:
            print(f"❌ Error en {label}: {e}")
            top3_por_estadistica[label] = []
    
    return top3_por_estadistica

def obtener_grupos_stats_equipos():
    """Devuelve los grupos de estadísticas de equipos"""
    return {
        "ofensivo": {
            "nombre": "Ofensivo",
            "icono": "bx-football",
            "estadisticas": [
                {"key": "goals_per_match", "nombre": "Goles por partido"},
                {"key": "expected_goals_xg", "nombre": "Goles esperados (xG)"},
                {"key": "shots_on_target_per_match", "nombre": "Tiros al arco por partido"},
                {"key": "big_chances", "nombre": "Ocasiones claras"},
                {"key": "touches_in_opposition_box", "nombre": "Toques en área rival"}
            ]
        },
        "creacion": {
            "nombre": "Creación",
            "icono": "bx-transfer",
            "estadisticas": [
                {"key": "accurate_passes_per_match", "nombre": "Pases precisos por partido"},
                {"key": "accurate_long_balls_per_match", "nombre": "Pases largos precisos"},
                {"key": "accurate_crosses_per_match", "nombre": "Centros precisos"},
                {"key": "average_possession", "nombre": "Posesión promedio"}
            ]
        },
        "defensivo": {
            "nombre": "Defensivo",
            "icono": "bx-shield",
            "estadisticas": [
                {"key": "goals_conceded_per_match", "nombre": "Goles concedidos por partido"},
                {"key": "clean_sheets", "nombre": "Vallas invictas"},
                {"key": "interceptions_per_match", "nombre": "Intercepciones por partido"},
                {"key": "successful_tackles_per_match", "nombre": "Entradas exitosas"}
            ]
        },
        "general": {
            "nombre": "General",
            "icono": "bx-stats",
            "estadisticas": [
                {"key": "fotmob_rating", "nombre": "Rating FotMob"},
                {"key": "fouls_per_match", "nombre": "Faltas por partido"},
                {"key": "yellow_cards", "nombre": "Tarjetas amarillas"},
                {"key": "red_cards", "nombre": "Tarjetas rojas"}
            ]
        }
    }