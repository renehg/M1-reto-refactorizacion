# Conversor de unidades

Conversor de unidades de línea de comandos en Python. Convierte temperatura (°C ↔ °F), distancia (km ↔ mi) y masa (kg ↔ lb), y rechaza valores físicamente imposibles: temperaturas por debajo del cero absoluto, distancias o masas negativas, `nan` e `inf`.

Este repositorio es la entrega del reto de refactorización asistida por IA. El proceso está documentado en `docs/bitacora.md`.

## Requisitos previos

- Python 3.12 o superior.
- El programa solo usa la biblioteca estándar.
- Para desarrollo: `pytest>=8.0` y `ruff>=0.16`, declarados en `requirements.txt`.

## Instalación

```bash
git clone <url-del-repositorio>
cd proyecto
python -m venv .venv
.venv\Scripts\Activate.ps1        # PowerShell en Windows
# source .venv/bin/activate       # Linux o macOS
pip install -r requirements.txt
```

## Uso

```bash
python src/cli.py 100 c2f    # 212.0
python src/cli.py 1 km2mi    # 0.6214
python src/cli.py --listar   # muestra las claves disponibles
```

| Clave | Conversión |
|---|---|
| `c2f` | Celsius → Fahrenheit |
| `f2c` | Fahrenheit → Celsius |
| `km2mi` | Kilómetros → millas |
| `mi2km` | Millas → kilómetros |
| `kg2lb` | Kilogramos → libras |
| `lb2kg` | Libras → kilogramos |

Códigos de salida: `0` si la conversión sale bien, `1` si el valor no es válido o la clave no existe, y `2` si faltan argumentos o no son válidos.

Para usarlo como biblioteca, `convertir(valor, clave)` devuelve el resultado sin redondear. La CLI lo muestra con 4 decimales.

## Pruebas

```bash
pytest                                  # todas las pruebas
pytest tests/test_conversor.py -q       # solo las 4 pruebas originales
```

## Linter

```bash
ruff check .            # reglas configuradas en pyproject.toml
ruff format --check .   # formato
```

## Documentación del reto

| Archivo | Contenido |
|---|---|
| `CLAUDE.md` | Guía del proyecto para Claude Code |
| `MAPA_GENERAL.md` | Mapa del proyecto antes del refactor |
| `DIAGNOSTICO.md` | Code smells identificados |
| `RIESGOS.md` | Qué cubrían las pruebas originales y qué no |
| `PLAN.md` | Plan de 14 pasos, de menor a mayor riesgo |
| `docs/bitacora.md` | Por qué, qué se cambió y cómo se verificó cada paso |
| `docs/reflexion.md` | Aprendizajes y conclusiones |
| `docs/evidenciaestadoactual/` | Salidas de pytest y ruff antes del refactor |
| `docs/evidenciaestadofinal/` | Salidas de pytest y ruff después del refactor |
