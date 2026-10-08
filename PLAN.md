# Plan de refactorización (de menor a mayor riesgo)

Son 14 pasos, del 0 al 13, con una refactorización por paso. Los números de smell se refieren a `DIAGNOSTICO.md`.

- **Pasos 0 a 9:** no deberían cambiar ningún resultado del programa, y las pruebas del paso 0 lo comprueban en cada paso.
- **Pasos 10 a 13:** cambian el comportamiento a propósito, así que cada uno actualiza las pruebas que corresponda.

## Criterios de aceptación globales

Se verifican después de cada paso:

1. **Las 4 pruebas originales de `tests/test_conversor.py` pasan.** Se comprueba con `pytest tests/test_conversor.py -q`, que debe mostrar `4 passed`. Ningún paso puede romperlas ni marcarlas como `skip` o `xfail`.
2. `pytest -q` pasa por completo, incluidas las pruebas nuevas del paso 0.
3. `ruff format --check .` no encuentra cambios pendientes.

**Sobre las reglas de ruff:** con la configuración actual solo aparece I001. Las demás reglas que se mencionan son de `--select ALL` y empiezan a contar desde el paso 1, que activa esas reglas en el proyecto.

---

## Paso 0 · Pruebas de caracterización

- **Objetivo:** proteger el comportamiento actual antes de tocar el código, sin modificar el código de producción.
- **Archivos:** `tests/test_caracterizacion.py`, que es nuevo.
- **Smells que elimina:** el 15, la cobertura insuficiente.
- **Reglas de ruff:** ninguna desaparece. El archivo nuevo no debe agregar errores.
- **Criterios de aceptación:**
  - Hay pruebas para las 6 conversiones a través de `convertir`.
  - Hay pruebas de cada `ValueError` y de sus límites (−273.15 °C y 0).
  - Hay pruebas del mensaje del `KeyError`, del redondeo a 4 decimales y de las claves de `CONVERSIONES`.
  - Hay pruebas de `cli.main` que revisan los códigos 0, 1 y 2, la salida de `--listar` y que el mensaje de error no lleve comillas (con `capsys`).
  - La prueba de `f2c` usa el valor correcto (212 → 100) y se marca con `@pytest.mark.xfail(strict=True)` hasta el paso 10.
  - `pytest -q` termina en verde.

## Paso 1 · Configurar ruff en el proyecto

- **Objetivo:** que todos obtengan el mismo resultado de ruff y que los falsos positivos dejen de aparecer.
- **Archivos:** `pyproject.toml`, que es nuevo, y `requirements.txt`.
- **Smells que elimina:** que no haya configuración de ruff en el repositorio y que `ruff` no esté declarado como dependencia.
- **Reglas de ruff:** este paso las define.
  - Activa `select = ["E","F","W","I","B","UP","ANN","D","EM","TRY","PL","RUF"]` y fija la convención de docstrings en `google`.
  - En `tests/**`, ignora `PLR2004`, `D` y `ANN`.
  - T201, S101 y CPY001 no se activan.
- **Criterios de aceptación:**
  - `requirements.txt` incluye `ruff`.
  - `ruff check .` lista solo I001, ANN001, ANN201, D100, D103, EM101, EM102 y TRY003. No aparecen falsos positivos.

## Paso 2 · Ordenar imports

- **Objetivo:** dejar el bloque de imports en el orden que pide ruff.
- **Archivos:** `tests/test_conversor.py`.
- **Smells que elimina:** el 10.
- **Reglas de ruff que desaparecen:** **I001**.
- **Criterios de aceptación:**
  - `ruff check --fix --select I .` aplica el cambio.
  - Después, `ruff check --select I .` no muestra errores.

## Paso 3 · Anotaciones de tipos

- **Objetivo:** agregar tipos a todas las funciones públicas, por ejemplo `float -> float` en las conversiones, `argv: list[str] | None` y `-> int` en `main`.
- **Archivos:** `conversor.py` y `cli.py`.
- **Smells que elimina:** el 11.
- **Reglas de ruff que desaparecen:** **ANN001** y **ANN201**.
- **Criterios de aceptación:**
  - `ruff check --select ANN .` termina en 0.
  - El código de producción no cambia, solo se agregan anotaciones (se revisa con `git diff`).

## Paso 4 · Docstrings en lugar de comentarios

- **Objetivo:** convertir los comentarios de cada módulo y función en docstrings, y quitar los encabezados del tipo `# conversor.py`.
- **Archivos:** `conversor.py`, `cli.py` y `conftest.py`.
- **Smells que elimina:** el 12.
- **Reglas de ruff que desaparecen:** **D100** y **D103**.
- **Criterios de aceptación:**
  - `ruff check --select D .` termina en 0.
  - `python -c "import conversor; help(conversor.convertir)"` muestra la descripción.

## Paso 5 · Constantes para las fórmulas de temperatura

- **Objetivo:** reemplazar `9`, `5` y `32` por constantes con nombre, por ejemplo `ESCALA_F_NUM`, `ESCALA_F_DEN` y `DESPLAZAMIENTO_F`.
- **Archivos:** `conversor.py`.
- **Smells que elimina:** el 3.
- **Reglas de ruff:** ninguna, porque PLR2004 no revisa operaciones aritméticas.
- **Criterios de aceptación:**
  - Se conserva el orden de las operaciones (`* NUM / DEN`). Si se reemplazara por `* 1.8`, algunos resultados podrían cambiar en los últimos decimales.
  - Las pruebas de caracterización de c2f y f2c siguen pasando.

