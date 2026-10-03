"""Cliente da PokeAPI: todo o HTTP do app passa por aqui.

Não usa print nem input. Recebe parâmetros, faz a requisição e
devolve objetos prontos (a tradução do JSON fica no mapper).
"""
import requests

from pokedex.mappers.pokeapi import page_from_api, pokemon_from_api
from pokedex.models.pokemon import Pokemon, PokemonPage


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
        data = self._get(f"/pokemon/{key}")
        return pokemon_from_api(data)

    def list_pokemon(self, offset: int = 0, limit: int = 20) -> PokemonPage:
        data = self._get("/pokemon", params={"offset": offset, "limit": limit})
        return page_from_api(data, offset, limit)

    def _get(self, path: str, params: dict | None = None) -> dict:
        """GET na API com timeout. Único lugar que chama o requests."""
        response = self.session.get(
            f"{self.base_url}{path}", params=params, timeout=self.timeout
        )
        # 4xx/5xx viram exceção aqui, perto da causa (na Etapa 5 a gente traduz)
        response.raise_for_status()
        return response.json()
