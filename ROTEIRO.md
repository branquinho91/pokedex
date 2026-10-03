# Roteiro: Pokedex CLI

Roteiro de estudo para construir a Pokedex CLI da spec (`pokedex_mvp_spec.pdf`), uma etapa por vez.

**Como funciona cada etapa:**
1. Explicação do objetivo e do porquê
2. Código escrito e comentado trecho a trecho
3. Rodamos juntos para verificar
4. Commit
5. Pausa para perguntas. Só seguimos quando estiver claro.

> Regra da spec: primeiro o MVP funcionando de ponta a ponta. Refatorar fica para depois.

---

## Arquitetura (aonde vamos chegar)

```
pokedex/
├── main.py                 # ponto de entrada: só chama o menu
├── requirements.txt
├── .gitignore
├── ROTEIRO.md
├── pokedex/                # pacote da aplicação
│   ├── __init__.py
│   ├── models/
│   │   └── pokemon.py      # dataclasses Pokemon/Stat + from_api()
│   ├── services/
│   │   ├── pokeapi.py      # PokeAPIClient: HTTP + JSON -> objetos
│   │   └── errors.py       # exceções próprias
│   └── cli/
│       └── menu.py         # menu, input do usuário, exibição
└── tests/
    ├── test_pokemon.py
    └── test_pokeapi.py
```

**Fluxo de dependências** (cada camada só conhece a de baixo):

```
cli/menu.py  ──usa──▶  services/pokeapi.py  ──usa──▶  models/pokemon.py
(usuário)              (API / HTTP)                   (dados do domínio)
```

- O **model** não sabe que existe HTTP nem terminal.
- O **service** não sabe que existe terminal (não usa `print` nem `input`).
- A **CLI** não sabe montar URL nem ler JSON.

Com isso, trocar a CLI por uma API web, por exemplo, só mexe numa camada.

---

## Etapa 0: Setup do projeto
- [x] Concluída

**Objetivo:** ambiente isolado, versionado e com as dependências declaradas.

**Conceitos:** ambiente virtual (venv), pip, `requirements.txt`, `.gitignore`, git.

**Arquivos:** `requirements.txt`, `.gitignore`

**Como verificar:**
```bash
source .venv/bin/activate
python -c "import requests; print(requests.__version__)"
git log --oneline
```

**Para refletir:**
- Por que não instalar o `requests` direto no Python do sistema?
- Por que a pasta `.venv/` não vai para o git?

---

## Etapa 1: Explorar a API na mão
- [ ] Concluída

**Objetivo:** entender o formato dos dados antes de escrever código.

**Conceitos:** REST, verbos HTTP, status codes (200, 404), JSON, paginação por `limit`/`offset`.

**O que fazer:**
```bash
curl -s https://pokeapi.co/api/v2/pokemon/pikachu | python -m json.tool | less
curl -s "https://pokeapi.co/api/v2/pokemon?limit=20&offset=0" | python -m json.tool
curl -i https://pokeapi.co/api/v2/pokemon/naoexiste    # olhar o status
```

**Para refletir:**
- Onde ficam os tipos? E os stats? Por que estão "aninhados" desse jeito?
- Em que unidade vêm `height` e `weight`?
- Para que servem os campos `next` e `previous` da listagem?

---

## Etapa 2: Primeiro script "sujo"
- [ ] Concluída

**Objetivo:** fazer a primeira requisição em Python, sem se preocupar com organização.

**Conceitos:** `requests.get`, `response.status_code`, `response.json()`, navegar em dicts/listas aninhados.

**Arquivos:** `rascunho.py` (vai ser apagado depois)

**Para refletir:**
- O que acontece se o Pokémon não existir? E se a internet cair?
- Que problemas esse script teria se crescesse?

---

## Etapa 3: Modelo `Pokemon`
- [ ] Concluída

**Objetivo:** criar a representação própria de Pokémon, só com o que o app usa.

**Conceitos:** classes, `@dataclass`, type hints, `@classmethod` como construtor alternativo (`from_api`), conversão de unidades, list comprehension.

