# Pasos ejecutados del plan

Registro de los pasos de `PLAN.md` que ya se ejecutaron, con lo que se cambió y la salida de las verificaciones. Los pasos 0 a 8 están en el commit `a11c800` (`refactor: aplicar pasos 0 a 8 del plan`). Los pasos 9 a 13 todavía no tienen commit.

Criterio global en todos los pasos: `pytest tests/test_conversor.py -q` → `4 passed`.

| Paso | Resultado de `pytest -q` | Errores de `ruff check .` |
|---|---|---|
| Inicio | 4 passed | 1 (solo I001, sin configuración propia) |
| 0 | 28 passed, 1 xfailed | 0 en el archivo nuevo |
| 1 | 28 passed, 1 xfailed | 47 |
| 2 | 28 passed, 1 xfailed | 46 |
| 3 | 28 passed, 1 xfailed | 27 |
| 4 | 28 passed, 1 xfailed | 14 |
| 5 | 28 passed, 1 xfailed | 14 |
| 6 | 28 passed, 1 xfailed | 6 |
| 7 | 28 passed, 1 xfailed | **0** |
| 8 | 29 passed, 1 xfailed | **0** |
| 9 | 29 passed, 1 xfailed | **0** |
| 10 | 36 passed | **0** |
| 11 | 40 passed | **0** |
| 12 | 42 passed | **0** |
| 13 | 43 passed | **0** |

---

## Paso 0 · Pruebas de caracterización

**Cambio:** nuevo archivo `tests/test_caracterizacion.py` con 25 pruebas. No se modificó el código de producción. Los valores esperados se obtuvieron ejecutando el código actual.

- Las 6 conversiones a través de `convertir`: 11 casos, entre ellos −273.15 °C, 0 y −40 °C.
- El redondeo: `convertir(1, "km2mi") == 0.6214`.
- Las 5 validaciones, con el mensaje exacto de cada `ValueError`.
- El mensaje exacto del `KeyError` y las 6 claves de `CONVERSIONES`.
- `cli.main`: códigos 0, 1 y 2, salida completa de `--listar` y mensaje de error sin comillas.
- `f2c` 212 → 100 marcada con `xfail(strict=True)` hasta el paso 10.

```
pytest -q                          → 28 passed, 1 xfailed
pytest tests/test_conversor.py -q  → 4 passed
ruff check (archivo nuevo)         → All checks passed!
ruff format --check .              → 10 files already formatted
```

## Paso 1 · Configurar ruff en el proyecto

**Cambio:** nuevo `pyproject.toml` con `target-version = "py312"`, los grupos `E, F, W, I, B, UP, ANN, D, EM, TRY, PL, RUF`, convención de docstrings `google` y, en `tests/**`, se ignoran `PLR2004`, `D` y `ANN`. Se agregó `ruff>=0.16` a `requirements.txt`.

```
ruff check .  → 47 errores:
   ANN201 10 · D103 10 · ANN001 9 · TRY003 7 · EM101 6 · D100 3 · EM102 1 · I001 1
ruff format --check .              → 10 files already formatted
pytest -q                          → 28 passed, 1 xfailed
pytest tests/test_conversor.py -q  → 4 passed
```

Aparecieron exactamente las 8 reglas previstas, sin falsos positivos (T201, S101, PLR2004, CPY001, INP001).

## Paso 2 · Ordenar imports

**Cambio:** `ruff check --fix --select I .` cambió una línea de `tests/test_conversor.py`:

```diff
-from conversor import celsius_a_fahrenheit, km_a_millas, convertir
+from conversor import celsius_a_fahrenheit, convertir, km_a_millas
```

```
ruff check --select I .            → All checks passed!
ruff check .                       → 46 errores (desapareció I001)
ruff format --check .              → 10 files already formatted
pytest -q                          → 28 passed, 1 xfailed
pytest tests/test_conversor.py -q  → 4 passed
```

## Paso 3 · Anotaciones de tipos

**Cambio:** se anotaron las 10 funciones públicas, sin tocar ninguna otra línea.

| Archivo | Funciones | Anotación |
|---|---|---|
| `conversor.py` | Las 6 funciones de conversión | `(x: float) -> float` |
| `conversor.py` | `convertir` | `(valor: float, clave: str) -> float` |
| `cli.py` | `construir_parser` | `() -> argparse.ArgumentParser` |
| `cli.py` | `listar_conversiones` | `() -> None` |
| `cli.py` | `main` | `(argv: list[str] \| None = None) -> int` |

