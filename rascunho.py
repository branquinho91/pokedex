# Rascunho da Etapa 2: tudo num arquivo só, sem tratar erro.
# Objetivo: ver em Python o que vimos com o curl. Vai ser apagado depois.
import requests

nome = input("Pokémon (nome ou número): ").strip().lower()

resposta = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nome}")
print("Status:", resposta.status_code)

dados = resposta.json()  # texto JSON -> dict do Python

# Campos simples: acesso direto pela chave
print("Nome:", dados["name"])
print("Número:", dados["id"])

# Unidades da API: decímetros e hectogramas, por isso ÷ 10
print("Altura:", dados["height"] / 10, "m")
print("Peso:", dados["weight"] / 10, "kg")

# Listas aninhadas: entra em cada item e pega o "name" de dentro
tipos = [t["type"]["name"] for t in dados["types"]]
print("Tipos:", ", ".join(tipos))

habilidades = [h["ability"]["name"] for h in dados["abilities"]]
print("Habilidades:", ", ".join(habilidades))

print("Stats:")
for s in dados["stats"]:
    print(f"  {s['stat']['name']}: {s['base_stat']}")
