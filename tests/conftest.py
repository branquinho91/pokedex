"""Fixtures compartilhadas: o pytest carrega este arquivo sozinho.

Os JSONs aqui são versões mínimas dos da PokeAPI, só com os campos
que o app usa. Nenhum teste acessa a internet.
"""
import pytest


@pytest.fixture
def pikachu_json() -> dict:
    """Resposta de /pokemon/pikachu, enxugada."""
    return {
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "types": [
            {"slot": 1, "type": {"name": "electric", "url": ".../type/13/"}},
        ],
        "abilities": [
            {"ability": {"name": "static", "url": "..."}, "is_hidden": False, "slot": 1},
            {"ability": {"name": "lightning-rod", "url": "..."}, "is_hidden": True, "slot": 3},
        ],
        "stats": [
            {"base_stat": 35, "effort": 0, "stat": {"name": "hp", "url": "..."}},
            {"base_stat": 55, "effort": 0, "stat": {"name": "attack", "url": "..."}},
            {"base_stat": 40, "effort": 0, "stat": {"name": "defense", "url": "..."}},
            {"base_stat": 50, "effort": 0, "stat": {"name": "special-attack", "url": "..."}},
            {"base_stat": 50, "effort": 0, "stat": {"name": "special-defense", "url": "..."}},
            {"base_stat": 90, "effort": 2, "stat": {"name": "speed", "url": "..."}},
        ],
        "moves": ["...centenas de golpes que o app ignora..."],
    }


@pytest.fixture
def first_page_json() -> dict:
    """Resposta de /pokemon?offset=0&limit=2."""
    return {
        "count": 1351,
        "next": "https://pokeapi.co/api/v2/pokemon?offset=2&limit=2",
        "previous": None,
        "results": [
            {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
            {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
        ],
    }
