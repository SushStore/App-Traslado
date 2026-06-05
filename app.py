"""
app.py — Asistente de Traslado Metropolitano
Interfaz web local con Streamlit. Ejecuta con: streamlit run app.py
"""

import streamlit as st
from datetime import datetime
import sys
import os

# Asegurar que los módulos locales sean encontrados
sys.path.insert(0, os.path.dirname(__file__))

from data import USUARIOS, DESTINOS
from clima import obtener_clima, alerta_lluvia
from trafico import estimar_tiempo, generar_urls, sugerir_hora_salida
from percances import obtener_reportes_viales, icono_severidad, generar_aviso_manual

# ── CONFIGURACIÓN DE PÁGINA ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Traslado Metro CDMX",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS PERSONALIZADO ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Fuente y fondo */
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

  .main { background: #0d1117; }
  .block-container { padding: 1.5rem 2rem 3rem 2rem; max-width: 1100px; }

  /* Tarjetas de clima */
  .clima-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: .5rem;
  }
  .clima-card.lluvia-fuerte { border-color: #f85149; background: #1a0d0d; }
  .clima-card.lluvia-leve   { border-color: #d29922; background: #191509; }
  .clima-card.despejado     { border-color: #238636; background: #0d1a12; }

  /* Temperatura grande */
  .temp-big { font-family: 'IBM Plex Mono', monospace; font-size: 2.4rem;
               font-weight: 700; line-height: 1; }
  .temp-label { font-size: .75rem; color: #8b949e; text-transform: uppercase;
                letter-spacing: .08em; }

  /* Botones de navegación */
  .nav-btn {
    display: inline-block;
    padding: .5rem 1.2rem;
    border-radius: 6px;
    font-weight: 600;
    font-size: .85rem;
    text-decoration: none;
    margin-right: .5rem;
    margin-bottom: .4rem;
  }
  .btn-gmaps { background: #1a73e8; color: white; }
  .btn-waze  { background: #33ccff; color: #0d1117; }

  /* Tiempo estimado */
  .tiempo-big {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 3rem; font-weight: 700; color: #58a6ff;
    line-height: 1;
  }
  .tiempo-rango { font-size: .85rem; color: #8b949e; font-family: 'IBM Plex Mono'; }

  /* Reporte vial */
  .reporte { border-left: 3px solid #30363d; padding: .4rem .8rem;
             margin-bottom: .4rem; font-size: .85rem; background: #161b22;
             border-radius: 0 6px 6px 0; }
  .reporte.sev-3 { border-color: #f85149; }
  .reporte.sev-2 { border-color: #d29922; }
  .reporte.sev-1 { border-color: #388bfd; }

  /* Header */
  .app-header { border-bottom: 1px solid #30363d; padding-bottom: 1rem; margin-bottom: 1.5rem; }
  .app-title { font-size: 1.6rem; font-weight: 700; color: #e6edf3; margin: 0; }
  .app-subtitle { font-size: .85rem; color: #8b949e; margin: 0; }

  /* Hora actual */
  .hora-badge {
    display: inline-block;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: .25rem .8rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: .8rem;
    color: #8b949e;
  }
  /* Seccion headers */
  .sec-header {
    font-size: .7rem; text-transform: uppercase; letter-spacing: .12em;
    color: #6e7681; font-weight: 600; margin: 1rem 0 .5rem;
    border-bottom: 1px solid #21262d; padding-bottom: .25rem;
  }
  /* Pronostico horas */
  .hora-item { display: inline-block; text-align: center; padding: .3rem .5rem;
               font-size: .75rem; margin-right: 4px; margin-bottom: 4px;
               background: #21262d; border-radius: 6px; min-width: 55px; }
  .hora-item.lluvia { background: #1a1a2e; }
  .hora-item.fuerte { background: #1a0a0a; }
  /* Factor pill */
  .factor-pill { display: inline-block; font-size: .75rem; background: #21262d;
                 border-radius: 4px; padding: 2px 7px; margin: 2px;
                 font-family: 'IBM Plex Mono'; color: #c9d1d9; }
  /* Mejor salida */
  .salida-opt { background: #0d1f36; border: 1px solid #1f6feb; border-radius: 8px;
                padding: .6rem .9rem; margin-bottom: .4rem; }
  .salida-best { background: #0a2d14; border-color: #238636; }
</style>
""", unsafe_allow_html=True)


# ── CACHÉ LIGERO DE CLIMA (5 minutos) ─────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def _clima_cached(ciudad: str):
    return obtener_clima(ciudad)

@st.cache_data(ttl=120, show_spinner=False)
def _viales_cached(vias_key: str, vias_list: list):
    return obtener_reportes_viales(vias_list)


# ── HEADER ────────────────────────────────────────────────────────────────────
ahora = datetime.now()
col_titulo, col_hora = st.columns([5, 1])
with col_titulo:
    st.markdown(
        '<div class="app-header">'
        '<p class="app-title">🚇 Asistente de Traslado Metropolitano</p>'
        '<p class="app-subtitle">CDMX · Estado de México — Ecatepec / Tecámac</p>'
        '</div>',
        unsafe_allow_html=True
    )
with col_hora:
    st.markdown(f'<div style="text-align:right;padding-top:1rem">'
                f'<span class="hora-badge">🕐 {ahora.strftime("%H:%M")} · '
                f'{["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"][ahora.weekday()]} '
                f'{ahora.day}/{ahora.month}</span></div>',
                unsafe_allow_html=True)

# ── SELECCIÓN PRINCIPAL ────────────────────────────────────────────────────────
col_usr, col_dest = st.columns([1, 1])

with col_usr:
    st.markdown('<p class="sec-header">¿Quién viaja?</p>', unsafe_allow_html=True)
    usuario_key = st.radio(
        "Usuario",
        list(USUARIOS.keys()),
        label_visibility="collapsed",
        horizontal=False,
    )

with col_dest:
    st.markdown('<p class="sec-header">¿A dónde vas?</p>', unsafe_allow_html=True)
    destino_key = st.selectbox(
        "Destino",
        list(DESTINOS.keys()),
        label_visibility="collapsed",
    )

usuario  = USUARIOS[usuario_key]
destino  = DESTINOS[destino_key]

# Ciudad de origen abreviada para los tiempos base
origen_abrev = "Ecatepec" if "Ecatepec" in usuario_key else "Tecámac"

st.markdown("---")

# ── TRES COLUMNAS: CLIMA ORIGEN / TIEMPO+TRÁFICO / CLIMA DESTINO ─────────────
col_clim1, col_centro, col_clim2 = st.columns([2, 2.5, 2])

# ── CLIMA ORIGEN ──────────────────────────────────────────────────────────────
with col_clim1:
    st.markdown(f'<p class="sec-header">☁️ Clima en {usuario["ciudad_clima"]}</p>',
                unsafe_allow_html=True)

    with st.spinner("Consultando clima..."):
        clima_orig = _clima_cached(usuario["ciudad_wttr"])

    if clima_orig["error"]:
        st.warning(clima_orig["error"])
    else:
        nivel = clima_orig["lluvia_nivel"]
        clase = {"fuerte": "lluvia-fuerte", "leve": "lluvia-leve"}.get(nivel, "despejado")
        alerta = alerta_lluvia(nivel)

        st.markdown(
            f'<div class="clima-card {clase}">'
            f'<span class="temp-big">{clima_orig["icono"]} {clima_orig["temp_c"]}°C</span><br>'
            f'<span class="temp-label">{clima_orig["descripcion"]}</span><br><br>'
            f'💧 Humedad: <b>{clima_orig["humedad"]}%</b> &nbsp;'
            f'💨 Viento: <b>{clima_orig["viento_kmh"]} km/h</b><br>'
            f'🌧️ Lluvia acum. hoy: <b>{clima_orig["lluvia_mm"]} mm</b>'
            f'</div>',
            unsafe_allow_html=True
        )
        if alerta:
            st.error(alerta)

        # Mini pronóstico por horas
        st.markdown('<p class="sec-header">Pronóstico hoy (cada 3h)</p>',
                    unsafe_allow_html=True)
        html_horas = ""
        for h in clima_orig["pronostico_horas"]:
            extra = "fuerte" if h["mm"] > 5 else ("lluvia" if h["mm"] > 0 else "")
            html_horas += (
                f'<div class="hora-item {extra}">'
                f'{h["hora"]}<br>{h["icono"]}<br><b>{h["temp"]}°</b><br>'
                f'{"💧" if h["mm"] > 0 else ""}{h["mm"] if h["mm"] > 0 else ""}'
                f'</div>'
            )
        st.markdown(html_horas, unsafe_allow_html=True)


# ── TIEMPO ESTIMADO Y NAVEGACIÓN ──────────────────────────────────────────────
with col_centro:
    st.markdown('<p class="sec-header">⏱️ Tiempo estimado de viaje</p>',
                unsafe_allow_html=True)

    # Nivel de lluvia (usar el peor entre origen y destino, se calcula abajo)
    nivel_lluvia_orig = clima_orig.get("lluvia_nivel", "ninguna") if not clima_orig.get("error") else "ninguna"

    tiempo_base = destino["tiempo_base_min"].get(origen_abrev, 60)

    # Nivel de lluvia del destino se calcula después; usar origen por ahora
    est = estimar_tiempo(tiempo_base, origen_abrev, nivel_lluvia_orig, ahora.hour)

    st.markdown(
        f'<div style="text-align:center;padding:1rem 0">'
        f'<div class="tiempo-big">{est["minutos"]} min</div>'
        f'<div class="tiempo-rango">Rango probable: {est["rango_min"]}–{est["rango_max"]} min</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('<p class="sec-header">Factores aplicados</p>', unsafe_allow_html=True)
    pills = "".join(f'<span class="factor-pill">{f}</span>' for f in est["factores_aplicados"])
    st.markdown(pills, unsafe_allow_html=True)

    # Sugerencia de hora de salida
    st.markdown('<p class="sec-header">🕐 Mejores horas de salida (próximas 8h)</p>',
                unsafe_allow_html=True)
    sugerencias = sugerir_hora_salida(tiempo_base, nivel_lluvia_orig)
    for i, s in enumerate(sugerencias):
        clase_s = "salida-best" if i == 0 else ""
        medal   = ["🥇", "🥈", "🥉"][i]
        st.markdown(
            f'<div class="salida-opt {clase_s}">'
            f'{medal} <b>{s["hora"]}</b> → <b>{s["minutos"]} min</b> &nbsp;'
            f'<span style="font-size:.8rem;color:#8b949e">{s["label"]}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Botones de navegación
    st.markdown('<p class="sec-header">🗺️ Abrir navegación en tiempo real</p>',
                unsafe_allow_html=True)
    urls = generar_urls(
        usuario["origen_coords"],
        destino["coords"],
        destino["nombre_completo"],
    )
    st.markdown(
        f'<a class="nav-btn btn-gmaps" href="{urls["google_maps"]}" target="_blank">'
        f'🗺️ Google Maps</a>'
        f'<a class="nav-btn btn-waze" href="{urls["waze"]}" target="_blank">'
        f'🔵 Waze</a>',
        unsafe_allow_html=True
    )
    st.caption(
        f"Origen: {usuario['origen_nombre']}  →  Destino: {destino['nombre_completo']}"
    )


# ── CLIMA DESTINO ─────────────────────────────────────────────────────────────
with col_clim2:
    # Inferir ciudad wttr del destino (por zona)
    zona = destino.get("zona", "Centro")
    ciudad_dest_map = {
        "Centro": "Ciudad+de+Mexico",
        "Centro Sur": "Ciudad+de+Mexico",
        "Poniente": "Ciudad+de+Mexico",
        "Norte": "Gustavo+A.+Madero+CDMX",
        "Sur": "Coyoacan+CDMX",
        "Oriente": "Iztacalco+CDMX",
    }
    ciudad_dest_wttr = ciudad_dest_map.get(zona, "Ciudad+de+Mexico")

    st.markdown(f'<p class="sec-header">☁️ Clima en destino ({zona})</p>',
                unsafe_allow_html=True)

    with st.spinner("Consultando clima destino..."):
        clima_dest = _clima_cached(ciudad_dest_wttr)

    if clima_dest["error"]:
        st.warning(clima_dest["error"])
    else:
        nivel_dest = clima_dest["lluvia_nivel"]
        clase_d = {"fuerte": "lluvia-fuerte", "leve": "lluvia-leve"}.get(nivel_dest, "despejado")
        alerta_d = alerta_lluvia(nivel_dest)

        st.markdown(
            f'<div class="clima-card {clase_d}">'
            f'<span class="temp-big">{clima_dest["icono"]} {clima_dest["temp_c"]}°C</span><br>'
            f'<span class="temp-label">{clima_dest["descripcion"]}</span><br><br>'
            f'💧 Humedad: <b>{clima_dest["humedad"]}%</b> &nbsp;'
            f'💨 Viento: <b>{clima_dest["viento_kmh"]} km/h</b><br>'
            f'🌧️ Lluvia acum. hoy: <b>{clima_dest["lluvia_mm"]} mm</b>'
            f'</div>',
            unsafe_allow_html=True
        )
        if alerta_d:
            st.error(alerta_d)

        st.markdown('<p class="sec-header">Pronóstico hoy (cada 3h)</p>',
                    unsafe_allow_html=True)
        html_horas_d = ""
        for h in clima_dest["pronostico_horas"]:
            extra = "fuerte" if h["mm"] > 5 else ("lluvia" if h["mm"] > 0 else "")
            html_horas_d += (
                f'<div class="hora-item {extra}">'
                f'{h["hora"]}<br>{h["icono"]}<br><b>{h["temp"]}°</b><br>'
                f'{"💧" if h["mm"] > 0 else ""}{h["mm"] if h["mm"] > 0 else ""}'
                f'</div>'
            )
        st.markdown(html_horas_d, unsafe_allow_html=True)


# ── REPORTES VIALES ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="sec-header">🚦 Reportes viales — Vías principales</p>',
            unsafe_allow_html=True)

col_rep, col_vias = st.columns([3, 1])

with col_rep:
    vias = usuario["vias_principales"]
    vias_key = usuario_key  # cache key

    with st.spinner("Buscando reportes viales..."):
        reportes = _viales_cached(vias_key, vias)

    if reportes.get("error"):
        st.info(generar_aviso_manual(vias))
        st.caption("💡 Los reportes RSS no estuvieron disponibles. Usa Waze o Google Maps para condiciones en vivo.")
    else:
        st.caption(f"Fuente: {reportes['fuente_usada']} · Actualizado: {reportes['ultima_actualizacion']}")
        if not reportes["reportes"]:
            st.success("✅ Sin incidentes graves reportados en tus vías principales.")
        for r in reportes["reportes"]:
            sev = r["severidad"]
            st.markdown(
                f'<div class="reporte sev-{sev}">'
                f'{icono_severidad(sev)} {r["texto"]}'
                f'<span style="color:#6e7681;float:right;font-size:.75rem">{r["fecha"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

with col_vias:
    st.markdown('<p class="sec-header">Vías monitoreadas</p>', unsafe_allow_html=True)
    for v in vias:
        st.markdown(f"• {v}")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#6e7681;font-size:.75rem">'
    'Clima: <a href="https://wttr.in" style="color:#388bfd">wttr.in</a> (sin API key) · '
    'Tráfico en vivo: Google Maps / Waze · '
    'Actualización automática: clima cada 5 min, viales cada 2 min<br>'
    'Herramienta 100% local · Sin datos enviados a terceros'
    '</div>',
    unsafe_allow_html=True
)

# ── BOTÓN DE REFRESCO MANUAL ──────────────────────────────────────────────────
if st.button("🔄 Actualizar todo ahora"):
    st.cache_data.clear()
    st.rerun()
