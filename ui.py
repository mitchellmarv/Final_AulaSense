"""Estilos (tema espacial) y componentes de telemetría compartidos."""
import streamlit as st

from mqtt_utils import esp32_en_linea, leer_estado

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Michroma&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg: #05070D;
    --panel: rgba(11, 18, 32, 0.78);
    --steel: #141E30;
    --line: rgba(170, 200, 255, 0.18);
    --text: #EAF1FF;
    --muted: #93A4C0;
    --blue: #4DA3FF;
    --ice: #BFD9FF;
    --alert: #FF6B6B;
}

/* Fondo: cielo profundo, resplandor azul y estrellas (solo CSS) */
.stApp {
    background-color: var(--bg);
    background-image:
        radial-gradient(900px 600px at 92% -10%, rgba(77,163,255,0.22), transparent 60%),
        radial-gradient(800px 500px at -10% 112%, rgba(150,170,200,0.14), transparent 60%),
        radial-gradient(1px 1px at 20px 30px, #fff, transparent),
        radial-gradient(1.5px 1.5px at 90px 120px, #cfe3ff, transparent),
        radial-gradient(1px 1px at 160px 60px, #fff, transparent),
        radial-gradient(2px 2px at 210px 170px, #fff, transparent),
        radial-gradient(1px 1px at 60px 200px, #9fc4ff, transparent),
        radial-gradient(1px 1px at 250px 20px, #fff, transparent);
    background-size: auto, auto, 230px 230px, 310px 310px, 270px 270px, 410px 410px, 350px 350px, 290px 290px;
    background-attachment: fixed;
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 900px; padding-top: 2.5rem; }

/* Tipografía */
h1, h2, h3 { font-family: 'Michroma', sans-serif !important; letter-spacing: 0.04em; }
h1 {
    font-size: 1.9rem !important;
    background: linear-gradient(90deg, #FFFFFF 0%, var(--ice) 55%, var(--blue) 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
}
h3 { font-size: 0.82rem !important; color: var(--ice) !important; text-transform: uppercase; letter-spacing: 0.18em; }
p, label, li, span { font-family: 'Inter', sans-serif; }
.sub { color: var(--muted); font-size: 0.95rem; margin: -0.3rem 0 1.4rem; }
.brand {
    font-family: 'Michroma', sans-serif; letter-spacing: 0.3em; font-size: 0.8rem;
    color: var(--ice); padding: 0.4rem 0 0.8rem; border-bottom: 1px solid var(--line); margin-bottom: 0.8rem;
}

/* Barra lateral */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060A14 0%, #0A1322 100%);
    border-right: 1px solid var(--line);
}

/* Paneles de cristal */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--panel);
    border: 1px solid var(--line) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(6px);
}

/* Métricas */
[data-testid="stMetric"] {
    background: rgba(20, 30, 48, 0.7);
    border: 1px solid var(--line);
    border-left: 3px solid var(--blue);
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
}
[data-testid="stMetricLabel"] p { color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.12em; }
[data-testid="stMetricValue"] { font-family: 'Michroma', sans-serif; font-size: 1.2rem; color: var(--text); }

/* Botones */
.stButton button, [data-testid="stPageLink"] a {
    width: 100%;
    background: transparent;
    color: var(--ice);
    border: 1px solid rgba(191, 217, 255, 0.45);
    border-radius: 8px;
    font-family: 'Inter', sans-serif; font-weight: 500;
    transition: background .15s ease, color .15s ease, box-shadow .15s ease;
}
.stButton button:hover, [data-testid="stPageLink"] a:hover {
    background: var(--blue); color: #04101F; border-color: var(--blue);
    box-shadow: 0 0 18px rgba(77, 163, 255, 0.45);
}

/* Entradas, cámara y alertas */
.stNumberInput input, .stTextInput input {
    background: #0B1220 !important; color: var(--text) !important;
    border: 1px solid var(--line) !important; border-radius: 8px !important;
}
[data-testid="stCameraInput"] { border: 1px solid var(--line); border-radius: 12px; padding: 6px; background: rgba(11,18,32,0.6); }
[data-testid="stImage"] img { border-radius: 10px; border: 1px solid var(--line); max-width: 100%; }
[data-testid="stExpander"] { background: rgba(11,18,32,0.55); border: 1px solid var(--line); border-radius: 12px; }
[data-testid="stAlert"] { border-radius: 10px; border: 1px solid var(--line); }

/* Componente de voz (iframe): fondo transparente */
iframe { color-scheme: normal; background: transparent; }

/* Chips de estado */
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 0.2rem 0 0.9rem; }
.chip {
    display: inline-flex; align-items: center; gap: 7px;
    padding: 4px 12px; border-radius: 999px;
    border: 1px solid var(--line); background: rgba(20,30,48,0.7);
    color: var(--muted); font-size: 0.78rem;
}
.chip .dot { width: 8px; height: 8px; border-radius: 50%; background: #5B6A85; }
.chip.on { color: var(--text); border-color: rgba(77,163,255,0.6); }
.chip.on .dot { background: var(--blue); box-shadow: 0 0 8px var(--blue); animation: pulso 2s ease-in-out infinite; }
.chip.alerta { color: #FFD9D9; border-color: rgba(255,107,107,0.7); }
.chip.alerta .dot { background: var(--alert); box-shadow: 0 0 8px var(--alert); }
@keyframes pulso { 50% { opacity: 0.45; } }

::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #22385c; border-radius: 8px; }

@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
</style>
"""


def aplicar_estilos():
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(titulo, subtitulo):
    st.title(titulo)
    st.markdown(f'<p class="sub">{subtitulo}</p>', unsafe_allow_html=True)


def _chip(texto, activo=False, alerta=False):
    clase = "chip alerta" if alerta else ("chip on" if activo else "chip")
    return f'<span class="{clase}"><span class="dot"></span>{texto}</span>'


def _fmt(valor, sufijo=""):
    if valor is None:
        return "—"
    try:
        return f"{float(valor):.1f}{sufijo}"
    except (TypeError, ValueError):
        return str(valor)


@st.fragment(run_every=2)
def panel_estado():
    """Telemetría del ESP32; se actualiza sola cada 2 segundos."""
    datos, seg, broker_ok = leer_estado()
    en_linea = esp32_en_linea(seg)

    chips = [
        _chip("Broker conectado" if broker_ok else "Broker sin conexión", broker_ok),
        _chip("ESP32 en línea" if en_linea else "ESP32 sin señal", en_linea),
    ]
    st.markdown('<div class="chips">' + "".join(chips) + "</div>", unsafe_allow_html=True)

    if not datos:
        st.caption("Esperando datos del ESP32… inicia la simulación en Wokwi.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temperatura", _fmt(datos.get("temp"), " °C"))
    c2.metric("Humedad", _fmt(datos.get("hum"), " %"))
    personas, maximo = datos.get("personas"), datos.get("max")
    c3.metric("Personas", f"{personas} / {maximo}" if personas is not None and maximo is not None else "—")
    c4.metric("Modo", {"auto": "Automático", "manual": "Manual"}.get(datos.get("modo"), "—"))

    estados = [
        _chip("Luces", bool(datos.get("luces"))),
        _chip("Ventilador", bool(datos.get("ventilador"))),
        _chip("Ventana abierta", bool(datos.get("ventana"))),
        _chip("Aforo superado", alerta=True) if datos.get("alerta") else _chip("Aforo OK", True),
    ]
    st.markdown('<div class="chips">' + "".join(estados) + "</div>", unsafe_allow_html=True)


@st.fragment(run_every=3)
def estado_lateral():
    """Indicador compacto para la barra lateral."""
    datos, seg, broker_ok = leer_estado()
    en_linea = esp32_en_linea(seg)
    st.markdown(
        '<div class="chips">'
        + _chip("ESP32 en línea" if en_linea else "ESP32 sin señal", en_linea)
        + "</div>",
        unsafe_allow_html=True,
    )
    if datos.get("temp") is not None:
        st.caption(f"Temperatura del salón: {_fmt(datos.get('temp'), ' °C')}")
