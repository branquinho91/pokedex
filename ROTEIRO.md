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

## 📍 Onde paramos

**Etapa 5 concluída.** Próximo: **Etapa 6** (menu CLI).

**Para retomar com o Claude:** "li o ROTEIRO.md, vamos seguir de onde paramos".

---

## Ambiente de desenvolvimento (WSL + VSCode)

O projeto vive **dentro do Ubuntu (WSL)**, em `~/pokedex`, e o Python e o venv são os do Linux.

### Abrir o projeto no VSCode
Abra **sempre pelo Ubuntu**, não pelo caminho `\\wsl.localhost\...` no Windows:
```bash
cd ~/pokedex
code .
```
- Se `code` não for encontrado, instale a extensão **WSL** (Microsoft) no VSCode. Outra opção: `Ctrl+Shift+P` → **WSL: Open Folder in WSL...**
- Confira o canto inferior esquerdo: tem que aparecer **`WSL: Ubuntu`**.
- `Ctrl+Shift+P` → **Python: Select Interpreter** → `.venv/bin/python`. Se a extensão Python pedir para instalar "no WSL", aceite.

> **Por quê?** Se o VSCode do Windows abre a pasta por `\\wsl.localhost\...`, ele procura um `.venv\python.exe` do Windows. O nosso venv é Linux (`.venv/bin/python`), então aparece `.venv (broken)`. Aberto "dentro" do WSL, o VSCode roda um servidor no Linux e enxerga o Python certo.

### Ativar o venv no terminal
Em todo terminal novo, dentro de `~/pokedex`:
```bash
source .venv/bin/activate    # o prompt passa a mostrar (.venv)
deactivate                   # para sair
```
O terminal integrado do VSCode costuma ativar sozinho depois que o interpretador está selecionado.

### Recriar o ambiente do zero (outra máquina, venv apagado)
```bash
sudo apt install python3.14-venv     # só uma vez por máquina
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Python × Node: tabela de consulta
| Node / JS | Python |
|---|---|
| `npm` | `pip` |
| registry npm | PyPI |
| `package.json` / `package-lock.json` | `requirements.txt` (versões fixadas com `==`) ou `pyproject.toml` |
| `node_modules/` | `.venv/` |
| `npm install` | `pip install -r requirements.txt` |
| instala local por padrão | instala **global** por padrão, por isso existe o venv |
| atualiza o package.json sozinho | **não** atualiza o requirements.txt: você edita (ou usa `pip freeze`) |
| `axios` | `requests` |
| `await axios.get(url)` | `requests.get(url)` (síncrono, sem `await`) |
| `res.data` / `res.status` | `res.json()` / `res.status_code` |
| `{ params: {...} }` | `params={...}` |
| 4xx/5xx lança exceção sozinho | **não** lança: chamar `res.raise_for_status()` |

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
│   │   └── pokemon.py      # dataclasses Pokemon/Stat (só dados)
│   ├── mappers/
│   │   └── pokeapi.py      # JSON da PokeAPI -> Pokemon (pokemon_from_api)
│   ├── services/
│   │   ├── pokeapi.py      # PokeAPIClient: HTTP, timeout, chama o mapper
│   │   └── errors.py       # exceções próprias
│   └── cli/
│       └── menu.py         # menu, input do usuário, exibição
└── tests/
    ├── test_mapper.py
    └── test_pokeapi.py
```

**Fluxo de dependências** (cada camada só conhece a de baixo):

```
cli/menu.py  ──usa──▶  services/pokeapi.py  ──usa──▶  mappers/pokeapi.py  ──usa──▶  models/pokemon.py
(usuário)              (HTTP)                         (formato da API)              (dados do domínio)
```

- O **model** não sabe que existe HTTP, terminal nem PokeAPI.
- O **mapper** é o único que conhece o formato do JSON da PokeAPI.
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

**O que aprendemos:**
- O Ubuntu vem sem `ensurepip`, por isso foi preciso o `apt install python3.14-venv`. O Python do sistema é usado pelo próprio Ubuntu (o `apt`, por exemplo), então ele fica "protegido" e um `pip install` global dá erro de *externally-managed-environment*.
- Pedimos 2 pacotes e vieram 10: o resto são dependências transitivas (`urllib3`, `certifi`... vêm do `requests`). No `requirements.txt` fixamos só as **diretas** (`requests==2.34.2`, `pytest==9.1.1`).

---

## Etapa 1: Explorar a API na mão
- [x] Concluída

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

