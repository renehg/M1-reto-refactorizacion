# Mapa general del proyecto

Conversor de unidades de línea de comandos en Python. Todo el código está en la raíz del repositorio (no hay carpeta `src/`).

## Código

| Archivo | Qué hace |
|---|---|
| `conversor.py` | Lógica pura: 6 funciones de conversión (`c2f`, `f2c`, `km2mi`, `mi2km`, `kg2lb`, `lb2kg`) que validan su entrada y lanzan `ValueError` ante valores imposibles; el registro `CONVERSIONES`; y `convertir(valor, clave)`, el punto de entrada, que lanza `KeyError` si la clave no existe y redondea a 4 decimales. |
| `cli.py` | Interfaz con argparse: `construir_parser()`, `listar_conversiones()` y `main(argv)`, que devuelve 0 (éxito), 1 (error de conversión) o 2 (faltan argumentos). Uso: `python cli.py VALOR CLAVE` o `python cli.py --listar`. |
| `conftest.py` | Solo comentarios; su presencia hace que pytest agregue la raíz a `sys.path`. |
| `tests/test_conversor.py` | 4 pruebas de `conversor.py` (2 de `c2f`, 1 de `km2mi`, 1 de clave inválida). `cli.py` no tiene pruebas. |

## Configuración y documentación

| Archivo | Qué hace |
|---|---|
| `requirements.txt` | Declara solo `pytest>=8.0`. |
| `.gitignore` | Excluye `.venv/`, `__pycache__/`, `.pytest_cache/` y `.ruff_cache/`. |
| `.claude/settings.json` | Reglas `permissions.deny` que impiden a Claude Code leer cachés, `.venv`, evidencias y archivos `.env`. |
| `.claudeignore` | Mismas rutas; Claude Code no lo usa, sirve como documentación. |
| `CLAUDE.md` | Guía del proyecto para Claude Code. |
| `docs/evidenciaestadoactual/` | Salidas de pytest y ruff antes del refactor (archivos en UTF-16). |
| `.venv/` | Entorno virtual con pytest y ruff (fuera de git). |

## Relaciones

```
cli.py ──────────────────► conversor.py   (CONVERSIONES, convertir)
tests/test_conversor.py ─► conversor.py   (celsius_a_fahrenheit, km_a_millas, convertir)
```

`conversor.py` no importa nada. No hay dependencias circulares. `conftest.py` es lo que permite el import desde `tests/`.

## Dependencias externas

- **En ejecución:** ninguna; solo biblioteca estándar (`argparse`, `sys`).
- **En desarrollo:** `pytest` (declarado en `requirements.txt`) y `ruff` (instalado en `.venv`, pero no declarado).

## Estado global compartido

Todo vive a nivel de módulo en `conversor.py`:

- `FACTOR_KM_A_MILLAS`, `FACTOR_KG_A_LIBRAS`, `CERO_ABSOLUTO_C`: constantes.
- `CONVERSIONES`: `dict` mutable importado por `cli.py`. Hoy solo se lee, pero cualquier módulo que lo importe podría modificarlo.

No hay variables de entorno, configuración en tiempo de ejecución ni otro estado. La única E/S son los `print` y la escritura a `stderr` de `cli.py`.