```
ruff check --select ANN .          → All checks passed!
ruff check .                       → 27 errores (desaparecieron ANN001 y ANN201)
ruff format --check .              → 10 files already formatted
pytest -q                          → 28 passed, 1 xfailed
pytest tests/test_conversor.py -q  → 4 passed
git diff                           → 10 líneas cambiadas, todas firmas de funciones
```

## Paso 4 · Docstrings en lugar de comentarios

**Cambio:** los encabezados de `conversor.py`, `cli.py` y `conftest.py` pasaron a ser docstrings de módulo, y se quitaron las líneas que repetían el nombre del archivo. Cada función tiene un docstring con estilo Google (`Args`, `Returns`, `Raises` donde aplica). Los comentarios que explican líneas o constantes concretas se conservaron. El diff filtrado confirmó que no cambió ninguna línea de código.

```
ruff check --select D .            → All checks passed!
ruff check .                       → 14 errores (desaparecieron D100 y D103)
ruff format --check .              → 10 files already formatted
pytest -q                          → 28 passed, 1 xfailed
pytest tests/test_conversor.py -q  → 4 passed
help(conversor.convertir)          → muestra la descripción con Args, Returns y Raises
```

## Paso 5 · Constantes para las fórmulas de temperatura

**Cambio:** en `conversor.py` se agregaron `ESCALA_F_NUM = 9`, `ESCALA_F_DEN = 5` y `DESPLAZAMIENTO_F = 32`, y las dos fórmulas las usan con el mismo orden de operaciones. `f2c` conserva el error `* 9 / 5` hasta el paso 10.

```
pytest -q                          → 28 passed, 1 xfailed
pytest tests/test_conversor.py -q  → 4 passed
ruff check .                       → 14 errores (sin cambios, como estaba previsto)
ruff format --check .              → 10 files already formatted
grep 9|5|32 en conversor.py        → solo en las definiciones de las constantes
equivalencia sobre 221 900 valores → 0 diferencias en c2f y en f2c
```

## Paso 6 · Centralizar las validaciones duplicadas

**Cambio:** en `conversor.py` se crearon `_validar_sobre_cero_absoluto(celsius)` y `_validar_no_negativo(valor, magnitud)`. Las 6 funciones de conversión las llaman en lugar de repetir el `if ...: raise`. `fahrenheit_a_celsius` sigue validando el resultado hasta el paso 10.

```
grep -c "raise ValueError" conversor.py  → 2 (antes 6)
pytest -q                                → 28 passed, 1 xfailed
pytest tests/test_conversor.py -q        → 4 passed
ruff check .                             → 6 errores: TRY003 ×3, EM102 ×2, EM101 ×1
ruff format --check .                    → 10 files already formatted
```

## Paso 7 · Excepción propia con mensajes centralizados

**Cambio:** en `conversor.py` se creó `ErrorConversion(ValueError)` con los mensajes `TEMPERATURA_BAJO_CERO_ABSOLUTO` y `MAGNITUD_NEGATIVA` como atributos de clase. Las validaciones lanzan `ErrorConversion`, y el mensaje del `KeyError` de `convertir` se asigna a una variable antes del `raise`. Los docstrings se actualizaron. `cli.py` no cambió.

```
ruff check .                       → All checks passed!
ruff format --check .              → 10 files already formatted
pytest -q                          → 28 passed, 1 xfailed
pytest tests/test_conversor.py -q  → 4 passed
python cli.py -1 kg2lb             → "Error: La masa no puede ser negativa", código 1
python cli.py -300 c2f             → "Error: Temperatura por debajo del cero absoluto", código 1
```

## Paso 8 · Registro de conversiones inmutable y con campos con nombre

**Cambio:**
- `conversor.py`: nueva clase `Conversion(NamedTuple)` con `funcion` y `descripcion`. `CONVERSIONES` está envuelto en `MappingProxyType` y `convertir` usa `CONVERSIONES[clave].funcion`.
- `cli.py`: `listar_conversiones` usa `conversion.descripcion`.
- `tests/test_caracterizacion.py`: nueva prueba `test_conversiones_es_de_solo_lectura`, que comprueba que asignar una clave lanza `TypeError`.

```
pytest -q                          → 29 passed, 1 xfailed
pytest tests/test_conversor.py -q  → 4 passed
ruff check .                       → All checks passed!
ruff format --check .              → 10 files already formatted
--listar antes vs. después         → idéntico byte a byte (cmp)
```

## Paso 9 · Quitar el uso de `KeyError` y el parche de las comillas