**O que aprendemos:**
- O JSON do Pikachu tem ~15.500 linhas formatado, 93% delas são `moves`. A gente usa uma fatia pequena, por isso o model vai filtrar.
- JSON é sempre **texto**: `json.loads` transforma em `dict`/`list`, `json.dumps` volta para string. No `requests`: `resp.text` (str) × `resp.json()` (dict).
- `types` e `stats` são **listas de objetos aninhados** no padrão "nome + link": `d["types"][0]["type"]["name"]`, `d["stats"][0]["base_stat"]`. Lista porque pode ter 1 ou 2 tipos; `slot` dá a ordem.
- `height` vem em **decímetros** e `weight` em **hectogramas**: os dois ÷ 10 viram metro e kg (Pikachu: 4 → 0,4 m, 60 → 6 kg).
- Inexistente dá **404** com corpo `{"status":404,"message":"Not Found"}`. O `requests` **não** lança erro sozinho com 404, a gente trata na Etapa 5.
- Paginação: `count` (total), `offset` (quantos pular), `limit` (por página), `next`/`previous` (URL pronta, `null` quando não existe). A listagem só traz `name` + `url`.

---

## Etapa 2: Primeiro script "sujo"
- [x] Concluída

**Objetivo:** fazer a primeira requisição em Python, sem se preocupar com organização.

**Conceitos:** `requests.get`, `response.status_code`, `response.json()`, navegar em dicts/listas aninhados.

**Arquivos:** `rascunho.py` (vai ser apagado depois)

**Para refletir:**
- O que acontece se o Pokémon não existir? E se a internet cair?
- Que problemas esse script teria se crescesse?

**O que aprendemos:**
- Traceback se lê **de baixo pra cima**: tipo do erro → código → arquivo e linha.
- Com 404, o script quebra **longe da causa**: o `requests.get` e o `.json()` passam, e só estoura `KeyError: 'name'` na linha 13. A mensagem não ajuda ninguém.
- **404/500** = o servidor **respondeu** com erro (tem status). **Sem internet/DNS** = **não houve resposta**: o `requests.get` lança `ConnectionError` na hora, sem status nenhum.
- Sem `timeout`, um servidor que aceita a conexão e nunca responde trava o script **para sempre** (testado: `ReadTimeout` com `timeout=3`; sem timeout, ficou esperando). Regra: toda requisição leva `timeout`.
- O script mistura 4 trabalhos (input, HTTP, regras dos dados, print). Crescendo, isso dá repetição, mudança espalhada, teste difícil e zero reuso. Daí as camadas model / service / cli.

---

## Etapa 3: Modelo `Pokemon`
- [x] Concluída

**Objetivo:** criar a representação própria de Pokémon, só com o que o app usa.

**Conceitos:** classes, `@dataclass`, type hints, `@classmethod` como construtor alternativo (`from_api`), conversão de unidades, list comprehension. Depois: padrão mapper.

**Arquivos:** `pokedex/models/pokemon.py`, `pokedex/mappers/pokeapi.py`, `__init__.py`s

**Como verificar:** no REPL, montar um `Pokemon` a partir de um JSON real.

**Para refletir:**
- Por que não usar o dict da API direto pelo app inteiro?
- Por que `from_api` fica no model, e não no service?

**O que aprendemos:**
- **Decorator** é uma função que recebe uma função/classe e devolve uma versão turbinada. `@dataclass class X` é o mesmo que `X = dataclass(X)`.
- `@dataclass` gera `__init__`, `__repr__` (o print bonito) e `__eq__` (comparar por valor) a partir dos campos declarados.
- **Type hints** (`name: str`, `list[Stat]`) não são checados em execução. Servem pro editor (autocompletar, sublinhar erro), pra documentação, e o dataclass usa pra descobrir os campos.
- `@classmethod` recebe `cls` (a classe), não `self` (a instância). `from_api` é um **construtor alternativo**: traduz o formato da API para o nosso. Em JS seria `static fromApi()`.
- `__init__.py` marca a pasta como pacote, e é isso que permite `from pokedex.models.pokemon import Pokemon`.
- Por que um model próprio: só os campos usados, conversão (÷ 10) feita uma vez, mudança da API corrigida num lugar só, e o editor pega erros de digitação.
- Por que `from_api` no model: quem sabe montar um Pokemon é o Pokemon. E ele recebe um dict, então dá pra testar sem internet.
- **Refatoração (decisão nossa):** extraímos o `from_api` para um **mapper**, `pokedex/mappers/pokeapi.py` → `pokemon_from_api(data)`. Agora o `Pokemon` é "puro" e não conhece a PokeAPI. O mapper é o único lugar que conhece o formato da API, e outra fonte (cache, banco) ganharia o seu próprio mapper sem mexer no model. Custo: um arquivo a mais. Continua testável sem internet, porque recebe um dict.

---

## Etapa 4: Service `PokeAPIClient`
- [x] Concluída

**Objetivo:** concentrar toda a comunicação HTTP num só lugar.

**Conceitos:** separação de responsabilidades, `requests.Session`, timeout, módulos e imports absolutos, retorno tipado.

**Arquivos:** `pokedex/services/pokeapi.py` (+ `PokemonSummary`/`PokemonPage` no model e `page_from_api` no mapper)

**Métodos:**
- `get_pokemon(name_or_id) -> Pokemon`
- `list_pokemon(offset, limit) -> PokemonPage` (nomes + se tem próxima/anterior)

