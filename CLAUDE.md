# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

Conversor de unidades de línea de comandos en Python, usado para el reto de refactorización de un curso. Todos los identificadores, comentarios, mensajes al usuario y nombres de pruebas están en **español**; el código nuevo debe seguir esa convención.

## Comandos

Hay un entorno virtual en `.venv/` (Windows) que ya tiene instalados `pytest` y `ruff`. `requirements.txt` solo declara `pytest`.

```bash
.venv/Scripts/activate                    # o .venv\Scripts\Activate.ps1 en PowerShell
pip install -r requirements.txt

python cli.py 100 c2f                     # convierte VALOR usando CLAVE
python cli.py --listar                    # muestra las claves de conversión disponibles

pytest                                    # ejecuta todas las pruebas
pytest tests/test_conversor.py::test_convertir_clave_invalida   # una sola prueba

ruff check .                              # lint
ruff format --check .                     # verifica el formato
```

Ejecuta los comandos desde la raíz del repositorio. El `conftest.py` de la raíz no tiene código a propósito: su presencia hace que pytest añada la raíz a `sys.path`, de modo que las pruebas pueden hacer `import conversor` sin instalar ningún paquete.

## Arquitectura

- `conversor.py`: lógica de conversión pura. Cada conversión es una función independiente que valida su entrada y lanza `ValueError` ante valores físicamente imposibles (temperaturas bajo el cero absoluto, distancias o masas negativas). Todas se registran en el diccionario `CONVERSIONES` como `clave -> (función, descripción)`. `convertir(valor, clave)` es el único punto de entrada: lanza `KeyError` si la clave no existe y redondea el resultado a 4 decimales.
- `cli.py`: envoltorio con argparse sobre `convertir`. `main(argv)` devuelve un código de salida en lugar de terminar el proceso (0 éxito, 1 error de conversión, 2 faltan argumentos), así que se puede probar pasándole `argv`. Captura `ValueError` y `KeyError`, y quita las comillas que Python añade al mensaje de un `KeyError`. `--listar` se genera directamente a partir de `CONVERSIONES`.

Para añadir una conversión, escribe la función en `conversor.py` y agrega una entrada en `CONVERSIONES`. La CLI y `--listar` la detectan automáticamente.

## Estado y evidencias del reto

- `tests/test_conversor.py` es parcial a propósito: `f2c`, las conversiones inversas y la CLI no tienen pruebas.
- `fahrenheit_a_celsius` usa `* 9 / 5` en lugar de `* 5 / 9`, así que `f2c` da resultados incorrectos (212 °F → 324 en vez de 100) y su validación del cero absoluto no es fiable.
- `docs/evidenciaestadoactual/` guarda las salidas de las herramientas antes del refactor (`00_pytest_inicio.txt`, `00_ruff_inicio.txt`). Los archivos están en UTF-16 porque se generaron con redirección de PowerShell. Si agregas evidencias nuevas, sigue la numeración (`01_...`).
