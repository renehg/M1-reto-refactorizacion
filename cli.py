# cli.py
# Interfaz de línea de comandos del conversor de unidades.
# Uso: python cli.py VALOR CLAVE   |   python cli.py --listar

import argparse
import sys

from conversor import CONVERSIONES, convertir


def construir_parser():
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


def listar_conversiones():
    # Imprime la tabla de conversiones disponibles
    print("Conversiones disponibles:")
    for clave, (_, descripcion) in sorted(CONVERSIONES.items()):
        print(f"  {clave:8s} {descripcion}")


def main(argv=None):
    parser = construir_parser()
    args = parser.parse_args(argv)

    if args.listar:
        listar_conversiones()
        return 0

    # Sin --listar se requieren ambos argumentos posicionales
    if args.valor is None or args.clave is None:
        parser.print_usage()
        print("Error: se requieren VALOR y CLAVE (o usa --listar)", file=sys.stderr)
        return 2

    try:
        resultado = convertir(args.valor, args.clave)
    except (ValueError, KeyError) as error:
        # KeyError envuelve el mensaje entre comillas; lo limpiamos para el usuario
        print(f"Error: {str(error).strip(chr(39))}", file=sys.stderr)
        return 1

    print(resultado)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
