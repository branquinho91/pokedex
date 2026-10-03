"""CLI: formatação (funções puras) e fluxos com input simulado e cliente falso."""
import pytest

from pokedex.cli.menu import browse, format_page, format_pokemon, run, search
from pokedex.mappers.pokeapi import pokemon_from_api
from pokedex.models.pokemon import PokemonPage, PokemonSummary
from pokedex.services.errors import APIUnavailableError, PokemonNotFoundError


class FakeClient:
    """Finge ser o PokeAPIClient: mesmos métodos, sem internet.

    Tem 3 páginas de 2 Pokémon cada (total 6).
    """

    def __init__(self, pokemon=None, error=None):
        self.pokemon = pokemon
        self.error = error
        self.offsets_pedidos = []

    def get_pokemon(self, name_or_id):
        if self.error:
            raise self.error
        return self.pokemon

    def list_pokemon(self, offset=0, limit=20):
        if self.error:
            raise self.error
        self.offsets_pedidos.append(offset)
        ids = range(offset + 1, min(offset + limit, 6) + 1)
        return PokemonPage(
            results=[PokemonSummary(id=i, name=f"poke{i}") for i in ids],
            total=6,
            offset=offset,
            limit=limit,
            has_next=offset + limit < 6,
            has_previous=offset > 0,
        )


@pytest.fixture
def pikachu(pikachu_json):
    return pokemon_from_api(pikachu_json)


@pytest.fixture
def typing(monkeypatch):
    """Simula o usuário digitando: typing("1", "pikachu", "3")."""

    def _typing(*answers):
        answers_iter = iter(answers)
        monkeypatch.setattr("builtins.input", lambda prompt="": next(answers_iter))

    return _typing


# --- Formatação: recebem objeto, devolvem texto ---


def test_format_pokemon(pikachu):
    text = format_pokemon(pikachu)
    assert "#025 Pikachu" in text
    assert "Types:     Electric" in text
    assert "Height:    0.4 m" in text
    assert "Weight:    6.0 kg" in text
    assert "Abilities: Static, Lightning-Rod (hidden)" in text


def test_stats_com_rotulos_da_spec_e_alinhados(pikachu):
    lines = format_pokemon(pikachu).splitlines()
    stats = lines[lines.index("Stats") + 1 :]
    assert [line.split()[0] for line in stats] == ["HP", "Attack", "Defense", "Sp.", "Sp.", "Speed"]
    assert stats[0] == "  HP          35"
    assert len({len(line) for line in stats}) == 1  # todas do mesmo tamanho = alinhadas


def test_format_page_primeira_pagina():
    text = format_page(FakeClient().list_pokemon(0, 2))
    assert "Showing Pokémon 1-2 of 6" in text
    assert "1. Poke1" in text
    assert "[n] Next page" in text
    assert "[p] Previous page" not in text  # não tem anterior
    assert "[q] Quit" in text


# --- Fluxos ---


def test_search_mostra_o_pokemon(typing, capsys, pikachu):
    typing("pikachu")
    search(FakeClient(pokemon=pikachu))
    assert "#025 Pikachu" in capsys.readouterr().out


@pytest.mark.parametrize(
    "error",
    [PokemonNotFoundError("Pokémon 'xyz' not found."), APIUnavailableError("Could not reach the PokeAPI.")],
)
def test_search_mostra_erro_sem_traceback(typing, capsys, error):
    typing("xyz")
    search(FakeClient(error=error))  # não pode levantar exceção
    assert str(error) in capsys.readouterr().out


def test_browse_navega_n_n_p_q(typing):
    api = FakeClient()
    typing("n", "n", "p", "q")
    browse(api, limit=2)
    assert api.offsets_pedidos == [0, 2, 4, 2]


def test_browse_p_na_primeira_pagina_avisa_e_nao_busca_de_novo(typing, capsys):
    api = FakeClient()
    typing("p", "x", "q")
    browse(api, limit=2)
    out = capsys.readouterr().out
    assert "This is the first page." in out
    assert "Type n, p or q." in out
    assert api.offsets_pedidos == [0]


def test_browse_n_na_ultima_pagina(typing, capsys):
    api = FakeClient()
    typing("n", "n", "n", "q")
    browse(api, limit=2)
    assert "This is the last page." in capsys.readouterr().out
    assert api.offsets_pedidos == [0, 2, 4]


def test_menu_principal_opcao_invalida_e_sair(typing, capsys):
    typing("9", "3")
    run(FakeClient())
    out = capsys.readouterr().out
    assert "Invalid option. Type 1, 2 or 3." in out
    assert "Bye!" in out
