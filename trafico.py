"""
trafico.py — Estimación de tiempo en TRANSPORTE PÚBLICO + URLs de navegación.
Calcula tiempo total: caminar → combi/mexibús → espera metro → metro → caminar destino.
"""

from datetime import datetime
from urllib.parse import quote
from typing import Optional, List
from data import TRAFICO_HORA, FACTOR_LLUVIA_LEVE, FACTOR_LLUVIA_FUERTE
from data import WAZE_BASE, GMAPS_BASE, GMAPS_TP_BASE


def estimar_tiempo(
    tiempo_base_min: int,
    origen_abrev: str,       # "Ecatepec" o "Tecámac"
    lluvia_nivel: str = "ninguna",
    hora: Optional[int] = None,
    usuario_data: Optional[dict] = None,
) -> dict:
    """
    Estima tiempo de viaje completo en transporte público.
    Desglose: caminar → alimentador (combi/mexibús) → metro → caminar destino.
    """
    if hora is None:
        hora = datetime.now().hour

    factor_hora = TRAFICO_HORA.get(hora, 1.3)

    if lluvia_nivel == "fuerte":
        factor_lluvia = FACTOR_LLUVIA_FUERTE
        lluvia_label  = f"🌧️ lluvia fuerte (+{int((FACTOR_LLUVIA_FUERTE-1)*100)}%)"
    elif lluvia_nivel == "leve":
        factor_lluvia = FACTOR_LLUVIA_LEVE
        lluvia_label  = f"🌦️ lluvia leve (+{int((FACTOR_LLUVIA_LEVE-1)*100)}%)"
    else:
        factor_lluvia = 1.0
        lluvia_label  = None

    if factor_hora >= 1.9:
        trafico_label = f"🔴 hora pico — metro saturado (×{factor_hora})"
    elif factor_hora >= 1.5:
        trafico_label = f"🟠 demanda alta en TP (×{factor_hora})"
    elif factor_hora >= 1.2:
        trafico_label = f"🟡 demanda moderada (×{factor_hora})"
    else:
        trafico_label = f"🟢 flujo normal (×{factor_hora})"

    factor_total = factor_hora * factor_lluvia
    tiempo_est   = int(tiempo_base_min * factor_total)
    margen       = max(8, int(tiempo_est * 0.18))  # TP tiene más variabilidad

    factores = [trafico_label]
    if lluvia_label:
        factores.append(lluvia_label)

    # Desglose por etapas si tenemos datos del usuario
    desglose = None
    if usuario_data and "transporte" in usuario_data:
        tp = usuario_data["transporte"]
        t_caminar   = tp.get("tiempo_caminata_estacion_min", 7)
        t_alimentador = tp.get("tiempo_combi_metro_min" if "combi" in tp.get("modo_principal","").lower()
                               else "tiempo_mexibus_metro_min", 30)
        # El resto es metro + caminar al destino (estimado)
        t_metro_destino = max(10, tiempo_est - t_caminar - t_alimentador)

        desglose = {
            "caminar_origen":   t_caminar,
            "alimentador":      int(t_alimentador * factor_total),
            "metro_destino":    int(t_metro_destino * min(factor_total, 1.6)),
            "modo_alimentador": tp.get("modo_principal", "Transporte").split("+")[0].strip(),
        }

    return {
        "minutos":            tiempo_est,
        "rango_min":          tiempo_est - margen,
        "rango_max":          tiempo_est + margen,
        "factores_aplicados": factores,
        "factor_total":       round(factor_total, 2),
        "hora_usada":         hora,
        "desglose":           desglose,
    }


def generar_urls(orig_coords: str, dest_coords: str, dest_nombre: str) -> dict:
    """
    Genera URLs para Google Maps (modo TP forzado) y complemento en Waze/Maps normal.
    """
    gmaps_tp = GMAPS_TP_BASE.format(orig=orig_coords, dest=dest_coords)
    gmaps    = GMAPS_BASE.format(orig=orig_coords, dest=dest_coords)
    waze     = WAZE_BASE.format(
        dest=dest_coords.replace(",", "%2C"),
        orig=orig_coords.replace(",", "%2C"),
    )
    gmaps_nombre_tp = (
        f"https://www.google.com/maps/dir/"
        f"{orig_coords}/{quote(dest_nombre)}/"
        f"data=!3m1!4b1!4m2!4m1!3e3"
    )
    return {
        "google_maps_tp":    gmaps_tp,           # Transporte público directo
        "google_maps_nombre_tp": gmaps_nombre_tp,
        "google_maps":       gmaps,              # Por si quieren ver a pie/otro
        "waze":              waze,
    }


def sugerir_hora_salida(
    tiempo_base_min: int,
    lluvia_nivel: str = "ninguna",
    usuario_data: Optional[dict] = None,
) -> List[dict]:
    """
    Evalúa las próximas 9 horas y recomienda las 3 con menor tiempo de viaje.
    Considera horario del transporte público.
    """
    hora_actual = datetime.now().hour
    opciones    = []

    for delta in range(9):
        hora = (hora_actual + delta) % 24

        # El TP tiene horario: muy madrugada no sirven combis/mexibús
        if hora < 5 or hora > 22:
            disponible = False
            nota = "⚫ sin servicio de combis/Mexibús"
        elif hora == 5:
            disponible = True
            nota = "🟤 servicio iniciando"
        else:
            disponible = True
            nota = None

        est = estimar_tiempo(tiempo_base_min, "", lluvia_nivel, hora, usuario_data)

        opciones.append({
            "hora":       f"{hora:02d}:00",
            "minutos":    est["minutos"] if disponible else 999,
            "factor":     est["factor_total"],
            "label":      nota if not disponible else est["factores_aplicados"][0],
            "disponible": disponible,
            "delta":      delta,
        })

    disponibles = [o for o in opciones if o["disponible"]]
    no_disponibles = [o for o in opciones if not o["disponible"]]

    ordenadas = sorted(disponibles, key=lambda x: x["minutos"])[:3]
    for i, op in enumerate(ordenadas):
        op["rank"] = i + 1

    return ordenadas
