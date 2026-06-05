"""
data.py — Configuración central de perfiles, destinos y rutas.
Edita este archivo para personalizar tus destinos frecuentes.
"""

# ── PERFILES DE USUARIO ────────────────────────────────────────────────────────
USUARIOS = {
    "🧑 Tú (Ecatepec)": {
        "nombre": "Tú",
        "origen_nombre": "Ecatepec de Morelos, Edomex",
        "origen_coords": "19.6017,-98.9917",
        "ciudad_clima": "Ecatepec de Morelos",
        "ciudad_wttr": "Ecatepec+de+Morelos",
        "vias_principales": [
            "Autopista México-Pachuca (Arco Norte)",
            "Vía Morelos",
            "Av. Central / Insurgentes Norte",
            "Circuito Exterior Mexiquense",
        ],
    },
    "👩 Ella (Tecámac)": {
        "nombre": "Ella",
        "origen_nombre": "Tecámac, Edomex",
        "origen_coords": "19.7167,-98.9667",
        "ciudad_clima": "Tecámac",
        "ciudad_wttr": "Tecamac",
        "vias_principales": [
            "Autopista México-Pachuca",
            "Av. López Portillo",
            "Circuito Exterior Mexiquense",
            "Periférico Norte",
        ],
    },
}

# ── DESTINOS FRECUENTES EN CDMX ───────────────────────────────────────────────
DESTINOS = {
    "🏛️ Centro Histórico": {
        "coords": "19.4326,-99.1332",
        "nombre_completo": "Centro Histórico, Ciudad de México",
        "zona": "Centro",
        "tiempo_base_min": {"Ecatepec": 55, "Tecámac": 70},   # minutos sin tráfico
    },
    "💼 Polanco": {
        "coords": "19.4325,-99.1958",
        "nombre_completo": "Polanco, Miguel Hidalgo, CDMX",
        "zona": "Poniente",
        "tiempo_base_min": {"Ecatepec": 65, "Tecámac": 80},
    },
    "🎓 UNAM / Ciudad Universitaria": {
        "coords": "19.3326,-99.1870",
        "nombre_completo": "Ciudad Universitaria, Coyoacán, CDMX",
        "zona": "Sur",
        "tiempo_base_min": {"Ecatepec": 80, "Tecámac": 95},
    },
    "🛍️ Santa Fe": {
        "coords": "19.3588,-99.2603",
        "nombre_completo": "Santa Fe, Cuajimalpa, CDMX",
        "zona": "Poniente",
        "tiempo_base_min": {"Ecatepec": 90, "Tecámac": 105},
    },
    "🏥 Hospital General (Dr. Balmis)": {
        "coords": "19.4180,-99.1495",
        "nombre_completo": "Hospital General de México, CDMX",
        "zona": "Centro Sur",
        "tiempo_base_min": {"Ecatepec": 60, "Tecámac": 75},
    },
    "✈️ AICM (Aeropuerto)": {
        "coords": "19.4363,-99.0721",
        "nombre_completo": "Aeropuerto Internacional Ciudad de México",
        "zona": "Oriente",
        "tiempo_base_min": {"Ecatepec": 40, "Tecámac": 55},
    },
    "🎭 Coyoacán": {
        "coords": "19.3500,-99.1628",
        "nombre_completo": "Coyoacán, Ciudad de México",
        "zona": "Sur",
        "tiempo_base_min": {"Ecatepec": 75, "Tecámac": 90},
    },
    "🛒 Plaza Lindavista": {
        "coords": "19.4756,-99.1311",
        "nombre_completo": "Plaza Lindavista, Gustavo A. Madero, CDMX",
        "zona": "Norte",
        "tiempo_base_min": {"Ecatepec": 45, "Tecámac": 60},
    },
    "🏢 Insurgentes Sur / Roma": {
        "coords": "19.4100,-99.1700",
        "nombre_completo": "Colonia Roma, Cuauhtémoc, CDMX",
        "zona": "Centro Sur",
        "tiempo_base_min": {"Ecatepec": 65, "Tecámac": 80},
    },
    "🌳 Xochimilco": {
        "coords": "19.2570,-99.1035",
        "nombre_completo": "Xochimilco, Ciudad de México",
        "zona": "Sur",
        "tiempo_base_min": {"Ecatepec": 90, "Tecámac": 105},
    },
}

# ── MULTIPLICADORES DE TRÁFICO POR HORA ───────────────────────────────────────
# Factor que multiplica el tiempo base según la hora del día
TRAFICO_HORA = {
    0: 1.0,   1: 1.0,   2: 1.0,   3: 1.0,   4: 1.0,
    5: 1.1,   6: 1.4,   7: 1.9,   8: 2.3,   # Mañana pico
    9: 1.8,   10: 1.5,  11: 1.3,  12: 1.3,
    13: 1.5,  14: 1.7,  15: 1.6,  16: 1.6,
    17: 2.0,  18: 2.4,  19: 2.2,  # Tarde pico
    20: 1.7,  21: 1.4,  22: 1.2,  23: 1.0,
}

# Factor adicional por lluvia
FACTOR_LLUVIA_LEVE = 1.25
FACTOR_LLUVIA_FUERTE = 1.55

# ── URLs BASE PARA TRÁFICO EN TIEMPO REAL ─────────────────────────────────────
WAZE_BASE = "https://www.waze.com/ul?ll={dest}&navigate=yes&from=ll.{orig}"
GMAPS_BASE = "https://www.google.com/maps/dir/{orig}/{dest}/"
