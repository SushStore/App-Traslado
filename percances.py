"""
percances.py — Raspado ligero de incidentes viales de fuentes públicas gratuitas.
Usa RSS de OVIAL CDMX y fallback a detección por keywords en páginas públicas.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict

TIMEOUT = 5

# Fuentes RSS / JSON públicas gratuitas
FUENTES = [
    {
        "nombre":  "OVIAL CDMX (Twitter/X público)",
        "url":     "https://nitter.net/OVIAL_CDMX/rss",
        "tipo":    "rss_nitter",
    },
    {
        "nombre":  "SSC CDMX Vialidad",
        "url":     "https://nitter.net/SSC_CDMX/rss",
        "tipo":    "rss_nitter",
    },
]

# Vías que nos interesan (para filtrar resultados)
VIAS_INTERES = [
    "pachuca", "morelos", "central", "mexiquense",
    "insurgentes", "periférico", "norte", "ecatepec", "tecámac",
    "indios verdes", "autobuses del norte", "tepexpan",
]

# Palabras clave de incidente grave
KEYWORDS_GRAVE = [
    "accidente", "choque", "volcadura", "cierre", "bloqueo",
    "manifestación", "corte vial", "derrumbe", "inundación",
]


def obtener_reportes_viales(vias_usuario: List[str]) -> Dict:
    """
    Intenta obtener reportes de incidentes viales de fuentes RSS públicas.
    Retorna dict con: reportes (lista), fuente_usada, error
    """
    resultado = {
        "reportes":     [],
        "fuente_usada": None,
        "ultima_actualizacion": datetime.now().strftime("%H:%M"),
        "error": None,
    }

    for fuente in FUENTES:
        try:
            resp = requests.get(
                fuente["url"], timeout=TIMEOUT,
                headers={
                    "User-Agent": "Mozilla/5.0 TrasladorMetro/1.0",
                    "Accept": "application/rss+xml, application/xml, text/xml",
                }
            )
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item")[:20]  # Últimos 20 tweets/posts

            for item in items:
                titulo = (item.find("title") or item.find("description") or item.find("summary"))
                if not titulo:
                    continue
                texto = titulo.get_text(strip=True).lower()

                # Filtrar por vías de interés del usuario
                via_relevante = any(v.lower() in texto for v in VIAS_INTERES)
                via_usuario   = any(v.lower() in texto for v in vias_usuario)
                es_incidente  = any(k in texto for k in KEYWORDS_GRAVE)

                if (via_relevante or via_usuario) and es_incidente:
                    pub_date = item.find("pubDate")
                    fecha_str = pub_date.get_text(strip=True)[:16] if pub_date else "—"

                    # Calcular severidad
                    severidad = _calcular_severidad(texto)

                    resultado["reportes"].append({
                        "texto":     titulo.get_text(strip=True)[:200],
                        "fecha":     fecha_str,
                        "severidad": severidad,
                        "fuente":    fuente["nombre"],
                    })

            if resultado["reportes"]:
                resultado["fuente_usada"] = fuente["nombre"]
                resultado["reportes"] = sorted(
                    resultado["reportes"],
                    key=lambda x: x["severidad"], reverse=True
                )[:8]  # Máx 8 reportes
                return resultado

        except Exception:
            continue  # Prueba siguiente fuente

    # Si no se obtuvo nada de RSS, retornar aviso
    resultado["error"] = (
        "No se pudo obtener reportes en tiempo real. "
        "Usa los botones de Google Maps / Waze para ver tráfico actual."
    )
    return resultado


def _calcular_severidad(texto: str) -> int:
    """Puntaje de severidad 1-3 según keywords."""
    if any(k in texto for k in ["cierre total", "volcadura", "derrumbe", "inundación", "bloqueo total"]):
        return 3
    if any(k in texto for k in ["accidente", "choque", "manifestación", "corte vial"]):
        return 2
    return 1


def icono_severidad(nivel: int) -> str:
    return {3: "🔴", 2: "🟠", 1: "🟡"}.get(nivel, "⚪")


def generar_aviso_manual(vias: List[str]) -> str:
    """Genera aviso genérico cuando el scraping falla."""
    hora = datetime.now().hour
    if 7 <= hora <= 9 or 17 <= hora <= 20:
        return (
            "⚠️ **Hora pico activa** — Alta probabilidad de tráfico intenso en: "
            + ", ".join(vias[:3])
            + ". Verifica en tiempo real con los botones de navegación."
        )
    return (
        "ℹ️ Sin reportes críticos detectados automáticamente. "
        "Confirma condiciones con Google Maps / Waze antes de salir."
    )
