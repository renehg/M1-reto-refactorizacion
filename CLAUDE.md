# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

Conversor de unidades de línea de comandos en Python, usado para el reto de refactorización de un curso. Todos los identificadores, comentarios, mensajes al usuario y nombres de pruebas están en **español**; el código nuevo debe seguir esa convención.

## Comandos

Hay un entorno virtual en `.venv/` (Windows) que ya tiene instalados `pytest` y `ruff`. `requirements.txt` declara ambos.

```bash
.venv/Scripts/activate                    # o .venv\Scripts\Activate.ps1 en PowerShell
pip install -r requirements.txt

python src/cli.py 100 c2f                 # convierte VALOR usando CLAVE
python src/cli.py --listar                # muestra las claves de conversión disponibles

pytest                                    # ejecuta todas las pruebas
pytest tests/test_conversor.py::test_convertir_clave_invalida   # una sola prueba

ruff check .                              # lint
ruff format --check .                     # verifica el formato
```

Ejecuta los comandos desde la raíz del repositorio. El código está en `src/`; `pyproject.toml` configura pytest con `pythonpath = ["src"]`, de modo que las pruebas pueden hacer `import conversor` sin instalar ningún paquete.

## Arquitectura

- `src/conversor.py`: lógica de conversión pura. Cada conversión es una función independiente que valida su entrada con `_validar_sobre_cero_absoluto` o `_validar_no_negativo` y lanza `ErrorConversion` (subclase de `ValueError`, con los mensajes como atributos de clase) ante valores físicamente imposibles. Todas se registran en `CONVERSIONES`, un `MappingProxyType` de solo lectura que mapea cada clave a un `Conversion(funcion, descripcion)`. `convertir(valor, clave)` es el único punto de entrada: lanza `ClaveNoSoportada` (subclase de `ErrorConversion` y de `KeyError`, con un `__str__` sin comillas) si la clave no existe, `ErrorConversion` si el valor no es finito, y devuelve el resultado sin redondear.
- `src/cli.py`: envoltorio con argparse sobre `convertir`. `main(argv)` devuelve 0 si todo sale bien y 1 si falla la conversión, así que se puede probar pasándole `argv`. Si faltan argumentos o no son válidos, usa `parser.error()`, que imprime el uso en `stderr` y lanza `SystemExit(2)`; en las pruebas se captura con `pytest.raises(SystemExit)`. Captura `ErrorConversion` e imprime su mensaje en `stderr`. `--listar` se genera directamente a partir de `CONVERSIONES`.

Para añadir una conversión, escribe la función en `src/conversor.py` y agrega una entrada `Conversion(...)` en `CONVERSIONES`. La CLI y `--listar` la detectan automáticamente.

## Estado y evidencias del reto

- `tests/test_conversor.py` tiene las 4 pruebas originales, que deben seguir pasando tras cada paso. `tests/test_caracterizacion.py` fija el comportamiento de todas las conversiones, las validaciones y la CLI.
- El refactor sigue `PLAN.md`; `docs/bitacora.md` registra los pasos ya ejecutados, su justificación y su verificación. `README.md` explica la instalación y el uso, y `docs/reflexion.md` recoge los aprendizajes del reto.
- `docs/evidenciaestadoactual/` guarda las salidas de las herramientas antes del refactor (`00_pytest_inicio.txt`, `00_ruff_inicio.txt`). Los archivos están en UTF-16 porque se generaron con redirección de PowerShell. Si agregas evidencias nuevas, sigue la numeración (`01_...`).