**Cambio:**
- `conversor.py`: nueva clase `ClaveNoSoportada(ErrorConversion, KeyError)`, que arma su mensaje con la clave pedida y las disponibles y redefine `__str__` para que salga sin comillas. `convertir` lanza `ClaveNoSoportada(clave, disponibles)`. Se actualizaron los docstrings de `ErrorConversion` y `convertir`.
- `cli.py`: captura solo `ErrorConversion` e imprime `f"Error: {error}"`. Se eliminó el parche `strip(chr(39))`.

```
pytest -q                          → 29 passed, 1 xfailed
pytest tests/test_conversor.py -q  → 4 passed  (test_convertir_clave_invalida sigue recibiendo KeyError)
ruff check .                       → All checks passed!
ruff format --check .              → sin cambios pendientes
grep chr(39) cli.py                → 0
str(error) contiene "'"            → False  (y sigue siendo ValueError y KeyError)
salida de la CLI antes vs. después → idéntica (cmp), con clave inválida, valor imposible y conversión válida
```

Con este paso terminan los pasos que no cambian el comportamiento.

## Paso 10 · Corregir `f2c`

*Este paso cambia el comportamiento a propósito.*

**Cambio:**
- `conversor.py`:
  - La fórmula pasa a `(fahrenheit - DESPLAZAMIENTO_F) * ESCALA_F_DEN / ESCALA_F_NUM`, es decir, `* 5 / 9`.
  - La validación se hace sobre la entrada. `_validar_sobre_cero_absoluto(temperatura, cero_absoluto)` recibe el límite de cada escala: c2f usa `CERO_ABSOLUTO_C` y f2c usa `CERO_ABSOLUTO_F`.
  - Nueva constante `CERO_ABSOLUTO_F = -459.67`, escrita como valor fijo: calcularla desde `CERO_ABSOLUTO_C` da `-459.66999999999996` y rechazaría −459.67 °F, que es válido.
- `tests/test_caracterizacion.py`: se quitó el `xfail` de `test_convertir_f2c_punto_ebullicion`. Se agregaron 4 casos válidos (212 → 100, −40 → −40, −200 → −128.8889, −459.67 → −273.15) y 2 casos con error (−459.68 °F y −500 °F).
- `CLAUDE.md`: se actualizó para describir el código actual (`ErrorConversion`, `ClaveNoSoportada`, `Conversion`, el nuevo archivo de pruebas y estos documentos del refactor) y se quitó la nota sobre el error de `f2c`.

```
pytest -q                          → 36 passed  (antes 29 passed, 1 xfailed; ya no hay xfail)
pytest tests/test_conversor.py -q  → 4 passed
ruff check .                       → All checks passed!
ruff format --check .              → sin cambios pendientes
python cli.py 212 f2c              → 100.0
python cli.py -200 f2c             → -128.8889   (antes daba error)
python cli.py -500 f2c             → Error: Temperatura por debajo del cero absoluto   (antes lo aceptaba)
python cli.py -459.67 f2c          → -273.15
```

En el primer intento ruff marcó un docstring de 90 caracteres (E501, el límite es 88). Se acortó y se volvió a verificar todo.

## Paso 11 · Rechazar `nan` e `inf`

*Este paso cambia el comportamiento.*

**Cambio:**
- `conversor.py`: nuevo mensaje `ErrorConversion.VALOR_NO_FINITO = "El valor debe ser un número finito"`. `convertir` comprueba `math.isfinite(valor)` después de revisar la clave y lanza `ErrorConversion` si el valor no es finito. Se actualizó su docstring.
- `tests/test_caracterizacion.py`: 3 casos nuevos en la prueba de valores imposibles (`nan`, `inf` y `-inf`) y la prueba nueva `test_cli_valor_no_finito`.

```
pytest -q                          → 40 passed  (antes 36)
pytest tests/test_conversor.py -q  → 4 passed
ruff check .                       → All checks passed!
ruff format --check .              → sin cambios pendientes
```

| Comando | Antes | Después |
|---|---|---|
| `python cli.py nan c2f` | `nan`, código 0 | `Error: El valor debe ser un número finito`, código 1 |
| `python cli.py inf km2mi` | `inf`, código 0 | el mismo error, código 1 |
| `python cli.py -- -inf lb2kg` | `Error: La masa no puede ser negativa`, código 1 | el mismo error de número finito, código 1 |

Con `-inf` cambia el mensaje: antes daba el error de masa negativa y ahora el de número no finito, porque la comprobación de finitud va antes que las demás validaciones.

