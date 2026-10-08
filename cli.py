"""Interfaz de línea de comandos del conversor de unidades.

Uso: python cli.py VALOR CLAVE   |   python cli.py --listar
"""

import argparse
import sys

from conversor import CONVERSIONES, ErrorConversion, convertir

# Decimales con los que se muestra el resultado
DECIMALES_SALIDA = 4


def construir_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos de la CLI."""
    parser = argparse.ArgumentParser(
        prog="conversor",
        description="Conversor de unidades de línea de comandos",
    )
    parser.add_argument(
        "valor",
        nargs="?",
        type=float,
        help="Valor numérico a convertir",
    )
    parser.add_argument(
        "clave",
        nargs="?",
        help="Clave de conversión (ej. c2f, km2mi). Usa --listar para verlas todas",
    )
    parser.add_argument(
        "--listar",
        action="store_true",
        help="Muestra las conversiones disponibles",
    )
    return parser


def listar_conversiones() -> None:
    """Imprime la tabla de conversiones disponibles."""
    print("Conversiones disponibles:")
    for clave, conversion in sorted(CONVERSIONES.items()):
        print(f"  {clave:8s} {conversion.descripcion}")


def main(argv: list[str] | None = None) -> int:
    """Ejecuta la CLI y devuelve el código de salida.

    Args:
        argv: Argumentos de línea de comandos; si es ``None`` se usa ``sys.argv``.

    Returns:
        0 si todo sale bien y 1 si falla la conversión.

    Raises:
        SystemExit: Con código 2 si los argumentos son inválidos o faltan.
    """
    parser = construir_parser()
    args = parser.parse_args(argv)

    if args.listar:
        listar_conversiones()
        return 0

    # Sin --listar se requieren ambos argumentos posicionales
    if args.valor is None or args.clave is None:
        parser.error("se requieren VALOR y CLAVE (o usa --listar)")

    try:
        resultado = convertir(args.valor, args.clave)
    except ErrorConversion as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(round(resultado, DECIMALES_SALIDA))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
