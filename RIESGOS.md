# Riesgos de las pruebas antes del refactor

Análisis de `tests/test_conversor.py`: qué cubren las pruebas actuales y qué refactorizaciones podrían cambiar el comportamiento sin que ninguna prueba falle.

**Resumen:** hay 4 pruebas. Llaman directamente a 2 de las 6 funciones de conversión y comprueban el tipo de error de `convertir` con una clave inválida. Ninguna ejecuta una conversión correcta a través de `convertir` y ninguna toca `cli.py`.

## Qué está cubierto

| Prueba | Qué comprueba |
|---|---|
| `test_celsius_a_fahrenheit_punto_ebullicion` | `celsius_a_fahrenheit(100) == 212`, llamando a la función directamente. |
| `test_celsius_a_fahrenheit_punto_congelacion` | `celsius_a_fahrenheit(0) == 32`. |
| `test_km_a_millas_valor_conocido` | `km_a_millas(10)` da aproximadamente 6.21371, con la tolerancia por defecto de `pytest.approx` (diferencia relativa de 1e-6). |
| `test_convertir_clave_invalida` | `convertir(5, "leguas2parsecs")` lanza `KeyError`. Solo revisa el tipo de error, no el mensaje. |

## Qué NO está cubierto

### En `conversor.py`

- `fahrenheit_a_celsius`, `millas_a_km`, `kg_a_libras` y `libras_a_kg` no tienen ninguna prueba. Por eso nadie detectó el error de fórmula de `f2c`.
- **Ninguna validación.** No se prueba ningún `ValueError` (temperatura bajo el cero absoluto, distancia o masa negativas) ni los valores en el límite (−273.15 o 0).
- **`convertir` con una clave válida.** No se comprueba que cada clave llame a la función correcta ni que el resultado se redondee a 4 decimales.
- **El contenido de `CONVERSIONES`:** qué claves existen y cuáles son sus descripciones.
- **El mensaje** del `KeyError`.
- **Entradas especiales:** `nan`, `inf`, valores negativos válidos como −40 °C y números con decimales.

### En `cli.py` no hay ninguna prueba

- Los códigos de salida 0, 1 y 2.
- Lo que se imprime en `stdout` y en `stderr`.
- El formato y el orden de `--listar`.
- El parche que quita las comillas con `strip(chr(39))`.
- Qué pasa cuando falta `valor`, falta `clave` o `valor` no es un número.

## Refactorizaciones que cambiarían el comportamiento sin que falle ninguna prueba

1. **Cambiar la fórmula de `f2c`**, ya sea para corregirla o para estropearla más.
2. **Modificar cualquier validación.** Por ejemplo:
   - Quitarla.
   - Cambiar `<` por `<=`, que haría que 0 km pasara a dar error.
   - Mover la validación de `f2c` de la salida a la entrada.
   - Cambiar los mensajes de error.
3. **Cambiar el tipo de excepción de las validaciones** por una excepción propia que no herede de `ValueError`. Las pruebas seguirían pasando, pero `cli.py` dejaría de capturarla y terminaría mostrando un traceback.
4. **Cambiar o quitar el `round(..., 4)`** de `convertir`.
5. **Mezclar entradas de `CONVERSIONES`.** Si `mi2km` apuntara a `km_a_millas`, o si se renombrara o eliminara una clave, nada fallaría. La única excepción es que la clave `leguas2parsecs` llegara a existir.
6. **Cambiar `FACTOR_KG_A_LIBRAS`** o la forma en que `millas_a_km` lo calcula. Por ejemplo, pasar de `/ 0.621371` a `* 1.609344` cambia los decimales del resultado. En cambio, un cambio en `FACTOR_KM_A_MILLAS` sí se detecta por `km_a_millas`, salvo que sea menor que la tolerancia de 1e-6.
7. **Cambiar el mensaje de `convertir`**, o hacer que la excepción herede de `KeyError` pero tenga otro formato. Así se podría romper el parche de las comillas de `cli.py`.
8. **Cualquier cambio en `cli.py`**: los códigos de salida, cómo se manejan los argumentos (por ejemplo, pasar a `parser.error()`, que termina el proceso en lugar de devolver 2), lo que se imprime o el orden de `--listar`.
9. **Cambiar las validaciones de `celsius_a_fahrenheit`.** Las pruebas solo revisan dos valores válidos, así que el límite no está protegido.

## Recomendación

Antes de empezar el refactor, escribir pruebas de caracterización (pruebas que registren cómo se comporta el código hoy), al menos de los puntos 1 a 5 y de `cli.main`.

Hay un caso que se debe decidir de forma explícita: si se escribe una prueba de `f2c` con el comportamiento actual, la prueba fijaría el error. Lo razonable es escribirla con el valor correcto (212 °F → 100 °C) y aceptar que falle hasta que se corrija la fórmula.
