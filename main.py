"""Ponto de entrada da Pokedex CLI: python main.py"""
from pokedex.cli.menu import run


def main() -> None:
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")


if __name__ == "__main__":
    main()
