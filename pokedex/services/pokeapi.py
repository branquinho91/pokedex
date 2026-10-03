"""Cliente da PokeAPI: todo o HTTP do app passa por aqui.

Não usa print nem input. Recebe parâmetros, faz a requisição e
devolve objetos prontos (a tradução do JSON fica no mapper).
Erros do requests nunca saem daqui: viram exceções de errors.py.
"""
import re

import requests

from pokedex.mappers.pokeapi import page_from_api, pokemon_from_api
from pokedex.models.pokemon import Pokemon, PokemonPage
from pokedex.services.errors import (
    APIError,
    APITimeoutError,
    APIUnavailableError,
    InvalidInputError,
    InvalidResponseError,
    PokemonNotFoundError,
)

# Nomes da PokeAPI: minúsculas, números e hífen (ex.: "mr-mime", "porygon-z")
_VALID_KEY = re.compile(r"[a-z0-9-]+")


class PokeAPIClient:
    BASE_URL = "https://pokeapi.co/api/v2"

    def __init__(self, base_url: str = BASE_URL, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        # A Session reaproveita a conexão entre requisições
        self.session = requests.Session()

    def get_pokemon(self, name_or_id: str | int) -> Pokemon:
        # " Pikachu " -> "pikachu"; 25 -> "25"
        key = str(name_or_id).strip().lower()
        if not key:
            raise InvalidInputError("Please type a Pokémon name or number.")
        if not _VALID_KEY.fullmatch(key):
            raise InvalidInputError(
                f"Invalid name: '{key}'. Use letters, numbers and hyphens (e.g. mr-mime)."
            )

        try:
            data = self._get(f"/pokemon/{key}")
        except APIError as err:
            if err.status_code == 404:
                raise PokemonNotFoundError(f"Pokémon '{key}' not found.") from err
            raise  # qualquer outro erro sobe do jeito que veio

        try:
            return pokemon_from_api(data)
        except (KeyError, TypeError, ValueError) as err:
            raise InvalidResponseError("The PokeAPI sent data in an unexpected format.") from err

    def list_pokemon(self, offset: int = 0, limit: int = 20) -> PokemonPage:
        data = self._get("/pokemon", params={"offset": offset, "limit": limit})
        try:
            return page_from_api(data, offset, limit)
        except (KeyError, TypeError, ValueError) as err:
            raise InvalidResponseError("The PokeAPI sent data in an unexpected format.") from err

    def _get(self, path: str, params: dict | None = None) -> dict:
        """GET na API com timeout. Único lugar que chama o requests."""
        try:
            response = self.session.get(
                f"{self.base_url}{path}", params=params, timeout=self.timeout
            )
            response.raise_for_status()
        # Timeout antes de ConnectionError: ConnectTimeout é filho dos dois
        except requests.Timeout as err:
            raise APITimeoutError("The PokeAPI took too long to respond. Try again.") from err
        except requests.ConnectionError as err:
            raise APIUnavailableError("Could not reach the PokeAPI. Check your connection.") from err
        except requests.HTTPError as err:
            status = err.response.status_code
            raise APIError(f"The PokeAPI returned an error (HTTP {status}).", status) from err
        except requests.RequestException as err:  # qualquer outra falha do requests
            raise APIError("Unexpected error talking to the PokeAPI.") from err

        try:
            return response.json()
        except ValueError as err:  # corpo não é JSON
            raise InvalidResponseError("The PokeAPI sent an invalid response.") from err
