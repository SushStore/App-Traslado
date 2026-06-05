"""
trafico.py — Estimación de tiempo de viaje y generación de URLs de navegación.
No usa APIs de pago: calcula con factores locales + hora + clima.
"""

from datetime import datetime
from urllib.parse import quote
from typing import Optional, List
from data import TRAFICO_HORA, FACTOR_LLUVIA_LEVE, FACTOR_LLUVIA_FUERTE
from data import WAZE_BASE, GMAPS_BASE


def estimar_tiempo(
    tiempo_base_min: int,
    ciudad_origen: str,
    lluvia_nivel: str = "ninguna",
    hora: Optional[int] = None,
) -> dict:
    if hora is None:
        hora = datetime.now().hour

    factor_hora = TRAFICO_HORA.get(hora, 1.3)

    if lluvia_nivel == "fuerte":
        factor_lluvia = FACTOR_LLUVIA_FUERTE
        lluvia_label  = f"lluvia fuerte (+{int((FACTOR_LLUVIA_FUERTE-1)*100)}%)"
    elif lluvia_nivel == "leve":
        factor_lluvia = FACTOR_LLUVIA_LEVE
        lluvia_label  = f"lluvia leve (+{int((FACTOR_LLUVIA_LEVE-1)*100)}%)"
    else:
        factor_lluvia = 1.0
        lluvia_label  = None

    if factor_hora >= 2.0:
        trafico_label = f"hora pico intensa (x{factor_hora})"
    elif factor_hora >= 1.6:
        trafico_label = f"trafico moderado-alto (x{factor_hora})"
    elif factor_hora >= 1.3:
        trafico_label = f"trafico moderado (x{factor_hora})"
    else:
        trafico_label = f"trafico fluido (x{factor_hora})"

    factor_total = factor_hora * factor_lluvia
    tiempo_est   = int(tiempo_base_min * factor_total)
    margen       = max(5, int(tiempo_est * 0.15))

    factores = [trafico_label]
    if lluvia_label:
        factores.append(lluvia_label)

    return {
        "minutos":           tiempo_est,
        "rango_min":         tiempo_est - margen,
        "rango_max":         tiempo_est + margen,
        "factores_aplicados": factores,
        "factor_total":      round(factor_total, 2),
        "hora_usada":        hora,
    }


def generar_urls(orig_coords: str, dest_coords: str, dest_nombre: str) -> dict:
    gmaps = GMAPS_BASE.format(orig=orig_coords, dest=dest_coords)
    waze  = WAZE_BASE.format(
        dest=dest_coords.replace(",", "%2C"),
        orig=orig_coords.replace(",", "%2C"),
    )
    gmaps_nombre = (
        "https://www.google.com/maps/dir/"
        f"{orig_coords}/{quote(dest_nombre)}/"
    )
    return {
        "google_maps":        gmaps,
        "google_maps_nombre": gmaps_nombre,
        "waze":               waze,
    }


def sugerir_hora_salida(tiempo_base_min: int, lluvia_nivel: str = "ninguna") -> List[dict]:
    hora_actual = datetime.now().hour
    opciones    = []

    for delta in range(9):
        hora = (hora_actual + delta) % 24
        est  = estimar_tiempo(tiempo_base_min, "", lluvia_nivel, hora)
        opciones.append({
            "hora":    f"{hora:02d}:00",
            "minutos": est["minutos"],
            "factor":  est["factor_total"],
            "label":   est["factores_aplicados"][0],
        })

    opciones_ordenadas = sorted(opciones, key=lambda x: x["minutos"])
    for i, op in enumerate(opciones_ordenadas[:3]):
        op["rank"] = i + 1
    return opciones_ordenadas[:3]
