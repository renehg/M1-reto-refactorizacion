# test_conversor.py
# Suite de pruebas del conversor (parcial: no cubre todas las funciones)

import pytest

from conversor import celsius_a_fahrenheit, convertir, km_a_millas


def test_celsius_a_fahrenheit_punto_ebullicion():
    # 100 °C es el punto de ebullición del agua: 212 °F
    assert celsius_a_fahrenheit(100) == 212


def test_celsius_a_fahrenheit_punto_congelacion():
    # 0 °C corresponde a 32 °F
    assert celsius_a_fahrenheit(0) == 32


def test_km_a_millas_valor_conocido():
    # 10 km son aproximadamente 6.21 millas
    assert km_a_millas(10) == pytest.approx(6.21371)


def test_convertir_clave_invalida():
    # Una clave inexistente debe producir un KeyError
    with pytest.raises(KeyError):
        convertir(5, "leguas2parsecs")
