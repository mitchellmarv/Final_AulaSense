"""Convierte una frase hablada en comandos JSON para el ESP32."""
import re
import unicodedata

ENCENDER = {"enciende", "encender", "encienda", "prende", "prender", "prenda", "activa", "activar"}
APAGAR = {"apaga", "apagar", "apague", "desactiva", "desactivar"}
ABRIR = {"abre", "abrir", "abra"}
CERRAR = {"cierra", "cerrar", "cierre"}
LUCES = {"luz", "luces"}
VENTILADOR = {"ventilador", "ventiladores", "abanico"}
VENTANA = {"ventana", "ventanas"}
AUTO = {"automatico", "automatica"}
MANUAL = {"manual"}


def normalizar(texto):
    """Minúsculas y sin tildes."""
    t = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def interpretar(texto):
    """Devuelve un dict como {"luces": "ON", "ventana": "abre"} (vacío si no entendió).

    Admite varias órdenes en una frase: "enciende las luces y abre la ventana".
    """
    cmd = {}
    accion = None
    clausulas = re.split(r"\s+y\s+|,|\s+luego\s+|\s+despues\s+|\s+pero\s+", normalizar(texto))
    for clausula in clausulas:
        p = set(re.findall(r"[a-z]+", clausula))
        if p & APAGAR:
            accion = "apagar"
        elif p & ENCENDER:
            accion = "encender"
        elif p & ABRIR:
            accion = "abrir"
        elif p & CERRAR:
            accion = "cerrar"

        if p & LUCES and accion in ("encender", "apagar"):
            cmd["luces"] = "ON" if accion == "encender" else "OFF"
        if p & VENTILADOR and accion in ("encender", "apagar"):
            cmd["ventilador"] = "ON" if accion == "encender" else "OFF"
        if p & VENTANA and accion in ("abrir", "cerrar"):
            cmd["ventana"] = "abre" if accion == "abrir" else "cierra"
        if p & AUTO:
            cmd["modo"] = "auto"
        elif p & MANUAL:
            cmd["modo"] = "manual"
    return cmd
