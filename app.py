import streamlit as st

from ui import aplicar_estilos, estado_lateral

st.set_page_config(page_title="AulaSense", page_icon="🛰️", layout="centered")
aplicar_estilos()

navegacion = st.navigation(
    [
        st.Page("paginas/inicio.py", title="Inicio", icon=":material/home:", default=True),
        st.Page("paginas/control_voz.py", title="Comando por voz", icon=":material/mic:"),
        st.Page("paginas/aforo_camara.py", title="Escáner de aforo", icon=":material/photo_camera:"),
    ]
)

with st.sidebar:
    st.markdown('<div class="brand">AULASENSE</div>', unsafe_allow_html=True)
    estado_lateral()

navegacion.run()
