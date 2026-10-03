"""Service: o HTTP é trocado por um Mock, então dá pra forçar qualquer cenário."""
import json
from unittest.mock import Mock

import pytest
import requests

from pokedex.services.errors import (
    APIError,
    APITimeoutError,
    APIUnavailableError,
    InvalidInputError,
    InvalidResponseError,
    PokemonNotFoundError,
)
from pokedex.services.pokeapi import PokeAPIClient


def fake_response(status: int = 200, body: dict | bytes = b"{}") -> requests.Response:
    """Monta uma resposta do requests 'na mão', sem rede."""
    response = requests.Response()
    response.status_code = status
    response._content = body if isinstance(body, bytes) else json.dumps(body).encode()
    response.url = "https://fake/api"
    return response


@pytest.fixture
def api() -> PokeAPIClient:
    """Cliente com o session.get trocado por um Mock (que registra as chamadas)."""
    client = PokeAPIClient(timeout=5)
    client.session.get = Mock()
    return client


# --- Caminho feliz ---


def test_get_pokemon_devolve_objeto_pronto(api, pikachu_json):
    api.session.get.return_value = fake_response(200, pikachu_json)
    pokemon = api.get_pokemon(25)
    assert pokemon.name == "pikachu"
    assert pokemon.height_m == 0.4


def test_normaliza_a_entrada_antes_de_montar_a_url(api, pikachu_json):
    api.session.get.return_value = fake_response(200, pikachu_json)
    api.get_pokemon("  PiKaChU ")
    url = api.session.get.call_args.args[0]
    assert url == "https://pokeapi.co/api/v2/pokemon/pikachu"


def test_toda_requisicao_leva_timeout(api, pikachu_json, first_page_json):
    api.session.get.return_value = fake_response(200, pikachu_json)
    api.get_pokemon("pikachu")
    api.session.get.return_value = fake_response(200, first_page_json)
    api.list_pokemon()
    for call in api.session.get.call_args_list:
        assert call.kwargs["timeout"] == 5


def test_list_pokemon_manda_offset_e_limit(api, first_page_json):
    api.session.get.return_value = fake_response(200, first_page_json)
    page = api.list_pokemon(offset=40, limit=2)
    assert api.session.get.call_args.kwargs["params"] == {"offset": 40, "limit": 2}
    assert page.offset == 40


# --- Entrada inválida: nem chega a fazer a requisição ---


@pytest.mark.parametrize("entrada", ["", "   ", "pika/chu", "pikachu?x=1", "mr. mime"])
def test_entrada_invalida_nao_chama_a_api(api, entrada):
    with pytest.raises(InvalidInputError):
        api.get_pokemon(entrada)
    api.session.get.assert_not_called()


# --- Tabela de erros da Etapa 5 ---


@pytest.mark.parametrize(
    ("o_que_o_http_faz", "erro_esperado", "causa_esperada"),
    [
        (Mock(return_value=fake_response(404)), PokemonNotFoundError, APIError),
        (Mock(return_value=fake_response(500)), APIError, requests.HTTPError),
        (Mock(side_effect=requests.ReadTimeout()), APITimeoutError, requests.ReadTimeout),
        # ConnectTimeout é filho de Timeout E de ConnectionError: tem que virar timeout
        (Mock(side_effect=requests.ConnectTimeout()), APITimeoutError, requests.ConnectTimeout),
        (Mock(side_effect=requests.ConnectionError()), APIUnavailableError, requests.ConnectionError),
        (Mock(side_effect=requests.TooManyRedirects()), APIError, requests.TooManyRedirects),
        (Mock(return_value=fake_response(200, b"<html>oi</html>")), InvalidResponseError, ValueError),
        (Mock(return_value=fake_response(200, {"foo": 1})), InvalidResponseError, KeyError),
    ],
    ids=["404", "500", "read-timeout", "connect-timeout", "sem-conexao", "redirects", "nao-e-json", "json-inesperado"],
)
def test_traduz_erros(o_que_o_http_faz, erro_esperado, causa_esperada):
    api = PokeAPIClient()
    api.session.get = o_que_o_http_faz

    with pytest.raises(erro_esperado) as info:
        api.get_pokemon("pikachu")

    assert type(info.value) is erro_esperado  # exatamente essa, não uma filha
    assert isinstance(info.value.__cause__, causa_esperada)  # o raise ... from guardou a causa


def test_erro_http_guarda_o_status(api):
    api.session.get.return_value = fake_response(503)
    with pytest.raises(APIError) as info:
        api.list_pokemon()
    assert info.value.status_code == 503


def test_listagem_com_formato_inesperado(api):
    api.session.get.return_value = fake_response(200, {"foo": 1})
    with pytest.raises(InvalidResponseError):
        api.list_pokemon()
