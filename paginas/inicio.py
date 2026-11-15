import streamlit as st

from ui import encabezado, panel_estado

encabezado("AulaSense", "Centro de control del aula inteligente · voz, visión artificial y sensores")

with st.container(border=True):
    st.markdown("### Telemetría del salón")
    panel_estado()

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("### Comando por voz")
        st.write("Controla luces, ventilador y ventana hablando o con botones.")
        st.page_link("paginas/control_voz.py", label="Abrir comando por voz", icon=":material/mic:")
with col2:
    with st.container(border=True):
        st.markdown("### Escáner de aforo")
        st.write("Toma una foto del salón y la IA cuenta cuántas personas hay.")
        st.page_link("paginas/aforo_camara.py", label="Abrir escáner de aforo", icon=":material/photo_camera:")

with st.expander("¿Cómo funciona?", expanded=True):
    st.markdown(
        """
1. **Inicia la simulación en Wokwi.** Cuando el ESP32 se conecte, arriba aparecerá **ESP32 en línea**.
2. En **Comando por voz** puedes encender luces, usar el ventilador o abrir la ventana.
3. En **Escáner de aforo** la cámara cuenta personas. Si se supera el aforo, suena el buzzer del salón.
4. En **modo automático** el ESP32 decide solo: enciende el ventilador con calor y gente, y apaga las luces si el salón queda vacío.
        """
    )
