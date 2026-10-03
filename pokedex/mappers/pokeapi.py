"""Tradução do formato da PokeAPI para os nossos models.

É o único lugar do app que conhece o formato do JSON da PokeAPI.
Se a API mudar, a correção fica aqui.
"""
from pokedex.models.pokemon import Pokemon, Stat


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
