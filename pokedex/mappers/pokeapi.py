"""Tradução do formato da PokeAPI para os nossos models.

É o único lugar do app que conhece o formato do JSON da PokeAPI.
Se a API mudar, a correção fica aqui.
"""
from pokedex.models.pokemon import Pokemon, PokemonPage, PokemonSummary, Stat


def pokemon_from_api(data: dict) -> Pokemon:
    """Monta um Pokemon a partir do JSON de /api/v2/pokemon/{nome_ou_id}."""
    return Pokemon(
        id=data["id"],
        name=data["name"],
        # A API manda decímetros e hectogramas: ÷ 10 vira metro e kg
        height_m=data["height"] / 10,
        weight_kg=data["weight"] / 10,
        types=[t["type"]["name"] for t in data["types"]],
        abilities=[a["ability"]["name"] for a in data["abilities"]],
        stats=[Stat(name=s["stat"]["name"], value=s["base_stat"]) for s in data["stats"]],
    )


def page_from_api(data: dict, offset: int, limit: int) -> PokemonPage:
    """Monta uma PokemonPage a partir do JSON de /api/v2/pokemon?offset=&limit=."""
    return PokemonPage(
        results=[
            PokemonSummary(id=_id_from_url(r["url"]), name=r["name"])
            for r in data["results"]
        ],
        total=data["count"],
        offset=offset,
        limit=limit,
        # next/previous vêm null (None) quando não existe a página
        has_next=data["next"] is not None,
        has_previous=data["previous"] is not None,
    )


def _id_from_url(url: str) -> int:
    """'https://pokeapi.co/api/v2/pokemon/25/' -> 25"""
    return int(url.rstrip("/").split("/")[-1])
