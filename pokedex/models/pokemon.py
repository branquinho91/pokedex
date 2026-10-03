"""Representação própria de Pokémon: só os dados que o app usa.

Este módulo não sabe que existe HTTP nem terminal. Ele só transforma
o dict que veio da API em objetos Python.
"""
from dataclasses import dataclass


@dataclass
class Stat:
    """Um stat base, ex.: Stat(name="hp", value=35)."""

    name: str
    value: int


@dataclass
class Pokemon:
    id: int
    name: str
    height_m: float  # já convertido para metros
    weight_kg: float  # já convertido para quilos
    types: list[str]
    abilities: list[str]
    stats: list[Stat]

    @classmethod
    def from_api(cls, data: dict) -> "Pokemon":
        """Monta um Pokemon a partir do JSON de /api/v2/pokemon/{nome_ou_id}."""
        return cls(
            id=data["id"],
            name=data["name"],
            # A API manda decímetros e hectogramas: ÷ 10 vira metro e kg
            height_m=data["height"] / 10,
            weight_kg=data["weight"] / 10,
            types=[t["type"]["name"] for t in data["types"]],
            abilities=[a["ability"]["name"] for a in data["abilities"]],
            stats=[Stat(name=s["stat"]["name"], value=s["base_stat"]) for s in data["stats"]],
        )
