# 🚇 Asistente de Traslado Metropolitano CDMX

Herramienta local y gratuita para planear viajes desde Ecatepec y Tecámac hacia la CDMX.
**Sin APIs de pago. Sin registro. Sin tokens.**

---

## 🗂️ Estructura del proyecto

```
traslado_metro/
├── app.py          ← Interfaz web Streamlit (ejecuta esto)
├── data.py         ← Perfiles, destinos, factores de tráfico (editable)
├── clima.py        ← Scraping de clima con wttr.in
├── trafico.py      ← Estimación de tiempos y URLs de navegación
├── percances.py    ← Raspado de reportes viales RSS
└── requirements.txt
```

---

## ⚡ Instalación (una sola vez)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la app
streamlit run app.py
```

La app abrirá automáticamente en tu navegador en `http://localhost:8501`

---

## 🔧 Personalización

### Agregar destinos frecuentes
Edita el archivo `data.py`, sección `DESTINOS`:

```python
"🏢 Mi Trabajo": {
    "coords": "19.XXXX,-99.XXXX",          # Coordenadas exactas (busca en Google Maps)
    "nombre_completo": "Nombre completo, CDMX",
    "zona": "Centro",                        # Norte / Sur / Poniente / Oriente / Centro
    "tiempo_base_min": {"Ecatepec": 50, "Tecámac": 65},  # Minutos sin tráfico
},
```

### Obtener coordenadas de un lugar
1. Abre Google Maps
2. Haz clic derecho en el lugar
3. El primer dato del menú son las coordenadas (cópialas)

### Ajustar factores de tráfico
En `data.py`, modifica `TRAFICO_HORA` según tu experiencia real en esas rutas.

---

## 📡 Fuentes de datos (todas gratuitas)

| Dato | Fuente | Método |
|------|--------|--------|
| Clima | [wttr.in](https://wttr.in) | JSON público, sin key |
| Tráfico en vivo | Google Maps / Waze | URLs pre-configuradas |
| Reportes viales | OVIAL CDMX / SSC RSS | Scraping RSS público |
| Estimación de tiempo | Cálculo local | Factores por hora + clima |

---

## 💡 Funcionalidades

- **Perfiles**: cambia entre "Tú (Ecatepec)" y "Ella (Tecámac)" con un clic
- **Clima**: temperatura, humedad, viento y pronóstico cada 3 horas para origen y destino
- **Alertas de lluvia**: detecta lluvia leve/fuerte y ajusta el tiempo estimado
- **Tiempo de viaje**: calculado con factor de hora del día + clima
- **Mejores horas de salida**: compara las próximas 8 horas y recomienda las 3 mejores
- **Navegación**: botones de Google Maps y Waze con ruta exacta pre-cargada
- **Reportes viales**: intenta obtener incidentes en tiempo real de RSS públicos
- **Caché inteligente**: clima se cachea 5 min, reportes 2 min (conexión eficiente)

---

## 🔄 Actualización automática

La app usa caché de Streamlit: el clima se refresca cada 5 minutos automáticamente.
Usa el botón **"🔄 Actualizar todo ahora"** para forzar una actualización inmediata.

---

## 📱 Acceso desde el celular (misma red WiFi)

```bash
streamlit run app.py --server.address 0.0.0.0
```
Luego entra desde el celular a: `http://[IP-de-tu-PC]:8501`