**Arquivos:** `pokedex/models/pokemon.py`, `__init__.py`s

**Como verificar:** no REPL, montar um `Pokemon` a partir de um JSON real.

**Para refletir:**
- Por que não usar o dict da API direto pelo app inteiro?
- Por que `from_api` fica no model, e não no service?

---

## Etapa 4: Service `PokeAPIClient`
- [ ] Concluída

**Objetivo:** concentrar toda a comunicação HTTP num só lugar.

**Conceitos:** separação de responsabilidades, `requests.Session`, timeout, módulos e imports absolutos, retorno tipado.

**Arquivos:** `pokedex/services/pokeapi.py`

**Métodos:**
- `get_pokemon(name_or_id) -> Pokemon`
- `list_pokemon(offset, limit) -> PokemonPage` (nomes + se tem próxima/anterior)

**Para refletir:**
- Por que normalizar a entrada (`.strip().lower()`) aqui?
- Por que **todo** request precisa de timeout?

---

## Etapa 5: Tratamento de erros
- [ ] Concluída

**Objetivo:** transformar falhas técnicas em erros que fazem sentido para o domínio.

**Conceitos:** hierarquia de exceptions, exceções customizadas, `raise ... from err`, quais erros o `requests` lança.

**Arquivos:** `pokedex/services/errors.py`, `pokedex/services/pokeapi.py`

**Mapeamento:**
| Situação | Exceção do requests/Python | Nossa exceção |
|---|---|---|
| Pokémon inexistente | status 404 | `PokemonNotFoundError` |
| Timeout | `requests.Timeout` | `APITimeoutError` |
| Sem rede / API fora | `requests.ConnectionError` | `APIUnavailableError` |
| Outro erro HTTP | `requests.HTTPError` | `APIError` |
| JSON inválido/inesperado | `ValueError` / `KeyError` | `InvalidResponseError` |

**Para refletir:**
- Por que a CLI não deveria capturar `requests.Timeout` diretamente?

---

## Etapa 6: Menu CLI
- [ ] Concluída

**Objetivo:** a interface com o usuário.

**Conceitos:** loops de menu, `input()`, validação de entrada, f-strings e alinhamento, capturar exceções na borda da aplicação.

**Arquivos:** `pokedex/cli/menu.py`

**Partes:** menu principal, busca, listagem paginada (`[n]`, `[p]`, `[q]`) e exibição dos detalhes e stats.

---

## Etapa 7: `main.py` e teste ponta a ponta
- [ ] Concluída

**Objetivo:** o MVP rodando.

**Conceitos:** `if __name__ == "__main__":`, ponto de entrada, `KeyboardInterrupt` (Ctrl+C).

**Checklist manual:**
- [ ] Buscar `pikachu` e `25` dá o mesmo resultado
- [ ] Buscar `Pikachu ` (maiúscula e espaço) funciona
- [ ] Buscar `xyz` mostra `Pokémon not found.`
- [ ] Entrada vazia mostra mensagem de entrada inválida
- [ ] Listar, navegar com `n`/`p` e sair com `q`
- [ ] `p` na primeira página não quebra
- [ ] Sem rede, aparece mensagem amigável (sem stack trace)
- [ ] Ctrl+C sai sem stack trace

---

## Etapa 8: Testes com pytest
- [ ] Concluída

**Objetivo:** garantir que o comportamento não quebre quando mexermos no código.

**Conceitos:** pytest, asserts, fixtures, mocks (`monkeypatch` / `unittest.mock`), testar sem depender da internet.

**Arquivos:** `tests/test_pokemon.py`, `tests/test_pokeapi.py`

**Como verificar:** `pytest -v` todo verde.

---

## Etapa 9: Revisão e próximos passos (opcional)
- [ ] Concluída

Olhar o código com calma: o que ficou bom, o que refatorar. Ideias para depois: cache em memória, a lib `rich` para deixar a saída bonita, `typer`/`argparse` para comandos diretos (`pokedex search pikachu`).
