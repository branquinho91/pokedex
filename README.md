# Pokedex CLI

Uma Pokédex de terminal em Python que consulta a [PokéAPI](https://pokeapi.co/): busque um Pokémon por nome ou número, navegue pela lista paginada e veja tipos, habilidades e stats.

```
==============================
#006 Charizard
==============================
Types:     Fire, Flying
Height:    1.7 m
Weight:    90.5 kg
Abilities: Blaze, Solar-Power (hidden)

Stats
  HP          78
  Attack      84
  Defense     78
  Sp. Atk    109
  Sp. Def     85
  Speed      100
```

## Funcionalidades

- **Busca** por nome ou número (`pikachu`, `25`, ` PiKaChU `: maiúsculas e espaços não importam)
- **Detalhes**: número, tipos, altura (m), peso (kg), habilidades (com a oculta marcada) e os 6 stats base
- **Listagem paginada** de 20 em 20, navegando com `[n]` próxima, `[p]` anterior e `[q]` sair
- **Erros com mensagem clara**, nunca stack trace: Pokémon inexistente, entrada inválida, API fora do ar, timeout, erro HTTP e resposta inesperada
- `Ctrl+C` e `Ctrl+D` saem sem stack trace

## Como rodar

Requer **Python 3.10+** (desenvolvido no 3.14) e acesso à internet.

```bash
git clone https://github.com/branquinho91/pokedex.git
cd pokedex

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python main.py
```

```
==============================
POKEDEX
==============================
1. Search Pokémon
2. List Pokémon
3. Exit

Choose an option:
```

## Testes

```bash
pytest -v
```

São 39 testes que rodam em ~0,1 s **sem acessar a internet**: o HTTP é trocado por mocks e a CLI recebe um cliente falso.

| Arquivo | O que cobre |
|---|---|
| `tests/test_mapper.py` | Conversão do JSON da API: unidades, tipos, habilidade oculta, paginação, id vindo da URL |
| `tests/test_pokeapi.py` | Normalização da entrada, timeout em toda requisição e a tradução de cada erro do `requests` |
| `tests/test_menu.py` | Formatação da tela e fluxos do menu (busca, erros, navegação `n`/`p`/`q`) |

## Arquitetura

O código é dividido em camadas, e cada uma só conhece a de baixo:

```
cli/menu.py  ──▶  services/pokeapi.py  ──▶  mappers/pokeapi.py  ──▶  models/pokemon.py
(usuário)         (HTTP)                    (formato da API)          (dados do domínio)
```

```
pokedex/
├── main.py                  # ponto de entrada; trata Ctrl+C / Ctrl+D
├── pokedex/
│   ├── models/pokemon.py    # dataclasses: Pokemon, Stat, Ability, PokemonSummary, PokemonPage
│   ├── mappers/pokeapi.py   # JSON da PokéAPI -> models
│   ├── services/
│   │   ├── pokeapi.py       # PokeAPIClient: HTTP, timeout, validação, tradução de erros
│   │   └── errors.py        # hierarquia de exceções do app
│   └── cli/menu.py          # todo input() e print() fica aqui
└── tests/
```

| Camada | Sabe | Não sabe |
|---|---|---|
| **model** | o que é um Pokémon | que existe HTTP, terminal ou PokéAPI |
| **mapper** | o formato do JSON da PokéAPI | de onde o JSON veio |
| **service** | URL, timeout, status code, `requests` | que existe terminal (não usa `print` nem `input`) |
| **cli** | como conversar com o usuário | montar URL, ler JSON, que existe `requests` |

### Decisões de design

- **Model próprio em vez do dict da API.** O JSON de um Pokémon tem cerca de 15 mil linhas (93% são golpes). O `Pokemon` guarda só o que o app usa, já em metros e quilos (a API manda decímetros e hectogramas).
- **Mapper separado do model.** O `Pokemon` não conhece a PokéAPI. Se a API mudar de formato, ou surgir outra fonte (um cache, por exemplo), a mudança fica no mapper.
- **Um único ponto de HTTP.** Todo request passa pelo `PokeAPIClient._get`, que garante `timeout` e `raise_for_status()` em todas as chamadas e reaproveita a conexão com `requests.Session`.
- **Exceções do domínio.** O service traduz os erros do `requests` para exceções próprias (`raise ... from err`, sem perder a causa original). A CLI captura só `PokedexError` e mostra a mensagem, sem saber que o `requests` existe.

  | Situação | Exceção |
  |---|---|
  | Entrada vazia ou com caracteres inválidos | `InvalidInputError` |
  | Pokémon inexistente (404) | `PokemonNotFoundError` |
  | Timeout | `APITimeoutError` |
  | Sem rede / API fora | `APIUnavailableError` |
  | Outro erro HTTP | `APIError` |
  | JSON inválido ou inesperado | `InvalidResponseError` |

- **Id da listagem vem da URL, não da posição.** Depois do #1025, a PokéAPI lista as formas alternativas com ids a partir de 10001. Numerar por posição mostraria ids que não existem na busca.
- **POO moderada.** Classes onde há estado ou dados (`PokeAPIClient`, dataclasses), funções onde basta (mapper, formatação).

## Próximos passos

- Unidades imperiais (ft/in, lb) como `@property` calculada a partir de metro e kg
- `python -m pokedex` com um `__main__.py`
- Cache em memória das buscas
- Saída colorida com [`rich`](https://github.com/Textualize/rich)

## Sobre

Projeto de estudo de Python: HTTP e APIs REST, JSON, orientação a objetos, exceções, separação de responsabilidades e testes. O passo a passo da construção, com o que foi aprendido em cada etapa, está em [`ROTEIRO.md`](ROTEIRO.md).

Dados fornecidos pela [PokéAPI](https://pokeapi.co/). Pokémon e seus nomes são marcas da Nintendo, Game Freak e Creatures Inc.
