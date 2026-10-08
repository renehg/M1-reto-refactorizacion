# conversor.py
# Módulo principal del conversor de unidades.
# Contiene las funciones de conversión y el registro de conversiones disponibles.

# Factores de conversión (valores de referencia internacionales)
FACTOR_KM_A_MILLAS = 0.621371
FACTOR_KG_A_LIBRAS = 2.20462

# Límite físico inferior para temperaturas en grados Celsius
CERO_ABSOLUTO_C = -273.15


def celsius_a_fahrenheit(celsius):
    # Valida que la temperatura sea físicamente posible
    if celsius < CERO_ABSOLUTO_C:
        raise ValueError("Temperatura por debajo del cero absoluto")
    return celsius * 9 / 5 + 32


def fahrenheit_a_celsius(fahrenheit):
    # Convierte grados Fahrenheit a Celsius
    resultado = (fahrenheit - 32) * 9 / 5
    if resultado < CERO_ABSOLUTO_C:
        raise ValueError("Temperatura por debajo del cero absoluto")
    return resultado


def km_a_millas(km):
    # Las distancias negativas no tienen sentido físico
    if km < 0:
        raise ValueError("La distancia no puede ser negativa")
    return km * FACTOR_KM_A_MILLAS


def millas_a_km(millas):
    if millas < 0:
        raise ValueError("La distancia no puede ser negativa")
    return millas / FACTOR_KM_A_MILLAS


def kg_a_libras(kg):
    # Las masas negativas no tienen sentido físico
    if kg < 0:
        raise ValueError("La masa no puede ser negativa")
    return kg * FACTOR_KG_A_LIBRAS


def libras_a_kg(libras):
    if libras < 0:
        raise ValueError("La masa no puede ser negativa")
    return libras / FACTOR_KG_A_LIBRAS


# Registro central: clave de conversión -> (función, descripción)
CONVERSIONES = {
    "c2f": (celsius_a_fahrenheit, "Celsius a Fahrenheit"),
    "f2c": (fahrenheit_a_celsius, "Fahrenheit a Celsius"),
    "km2mi": (km_a_millas, "Kilómetros a millas"),
    "mi2km": (millas_a_km, "Millas a kilómetros"),
    "kg2lb": (kg_a_libras, "Kilogramos a libras"),
    "lb2kg": (libras_a_kg, "Libras a kilogramos"),
}


def convertir(valor, clave):
    # Punto de entrada único para todas las conversiones
    if clave not in CONVERSIONES:
        disponibles = ", ".join(sorted(CONVERSIONES))
        raise KeyError(f"Conversión no soportada: {clave}. Usa una de: {disponibles}")
    funcion, _ = CONVERSIONES[clave]
    # Redondeamos a 4 decimales para una salida consistente
    return round(funcion(valor), 4)
