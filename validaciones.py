# validaciones.py
from datetime import datetime

def validar_texto(texto, longitud_min=3):
    return len(texto.strip()) >= longitud_min

def validar_numero(valor, positivo=True):
    try:
        num = float(valor)
        return num >= 0 if positivo else True
    except ValueError:
        return False

def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
