"""Representação própria de Pokémon: só os dados que o app usa.

Este módulo não sabe que existe HTTP, terminal nem PokeAPI. A tradução
do JSON da API para estes objetos fica em pokedex/mappers/pokeapi.py.
"""
from dataclasses import dataclass


@dataclass
class Stat:
    """Um stat base, ex.: Stat(name="hp", value=35)."""

    name: str
    value: int


@dataclass
class Ability:
    """Uma habilidade. Cada Pokémon tem no máximo uma oculta (hidden)."""

    name: str
    is_hidden: bool


@dataclass
class Pokemon:
    id: int
    name: str
    height_m: float  # em metros
    weight_kg: float  # em quilos
    types: list[str]
    abilities: list[Ability]
    stats: list[Stat]


@dataclass
class PokemonSummary:
    """Item da listagem: a API só manda nome + link, sem detalhes."""

    id: int
    name: str


@dataclass
class PokemonPage:
    """Uma página da listagem paginada."""

    results: list[PokemonSummary]
    total: int  # quantos Pokémon existem na API ao todo
    offset: int  # quantos foram pulados antes desta página
    limit: int  # tamanho da página
    has_next: bool
    has_previous: bool