## Paso 6 · Centralizar las validaciones duplicadas

- **Objetivo:** extraer `_validar_no_negativo(valor, magnitud)` y `_validar_sobre_cero_absoluto(celsius)` y usarlos en las 6 funciones.
- **Archivos:** `conversor.py`.
- **Smells que elimina:** el 2.
- **Reglas de ruff:** ninguna por sí sola, pero prepara el paso 7.
- **Criterios de aceptación:**
  - El texto `raise ValueError` aparece como máximo 2 veces en `conversor.py` (`grep -c`).
  - Los mensajes de error son idénticos a los actuales, lo que comprueban las pruebas del paso 0.

## Paso 7 · Excepción propia con mensajes centralizados

- **Objetivo:** crear `class ErrorConversion(ValueError)` con los mensajes como constantes o como atributos de la clase. Hereda de `ValueError` para que `cli.py` y las pruebas sigan funcionando sin cambios.
- **Archivos:** `conversor.py`.
- **Smells que elimina:** el 13.
- **Reglas de ruff que desaparecen:** **EM101**, **EM102** y **TRY003**.
- **Criterios de aceptación:**
  - `ruff check .` termina en **0**.
  - `pytest.raises(ValueError)` sigue funcionando en todas las pruebas.

## Paso 8 · Registro de conversiones inmutable y con campos con nombre

- **Objetivo:** convertir cada entrada de `CONVERSIONES` en `Conversion(NamedTuple)` con los campos `funcion` y `descripcion`, y envolver el diccionario en `MappingProxyType`.
- **Archivos:** `conversor.py` y `cli.py`, que pasa a usar `.descripcion`.
- **Smells que elimina:** el 6.
- **Reglas de ruff:** ninguna.
- **Criterios de aceptación:**
  - `CONVERSIONES["x"] = ...` lanza `TypeError`, y hay una prueba nueva que lo comprueba.
  - La salida de `--listar` es idéntica, byte por byte.

## Paso 9 · Quitar el uso de `KeyError` y el parche de las comillas

- **Objetivo:** crear `ClaveNoSoportada(ErrorConversion, KeyError)` con su propio `__str__`, para que el mensaje salga sin comillas. Así se puede quitar `strip(chr(39))` y `cli.py` captura solo `ErrorConversion`.
- **Archivos:** `conversor.py` y `cli.py`.
- **Smells que elimina:** el 4 y el 5.
- **Reglas de ruff:** ninguna.
- **Criterios de aceptación:**
  - `test_convertir_clave_invalida`, que espera un `KeyError`, sigue pasando.
  - `str(error)` no contiene `'`.
  - `chr(39)` no aparece en `cli.py`.
  - La salida que ve el usuario es idéntica a la actual.

## Paso 10 · Corregir `f2c`

*Este paso cambia el comportamiento a propósito.*

- **Objetivo:** usar `* 5 / 9` y validar la entrada (el límite es −459.67 °F) en lugar del resultado.
- **Archivos:** `conversor.py` y `tests/test_caracterizacion.py`, donde se quita el `xfail`.
- **Smells que elimina:** el 1.
- **Reglas de ruff:** ninguna.
- **Criterios de aceptación:**
  - `convertir(212, "f2c") == 100`.
  - −200 °F se acepta y −500 °F lanza `ValueError`.
  - La prueba que estaba marcada con `xfail` pasa sin la marca.

## Paso 11 · Rechazar `nan` e `inf`

*Este paso cambia el comportamiento.*

- **Objetivo:** que `convertir` lance `ErrorConversion` si el valor no es un número finito (`math.isfinite`).
- **Archivos:** `conversor.py` y una prueba nueva.
- **Smells que elimina:** el 9.
- **Reglas de ruff:** ninguna.
- **Criterios de aceptación:**
  - `python cli.py nan c2f` termina con código 1 y un mensaje de error.
  - Hay pruebas para `nan`, `inf` y `-inf`.

## Paso 12 · Validar los argumentos con argparse

*Este paso cambia el comportamiento y la interfaz.*

- **Objetivo:** reemplazar la comprobación manual de `valor` y `clave` por `parser.error()`.
- **Archivos:** `cli.py` y las pruebas de la CLI.
- **Smells que elimina:** el 8.
- **Reglas de ruff:** ninguna.
- **Criterios de aceptación:**
  - `main([])` lanza `SystemExit(2)` en lugar de devolver 2, y la prueba correspondiente se actualiza.
  - El mensaje de error sale en `stderr`.

## Paso 13 · Llevar el redondeo a la CLI

*Este paso cambia el comportamiento de la biblioteca.*

- **Objetivo:** que `convertir` devuelva el valor completo y que `cli.py` lo formatee con 4 decimales.
- **Archivos:** `conversor.py`, `cli.py` y las pruebas de redondeo.
- **Smells que elimina:** el 7.
- **Reglas de ruff:** ninguna.
- **Criterios de aceptación:**
  - `convertir(1, "km2mi") == 0.621371`, sin redondear.
  - La salida de `python cli.py 1 km2mi` es igual a la de antes del paso.

---

## Al terminar

- `ruff check .` queda en 0 desde el paso 7.
- `pytest` termina en verde.
- Quedan resueltos los 9 smells de diseño y los 6 de estilo de `DIAGNOSTICO.md`. La excepción es el 14 (INP001), que queda fuera porque esa regla no se activa en el paso 1.
