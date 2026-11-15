import io

import numpy as np
import streamlit as st
from PIL import Image

from mqtt_utils import TOPIC_AFORO, enviar
from ui import encabezado, panel_estado

encabezado("Escáner de aforo", "La cámara cuenta personas y avisa al salón si se supera el aforo")


@st.cache_resource(show_spinner="Cargando modelo YOLO...")
def cargar_modelo():
    try:
        from ultralytics import YOLO
        return YOLO("yolov5su.pt")
    except Exception as e:
        return str(e)


def reportar(personas, maximo):
    """Muestra el estado del aforo y publica el conteo al ESP32."""
    ok = enviar(TOPIC_AFORO, {"personas": int(personas), "max": int(maximo)})
    c1, c2 = st.columns(2)
    c1.metric("Personas detectadas", int(personas))
    c2.metric("Aforo máximo", int(maximo))
    st.progress(min(personas / max(maximo, 1), 1.0))
    if personas > maximo:
        st.error(f"ALERTA: aforo superado ({personas}/{maximo}). El buzzer del salón sonará.")
    else:
        st.success(f"Aforo dentro del límite ({personas}/{maximo}).")
    if ok:
        st.caption("Conteo enviado al ESP32.")
    else:
        st.error("No se pudo enviar el conteo al broker.")


with st.expander("Instrucciones de uso", expanded=True):
    st.markdown(
        """
1. **Inicia la simulación en Wokwi** y espera a que aparezca *ESP32 en línea*.
2. Define el **aforo máximo** del salón.
3. Toma una **foto** del salón con la cámara. La primera vez el modelo tarda unos segundos en cargar.
4. La app cuenta las personas y envía el número al ESP32:
   - Si **no supera** el aforo, todo sigue normal.
   - Si lo **supera**, aparece una alerta y suena el buzzer en Wokwi.
5. ¿Sin cámara o sin modelo? Usa el **modo de prueba** para enviar un conteo a mano.
        """
    )

with st.container(border=True):
    st.markdown("### Parámetros")
    p1, p2 = st.columns(2)
    maximo = p1.number_input("Aforo máximo", min_value=1, max_value=500, value=25, step=1)
    confianza = p2.slider("Confianza mínima", 0.05, 0.95, 0.25, 0.05)

with st.container(border=True):
    st.markdown("### Escáner")
    foto = st.camera_input("Toma una foto del salón")

    if foto:
        modelo = cargar_modelo()
        if isinstance(modelo, str):
            st.warning(f"No se pudo cargar el modelo YOLO: {modelo}. Usa el modo de prueba de abajo.")
        else:
            imagen = Image.open(io.BytesIO(foto.getvalue())).convert("RGB")
            np_img = np.array(imagen)[..., ::-1]        # RGB -> BGR para YOLO
            with st.spinner("Contando personas..."):
                try:
                    resultado = modelo(np_img, conf=confianza, verbose=False)[0]
                except Exception as e:
                    st.error(f"Error durante la detección: {e}")
                    st.stop()
            nombres = modelo.names
            personas = sum(1 for b in resultado.boxes if nombres[int(b.cls.item())] == "person")
            st.image(resultado.plot()[:, :, ::-1], caption="Detecciones")
            reportar(personas, maximo)

with st.expander("Modo de prueba (sin cámara)"):
    st.caption("Útil para demostrar el sistema o si la cámara no está disponible.")
    manual = st.number_input("Número de personas", min_value=0, max_value=500, value=0, step=1)
    if st.button("Enviar conteo manual"):
        reportar(manual, maximo)

with st.container(border=True):
    st.markdown("### Telemetría del salón")
    panel_estado()
