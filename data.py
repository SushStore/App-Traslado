"""
data.py — Configuración central de perfiles, destinos y rutas.
Los destinos del usuario se guardan en destinos_usuario.json (editable desde la app).
"""

import json
import os

# ── RUTA DEL ARCHIVO DE DESTINOS PERSONALIZADOS ───────────────────────────────
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DESTINOS_JSON = os.path.join(DIR_BASE, "destinos_usuario.json")

# ── PERFILES DE USUARIO ────────────────────────────────────────────────────────
USUARIOS = {
    "🧑 Tú (Ecatepec)": {
        "nombre": "Tú",
        "origen_nombre": "Ecatepec de Morelos, Edomex",
        # Coordenadas exactas proporcionadas
        "origen_coords": "19.620372530297708,-99.0552915302304",
        "ciudad_clima": "Ecatepec de Morelos",
        "ciudad_wttr": "Ecatepec+de+Morelos",
        "origen_abrev": "Ecatepec",
        # Transporte público principal
        "transporte": {
            "modo_principal": "Mexibús + Metro",
            "descripcion": "Mexibús DIF → Metro (Línea 6 / correspondencia)",
            "estacion_metro_cercana": "Villa de Aragón / Martín Carrera",
            "lineas_metro": ["Línea 6 (Rosa)", "Línea 3 (Verde) vía correspondencia"],
            "tiempo_caminata_estacion_min": 8,   # minutos a pie hasta Mexibús DIF
            "tiempo_mexibus_metro_min": 25,       # Mexibús DIF → estación de metro
            "notas": "El Mexibús DIF opera 5:00–23:00. En lluvia fuerte puede haber demoras de 15–30 min.",
        },
        "vias_principales": [
            "Av. Central (Mexibús)",
            "Vía Morelos",
            "Autopista México-Pachuca",
            "Insurgentes Norte",
        ],
    },
    "👩 Ella (Tecámac)": {
        "nombre": "Ella",
        "origen_nombre": "Tecámac, Edomex",
        # Coordenadas exactas proporcionadas
        "origen_coords": "19.642003450943857,-99.03477021868001",
        "ciudad_clima": "Tecámac",
        "ciudad_wttr": "Tecamac",
        "origen_abrev": "Tecámac",
        # Transporte público principal
        "transporte": {
            "modo_principal": "Combi + Metro",
            "descripcion": "Combi Tecámac → Indios Verdes → Metro",
            "estacion_metro_cercana": "Indios Verdes (Línea 3)",
            "lineas_metro": ["Línea 3 (Verde)"],
            "tiempo_caminata_estacion_min": 5,
            "tiempo_combi_metro_min": 40,         # Combi Tecámac → Indios Verdes
            "notas": "Combis frecuentes 5:30–22:00. Ruta: Tecámac → López Portillo → Indios Verdes.",
        },
        "vias_principales": [
            "Autopista México-Pachuca",
            "Av. López Portillo",
            "Periférico Norte",
            "Insurgentes Norte",
        ],
    },
}

# ── DESTINOS PREDETERMINADOS (se muestran si no hay JSON personalizado) ────────
DESTINOS_DEFAULT = {
    "🏛️ Centro Histórico": {
        "coords": "19.4326,-99.1332",
        "nombre_completo": "Centro Histórico, Ciudad de México",
        "zona": "Centro",
        "estacion_metro_destino": "Zócalo (Línea 2)",
        # Tiempo TOTAL en transporte público: caminar + combi/mexibús + metro + caminar al destino
        "tiempo_tp_min": {"Ecatepec": 75, "Tecámac": 95},
    },
    "💼 Polanco": {
        "coords": "19.4325,-99.1958",
        "nombre_completo": "Polanco, Miguel Hidalgo, CDMX",
        "zona": "Poniente",
        "estacion_metro_destino": "Polanco (Línea 7)",
        "tiempo_tp_min": {"Ecatepec": 90, "Tecámac": 110},
    },
    "🎓 UNAM / Ciudad Universitaria": {
        "coords": "19.3326,-99.1870",
        "nombre_completo": "Ciudad Universitaria, Coyoacán, CDMX",
        "zona": "Sur",
        "estacion_metro_destino": "Copilco / Universidad (Línea 3)",
        "tiempo_tp_min": {"Ecatepec": 110, "Tecámac": 125},
    },
    "✈️ AICM (Aeropuerto)": {
        "coords": "19.4363,-99.0721",
        "nombre_completo": "Aeropuerto Internacional Ciudad de México",
        "zona": "Oriente",
        "estacion_metro_destino": "Terminal Aérea (Línea 5)",
        "tiempo_tp_min": {"Ecatepec": 65, "Tecámac": 80},
    },
    "🎭 Coyoacán": {
        "coords": "19.3500,-99.1628",
        "nombre_completo": "Coyoacán, Ciudad de México",
        "zona": "Sur",
        "estacion_metro_destino": "Viveros (Línea 3)",
        "tiempo_tp_min": {"Ecatepec": 100, "Tecámac": 120},
    },
    "🛒 Plaza Lindavista": {
        "coords": "19.4756,-99.1311",
        "nombre_completo": "Plaza Lindavista, Gustavo A. Madero, CDMX",
        "zona": "Norte",
        "estacion_metro_destino": "Deportivo 18 de Marzo (Línea 3/6)",
        "tiempo_tp_min": {"Ecatepec": 55, "Tecámac": 70},
    },
    "🏢 Roma / Insurgentes Sur": {
        "coords": "19.4100,-99.1700",
        "nombre_completo": "Colonia Roma, Cuauhtémoc, CDMX",
        "zona": "Centro Sur",
        "estacion_metro_destino": "Insurgentes (Línea 1)",
        "tiempo_tp_min": {"Ecatepec": 90, "Tecámac": 110},
    },
    "🏥 Hospital General": {
        "coords": "19.4180,-99.1495",
        "nombre_completo": "Hospital General de México, CDMX",
        "zona": "Centro Sur",
        "estacion_metro_destino": "Niños Héroes (Línea 3)",
        "tiempo_tp_min": {"Ecatepec": 85, "Tecámac": 105},
    },
}

