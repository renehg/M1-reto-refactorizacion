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
MENSAJE_NO_FINITO = "El valor debe ser un número finito"
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
        (212, "f2c", 100.0),
        (-40, "f2c", -40.0),
        (-200, "f2c", -128.8889),
        (-459.67, "f2c", -273.15),
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
    # Cada clave llama a la función correcta; los esperados tienen 4 decimales,
    # así que se acepta la diferencia máxima del redondeo (5e-5)
    assert convertir(valor, clave) == pytest.approx(esperado, abs=5e-5)


def test_convertir_f2c_punto_ebullicion():
    # 212 °F es el punto de ebullición del agua: 100 °C
    assert convertir(212, "f2c") == 100.0


def test_convertir_no_redondea():
    # 1 km = 0.621371 millas; convertir() devuelve el valor completo
    assert convertir(1, "km2mi") == 0.621371


# --- Validaciones ---


@pytest.mark.parametrize(
    ("valor", "clave", "mensaje"),
    [
        (-273.16, "c2f", MENSAJE_TEMPERATURA),
        (-459.68, "f2c", MENSAJE_TEMPERATURA),
        (-500, "f2c", MENSAJE_TEMPERATURA),
        (-1, "km2mi", MENSAJE_DISTANCIA),
        (-1, "mi2km", MENSAJE_DISTANCIA),
        (-1, "kg2lb", MENSAJE_MASA),
        (-1, "lb2kg", MENSAJE_MASA),
        (float("nan"), "c2f", MENSAJE_NO_FINITO),
        (float("inf"), "km2mi", MENSAJE_NO_FINITO),
        (float("-inf"), "lb2kg", MENSAJE_NO_FINITO),
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


def test_cli_redondea_a_4_decimales(capsys):
    # La CLI muestra el resultado de convertir() redondeado a 4 decimales
    assert main(["1", "km2mi"]) == 0
    assert capsys.readouterr().out == "0.6214\n"


def test_cli_listar(capsys):
    # --listar imprime las conversiones ordenadas por clave y devuelve 0
    assert main(["--listar"]) == 0
    assert capsys.readouterr().out == SALIDA_LISTAR


@pytest.mark.parametrize("argv", [[], ["5"]])
def test_cli_faltan_argumentos(argv, capsys):
    # Sin VALOR y CLAVE argparse imprime el uso y el error en stderr y sale con 2
    with pytest.raises(SystemExit) as salida_proceso:
        main(argv)
    assert salida_proceso.value.code == 2
    salida = capsys.readouterr()
    assert salida.out == ""
    assert salida.err.startswith("usage: conversor")
    assert salida.err.endswith(
        "conversor: error: se requieren VALOR y CLAVE (o usa --listar)\n"
    )


def test_cli_valor_no_numerico(capsys):
    # argparse rechaza un VALOR que no es número con el mismo código 2
    with pytest.raises(SystemExit) as salida_proceso:
        main(["abc", "c2f"])
    assert salida_proceso.value.code == 2
    assert "invalid float value: 'abc'" in capsys.readouterr().err


def test_cli_valor_imposible(capsys):
    # Un ValueError se muestra en stderr y devuelve 1
    assert main(["-1", "km2mi"]) == 1
    assert capsys.readouterr().err == f"Error: {MENSAJE_DISTANCIA}\n"


def test_cli_valor_no_finito(capsys):
    # nan pasa el parser (type=float), pero convertir() lo rechaza
    assert main(["nan", "c2f"]) == 1
    assert capsys.readouterr().err == f"Error: {MENSAJE_NO_FINITO}\n"


def test_cli_clave_invalida_sin_comillas(capsys):
    # El mensaje del KeyError llega al usuario sin las comillas de Python
    assert main(["5", "xx"]) == 1
    assert capsys.readouterr().err == f"Error: {MENSAJE_CLAVE_XX}\n"
