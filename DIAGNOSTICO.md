# Diagnóstico de code smells

Análisis del estado del código antes del refactor. No se modificó ningún archivo; ruff se ejecutó con `--no-cache`.

**Resumen:** 9 smells de diseño y 6 de estilo. Ruff detecta casi todos los de estilo, pero ninguno de los de diseño, incluido el más grave: el error de fórmula en `fahrenheit_a_celsius`.

## Ejecución de ruff

`ruff check src` falla con **E902** porque la carpeta `src/` no existe. Esto explica el `E902 io-error` guardado en `docs/evidenciaestadoactual/00_ruff_inicio.txt`: esa evidencia no refleja el estado real del código. Por eso se usaron dos comandos:

- `ruff check .` encuentra **1 error, I001**: los imports de `tests/test_conversor.py` están desordenados.
- `ruff check . --select ALL` activa todas las reglas y encuentra **71 errores**. Se usó para identificar qué regla detecta cada smell.

## Smells de diseño (ruff no detecta ninguno)

| # | Archivo y función | Tipo de smell | Por qué es un problema |
|---|---|---|---|
| 1 | `conversor.py` · `fahrenheit_a_celsius` | **Error de lógica** y validación en el lugar equivocado | Usa `* 9 / 5` en vez de `* 5 / 9`, así que 212 °F da 324. Además valida el resultado y no la entrada, al revés que `celsius_a_fahrenheit`. Por eso rechaza valores válidos, como −200 °F, y acepta valores imposibles, como −500 °F. |
| 2 | `conversor.py` · `km_a_millas`, `millas_a_km`, `kg_a_libras`, `libras_a_kg` | **Código duplicado** | Las cuatro funciones repiten el mismo `if x < 0: raise ValueError(...)` y los mismos mensajes. Para cambiar una regla hay que editar varios lugares. |
| 3 | `conversor.py` · `celsius_a_fahrenheit`, `fahrenheit_a_celsius` | **Números mágicos** e inconsistencia | `9`, `5` y `32` están escritos directamente en las fórmulas, mientras que los factores de distancia y masa sí tienen constantes. PLR2004 no los detecta porque solo revisa comparaciones, no operaciones aritméticas. |
| 4 | `conversor.py` · `convertir` | **Excepción inadecuada** | Usa `KeyError` para un error que debe ver el usuario, y Python muestra el mensaje de un `KeyError` entre comillas. Eso obliga a escribir el arreglo del punto 5 en otro archivo. |
| 5 | `cli.py` · `main` | **Parche frágil** | `str(error).strip(chr(39))` quita las comillas que pone el `KeyError`, pero también borraría un apóstrofo legítimo al inicio o al final de cualquier mensaje. Además, `chr(39)` no deja claro que se refiere a `'`. Es la consecuencia del punto 4. |
| 6 | `conversor.py` · `CONVERSIONES` | **Estado global mutable** y obsesión por primitivos | Es un `dict` mutable que importa `cli.py`, así que cualquier módulo podría modificarlo. Cada entrada es una tupla posicional `(función, descripción)` que se desempaqueta con `funcion, _`. Una `NamedTuple` o una `dataclass` con `frozen=True` dejaría claro qué es cada campo y evitaría cambios accidentales. |
| 7 | `conversor.py` · `convertir` | **Responsabilidades mezcladas** | `round(..., 4)` es una decisión de presentación que vive en la lógica de dominio. Quien use `convertir` como biblioteca no puede obtener el valor completo. |
| 8 | `cli.py` · `main` | **Validación manual de argumentos** | Revisa a mano que existan `valor` y `clave` e imprime el uso por su cuenta, en lugar de dejárselo a argparse, por ejemplo con `parser.error()`. |
| 9 | `conversor.py` (todas) y `cli.py` · `construir_parser` | **Entrada sin validar** | `type=float` acepta `nan` e `inf`, y ninguna validación los rechaza. Por ejemplo, `python cli.py nan c2f` imprime `nan`. |

## Smells de estilo y mantenibilidad (ruff sí los detecta)

| # | Dónde | Tipo de smell | Regla de ruff | Comentario |
|---|---|---|---|---|
| 10 | `tests/test_conversor.py`, en los imports | Imports desordenados | **I001** | Es el único error con la configuración actual, y se corrige automáticamente con `--fix`. |
| 11 | Todas las funciones de `conversor.py` y `cli.py` | Faltan anotaciones de tipos | **ANN001**, **ANN201** | No hay contrato de tipos, así que nada impide pasar un `str` a `convertir`. |
| 12 | Todos los módulos y funciones | Comentarios en lugar de docstrings | **D100**, **D103** | Lo que explica cada función está en comentarios `#`, que `help()` y los IDE no muestran. Los encabezados del tipo `# conversor.py` repiten el nombre del archivo y no aportan nada. |
| 13 | `conversor.py`, los 7 `raise` | Mensajes de error literales y repetidos | **EM101**, **EM102**, **TRY003** | Confirma el smell del punto 2. Una excepción propia, por ejemplo `ErrorConversion`, centralizaría los mensajes. |
| 14 | `tests/` | Paquete implícito | **INP001** | Falta `__init__.py`. Ahora no afecta porque `conftest.py` resuelve los imports. |
| 15 | `tests/test_conversor.py` | Cobertura insuficiente | Ninguna | Faltan pruebas de `f2c`, `mi2km`, `kg2lb`, `lb2kg`, de los casos con `ValueError` y de toda la CLI. Por eso nadie detectó el error del punto 1. |

### Falsos positivos de `--select ALL`

- **T201** marca los `print` de `cli.py`, pero en una CLI son correctos.
- **S101** y **PLR2004** marcan `assert` y números literales en las pruebas, que es lo normal en pytest.
- **CPY001** pide un aviso de copyright en cada archivo, algo que este proyecto no necesita.

### A nivel de proyecto

- No hay configuración de ruff en el repositorio (ni `pyproject.toml` ni `ruff.toml`). Sin embargo, I001 no está entre las reglas por defecto, así que la configuración activa probablemente viene de fuera del proyecto y otra persona podría obtener resultados distintos.
- `ruff` está instalado en `.venv` pero no aparece en `requirements.txt`.

## Prioridad sugerida

1. **Smell 1:** es un error real.
2. **Smell 15:** pruebas que lo cubran.
3. **Smells 4 y 5 juntos:** al cambiar la excepción ya no hace falta el parche de `cli.py`.
