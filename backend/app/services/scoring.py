from typing import Optional

def calculate_points(
    pred_goals1: int,
    pred_goals2: int,
    actual_goals1: int,
    actual_goals2: int,
    is_knockout: bool = False,
    # Configuración de puntos (valores por defecto según reglamento)
    pts_result: Optional[int] = None,
    pts_goals: Optional[int] = None,
    pts_diff: Optional[int] = None
) -> int:
    """
    Calcula los puntos obtenidos en un pronóstico basado en las reglas del reglamento.
    """
    # Establecer valores por defecto si no se proporcionan (basado en fase)
    if pts_result is None:
        pts_result = 10 if is_knockout else 5
    if pts_goals is None:
        pts_goals = 4 if is_knockout else 2
    if pts_diff is None:
        pts_diff = 2 if is_knockout else 1

    points = 0
    
    # 1. Acertar el resultado (ganador o empate)
    pred_res = (pred_goals1 > pred_goals2) - (pred_goals1 < pred_goals2)
    actual_res = (actual_goals1 > actual_goals2) - (actual_goals1 < actual_goals2)
    
    if pred_res == actual_res:
        points += pts_result
        
        # 2. Acertar la diferencia de goles
        # Solo se suma si acertó el resultado (implícito en el reglamento)
        if (pred_goals1 - pred_goals2) == (actual_goals1 - actual_goals2):
            points += pts_diff
            
    # 3. Acertar el número de goles de cada equipo (independiente del resultado)
    if pred_goals1 == actual_goals1:
        points += pts_goals
    if pred_goals2 == actual_goals2:
        points += pts_goals
        
    return points
