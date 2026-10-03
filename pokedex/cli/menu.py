"""Interface de linha de comando: todo input() e print() do app fica aqui.

Não sabe montar URL nem ler JSON. Só conversa com o PokeAPIClient
e mostra o resultado. Qualquer PokedexError vira uma mensagem na tela.
"""
from pokedex.models.pokemon import Ability, Pokemon, PokemonPage
from pokedex.services.errors import PokedexError
from pokedex.services.pokeapi import PokeAPIClient

# Nome do stat na API -> rótulo da spec
STAT_LABELS = {
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "special-attack": "Sp. Atk",
    "special-defense": "Sp. Def",
    "speed": "Speed",
}

LINE = "=" * 30


def run(api: PokeAPIClient | None = None) -> None:
    """Loop do menu principal. Só sai quando o usuário escolhe Exit."""
    api = api or PokeAPIClient()
    while True:
        print(f"\n{LINE}\nPOKEDEX\n{LINE}")
        print("1. Search Pokémon")
        print("2. List Pokémon")
        print("3. Exit")
        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            search(api)
        elif choice == "2":
            browse(api)
        elif choice == "3":
            print("Bye!")
            return
        else:
            print("Invalid option. Type 1, 2 or 3.")


def search(api: PokeAPIClient) -> None:
    query = input("Pokémon name or number: ")
    try:
        pokemon = api.get_pokemon(query)
    except PokedexError as err:
        print(err)  # a mensagem já foi escrita pensando no usuário
        return
    print(format_pokemon(pokemon))


def browse(api: PokeAPIClient, limit: int = 20) -> None:
    """Listagem paginada: busca uma página, mostra, pergunta para onde ir."""
    offset = 0
    while True:
        try:
            page = api.list_pokemon(offset, limit)
        except PokedexError as err:
            print(err)
            return
        print(format_page(page))

        offset = _ask_navigation(page)
        if offset is None:
            return


def _ask_navigation(page: PokemonPage) -> int | None:
    """Pergunta até receber um comando válido. Devolve o novo offset ou None (sair)."""
    while True:
        command = input("> ").strip().lower()
        if command == "q":
            return None
        if command == "n":
            if page.has_next:
                return page.offset + page.limit
            print("This is the last page.")
        elif command == "p":
            if page.has_previous:
                return page.offset - page.limit
            print("This is the first page.")
        else:
            print("Type n, p or q.")


# --- Formatação: recebem objetos e devolvem texto (não imprimem) ---


def format_pokemon(pokemon: Pokemon) -> str:
    lines = [
        "",
        LINE,
        f"#{pokemon.id:03d} {display_name(pokemon.name)}",
        LINE,
        f"{'Types:':<11}{', '.join(display_name(t) for t in pokemon.types)}",
        f"{'Height:':<11}{pokemon.height_m} m",
        f"{'Weight:':<11}{pokemon.weight_kg} kg",
        f"{'Abilities:':<11}{', '.join(format_ability(a) for a in pokemon.abilities)}",
        "",
        "Stats",
    ]
    for stat in pokemon.stats:
        label = STAT_LABELS.get(stat.name, display_name(stat.name))
        lines.append(f"  {label:<10}{stat.value:>4}")
    return "\n".join(lines)


def format_page(page: PokemonPage) -> str:
    first = page.offset + 1
    last = page.offset + len(page.results)
    lines = ["", f"Showing Pokémon {first}-{last} of {page.total}", ""]
    for summary in page.results:
        lines.append(f"{summary.id}. {display_name(summary.name)}")
    lines.append("")
    if page.has_next:
        lines.append("[n] Next page")
    if page.has_previous:
        lines.append("[p] Previous page")
    lines.append("[q] Quit")
    return "\n".join(lines)


def format_ability(ability: Ability) -> str:
    """Ability('lightning-rod', is_hidden=True) -> 'Lightning-Rod (hidden)'"""
    suffix = " (hidden)" if ability.is_hidden else ""
    return f"{display_name(ability.name)}{suffix}"


def display_name(name: str) -> str:
    """'mr-mime' -> 'Mr-Mime' (mantém o hífen para dar para buscar de volta)."""
    return name.title()