# ── EMOJIS DISPONIBLES PARA DESTINOS PERSONALIZADOS ──────────────────────────
EMOJIS_DESTINO = [
    "📍","🏠","🏢","🏥","🎓","🛍️","🍽️","🎭","💼","🏋️",
    "💇","🏪","🎮","🌳","⛪","🏨","🏦","🚉","🎪","🛒",
]

# ── FUNCIONES DE PERSISTENCIA ──────────────────────────────────────────────────

def cargar_destinos() -> dict:
    """Carga destinos desde JSON; si no existe usa los predeterminados."""
    if os.path.exists(DESTINOS_JSON):
        try:
            with open(DESTINOS_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Primera vez: guarda los default
    guardar_destinos(DESTINOS_DEFAULT)
    return dict(DESTINOS_DEFAULT)


def guardar_destinos(destinos: dict) -> None:
    """Persiste el dict de destinos en JSON."""
    with open(DESTINOS_JSON, "w", encoding="utf-8") as f:
        json.dump(destinos, f, ensure_ascii=False, indent=2)


def agregar_destino(nombre: str, coords: str, nombre_completo: str,
                    zona: str, estacion: str,
                    tiempo_ecatepec: int, tiempo_tecamac: int) -> dict:
    """Agrega un nuevo destino y lo persiste."""
    destinos = cargar_destinos()
    destinos[nombre] = {
        "coords": coords,
        "nombre_completo": nombre_completo,
        "zona": zona,
        "estacion_metro_destino": estacion,
        "tiempo_tp_min": {"Ecatepec": tiempo_ecatepec, "Tecámac": tiempo_tecamac},
    }
    guardar_destinos(destinos)
    return destinos


def eliminar_destino(nombre: str) -> dict:
    """Elimina un destino y persiste."""
    destinos = cargar_destinos()
    destinos.pop(nombre, None)
    guardar_destinos(destinos)
    return destinos


def editar_destino(nombre_original: str, nombre_nuevo: str, datos: dict) -> dict:
    """Renombra y/o actualiza datos de un destino."""
    destinos = cargar_destinos()
    destinos.pop(nombre_original, None)
    destinos[nombre_nuevo] = datos
    guardar_destinos(destinos)
    return destinos

# ── FACTORES DE TRÁFICO / FRECUENCIA TRANSPORTE PÚBLICO ──────────────────────
# Para TP el factor afecta principalmente la frecuencia de combis/mexibús y saturación del metro

TRAFICO_HORA = {
    0: 1.0,  1: 1.0,  2: 1.0,  3: 1.0,  4: 1.05,
    5: 1.1,  6: 1.35, 7: 1.7,  8: 2.0,  # Mañana pico — metro saturado
    9: 1.7,  10: 1.4, 11: 1.2, 12: 1.2,
    13: 1.3, 14: 1.5, 15: 1.45,16: 1.5,
    17: 1.8, 18: 2.1, 19: 1.9, # Tarde pico
    20: 1.5, 21: 1.25,22: 1.1, 23: 1.0,
}

FACTOR_LLUVIA_LEVE   = 1.20   # Combis más tardados, esperas más largas
FACTOR_LLUVIA_FUERTE = 1.45   # Caos en combis y metro saturado

WAZE_BASE  = "https://www.waze.com/ul?ll={dest}&navigate=yes&from=ll.{orig}"
GMAPS_BASE = "https://www.google.com/maps/dir/{orig}/{dest}/"
# Google Maps con modo transporte público forzado
GMAPS_TP_BASE = "https://www.google.com/maps/dir/{orig}/{dest}/data=!3m1!4b1!4m2!4m1!3e3"
