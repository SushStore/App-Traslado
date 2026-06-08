"""
app.py — Asistente de Traslado Metropolitano (Transporte Público)
Ejecutar: python -m streamlit run app.py
"""

import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from data import (USUARIOS, cargar_destinos, guardar_destinos,
                  agregar_destino, eliminar_destino, editar_destino,
                  EMOJIS_DESTINO)
from clima import obtener_clima, alerta_lluvia
from trafico import estimar_tiempo, generar_urls, sugerir_hora_salida
from percances import obtener_reportes_viales, icono_severidad, generar_aviso_manual

# ── CONFIG ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Traslado Metro CDMX",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;}
.main{background:#0d1117;}
.block-container{padding:1.2rem 1.8rem 3rem;max-width:1150px;}

.clima-card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:.9rem 1.1rem;margin-bottom:.5rem;}
.clima-card.lluvia-fuerte{border-color:#f85149;background:#1a0d0d;}
.clima-card.lluvia-leve{border-color:#d29922;background:#191509;}
.clima-card.despejado{border-color:#238636;background:#0d1a12;}
.temp-big{font-family:'IBM Plex Mono',monospace;font-size:2.2rem;font-weight:700;line-height:1;}
.temp-label{font-size:.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:.07em;}

.tiempo-big{font-family:'IBM Plex Mono',monospace;font-size:2.8rem;font-weight:700;color:#58a6ff;line-height:1;}
.tiempo-rango{font-size:.8rem;color:#8b949e;font-family:'IBM Plex Mono';}

.desglose-row{display:flex;align-items:center;gap:6px;margin:3px 0;font-size:.82rem;}
.desglose-time{font-family:'IBM Plex Mono';font-weight:600;color:#e6edf3;min-width:32px;}
.desglose-bar{height:8px;border-radius:4px;display:inline-block;}

.tp-badge{display:inline-block;background:#1c2d3a;border:1px solid #1f6feb;
          color:#58a6ff;border-radius:20px;padding:2px 10px;font-size:.75rem;
          font-weight:600;margin:2px;}

.nav-btn{display:inline-block;padding:.45rem 1rem;border-radius:6px;
         font-weight:600;font-size:.82rem;text-decoration:none;
         margin-right:.4rem;margin-bottom:.4rem;}
.btn-tp{background:#1a73e8;color:white;}
.btn-waze{background:#33ccff;color:#0d1117;}
.btn-maps{background:#21262d;color:#c9d1d9;border:1px solid #30363d;}

.reporte{border-left:3px solid #30363d;padding:.4rem .8rem;margin-bottom:.35rem;
         font-size:.82rem;background:#161b22;border-radius:0 6px 6px 0;}
.reporte.sev-3{border-color:#f85149;}
.reporte.sev-2{border-color:#d29922;}
.reporte.sev-1{border-color:#388bfd;}

.sec-header{font-size:.68rem;text-transform:uppercase;letter-spacing:.12em;
            color:#6e7681;font-weight:600;margin:1rem 0 .4rem;
            border-bottom:1px solid #21262d;padding-bottom:.2rem;}
.hora-item{display:inline-block;text-align:center;padding:.3rem .45rem;
           font-size:.72rem;margin-right:3px;margin-bottom:3px;
           background:#21262d;border-radius:6px;min-width:50px;}
.hora-item.lluvia{background:#1a1a2e;}
.hora-item.fuerte{background:#1a0a0a;}
.factor-pill{display:inline-block;font-size:.73rem;background:#21262d;
             border-radius:4px;padding:2px 7px;margin:2px;
             font-family:'IBM Plex Mono';color:#c9d1d9;}
.salida-opt{background:#0d1f36;border:1px solid #1f6feb;border-radius:8px;
            padding:.5rem .85rem;margin-bottom:.35rem;}
.salida-best{background:#0a2d14;border-color:#238636;}
.hora-badge{display:inline-block;background:#21262d;border:1px solid #30363d;
            border-radius:20px;padding:.22rem .75rem;font-family:'IBM Plex Mono';
            font-size:.78rem;color:#8b949e;}

/* Gestión de destinos */
.destino-card{background:#161b22;border:1px solid #30363d;border-radius:8px;
              padding:.7rem .9rem;margin-bottom:.4rem;display:flex;
              align-items:center;justify-content:space-between;}
.destino-nombre{font-weight:600;color:#e6edf3;font-size:.9rem;}
.destino-meta{font-size:.75rem;color:#8b949e;}
</style>
""", unsafe_allow_html=True)

# ── CACHÉ ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def _clima(ciudad):
    return obtener_clima(ciudad)

@st.cache_data(ttl=120, show_spinner=False)
def _viales(key, vias):
    return obtener_reportes_viales(vias)

# ── ESTADO DE SESIÓN ───────────────────────────────────────────────────────────
if "tab" not in st.session_state:
    st.session_state.tab = "viaje"
if "destinos" not in st.session_state:
    st.session_state.destinos = cargar_destinos()
if "editando" not in st.session_state:
    st.session_state.editando = None

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚇 Traslado Metro")
    ahora = datetime.now()
    st.markdown(
        f'<span class="hora-badge">🕐 {ahora.strftime("%H:%M")} · '
        f'{["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"][ahora.weekday()]} '
        f'{ahora.day}/{ahora.month}</span>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    vista = st.radio(
        "Vista",
        ["🗺️ Planear viaje", "📍 Mis destinos"],
        label_visibility="collapsed",
    )
    st.session_state.tab = "viaje" if "Planear" in vista else "destinos"

    st.markdown("---")
    st.markdown("**Transporte público**")
    for key, u in USUARIOS.items():
        tp = u["transporte"]
        st.markdown(
            f"**{key.split('(')[0].strip()}**  \n"
            f"🚌 {tp['modo_principal']}  \n"
            f"🚇 Sale en: ~{tp['tiempo_caminata_estacion_min']} min caminando"
        )
        st.markdown("")

    st.markdown("---")
    if st.button("🔄 Actualizar datos"):
        st.cache_data.clear()
        st.rerun()
    st.caption("Clima: wttr.in · Sin APIs de pago")

# ══════════════════════════════════════════════════════════════════════════════
# VISTA: PLANEAR VIAJE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.tab == "viaje":

    st.markdown(
        '<p style="font-size:1.5rem;font-weight:700;color:#e6edf3;margin-bottom:.2rem">'
        '🚇 Asistente de Traslado Metropolitano</p>'
        '<p style="font-size:.82rem;color:#8b949e;margin-bottom:1rem">'
        'Transporte público · Ecatepec / Tecámac → CDMX</p>',
        unsafe_allow_html=True
    )

    # ── Selección usuario + destino ────────────────────────────────────────────
    col_u, col_d = st.columns([1, 1])
    with col_u:
        st.markdown('<p class="sec-header">¿Quién viaja?</p>', unsafe_allow_html=True)
        usuario_key = st.radio("usr", list(USUARIOS.keys()),
                               label_visibility="collapsed")
    with col_d:
        st.markdown('<p class="sec-header">¿A dónde vas?</p>', unsafe_allow_html=True)
        destinos_actuales = st.session_state.destinos
        destino_key = st.selectbox("dest", list(destinos_actuales.keys()),
                                   label_visibility="collapsed")

    usuario = USUARIOS[usuario_key]
    destino = destinos_actuales[destino_key]
    origen_abrev = usuario["origen_abrev"]
    tp = usuario["transporte"]

    # Badge de transporte
    st.markdown(
        f'<span class="tp-badge">🚌 {tp["modo_principal"]}</span>'
        f'<span class="tp-badge">🚇 {tp["estacion_metro_cercana"]}</span>'
        f'<span class="tp-badge">📍 {destino.get("estacion_metro_destino","—")}</span>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    # ── 3 columnas principales ─────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2.4, 2])

    # ── CLIMA ORIGEN ──────────────────────────────────────────────────────────
    with col1:
        st.markdown(f'<p class="sec-header">☁️ Clima — {usuario["ciudad_clima"]}</p>',
                    unsafe_allow_html=True)
        with st.spinner(""):
            co = _clima(usuario["ciudad_wttr"])

        if co["error"]:
            st.warning(co["error"])
            lluvia_orig = "ninguna"
        else:
            nivel = co["lluvia_nivel"]
            lluvia_orig = nivel
            clase = {"fuerte":"lluvia-fuerte","leve":"lluvia-leve"}.get(nivel,"despejado")
            st.markdown(
                f'<div class="clima-card {clase}">'
                f'<span class="temp-big">{co["icono"]} {co["temp_c"]}°C</span><br>'
                f'<span class="temp-label">{co["descripcion"]}</span><br><br>'
                f'💧 {co["humedad"]}% &nbsp;💨 {co["viento_kmh"]} km/h &nbsp;'
                f'🌧️ {co["lluvia_mm"]} mm hoy</div>',
                unsafe_allow_html=True
            )
            alerta = alerta_lluvia(nivel)
            if alerta:
                st.error(alerta)

            st.markdown('<p class="sec-header">Pronóstico cada 3h</p>',
                        unsafe_allow_html=True)
            html_h = ""
            for h in co["pronostico_horas"]:
                ex = "fuerte" if h["mm"]>5 else ("lluvia" if h["mm"]>0 else "")
                html_h += (f'<div class="hora-item {ex}">{h["hora"]}<br>'
                           f'{h["icono"]}<br><b>{h["temp"]}°</b>'
                           + (f'<br>💧{h["mm"]}' if h["mm"]>0 else "")
                           + '</div>')
            st.markdown(html_h, unsafe_allow_html=True)

    # ── TIEMPO + NAVEGACIÓN ────────────────────────────────────────────────────
    with col2:
        st.markdown('<p class="sec-header">⏱️ Tiempo estimado (transporte público)</p>',
                    unsafe_allow_html=True)

        lluvia_nivel = lluvia_orig if "co" in dir() and not co.get("error") else "ninguna"
        tiempo_base  = destino["tiempo_tp_min"].get(origen_abrev, 80)
        est = estimar_tiempo(tiempo_base, origen_abrev, lluvia_nivel,
                             ahora.hour, usuario)

        st.markdown(
            f'<div style="text-align:center;padding:.8rem 0">'
            f'<div class="tiempo-big">{est["minutos"]} min</div>'
            f'<div class="tiempo-rango">Rango: {est["rango_min"]}–{est["rango_max"]} min</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Desglose por etapas
        if est["desglose"]:
            d = est["desglose"]
            total = d["caminar_origen"] + d["alimentador"] + d["metro_destino"]
            pct_cam  = max(5, int(d["caminar_origen"]/total*100))
            pct_ali  = max(5, int(d["alimentador"]/total*100))
            pct_met  = max(5, 100 - pct_cam - pct_ali)

            st.markdown('<p class="sec-header">Desglose del viaje</p>',
                        unsafe_allow_html=True)
            st.markdown(
                f'<div class="desglose-row">🚶 <span class="desglose-time">{d["caminar_origen"]} min</span>'
                f'<div class="desglose-bar" style="width:{pct_cam*1.8}px;background:#4d9375"></div>'
                f'<span style="font-size:.75rem;color:#8b949e">Caminar a parada</span></div>'

                f'<div class="desglose-row">🚌 <span class="desglose-time">{d["alimentador"]} min</span>'
                f'<div class="desglose-bar" style="width:{pct_ali*1.8}px;background:#d29922"></div>'
                f'<span style="font-size:.75rem;color:#8b949e">{d["modo_alimentador"]}</span></div>'

                f'<div class="desglose-row">🚇 <span class="desglose-time">{d["metro_destino"]} min</span>'
                f'<div class="desglose-bar" style="width:{pct_met*1.8}px;background:#388bfd"></div>'
                f'<span style="font-size:.75rem;color:#8b949e">Metro + llegar al destino</span></div>',
                unsafe_allow_html=True
            )

        # Factores
        st.markdown('<p class="sec-header">Factores</p>', unsafe_allow_html=True)
        pills = "".join(f'<span class="factor-pill">{f}</span>'
                        for f in est["factores_aplicados"])
        st.markdown(pills, unsafe_allow_html=True)

        # Notas del transporte
        if tp.get("notas"):
            st.info(f"ℹ️ {tp['notas']}")

        # Mejores horas de salida
        st.markdown('<p class="sec-header">🕐 Mejores horas para salir</p>',
                    unsafe_allow_html=True)
        sugs = sugerir_hora_salida(tiempo_base, lluvia_nivel, usuario)
        for i, s in enumerate(sugs):
            clase_s = "salida-best" if i == 0 else ""
            medal = ["🥇","🥈","🥉"][i]
            delta_txt = f"+{s['delta']}h" if s['delta'] > 0 else "ahora"
            st.markdown(
                f'<div class="salida-opt {clase_s}">'
                f'{medal} <b>{s["hora"]}</b> <span style="color:#8b949e;font-size:.75rem">({delta_txt})</span>'
                f' → <b>{s["minutos"]} min</b>'
                f'<br><span style="font-size:.75rem;color:#8b949e">{s["label"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        # Botones de navegación
        st.markdown('<p class="sec-header">🗺️ Navegación</p>', unsafe_allow_html=True)
        urls = generar_urls(
            usuario["origen_coords"],
            destino["coords"],
            destino["nombre_completo"],
        )
        st.markdown(
            f'<a class="nav-btn btn-tp" href="{urls["google_maps_tp"]}" target="_blank">'
            f'🚇 Maps · Transporte Público</a><br>'
            f'<a class="nav-btn btn-maps" href="{urls["google_maps"]}" target="_blank">'
            f'🗺️ Maps · General</a>'
            f'<a class="nav-btn btn-waze" href="{urls["waze"]}" target="_blank">'
            f'🔵 Waze</a>',
            unsafe_allow_html=True
        )
        st.caption(f"{usuario['origen_nombre']} → {destino['nombre_completo']}")

    # ── CLIMA DESTINO ─────────────────────────────────────────────────────────
    with col3:
        zona_map = {
            "Centro":"Ciudad+de+Mexico","Centro Sur":"Ciudad+de+Mexico",
            "Poniente":"Ciudad+de+Mexico","Norte":"Gustavo+A.+Madero+CDMX",
            "Sur":"Coyoacan+CDMX","Oriente":"Iztacalco+CDMX",
        }
        ciudad_d = zona_map.get(destino.get("zona","Centro"), "Ciudad+de+Mexico")
        st.markdown(f'<p class="sec-header">☁️ Clima — Destino ({destino.get("zona","CDMX")})</p>',
                    unsafe_allow_html=True)
        with st.spinner(""):
            cd = _clima(ciudad_d)

        if cd["error"]:
            st.warning(cd["error"])
        else:
            nivel_d = cd["lluvia_nivel"]
            clase_d = {"fuerte":"lluvia-fuerte","leve":"lluvia-leve"}.get(nivel_d,"despejado")
            st.markdown(
                f'<div class="clima-card {clase_d}">'
                f'<span class="temp-big">{cd["icono"]} {cd["temp_c"]}°C</span><br>'
                f'<span class="temp-label">{cd["descripcion"]}</span><br><br>'
                f'💧 {cd["humedad"]}% &nbsp;💨 {cd["viento_kmh"]} km/h &nbsp;'
                f'🌧️ {cd["lluvia_mm"]} mm hoy</div>',
                unsafe_allow_html=True
            )
            if alerta_lluvia(nivel_d):
                st.error(alerta_lluvia(nivel_d))

            st.markdown('<p class="sec-header">Pronóstico cada 3h</p>',
                        unsafe_allow_html=True)
            html_hd = ""
            for h in cd["pronostico_horas"]:
                ex = "fuerte" if h["mm"]>5 else ("lluvia" if h["mm"]>0 else "")
                html_hd += (f'<div class="hora-item {ex}">{h["hora"]}<br>'
                            f'{h["icono"]}<br><b>{h["temp"]}°</b>'
                            + (f'<br>💧{h["mm"]}' if h["mm"]>0 else "")
                            + '</div>')
            st.markdown(html_hd, unsafe_allow_html=True)

    # ── REPORTES VIALES ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<p class="sec-header">🚦 Reportes viales — vías de tu ruta</p>',
                unsafe_allow_html=True)
    col_r, col_v = st.columns([3, 1])
    with col_r:
        with st.spinner(""):
            rep = _viales(usuario_key, usuario["vias_principales"])
        if rep.get("error"):
            st.info(generar_aviso_manual(usuario["vias_principales"]))
            st.caption("Usa el botón de Maps Transporte Público para rutas en tiempo real.")
        else:
            st.caption(f"Fuente: {rep['fuente_usada']} · {rep['ultima_actualizacion']}")
            if not rep["reportes"]:
                st.success("✅ Sin incidentes graves en tus vías principales.")
            for r in rep["reportes"]:
                sev = r["severidad"]
                st.markdown(
                    f'<div class="reporte sev-{sev}">{icono_severidad(sev)} {r["texto"]}'
                    f'<span style="color:#6e7681;float:right;font-size:.72rem">{r["fecha"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
    with col_v:
        st.markdown('<p class="sec-header">Vías monitoreadas</p>', unsafe_allow_html=True)
        for v in usuario["vias_principales"]:
            st.markdown(f"• {v}")


# ══════════════════════════════════════════════════════════════════════════════
# VISTA: GESTIÓN DE DESTINOS
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown(
        '<p style="font-size:1.4rem;font-weight:700;color:#e6edf3;margin-bottom:.2rem">'
        '📍 Mis destinos frecuentes</p>'
        '<p style="font-size:.82rem;color:#8b949e;margin-bottom:1rem">'
        'Agrega, edita o elimina destinos. Se guardan automáticamente.</p>',
        unsafe_allow_html=True
    )

    destinos = st.session_state.destinos

    # ── LISTA DE DESTINOS EXISTENTES ──────────────────────────────────────────
    st.markdown('<p class="sec-header">Destinos guardados</p>', unsafe_allow_html=True)

    for nombre, datos in list(destinos.items()):
        col_n, col_t1, col_t2, col_ed, col_del = st.columns([3, 1.2, 1.2, 0.7, 0.7])
        with col_n:
            st.markdown(
                f'<div class="destino-nombre">{nombre}</div>'
                f'<div class="destino-meta">'
                f'{datos.get("estacion_metro_destino","—")} · {datos.get("zona","—")}'
                f'</div>',
                unsafe_allow_html=True
            )
        with col_t1:
            t_ec = datos.get("tiempo_tp_min",{}).get("Ecatepec","?")
            st.markdown(f'<div style="font-size:.8rem;color:#8b949e">🧑 Ecatepec<br>'
                        f'<b style="color:#58a6ff">{t_ec} min</b></div>',
                        unsafe_allow_html=True)
        with col_t2:
            t_tec = datos.get("tiempo_tp_min",{}).get("Tecámac","?")
            st.markdown(f'<div style="font-size:.8rem;color:#8b949e">👩 Tecámac<br>'
                        f'<b style="color:#58a6ff">{t_tec} min</b></div>',
                        unsafe_allow_html=True)
        with col_ed:
            if st.button("✏️", key=f"ed_{nombre}", help="Editar"):
                st.session_state.editando = nombre
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{nombre}", help="Eliminar"):
                st.session_state.destinos = eliminar_destino(nombre)
                st.success(f"Eliminado: {nombre}")
                st.rerun()

        st.divider()

    # ── FORMULARIO EDITAR ─────────────────────────────────────────────────────
    if st.session_state.editando:
        nombre_ed = st.session_state.editando
        datos_ed  = destinos.get(nombre_ed, {})

        st.markdown(f'<p class="sec-header">✏️ Editando: {nombre_ed}</p>',
                    unsafe_allow_html=True)

        with st.form("form_editar"):
            col_emoji, col_nombre = st.columns([1, 4])
            with col_emoji:
                emoji_actual = nombre_ed.split()[0] if nombre_ed else "📍"
                emoji = st.selectbox("Emoji", EMOJIS_DESTINO,
                                     index=EMOJIS_DESTINO.index(emoji_actual)
                                     if emoji_actual in EMOJIS_DESTINO else 0)
            with col_nombre:
                nombre_texto = " ".join(nombre_ed.split()[1:]) if len(nombre_ed.split())>1 else nombre_ed
                nuevo_texto = st.text_input("Nombre del destino", value=nombre_texto)

            col_coords, col_zona = st.columns([2, 1])
            with col_coords:
                coords = st.text_input(
                    "Coordenadas (lat,lon)",
                    value=datos_ed.get("coords",""),
                    help="Clic derecho en Google Maps → copiar coordenadas"
                )
            with col_zona:
                zonas = ["Centro","Centro Sur","Norte","Sur","Poniente","Oriente"]
                zona_actual = datos_ed.get("zona","Centro")
                zona = st.selectbox("Zona CDMX", zonas,
                                    index=zonas.index(zona_actual) if zona_actual in zonas else 0)

            nombre_completo = st.text_input(
                "Nombre completo (para navegación)",
                value=datos_ed.get("nombre_completo","")
            )
            estacion = st.text_input(
                "Estación de metro más cercana al destino",
                value=datos_ed.get("estacion_metro_destino","")
            )

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                t_ec = st.number_input("⏱️ Tiempo desde Ecatepec (min)",
                                       min_value=10, max_value=240,
                                       value=int(datos_ed.get("tiempo_tp_min",{}).get("Ecatepec",70)))
            with col_t2:
                t_tec = st.number_input("⏱️ Tiempo desde Tecámac (min)",
                                        min_value=10, max_value=240,
                                        value=int(datos_ed.get("tiempo_tp_min",{}).get("Tecámac",85)))

            col_s, col_c = st.columns(2)
            with col_s:
                submitted = st.form_submit_button("💾 Guardar cambios", type="primary")
            with col_c:
                cancelar = st.form_submit_button("✖ Cancelar")

            if submitted:
                nuevo_nombre = f"{emoji} {nuevo_texto}".strip()
                nuevos_datos = {
                    "coords":                  coords.strip(),
                    "nombre_completo":         nombre_completo.strip() or nuevo_texto,
                    "zona":                    zona,
                    "estacion_metro_destino":  estacion.strip(),
                    "tiempo_tp_min":           {"Ecatepec": t_ec, "Tecámac": t_tec},
                }
                st.session_state.destinos = editar_destino(nombre_ed, nuevo_nombre, nuevos_datos)
                st.session_state.editando = None
                st.success(f"✅ Guardado: {nuevo_nombre}")
                st.rerun()
            if cancelar:
                st.session_state.editando = None
                st.rerun()

    # ── FORMULARIO AGREGAR NUEVO ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<p class="sec-header">➕ Agregar nuevo destino</p>',
                unsafe_allow_html=True)

    with st.expander("Abrir formulario de nuevo destino", expanded=False):
        with st.form("form_nuevo"):
            st.markdown(
                "💡 **Obtener coordenadas:** Abre Google Maps, haz clic derecho "
                "en el lugar exacto y selecciona el primer dato (ej. `19.4326, -99.1332`)"
            )
            col_em, col_nm = st.columns([1, 4])
            with col_em:
                emoji_n = st.selectbox("Emoji", EMOJIS_DESTINO, key="emoji_nuevo")
            with col_nm:
                nombre_n = st.text_input("Nombre del lugar", placeholder="Ej. Mi trabajo")

            col_c1, col_z1 = st.columns([2,1])
            with col_c1:
                coords_n = st.text_input("Coordenadas", placeholder="19.4326,-99.1332")
            with col_z1:
                zonas = ["Centro","Centro Sur","Norte","Sur","Poniente","Oriente"]
                zona_n = st.selectbox("Zona", zonas, key="zona_nuevo")

            nombre_c_n = st.text_input("Nombre completo",
                                       placeholder="Ej. Torre Mayor, Paseo de la Reforma, CDMX")
            estacion_n = st.text_input("Estación de metro más cercana",
                                       placeholder="Ej. Auditorio (Línea 7)")

            col_t1n, col_t2n = st.columns(2)
            with col_t1n:
                t_ec_n  = st.number_input("⏱️ Min desde Ecatepec",
                                          min_value=10, max_value=240, value=70)
            with col_t2n:
                t_tec_n = st.number_input("⏱️ Min desde Tecámac",
                                          min_value=10, max_value=240, value=85)

            ok = st.form_submit_button("✅ Agregar destino", type="primary")
            if ok:
                if not nombre_n or not coords_n:
                    st.error("El nombre y las coordenadas son obligatorios.")
                else:
                    nombre_final = f"{emoji_n} {nombre_n}".strip()
                    st.session_state.destinos = agregar_destino(
                        nombre_final, coords_n.strip(),
                        nombre_c_n.strip() or nombre_n,
                        zona_n, estacion_n.strip(),
                        t_ec_n, t_tec_n
                    )
                    st.success(f"✅ Agregado: {nombre_final}")
                    st.rerun()

    # ── RESTAURAR DEFAULTS ─────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("⚠️ Restaurar destinos predeterminados"):
        st.warning("Esto reemplazará TODOS tus destinos personalizados con los de fábrica.")
        if st.button("🔁 Restaurar destinos por defecto", type="secondary"):
            from data import DESTINOS_DEFAULT
            guardar_destinos(DESTINOS_DEFAULT)
            st.session_state.destinos = dict(DESTINOS_DEFAULT)
            st.success("Destinos restaurados.")
            st.rerun()

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#6e7681;font-size:.72rem">'
    'Sin auto particular · Transporte público · '
    'Clima: <a href="https://wttr.in" style="color:#388bfd">wttr.in</a> (gratis, sin API key) · '
    'Destinos en <code>destinos_usuario.json</code></div>',
    unsafe_allow_html=True
)
