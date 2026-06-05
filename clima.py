"""
clima.py — Módulo de clima usando wttr.in (100% gratuito, sin API key).
Hace scraping/consulta JSON ligera a wttr.in que no requiere registro.
"""

import requests
from datetime import datetime
from typing import Optional

TIMEOUT = 6  # segundos máximo de espera

# Códigos de condición que indican lluvia según wttr.in WMO
CODIGOS_LLUVIA_LEVE  = {61, 63, 80, 81}     # lluvia ligera / chubascos
CODIGOS_LLUVIA_FUERTE = {65, 67, 82, 95, 96, 99}  # lluvia fuerte / tormenta


def obtener_clima(ciudad_wttr: str) -> dict:
    """
    Consulta wttr.in en formato JSON para una ciudad.
    Retorna dict con: temp_c, descripcion, lluvia_mm, lluvia_nivel, icono, error
    """
    url = f"https://wttr.in/{ciudad_wttr}?format=j1"
    resultado = {
        "temp_c": None,
        "descripcion": "Sin datos",
        "lluvia_mm": 0.0,
        "lluvia_nivel": "ninguna",   # ninguna | leve | fuerte
        "icono": "❓",
        "humedad": None,
        "viento_kmh": None,
        "pronostico_horas": [],
        "error": None,
    }

    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "TrasladorMetro/1.0"})
        resp.raise_for_status()
        data = resp.json()

        actual = data["current_condition"][0]
        resultado["temp_c"]    = int(actual["temp_C"])
        resultado["humedad"]   = int(actual["humidity"])
        resultado["viento_kmh"] = int(actual["windspeedKmph"])
        resultado["descripcion"] = actual["weatherDesc"][0]["value"]
        resultado["icono"]     = _icono_clima(resultado["descripcion"])

        # Precipitación acumulada próximas horas (wttr.in campo precipMM)
        hoy = data["weather"][0]
        lluvia_total = 0.0
        pronostico = []

        for hora in hoy["hourly"]:
            h_val = int(hora["time"]) // 100
            mm    = float(hora.get("precipMM", 0))
            lluvia_total += mm
            desc  = hora["weatherDesc"][0]["value"]
            pronostico.append({
                "hora": f"{h_val:02d}:00",
                "temp":  int(hora["tempC"]),
                "mm":    mm,
                "desc":  desc,
                "icono": _icono_clima(desc),
            })

        resultado["lluvia_mm"]        = round(lluvia_total, 1)
        resultado["pronostico_horas"] = pronostico
        resultado["lluvia_nivel"]     = _nivel_lluvia(lluvia_total, resultado["descripcion"])

    except requests.exceptions.Timeout:
        resultado["error"] = "⏱️ Tiempo de espera agotado"
    except requests.exceptions.ConnectionError:
        resultado["error"] = "🔌 Sin conexión a internet"
    except Exception as e:
        resultado["error"] = f"⚠️ Error: {str(e)[:60]}"

    return resultado


def _nivel_lluvia(mm: float, descripcion: str) -> str:
    """Determina nivel de lluvia según mm acumulados y descripción."""
    desc_lower = descripcion.lower()
    palabras_fuerte = ["heavy", "thunder", "storm", "torrential", "blizzard", "fuerte", "tormenta"]
    palabras_leve   = ["light", "drizzle", "rain", "shower", "llovizna", "lluvia", "chubasco"]

    if any(p in desc_lower for p in palabras_fuerte) or mm > 10:
        return "fuerte"
    if any(p in desc_lower for p in palabras_leve) or mm > 2:
        return "leve"
    return "ninguna"


def _icono_clima(desc: str) -> str:
    """Mapea descripción en inglés/español a emoji."""
    d = desc.lower()
    if any(k in d for k in ["thunder", "storm", "tormenta"]):  return "⛈️"
    if any(k in d for k in ["heavy rain", "torrential"]):       return "🌧️"
    if any(k in d for k in ["light rain", "drizzle", "llovizna"]): return "🌦️"
    if any(k in d for k in ["shower", "rain", "lluvia", "chubasco"]): return "🌧️"
    if any(k in d for k in ["fog", "mist", "niebla", "neblina"]):    return "🌫️"
    if any(k in d for k in ["overcast", "nublado", "cloudy"]):       return "☁️"
    if any(k in d for k in ["partly", "parcial"]):                   return "⛅"
    if any(k in d for k in ["clear", "sunny", "despejado", "sol"]):  return "☀️"
    return "🌡️"


def alerta_lluvia(nivel: str) -> Optional[str]:
    """Devuelve mensaje de alerta si hay lluvia significativa."""
    if nivel == "fuerte":
        return "🚨 LLUVIA FUERTE esperada — considera salir antes o retrasar el viaje 30-45 min"
    if nivel == "leve":
        return "🌦️ Lluvia leve posible — lleva paraguas y suma ~15 min al tiempo estimado"
    return None
