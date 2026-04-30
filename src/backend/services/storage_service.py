# backend/services/storage_service.py
from backend.database.connection import get_postgres_connection
from fastapi import HTTPException, status  # Add these imports

def save_pokemon_to_postgres(pokemon_data):
    """Guarda datos de Pokémon en PostgreSQL"""
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()
        
        # Insertar Pokémon
        cur.execute("""
            INSERT INTO pokemon (id, name, height, weight, sprite)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (pokemon_data["id"], pokemon_data["name"], 
              pokemon_data["height"], pokemon_data["weight"], 
              pokemon_data["sprite"]))
        
        # Insertar tipos
        for type_name in pokemon_data["types"]:
            cur.execute("""
                INSERT INTO pokemon_types (pokemon_id, type_name)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (pokemon_data["id"], type_name))
        
        # Guardar historial
        cur.execute("INSERT INTO search_history (name) VALUES (%s)", 
                   (pokemon_data["name"],))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error guardando en PostgreSQL: {e}")
        return False


def get_history_from_postgres(limit=10):
    """Obtiene el historial de búsquedas recientes"""
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT name, searched_at 
            FROM search_history 
            ORDER BY searched_at DESC 
            LIMIT %s
        """, (limit,))
        
        history = [
            {"name": row[0], "searched_at": row[1].isoformat()}
            for row in cur.fetchall()
        ]
        
        cur.close()
        conn.close()
        print(f"Historial obtenido: {history}")  # Debug
        return history  # ← Devuelve solo la lista, no el diccionario
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )