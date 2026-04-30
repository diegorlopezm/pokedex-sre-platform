# Añadir import requests al inicio
import requests
from fastapi import APIRouter, HTTPException, status
from backend.services.pokemon_service import get_pokemon_with_cache
from backend.services.storage_service import get_history_from_postgres

router = APIRouter(prefix="/api", tags=["pokemon"])

@router.get("/pokemon/{pokemon_name}")
async def get_pokemon(pokemon_name: str):
    """Endpoint para buscar Pokémon"""
    pokemon_name = pokemon_name.lower().strip()
    
    if not pokemon_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del Pokémon no puede estar vacío"
        )
    
    try:
        # ❌ QUITAR EL AWAIT - la función no es async
        return get_pokemon_with_cache(pokemon_name)
        
    except requests.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="PokeAPI no respondió a tiempo. Intenta nuevamente."
        )
    except requests.ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se puede conectar con PokeAPI. Verifica tu conexión."
        )
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pokémon '{pokemon_name}' no encontrado. Verifica el nombre."
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error de PokeAPI: {str(e)}"
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al consultar PokeAPI: {str(e)}"
        )

@router.get("/history")
async def get_search_history(limit: int = 20):
    try:
        history = get_history_from_postgres(limit)
        return history  # ← Devuelve la lista directamente
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")