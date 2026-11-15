# AulaSense

Aula inteligente multimodal: **Streamlit** (voz, cámara y botones) + **ESP32 simulado en Wokwi** conectados por **MQTT**.

## Estructura

```
app.py                  # navegación, estilos y barra lateral
ui.py                   # tema espacial y panel de telemetría
mqtt_utils.py           # conexión MQTT compartida (publica y escucha)
comandos.py             # convierte frases habladas en comandos JSON
paginas/
  inicio.py
  control_voz.py        # página 1: voz y botones
  aforo_camara.py       # página 2: cámara + YOLO
.streamlit/config.toml  # tema oscuro
requirements.txt
packages.txt
```

## Ejecutar en local

```
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Cloud

Main file: `app.py`. En *Advanced settings* elige **Python 3.11** (compatible con `bokeh==2.4.3`).

## Tópicos MQTT (broker.mqttdashboard.com)

| Tópico | Dirección | Contenido |
|---|---|---|
| `lizalda/aula/comando` | app → ESP32 | `{"luces":"ON"}`, `{"ventilador":"OFF"}`, `{"ventana":"abre"}`, `{"modo":"auto"}` |
| `lizalda/aula/aforo` | app → ESP32 | `{"personas":18,"max":25}` |
| `lizalda/aula/sensores` | ESP32 → app | temperatura, humedad, estados, modo, alerta |
