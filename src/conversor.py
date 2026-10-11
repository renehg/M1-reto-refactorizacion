"""Módulo principal del conversor de unidades.

Contiene las funciones de conversión y el registro de conversiones disponibles.
"""

import math
from collections.abc import Callable
from types import MappingProxyType
from typing import NamedTuple

# Factores de conversión (valores de referencia internacionales)
FACTOR_KM_A_MILLAS = 0.621371
FACTOR_KG_A_LIBRAS = 2.20462

# Límite físico inferior para temperaturas en grados Celsius y Fahrenheit.
# CERO_ABSOLUTO_F se escribe literal: calcularlo desde CERO_ABSOLUTO_C da
# -459.66999999999996 y rechazaría -459.67 °F, que sí es válido.
CERO_ABSOLUTO_C = -273.15
CERO_ABSOLUTO_F = -459.67

# Relación entre escalas: °F = °C * ESCALA_F_NUM / ESCALA_F_DEN + DESPLAZAMIENTO_F
ESCALA_F_NUM = 9
ESCALA_F_DEN = 5
DESPLAZAMIENTO_F = 32


class ErrorConversion(ValueError):
    """Error al convertir: valor físicamente imposible o clave no soportada.

    Hereda de ``ValueError`` para que el código que ya captura ``ValueError``
    siga funcionando. Los mensajes se centralizan como atributos de la clase.
    """

    TEMPERATURA_BAJO_CERO_ABSOLUTO = "Temperatura por debajo del cero absoluto"
    MAGNITUD_NEGATIVA = "La {magnitud} no puede ser negativa"
    VALOR_NO_FINITO = "El valor debe ser un número finito"


class ClaveNoSoportada(ErrorConversion, KeyError):
    """La clave de conversión pedida no existe en el registro.

    Hereda también de ``KeyError`` por compatibilidad con el código existente.
    Redefine ``__str__`` porque ``KeyError`` mostraría el mensaje entre comillas.
    """

    def __init__(self, clave: str, disponibles: str) -> None:
        """Arma el mensaje con la clave pedida y las claves disponibles."""
        super().__init__(f"Conversión no soportada: {clave}. Usa una de: {disponibles}")

    def __str__(self) -> str:
        """Devuelve el mensaje sin las comillas que añade ``KeyError``."""
        return str(self.args[0])


def _validar_sobre_cero_absoluto(temperatura: float, cero_absoluto: float) -> None:
    """Lanza ErrorConversion si la temperatura está bajo el cero absoluto dado."""
    if temperatura < cero_absoluto:
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
    _validar_sobre_cero_absoluto(celsius, CERO_ABSOLUTO_C)
    return celsius * ESCALA_F_NUM / ESCALA_F_DEN + DESPLAZAMIENTO_F


def fahrenheit_a_celsius(fahrenheit: float) -> float:
    """Convierte grados Fahrenheit a Celsius.

    Raises:
        ErrorConversion: Si la temperatura está por debajo del cero absoluto.
    """
    _validar_sobre_cero_absoluto(fahrenheit, CERO_ABSOLUTO_F)
    return (fahrenheit - DESPLAZAMIENTO_F) * ESCALA_F_DEN / ESCALA_F_NUM


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
        El valor convertido, sin redondear; el redondeo es cosa de quien lo muestra.

    Raises:
        ClaveNoSoportada: Si la clave no está en ``CONVERSIONES``.
        ErrorConversion: Si el valor no es finito (``nan``, ``inf``) o es
            físicamente imposible.
    """
    if clave not in CONVERSIONES:
        disponibles = ", ".join(sorted(CONVERSIONES))
        raise ClaveNoSoportada(clave, disponibles)
    if not math.isfinite(valor):
        raise ErrorConversion(ErrorConversion.VALOR_NO_FINITO)
    return CONVERSIONES[clave].funcion(valor)
