"""Módulo principal del conversor de unidades.

Contiene las funciones de conversión y el registro de conversiones disponibles.
"""

from collections.abc import Callable
from types import MappingProxyType
from typing import NamedTuple

# Factores de conversión (valores de referencia internacionales)
FACTOR_KM_A_MILLAS = 0.621371
FACTOR_KG_A_LIBRAS = 2.20462

# Límite físico inferior para temperaturas en grados Celsius
CERO_ABSOLUTO_C = -273.15

# Relación entre escalas: °F = °C * ESCALA_F_NUM / ESCALA_F_DEN + DESPLAZAMIENTO_F
ESCALA_F_NUM = 9
ESCALA_F_DEN = 5
DESPLAZAMIENTO_F = 32


class ErrorConversion(ValueError):
    """Valor físicamente imposible para una conversión.

    Hereda de ``ValueError`` para que el código que ya captura ``ValueError``
    siga funcionando. Los mensajes se centralizan como atributos de la clase.
    """

    TEMPERATURA_BAJO_CERO_ABSOLUTO = "Temperatura por debajo del cero absoluto"
    MAGNITUD_NEGATIVA = "La {magnitud} no puede ser negativa"


def _validar_sobre_cero_absoluto(celsius: float) -> None:
    """Lanza ErrorConversion si la temperatura en Celsius está bajo el cero absoluto."""
    if celsius < CERO_ABSOLUTO_C:
        raise ErrorConversion(ErrorConversion.TEMPERATURA_BAJO_CERO_ABSOLUTO)


def _validar_no_negativo(valor: float, magnitud: str) -> None:
    """Lanza ErrorConversion si el valor es negativo; ``magnitud`` va en el mensaje."""
    if valor < 0:
        mensaje = ErrorConversion.MAGNITUD_NEGATIVA.format(magnitud=magnitud)
        raise ErrorConversion(mensaje)


def celsius_a_fahrenheit(celsius: float) -> float:
    """Convierte grados Celsius a Fahrenheit.

    Raises:
        ErrorConversion: Si la temperatura está por debajo del cero absoluto.
    """
    _validar_sobre_cero_absoluto(celsius)
    return celsius * ESCALA_F_NUM / ESCALA_F_DEN + DESPLAZAMIENTO_F


def fahrenheit_a_celsius(fahrenheit: float) -> float:
    """Convierte grados Fahrenheit a Celsius.

    Raises:
        ErrorConversion: Si el resultado está por debajo del cero absoluto.
    """
    resultado = (fahrenheit - DESPLAZAMIENTO_F) * ESCALA_F_NUM / ESCALA_F_DEN
    _validar_sobre_cero_absoluto(resultado)
    return resultado


def km_a_millas(km: float) -> float:
    """Convierte kilómetros a millas.

    Raises:
        ErrorConversion: Si la distancia es negativa.
    """
    _validar_no_negativo(km, "distancia")
    return km * FACTOR_KM_A_MILLAS


def millas_a_km(millas: float) -> float:
    """Convierte millas a kilómetros.

    Raises:
        ErrorConversion: Si la distancia es negativa.
    """
    _validar_no_negativo(millas, "distancia")
    return millas / FACTOR_KM_A_MILLAS


def kg_a_libras(kg: float) -> float:
    """Convierte kilogramos a libras.

    Raises:
        ErrorConversion: Si la masa es negativa.
    """
    _validar_no_negativo(kg, "masa")
    return kg * FACTOR_KG_A_LIBRAS


def libras_a_kg(libras: float) -> float:
    """Convierte libras a kilogramos.

    Raises:
        ErrorConversion: Si la masa es negativa.
    """
    _validar_no_negativo(libras, "masa")
    return libras / FACTOR_KG_A_LIBRAS


class Conversion(NamedTuple):
    """Entrada del registro: la función que convierte y su descripción."""

    funcion: Callable[[float], float]
    descripcion: str


# Registro central de solo lectura: clave de conversión -> Conversion
CONVERSIONES = MappingProxyType(
    {
        "c2f": Conversion(celsius_a_fahrenheit, "Celsius a Fahrenheit"),
        "f2c": Conversion(fahrenheit_a_celsius, "Fahrenheit a Celsius"),
        "km2mi": Conversion(km_a_millas, "Kilómetros a millas"),
        "mi2km": Conversion(millas_a_km, "Millas a kilómetros"),
        "kg2lb": Conversion(kg_a_libras, "Kilogramos a libras"),
        "lb2kg": Conversion(libras_a_kg, "Libras a kilogramos"),
    }
)


def convertir(valor: float, clave: str) -> float:
    """Punto de entrada único para todas las conversiones.

    Args:
        valor: Valor numérico a convertir.
        clave: Clave de la conversión, por ejemplo ``"c2f"`` o ``"km2mi"``.

    Returns:
        El valor convertido, redondeado a 4 decimales.

    Raises:
        KeyError: Si la clave no está en ``CONVERSIONES``.
        ErrorConversion: Si el valor es físicamente imposible.
    """
    if clave not in CONVERSIONES:
        disponibles = ", ".join(sorted(CONVERSIONES))
        mensaje = f"Conversión no soportada: {clave}. Usa una de: {disponibles}"
        raise KeyError(mensaje)
    funcion = CONVERSIONES[clave].funcion
    # Redondeamos a 4 decimales para una salida consistente
    return round(funcion(valor), 4)
