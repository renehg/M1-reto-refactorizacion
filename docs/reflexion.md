# Reflexión sobre el reto

## Qué funcionó

**Analizar antes de tocar el código.** Antes de cambiar una sola línea se generaron tres documentos de solo lectura: `MAPA_GENERAL.md`, `DIAGNOSTICO.md` y `RIESGOS.md`. El diagnóstico encontró algo que ruff no podía ver: `fahrenheit_a_celsius` tenía la fórmula invertida (212 °F daba 324 °C). Si hubiera empezado por lo que marca el linter, habría dejado el código "limpio" pero con el error dentro.

**Pruebas de caracterización primero.** `RIESGOS.md` mostró que las 4 pruebas originales no tocaban la CLI ni las validaciones, así que casi cualquier cambio podía romper algo sin que nada fallara. Fijar el comportamiento con 25 pruebas antes de refactorizar convirtió cada paso en algo verificable. La decisión de escribir la prueba de `f2c` con el valor correcto y marcarla `xfail(strict=True)` evitó congelar el error en las pruebas.

**Un plan ordenado por riesgo, un cambio por paso.** Separar los pasos que no cambian el comportamiento (0 a 9) de los que sí lo cambian (10 a 13) hizo que cada diff fuera pequeño y fácil de revisar. Registrar en cada paso el resultado de pytest y de ruff dejó una evidencia clara: ruff pasó de 47 errores a 0 en el paso 7, y las pruebas de 4 a 43.

**Verificar lo que las pruebas no cubren.** En los pasos donde la salida debía quedar igual se comparó antes y después de forma directa: `--listar` byte a byte en el paso 8 y 1872 casos de la CLI en el paso 13.

## Qué no funcionó o costó más

- La evidencia inicial de ruff se generó con `ruff check src`, pero la carpeta `src/` no existía, así que el archivo guardaba un error de E/S y no el estado real del código.
- Sin configuración de ruff en el repositorio, el resultado dependía de la máquina. Hubo que fijar las reglas en `pyproject.toml` antes de poder medir el avance.
- Claude Code no lee `.claudeignore`. Para que no leyera cachés, `.venv` ni evidencias, hubo que repetir las rutas como reglas `permissions.deny` en `.claude/settings.json`.
- En el paso 11 un script de edición falló por un `\n` y dejó un archivo sin cambios. Se detectó porque la verificación se repetía al final de cada paso.
- Algunos detalles se resolvieron solo al revisar con cuidado: `CERO_ABSOLUTO_F` calculado desde °C daba `-459.66999999999996` y rechazaba un valor válido, y usar `f"{x:.4f}"` en lugar de `round()` habría cambiado la salida de `212.0` a `212.0000`.

## Lo que aprendí sobre trabajar con IA

- Darle contexto persistente (`CLAUDE.md`) y pedirle documentos intermedios da mejores resultados que pedirle directamente "refactoriza este código".
- La IA propone y ejecuta rápido, pero la verificación tiene que ser automática y estar en cada paso: pruebas, linter y comparación de salidas.
- Conviene pedirle que separe el análisis de la edición. Los modos de solo lectura sirvieron para entender el código sin riesgo de cambiarlo.

## Qué haría diferente

- Guardar los prompts en la bitácora en el momento, en lugar de reconstruirlos al final.
- Revisar desde el principio que la evidencia inicial refleje el código real.
- Activar INP001 y agregar `tests/__init__.py`, el único smell que quedó pendiente.
