from django.shortcuts import render
from django.http import JsonResponse
from .models import EstadisticasJugador

def stats_jugadores(request):
    """Vista para estadísticas de jugadores - TODAS LAS 47 ESTADÍSTICAS"""
    print("🔄 stats_jugadores ejecutado")
    
    # ✅ DETECCIÓN JSON PARA LIGAS.JS
    if (request.path.endswith('/ajax/stats-jugadores/') or 
        request.GET.get('ajax') == '1' or 
        'ajax' in request.path.lower()):
        
        print("📊 Petición JSON detectada - Devolviendo datos para ligas.js")
        
        try:
            jugadores_stats = EstadisticasJugador.objects.select_related('jugador', 'jugador__equipo').all()
            print(f"📊 Stats Jugadores: {len(jugadores_stats)} jugadores")
            
            # ✅ FUNCIÓN HELPER PARA PROCESAR CADA ESTADÍSTICA
            def procesar_estadistica_jugador(campo_modelo):
                jugadores_data = []
                for jug_stat in jugadores_stats:
                    if jug_stat.jugador and hasattr(jug_stat, campo_modelo):
                        valor = getattr(jug_stat, campo_modelo, None)
                        if valor is not None and valor != '' and str(valor) != '0' and str(valor) != '0.0':
                            try:
                                if isinstance(valor, str):
                                    valor_numerico = float(valor.replace('%', '').replace(',', '.'))
                                else:
                                    valor_numerico = float(valor)
                                
                                if valor_numerico > 0:
                                    obj = {
                                        'jugador': jug_stat.jugador.nombre,
                                        'equipo': jug_stat.jugador.equipo.nombre if jug_stat.jugador.equipo else 'Sin equipo',
                                        'posicion': jug_stat.tipo or 'N/A',
                                        'valor': valor_numerico
                                    }
                                    jugadores_data.append(obj)
                            except (ValueError, TypeError):
                                continue
                return jugadores_data
            
            # ✅ PROCESAR TODAS LAS ESTADÍSTICAS DEL MODELO (47 CAMPOS)
            
            # 🏆 ARQUEROS (10)
            saves = procesar_estadistica_jugador('saves')
            saves.sort(key=lambda x: x['valor'], reverse=True)
            
            save_percentage = procesar_estadistica_jugador('save_percentage')
            save_percentage.sort(key=lambda x: x['valor'], reverse=True)
            
            goals_conceded = procesar_estadistica_jugador('goals_conceded')
            goals_conceded.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            goals_prevented = procesar_estadistica_jugador('goals_prevented')
            goals_prevented.sort(key=lambda x: x['valor'], reverse=True)
            
            clean_sheets = procesar_estadistica_jugador('clean_sheets')
            clean_sheets.sort(key=lambda x: x['valor'], reverse=True)
            
            error_led_to_goal = procesar_estadistica_jugador('error_led_to_goal')
            error_led_to_goal.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            high_claim = procesar_estadistica_jugador('high_claim')
            high_claim.sort(key=lambda x: x['valor'], reverse=True)
            
            pass_accuracy = procesar_estadistica_jugador('pass_accuracy')
            pass_accuracy.sort(key=lambda x: x['valor'], reverse=True)
            
            accurate_long_balls = procesar_estadistica_jugador('accurate_long_balls')
            accurate_long_balls.sort(key=lambda x: x['valor'], reverse=True)
            
            long_ball_accuracy = procesar_estadistica_jugador('long_ball_accuracy')
            long_ball_accuracy.sort(key=lambda x: x['valor'], reverse=True)
            
            # ⚽ ATAQUE (10)
            goals = procesar_estadistica_jugador('goals')
            goals.sort(key=lambda x: x['valor'], reverse=True)
            
            expected_goals_xg = procesar_estadistica_jugador('expected_goals_xg')
            expected_goals_xg.sort(key=lambda x: x['valor'], reverse=True)
            
            xg_on_target_xgot = procesar_estadistica_jugador('xg_on_target_xgot')
            xg_on_target_xgot.sort(key=lambda x: x['valor'], reverse=True)
            
            non_penalty_xg = procesar_estadistica_jugador('non_penalty_xg')
            non_penalty_xg.sort(key=lambda x: x['valor'], reverse=True)
            
            shots = procesar_estadistica_jugador('shots')
            shots.sort(key=lambda x: x['valor'], reverse=True)
            
            shots_on_target = procesar_estadistica_jugador('shots_on_target')
            shots_on_target.sort(key=lambda x: x['valor'], reverse=True)
            
            assists = procesar_estadistica_jugador('assists')
            assists.sort(key=lambda x: x['valor'], reverse=True)
            
            expected_assists_xa = procesar_estadistica_jugador('expected_assists_xa')
            expected_assists_xa.sort(key=lambda x: x['valor'], reverse=True)
            
            touches_in_opposition_box = procesar_estadistica_jugador('touches_in_opposition_box')
            touches_in_opposition_box.sort(key=lambda x: x['valor'], reverse=True)
            
            penalties_awarded = procesar_estadistica_jugador('penalties_awarded')
            penalties_awarded.sort(key=lambda x: x['valor'], reverse=True)
            
            # 📋 PASES Y CREACIÓN (8)
            successful_passes = procesar_estadistica_jugador('successful_passes')
            successful_passes.sort(key=lambda x: x['valor'], reverse=True)
            
            pass_accuracy_outfield = procesar_estadistica_jugador('pass_accuracy_outfield')
            pass_accuracy_outfield.sort(key=lambda x: x['valor'], reverse=True)
            
            accurate_long_balls_outfield = procesar_estadistica_jugador('accurate_long_balls_outfield')
            accurate_long_balls_outfield.sort(key=lambda x: x['valor'], reverse=True)
            
            long_ball_accuracy_outfield = procesar_estadistica_jugador('long_ball_accuracy_outfield')
            long_ball_accuracy_outfield.sort(key=lambda x: x['valor'], reverse=True)
            
            chances_created = procesar_estadistica_jugador('chances_created')
            chances_created.sort(key=lambda x: x['valor'], reverse=True)
            
            successful_crosses = procesar_estadistica_jugador('successful_crosses')
            successful_crosses.sort(key=lambda x: x['valor'], reverse=True)
            
            cross_accuracy = procesar_estadistica_jugador('cross_accuracy')
            cross_accuracy.sort(key=lambda x: x['valor'], reverse=True)
            
            touches = procesar_estadistica_jugador('touches')
            touches.sort(key=lambda x: x['valor'], reverse=True)
            
            # 🤸 REGATES Y HABILIDAD (4)
            successful_dribbles = procesar_estadistica_jugador('successful_dribbles')
            successful_dribbles.sort(key=lambda x: x['valor'], reverse=True)
            
            dribble_success = procesar_estadistica_jugador('dribble_success')
            dribble_success.sort(key=lambda x: x['valor'], reverse=True)
            
            dispossessed = procesar_estadistica_jugador('dispossessed')
            dispossessed.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            fouls_won = procesar_estadistica_jugador('fouls_won')
            fouls_won.sort(key=lambda x: x['valor'], reverse=True)
            
            # 🛡️ DEFENSA Y DUELOS (10)
            tackles_won = procesar_estadistica_jugador('tackles_won')
            tackles_won.sort(key=lambda x: x['valor'], reverse=True)
            
            tackles_won_percentage = procesar_estadistica_jugador('tackles_won_percentage')
            tackles_won_percentage.sort(key=lambda x: x['valor'], reverse=True)
            
            duels_won = procesar_estadistica_jugador('duels_won')
            duels_won.sort(key=lambda x: x['valor'], reverse=True)
            
            duels_won_percentage = procesar_estadistica_jugador('duels_won_percentage')
            duels_won_percentage.sort(key=lambda x: x['valor'], reverse=True)
            
            aerial_duels_won = procesar_estadistica_jugador('aerial_duels_won')
            aerial_duels_won.sort(key=lambda x: x['valor'], reverse=True)
            
            aerial_duels_won_percentage = procesar_estadistica_jugador('aerial_duels_won_percentage')
            aerial_duels_won_percentage.sort(key=lambda x: x['valor'], reverse=True)
            
            interceptions = procesar_estadistica_jugador('interceptions')
            interceptions.sort(key=lambda x: x['valor'], reverse=True)
            
            blocked = procesar_estadistica_jugador('blocked')
            blocked.sort(key=lambda x: x['valor'], reverse=True)
            
            recoveries = procesar_estadistica_jugador('recoveries')
            recoveries.sort(key=lambda x: x['valor'], reverse=True)
            
            possession_won_final_3rd = procesar_estadistica_jugador('possession_won_final_3rd')
            possession_won_final_3rd.sort(key=lambda x: x['valor'], reverse=True)
            
            # 🟨 DISCIPLINA (3)
            fouls_committed = procesar_estadistica_jugador('fouls_committed')
            fouls_committed.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            yellow_cards = procesar_estadistica_jugador('yellow_cards')
            yellow_cards.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            red_cards = procesar_estadistica_jugador('red_cards')
            red_cards.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            # 🤕 OTROS (2)
            dribbled_past = procesar_estadistica_jugador('dribbled_past')
            dribbled_past.sort(key=lambda x: x['valor'])  # Ascendente (menos es mejor)
            
            print(f"✅ JSON Jugadores: Procesados {len(jugadores_stats)} jugadores")
            print(f"📊 Rankings generados (ejemplo):")
            print(f"   ⚽ Goles: {len(goals)} jugadores con datos")
            print(f"   🎯 Asistencias: {len(assists)} jugadores con datos")
            print(f"   🧤 Atajadas: {len(saves)} jugadores con datos")
            
            # ✅ DEVOLVER TODAS LAS 47 ESTADÍSTICAS
            return JsonResponse({
                # 🏆 ARQUEROS (10)
                'saves': saves[:15],
                'save_percentage': save_percentage[:15],
                'goals_conceded': goals_conceded[:15],
                'goals_prevented': goals_prevented[:15],
                'clean_sheets': clean_sheets[:15],
                'error_led_to_goal': error_led_to_goal[:15],
                'high_claim': high_claim[:15],
                'pass_accuracy': pass_accuracy[:15],
                'accurate_long_balls': accurate_long_balls[:15],
                'long_ball_accuracy': long_ball_accuracy[:15],
                
                # ⚽ ATAQUE (10)
                'goals': goals[:15],
                'expected_goals_xg': expected_goals_xg[:15],
                'xg_on_target_xgot': xg_on_target_xgot[:15],
                'non_penalty_xg': non_penalty_xg[:15],
                'shots': shots[:15],
                'shots_on_target': shots_on_target[:15],
                'assists': assists[:15],
                'expected_assists_xa': expected_assists_xa[:15],
                'touches_in_opposition_box': touches_in_opposition_box[:15],
                'penalties_awarded': penalties_awarded[:15],
                
                # 📋 PASES Y CREACIÓN (8)
                'successful_passes': successful_passes[:15],
                'pass_accuracy_outfield': pass_accuracy_outfield[:15],
                'accurate_long_balls_outfield': accurate_long_balls_outfield[:15],
                'long_ball_accuracy_outfield': long_ball_accuracy_outfield[:15],
                'chances_created': chances_created[:15],
                'successful_crosses': successful_crosses[:15],
                'cross_accuracy': cross_accuracy[:15],
                'touches': touches[:15],
                
                # 🤸 REGATES Y HABILIDAD (4)
                'successful_dribbles': successful_dribbles[:15],
                'dribble_success': dribble_success[:15],
                'dispossessed': dispossessed[:15],
                'fouls_won': fouls_won[:15],
                
                # 🛡️ DEFENSA Y DUELOS (10)
                'tackles_won': tackles_won[:15],
                'tackles_won_percentage': tackles_won_percentage[:15],
                'duels_won': duels_won[:15],
                'duels_won_percentage': duels_won_percentage[:15],
                'aerial_duels_won': aerial_duels_won[:15],
                'aerial_duels_won_percentage': aerial_duels_won_percentage[:15],
                'interceptions': interceptions[:15],
                'blocked': blocked[:15],
                'recoveries': recoveries[:15],
                'possession_won_final_3rd': possession_won_final_3rd[:15],
                
                # 🟨 DISCIPLINA (3)
                'fouls_committed': fouls_committed[:15],
                'yellow_cards': yellow_cards[:15],
                'red_cards': red_cards[:15],
                
                # 🤕 OTROS (2)
                'dribbled_past': dribbled_past[:15],
                
                'total_jugadores': len(jugadores_stats),
                'status': 'success'
            })
            
        except Exception as e:
            print(f"❌ Error en JSON stats jugadores: {e}")
            import traceback
            traceback.print_exc()
            
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    # ✅ VISTA RESUMEN SIMPLE
    return JsonResponse({
        'message': 'Stats jugadores - Vista básica',
        'status': 'success'
    })