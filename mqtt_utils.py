"""Conexión MQTT compartida por todas las páginas.

Se mantiene UN solo cliente MQTT en segundo plano (st.cache_resource):
  - publica los comandos y el aforo hacia el ESP32
  - escucha la telemetría que publica el ESP32 y la guarda en memoria
"""
import json
import threading
import time

import paho.mqtt.client as paho
import streamlit as st

# ---------- Configuración (igual que en el firmware de Wokwi) ----------
BROKER = "broker.mqttdashboard.com"
PORT = 1883
CLIENT_ID = "Lizalda_App"          # el ESP32 usa "Lizalda"; deben ser distintos

TOPIC_CMD = "lizalda/aula/comando"     # app -> ESP32 (voz y botones)
TOPIC_AFORO = "lizalda/aula/aforo"     # app -> ESP32 (conteo de personas)
TOPIC_SENS = "lizalda/aula/sensores"   # ESP32 -> app (telemetría)

SEGUNDOS_SIN_SENAL = 15                # si pasan más, se considera sin señal


class Estado:
    """Última telemetría recibida (segura para usar desde varios hilos)."""

    def __init__(self):
        self._lock = threading.Lock()
        self._datos = {}
        self._ultima = None
        self._broker_ok = False

    def actualizar(self, datos):
        with self._lock:
            self._datos = datos
            self._ultima = time.time()

    def set_broker(self, ok):
        with self._lock:
            self._broker_ok = ok

    def leer(self):
        with self._lock:
            seg = None if self._ultima is None else time.time() - self._ultima
            return dict(self._datos), seg, self._broker_ok


def _crear_cliente():
    """Compatible con paho-mqtt 1.x y 2.x."""
    try:
        return paho.Client(paho.CallbackAPIVersion.VERSION1, CLIENT_ID)
    except AttributeError:
        return paho.Client(CLIENT_ID)


@st.cache_resource
def obtener_conexion():
    estado = Estado()
    client = _crear_cliente()

    def on_connect(c, userdata, flags, rc):
        estado.set_broker(rc == 0)
        if rc == 0:
            c.subscribe(TOPIC_SENS)

    def on_disconnect(c, userdata, rc):
        estado.set_broker(False)

    def on_message(c, userdata, msg):
        try:
            estado.actualizar(json.loads(msg.payload.decode("utf-8")))
        except Exception:
            pass

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect_async(BROKER, PORT, keepalive=30)
    client.loop_start()          # reconecta solo si se cae
    return client, estado


def enviar(topic, payload):
    """Publica un JSON. Devuelve True si el broker lo recibió."""
    client, _ = obtener_conexion()
    try:
        info = client.publish(topic, json.dumps(payload))
        info.wait_for_publish(timeout=5)
        return info.is_published()
    except Exception:
        return False


def leer_estado():
    """Devuelve (datos, segundos_desde_el_último_mensaje, broker_conectado)."""
    _, estado = obtener_conexion()
    return estado.leer()


def esp32_en_linea(segundos):
    return segundos is not None and segundos < SEGUNDOS_SIN_SENAL
