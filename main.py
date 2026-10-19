import os
import json
import pandas as pd
import pandas_gbq
import requests

# 1. Authentification BigQuery (via GitHub Secret)
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
  cred_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
  with open("credentials.json", "w") as f:
    f.write(cred_json)
  os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

# 2. Collecte API Pokémon
url = "https://pokeapi.co/api/v2/pokemon?limit=150"
response = requests.get(url)
data = response.json()["results"]

# vérifier l'éxecution de lAPI
if response.status_code == 200:
    data = response.json()
    print("Données récupérées !")
else:
    print("Erreur :", response.status_code)

rows = []
for p in data:
  details = requests.get(p["url"]).json()
  rows.append({
      "id": details["id"],
      "name": details["name"],
      "height": details["height"],
      "weight": details["weight"],
      "base_experience": details["base_experience"],
      "type": details["types"][0]["type"]["name"],
  })

df = pd.DataFrame(rows)
df = df.drop_duplicates().dropna()

# 3. Insertion BigQuery
pandas_gbq.to_gbq(
    df,
    "pokemon_db.raw_pokemon",
    project_id="pokemon-api-511811",
    if_exists="replace",
)
print("Pipeline exécuté avec succès.")