**Para refletir:**
- Por que normalizar a entrada (`.strip().lower()`) aqui?
- Por que **todo** request precisa de timeout?

**O que aprendemos:**
- `self` é o `this`, mas declarado explicitamente. `__init__` é o construtor. `BASE_URL` em maiúsculas é atributo de classe (constante).
- Classe × função: o cliente **guarda estado** (URL, timeout, sessão), então é classe. O mapper não guarda nada, então é função.
- `requests.Session` reaproveita a conexão entre requisições.
- `_get` é o **funil**: toda requisição passa por ele, então timeout e `raise_for_status()` ficam num lugar só. O `_` no nome indica "uso interno" (convenção, não regra).
- Timeout no `__init__`: é configuração decidida uma vez, e quem chama não tem como esquecer. Igual ao `axios.create({ timeout })`.
- Normalizar (`.strip().lower()`) no service: a regra é **da API**, então todo mundo que usa o cliente ganha de graça.
- `raise_for_status()` faz o 404 estourar perto da causa (`HTTPError: 404 Not Found`), e não mais como `KeyError` lá na frente.
- O id da listagem vem da **URL**, não de `offset + posição`: depois do 1025 vêm as formas alternativas, com ids a partir de 10001.
- Buraco conhecido para a Etapa 5: entrada vazia vira `/pokemon/` (a listagem) e o mapper quebra.

---

## Etapa 5: Tratamento de erros
- [x] Concluída

**Objetivo:** transformar falhas técnicas em erros que fazem sentido para o domínio.

**Conceitos:** hierarquia de exceptions, exceções customizadas, `raise ... from err`, quais erros o `requests` lança.

**Arquivos:** `pokedex/services/errors.py`, `pokedex/services/pokeapi.py`

**Mapeamento:**
| Situação | Exceção do requests/Python | Nossa exceção |
|---|---|---|
| Entrada vazia ou com caracteres inválidos | (validado antes do request) | `InvalidInputError` |
| Pokémon inexistente | status 404 | `PokemonNotFoundError` |
| Timeout | `requests.Timeout` | `APITimeoutError` |
| Sem rede / API fora | `requests.ConnectionError` | `APIUnavailableError` |
| Outro erro HTTP | `requests.HTTPError` | `APIError` |
| JSON inválido/inesperado | `ValueError` / `KeyError` | `InvalidResponseError` |

**Para refletir:**
- Por que a CLI não deveria capturar `requests.Timeout` diretamente?

**O que aprendemos:**
- Exceção própria é só uma classe que herda de `Exception` (herança = `extends`). A docstring já basta como corpo.
- **Hierarquia:** `except PokedexError` pega ela e todas as filhas. A CLI vai precisar de um `except` só. O `except` captura pelo **tipo**, não pela mensagem.
- `APIError` guarda `status_code` (via `super().__init__(message)` + atributo), e o `get_pokemon` decide "404 → `PokemonNotFoundError`" sem ler texto. O `_get` é genérico, então quem interpreta o 404 é quem conhece o contexto.
- `raise NossoErro(...) from err`: o usuário vê a mensagem amigável e o erro original fica em `__cause__` para debug. `raise` sozinho relança o mesmo erro.
- **Ordem dos `except`:** do mais específico pro mais genérico. `ConnectTimeout` é filho de `Timeout` **e** de `ConnectionError`, por isso o `Timeout` vem primeiro. `RequestException` por último, como rede de segurança.
- A entrada é validada antes do request (`re.compile` + `fullmatch`): vazio e `pika/chu` viram `InvalidInputError`.
- O mapper continua "inocente" (lança `KeyError`) e o service traduz para `InvalidResponseError`.
- Testado com servidores falsos locais: mudo (timeout), porta fechada (fora), 500, HTML e JSON torto.
- Por que a CLI não captura `requests.Timeout`: cada lib tem suas exceções (`httpx.TimeoutException`...). Se a CLI conhecesse o `requests`, trocar a lib quebraria a CLI. O service esconde os detalhes (encapsulamento / não vazar a abstração).
- Mensagens ao usuário em inglês, como o menu da spec. Comentários em português.

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

**Arquivos:** `tests/test_mapper.py`, `tests/test_pokeapi.py`

**Como verificar:** `pytest -v` todo verde.

---

## Etapa 9: Revisão e próximos passos (opcional)
- [ ] Concluída

Olhar o código com calma: o que ficou bom, o que refatorar. Ideias para depois: cache em memória, a lib `rich` para deixar a saída bonita, `typer`/`argparse` para comandos diretos (`pokedex search pikachu`), unidades imperiais (ft/in, lb) como `@property` calculada a partir de metro/kg (guardar uma unidade só).

**Documentação:** escrever o `README.md` (o que é, como instalar, rodar e testar) e passar o essencial da spec para markdown (`docs/spec.md`). Decidir se o `pokedex_mvp_spec.pdf` sai do repo ou vai para `docs/`.
