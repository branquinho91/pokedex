"""Mapper: dict entra, objeto sai. Funções puras, sem truque nenhum."""
import pytest

from pokedex.mappers.pokeapi import page_from_api, pokemon_from_api
from pokedex.models.pokemon import Ability, Stat


def test_campos_simples(pikachu_json):
    pokemon = pokemon_from_api(pikachu_json)
    assert pokemon.id == 25
    assert pokemon.name == "pikachu"


def test_converte_decimetros_e_hectogramas(pikachu_json):
    pokemon = pokemon_from_api(pikachu_json)
    assert pokemon.height_m == 0.4
    assert pokemon.weight_kg == 6.0


def test_tipos_mantem_a_ordem_dos_slots(pikachu_json):
    pikachu_json["types"].append({"slot": 2, "type": {"name": "flying", "url": "..."}})
    assert pokemon_from_api(pikachu_json).types == ["electric", "flying"]


def test_habilidades_indicam_a_oculta(pikachu_json):
    assert pokemon_from_api(pikachu_json).abilities == [
        Ability(name="static", is_hidden=False),
        Ability(name="lightning-rod", is_hidden=True),
    ]


def test_stats(pikachu_json):
    stats = pokemon_from_api(pikachu_json).stats
    assert len(stats) == 6
    assert stats[0] == Stat(name="hp", value=35)
    assert stats[-1] == Stat(name="speed", value=90)


def test_json_sem_campo_obrigatorio_lanca_keyerror(pikachu_json):
    # O mapper não trata erro: quem traduz é o service
    del pikachu_json["types"]
    with pytest.raises(KeyError):
        pokemon_from_api(pikachu_json)


# --- Listagem ---


def test_pagina(first_page_json):
    page = page_from_api(first_page_json, offset=0, limit=2)
    assert [(s.id, s.name) for s in page.results] == [(1, "bulbasaur"), (2, "ivysaur")]
    assert page.total == 1351
    assert (page.offset, page.limit) == (0, 2)


def test_primeira_pagina_nao_tem_anterior(first_page_json):
    page = page_from_api(first_page_json, offset=0, limit=2)
    assert page.has_next is True
    assert page.has_previous is False


def test_ultima_pagina_nao_tem_proxima(first_page_json):
    first_page_json["next"] = None
    first_page_json["previous"] = "https://pokeapi.co/api/v2/pokemon?offset=0&limit=2"
    page = page_from_api(first_page_json, offset=2, limit=2)
    assert page.has_next is False
    assert page.has_previous is True


def test_id_vem_da_url_e_nao_da_posicao(first_page_json):
    # Depois do 1025 vêm as formas alternativas, com ids a partir de 10001
    first_page_json["results"] = [
        {"name": "golisopod-mega", "url": "https://pokeapi.co/api/v2/pokemon/10316/"},
    ]
    page = page_from_api(first_page_json, offset=1340, limit=20)
    assert page.results[0].id == 10316
