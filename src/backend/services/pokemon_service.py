# backend/services/pokemon_service.py
import requests
from backend.services.cache_service import get_from_cache, set_to_cache
from backend.services.storage_service import save_pokemon_to_postgres

def fetch_pokemon_data(pokemon_name):
    """Obtiene datos de Pokémon de PokeAPI"""
    response = requests.get(
        f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()

def process_pokemon_data(raw_data):
    """Procesa datos crudos de PokeAPI"""
    return {
        "id": raw_data["id"],
        "name": raw_data["name"],
        "types": [t["type"]["name"] for t in raw_data["types"]],
        "stats": {s["stat"]["name"]: s["base_stat"] for s in raw_data["stats"]},
        "abilities": [a["ability"]["name"] for a in raw_data["abilities"]],
        "sprite": raw_data["sprites"]["front_default"],
        "height": raw_data["height"],
        "weight": raw_data["weight"],
        "official_artwork": raw_data["sprites"]["other"]["official-artwork"]["front_default"]
    }

def get_pokemon_with_cache(pokemon_name):
    """Obtiene Pokémon con sistema de cache"""
    cache_key = f"pokemon:{pokemon_name}"
    
    # 1. Verificar cache
    cached_data = get_from_cache(cache_key)
    if cached_data:
        save_pokemon_to_postgres(cached_data)
        return cached_data
    
    # 2. Fetch de PokeAPI
    raw_data = fetch_pokemon_data(pokemon_name)
    processed_data = process_pokemon_data(raw_data)
    
    # 3. Guardar en cache y almacenamiento
    set_to_cache(cache_key, processed_data)
    save_pokemon_to_postgres(processed_data)
    
    return processed_data