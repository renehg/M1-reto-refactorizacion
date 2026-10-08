# test_caracterizacion.py
# Pruebas de caracterización: fijan el comportamiento actual antes del refactor.
# Si una de estas pruebas falla durante un paso que no debía cambiar el
# comportamiento, el refactor introdujo una regresión.

import pytest

from cli import main
from conversor import CONVERSIONES, convertir

MENSAJE_TEMPERATURA = "Temperatura por debajo del cero absoluto"
MENSAJE_DISTANCIA = "La distancia no puede ser negativa"
MENSAJE_MASA = "La masa no puede ser negativa"
MENSAJE_CLAVE_XX = (
    "Conversión no soportada: xx. Usa una de: c2f, f2c, kg2lb, km2mi, lb2kg, mi2km"
)

SALIDA_LISTAR = (
    "Conversiones disponibles:\n"
    "  c2f      Celsius a Fahrenheit\n"
    "  f2c      Fahrenheit a Celsius\n"
    "  kg2lb    Kilogramos a libras\n"
    "  km2mi    Kilómetros a millas\n"
    "  lb2kg    Libras a kilogramos\n"
    "  mi2km    Millas a kilómetros\n"
)


# --- Conversiones a través de convertir() ---


@pytest.mark.parametrize(
    ("valor", "clave", "esperado"),
    [
        (100, "c2f", 212.0),
        (-40, "c2f", -40.0),
        (-273.15, "c2f", -459.67),
        (32, "f2c", 0.0),
        (10, "km2mi", 6.2137),
        (0, "km2mi", 0.0),
        (10, "mi2km", 16.0934),
        (1, "mi2km", 1.6093),
        (1, "kg2lb", 2.2046),
        (1, "lb2kg", 0.4536),
        (0, "lb2kg", 0.0),
    ],
)
def test_convertir_valores_conocidos(valor, clave, esperado):
    # Cada clave llama a la función correcta y el resultado coincide exactamente
    assert convertir(valor, clave) == esperado


@pytest.mark.xfail(
    strict=True,
    reason="Error conocido en fahrenheit_a_celsius (* 9 / 5); se corrige en el paso 10",
)
def test_convertir_f2c_punto_ebullicion():
    # 212 °F es el punto de ebullición del agua: 100 °C
    assert convertir(212, "f2c") == 100.0


def test_convertir_redondea_a_4_decimales():
    # 1 km = 0.621371 millas; convertir() lo redondea a 4 decimales
    assert convertir(1, "km2mi") == 0.6214


# --- Validaciones ---


@pytest.mark.parametrize(
    ("valor", "clave", "mensaje"),
    [
        (-273.16, "c2f", MENSAJE_TEMPERATURA),
        (-1, "km2mi", MENSAJE_DISTANCIA),
        (-1, "mi2km", MENSAJE_DISTANCIA),
        (-1, "kg2lb", MENSAJE_MASA),
        (-1, "lb2kg", MENSAJE_MASA),
    ],
)
def test_convertir_rechaza_valores_imposibles(valor, clave, mensaje):
    # Los valores físicamente imposibles lanzan ValueError con un mensaje fijo
    with pytest.raises(ValueError, match=f"^{mensaje}$"):
        convertir(valor, clave)


# --- Claves ---


def test_convertir_clave_invalida_mensaje():
    # El KeyError trae la clave pedida y la lista ordenada de claves válidas
    with pytest.raises(KeyError) as error:
        convertir(5, "xx")
    assert error.value.args[0] == MENSAJE_CLAVE_XX


def test_conversiones_claves_disponibles():
    # El registro expone exactamente estas seis claves
    assert set(CONVERSIONES) == {"c2f", "f2c", "km2mi", "mi2km", "kg2lb", "lb2kg"}


def test_conversiones_es_de_solo_lectura():
    # El registro no se puede modificar desde otros módulos
    with pytest.raises(TypeError):
        CONVERSIONES["x"] = CONVERSIONES["c2f"]


# --- CLI ---


def test_cli_conversion_exitosa(capsys):
    # Una conversión válida imprime el resultado y devuelve 0
    assert main(["100", "c2f"]) == 0
    salida = capsys.readouterr()
    assert salida.out == "212.0\n"
    assert salida.err == ""


def test_cli_listar(capsys):
    # --listar imprime las conversiones ordenadas por clave y devuelve 0
    assert main(["--listar"]) == 0
    assert capsys.readouterr().out == SALIDA_LISTAR


def test_cli_sin_argumentos(capsys):
    # Sin VALOR ni CLAVE se imprime el uso y devuelve 2
    assert main([]) == 2
    salida = capsys.readouterr()
    assert salida.out.startswith("usage: conversor")
    assert salida.err == "Error: se requieren VALOR y CLAVE (o usa --listar)\n"


def test_cli_valor_imposible(capsys):
    # Un ValueError se muestra en stderr y devuelve 1
    assert main(["-1", "km2mi"]) == 1
    assert capsys.readouterr().err == f"Error: {MENSAJE_DISTANCIA}\n"


def test_cli_clave_invalida_sin_comillas(capsys):
    # El mensaje del KeyError llega al usuario sin las comillas de Python
    assert main(["5", "xx"]) == 1
    assert capsys.readouterr().err == f"Error: {MENSAJE_CLAVE_XX}\n"