Durante la ejecución, el script de edición modificó `conversor.py` pero falló al editar el archivo de pruebas por un problema con el `\n` dentro del script, y ese archivo quedó sin cambios. Las pruebas se agregaron con el editor y se volvió a verificar todo.

## Paso 12 · Validar los argumentos con argparse

*Este paso cambia el comportamiento y la interfaz.*

**Cambio:**
- `cli.py`: la comprobación manual (`print_usage()`, un `print` a `stderr` y `return 2`) se reemplazó por `parser.error("se requieren VALOR y CLAVE (o usa --listar)")`. El docstring de `main` ahora dice que devuelve 0 o 1 y documenta `SystemExit(2)` en `Raises`.
- `tests/test_caracterizacion.py`: `test_cli_sin_argumentos` pasó a ser `test_cli_faltan_argumentos`, que prueba `[]` y `["5"]` y espera `SystemExit` con código 2, nada en `stdout`, y el uso y el error en `stderr`. La prueba nueva `test_cli_valor_no_numerico` fija que `abc` también termina con código 2, algo que antes no cubría ninguna prueba.
- `CLAUDE.md`: se actualizó la descripción de `main` (lanza `SystemExit(2)` en lugar de devolver 2).

```
pytest -q                          → 42 passed  (antes 40)
pytest tests/test_conversor.py -q  → 4 passed
ruff check .                       → All checks passed!
ruff format --check .              → sin cambios pendientes
```

| Comando | Antes | Después |
|---|---|---|
| `python cli.py` | uso en **stdout** + `Error: se requieren VALOR y CLAVE (o usa --listar)` en stderr, código 2 | uso + `conversor: error: se requieren VALOR y CLAVE (o usa --listar)`, **todo en stderr**, código 2 |
| `python cli.py 5` | igual que la fila anterior | igual que la fila anterior |
| `python cli.py abc c2f` | `argument valor: invalid float value: 'abc'`, código 2 | sin cambios |
| `python cli.py 100 c2f` | `212.0`, código 0 | sin cambios |

Desde la terminal el código de salida sigue siendo 2. Lo que cambia es que `main` como función lanza `SystemExit(2)` en lugar de devolver 2, y que el uso sale en `stderr`. Los mensajes propios de argparse (`conversor: error:`, `invalid float value`) salen en inglés, algo que ya pasaba antes con los valores no numéricos.

## Paso 13 · Llevar el redondeo a la CLI

*Este paso cambia el comportamiento de la biblioteca.*

**Cambio:**
- `conversor.py`: `convertir` devuelve `CONVERSIONES[clave].funcion(valor)` sin redondear. Su docstring lo dice explícitamente.
- `cli.py`: nueva constante `DECIMALES_SALIDA = 4`, y la salida es `print(round(resultado, DECIMALES_SALIDA))`. Se usó `round()` y no `f"{x:.4f}"` para que la salida no cambie: con `.4f`, 212 se mostraría como `212.0000` en lugar de `212.0`.
- `tests/test_caracterizacion.py`:
  - `test_convertir_valores_conocidos` usa `pytest.approx(esperado, abs=5e-5)`, la diferencia máxima que deja el redondeo a 4 decimales.
  - `test_convertir_redondea_a_4_decimales` pasó a ser `test_convertir_no_redondea` y espera `0.621371`.
  - Nueva prueba `test_cli_redondea_a_4_decimales`, que comprueba que la CLI muestra `0.6214`.
- `CLAUDE.md`: se actualizó la descripción de `convertir`.

```
pytest -q                          → 43 passed  (antes 42)
pytest tests/test_conversor.py -q  → 4 passed
ruff check .                       → All checks passed!
ruff format --check .              → sin cambios pendientes
convertir(1, "km2mi")              → 0.621371   (antes 0.6214)
python cli.py 1 km2mi              → 0.6214     (igual que antes)
salida de main() antes vs. después → idéntica en 1872 casos
```

La última comparación cubre las 6 conversiones, cada una con 12 valores fijos y 300 valores aleatorios, y revisa en cada caso el código de salida, `stdout` y `stderr`.

---

## Estado final

Se ejecutaron los 14 pasos de `PLAN.md`.

- **Ruff:** 0 errores con 12 grupos de reglas activos. Al principio había 47.
- **Pruebas:** 43 en verde, frente a las 4 originales, que siguen pasando.
- **Smells de `DIAGNOSTICO.md`:** quedan resueltos todos menos el 14, INP001 (falta `__init__.py` en `tests/`), que el plan dejó fuera porque esa regla no se activó.
