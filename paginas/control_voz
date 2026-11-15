import time

import streamlit as st
from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from streamlit_bokeh_events import streamlit_bokeh_events

from comandos import interpretar
from mqtt_utils import TOPIC_CMD, enviar
from ui import encabezado, panel_estado

encabezado("Comando por voz", "Habla con el salón: luces, ventilador y ventana")

for clave, valor in {"historial": [], "ultimo_evento": None, "ultima_frase": None}.items():
    st.session_state.setdefault(clave, valor)


def ejecutar(cmd, origen, texto=""):
    """Envía el comando al ESP32 y lo anota en el registro."""
    ok = enviar(TOPIC_CMD, cmd)
    st.session_state.historial.insert(
        0, {"hora": time.strftime("%H:%M:%S"), "origen": origen, "texto": texto, "cmd": cmd, "ok": ok}
    )
    del st.session_state.historial[8:]
    return ok


with st.expander("Instrucciones de uso", expanded=True):
    st.markdown(
        """
1. **Inicia la simulación en Wokwi** y espera a que arriba aparezca *ESP32 en línea*.
2. **Usa Chrome o Edge.** El reconocimiento de voz no funciona en todos los navegadores.
3. Presiona **Iniciar escucha una sola vez**, acepta el permiso del micrófono y habla en español.
4. Frases que entiende:
   - *"Enciende las luces"* / *"Apaga las luces"*
   - *"Enciende el ventilador"* / *"Apaga el ventilador"*
   - *"Abre la ventana"* / *"Cierra la ventana"*
   - *"Modo automático"* para que el salón decida solo
   - Puedes combinar: *"Enciende las luces y abre la ventana"*
5. Si prefieres no hablar, usa los **controles manuales**.
        """
    )

with st.container(border=True):
    st.markdown("### Comando por voz")

    boton = Button(label="Iniciar escucha", width=200, button_type="primary")
    boton.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'es-ES';
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) { value += e.results[i][0].transcript; }
            }
            if (value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: {text: value, ts: Date.now()}}));
            }
        }
        recognition.start();
    """))

    resultado = streamlit_bokeh_events(
        boton, events="GET_TEXT", key="escucha",
        refresh_on_update=False, override_height=75, debounce_time=0,
    )

    if resultado and "GET_TEXT" in resultado:
        evento = resultado["GET_TEXT"]
        texto = str(evento.get("text", "")).strip() if isinstance(evento, dict) else str(evento).strip()
        marca = evento.get("ts") if isinstance(evento, dict) else evento
        if marca != st.session_state.ultimo_evento:      # evita reenviar al recargar la página
            st.session_state.ultimo_evento = marca
            cmd = interpretar(texto)
            if cmd:
                ok = ejecutar(cmd, "voz", texto)
                st.session_state.ultima_frase = (texto, cmd, ok)
            else:
                st.session_state.ultima_frase = (texto, None, None)

    if st.session_state.ultima_frase:
        texto, cmd, ok = st.session_state.ultima_frase
        st.markdown(f"**Escuché:** {texto}")
        if cmd is None:
            st.warning("No reconocí una orden. Prueba con «enciende las luces» o «abre la ventana».")
        elif ok:
            st.success(f"Comando enviado: {cmd}")
        else:
            st.error("No se pudo enviar el comando al broker.")

with st.container(border=True):
    st.markdown("### Controles manuales")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption("Luces")
        a, b = st.columns(2)
        if a.button("ON", key="luces_on"):
            ejecutar({"luces": "ON"}, "botón", "Luces ON")
        if b.button("OFF", key="luces_off"):
            ejecutar({"luces": "OFF"}, "botón", "Luces OFF")
    with c2:
        st.caption("Ventilador")
        a, b = st.columns(2)
        if a.button("ON", key="vent_on"):
            ejecutar({"ventilador": "ON"}, "botón", "Ventilador ON")
        if b.button("OFF", key="vent_off"):
            ejecutar({"ventilador": "OFF"}, "botón", "Ventilador OFF")
    with c3:
        st.caption("Ventana")
        a, b = st.columns(2)
        if a.button("Abrir", key="vent_abre"):
            ejecutar({"ventana": "abre"}, "botón", "Abrir ventana")
        if b.button("Cerrar", key="vent_cierra"):
            ejecutar({"ventana": "cierra"}, "botón", "Cerrar ventana")
    st.caption("Al usar luces o ventilador a mano, el salón pasa a modo manual.")
    if st.button("Volver al modo automático", key="modo_auto"):
        ejecutar({"modo": "auto"}, "botón", "Modo automático")

with st.container(border=True):
    st.markdown("### Telemetría del salón")
    panel_estado()

with st.container(border=True):
    st.markdown("### Registro de comandos")
    if not st.session_state.historial:
        st.caption("Aún no hay comandos.")
    for h in st.session_state.historial:
        estado = "enviado" if h["ok"] else "falló"
        detalle = f" · «{h['texto']}»" if h["origen"] == "voz" and h["texto"] else ""
        st.markdown(f"`{h['hora']}` · {h['origen']}{detalle} → `{h['cmd']}` ({estado})")
