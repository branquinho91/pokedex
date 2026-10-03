"""Exceções do app: erros com nome e sentido para o domínio.

Hierarquia (quem captura a de cima, captura todas as de baixo):

    PokedexError
    ├── InvalidInputError
    ├── PokemonNotFoundError
    └── APIError
        ├── APITimeoutError
        ├── APIUnavailableError
        └── InvalidResponseError

A mensagem de cada exceção já é pensada para o usuário final.
"""


class PokedexError(Exception):
    """Base de todos os erros esperados do app. A CLI captura esta."""


class InvalidInputError(PokedexError):
    """O usuário digitou algo que não dá para buscar."""


class PokemonNotFoundError(PokedexError):
    """A API respondeu 404: o Pokémon não existe."""


class APIError(PokedexError):
    """Falha ao falar com a PokeAPI."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code  # None quando nem houve resposta


class APITimeoutError(APIError):
    """A API demorou mais que o timeout para responder."""


class APIUnavailableError(APIError):
    """Não deu para conectar: sem internet, DNS falhou ou API fora do ar."""


class InvalidResponseError(APIError):
    """A API respondeu, mas com um JSON inválido ou num formato inesperado."""
