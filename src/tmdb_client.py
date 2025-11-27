import requests
import os
from dotenv import load_dotenv

# Carrega as chaves do arquivo .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def buscar_id_filme(nome_filme):
    """
    Busca o ID de um filme pelo nome na API do TMDB.
    """
    if not TMDB_API_KEY:
        print("❌ ERRO: Chave do TMDB não encontrada no arquivo .env")
        return None

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": nome_filme,
        "language": "en-US", # Mantemos inglês para garantir mais reviews
        "page": 1,
        "include_adult": "false"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            return None
            
        # Retorna o primeiro resultado
        return data["results"][0]["id"]
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar ID do filme: {e}")
        return None

def buscar_reviews_tmdb(nome_filme):
    """
    Função principal: Busca o ID e depois as reviews do filme.
    Retorna uma lista de textos de reviews em Inglês.
    """
    movie_id = buscar_id_filme(nome_filme)
    
    if not movie_id:
        print(f"❌ Filme '{nome_filme}' não encontrado.")
        return []
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }
    
    print(f"⬇️ Baixando reviews para o filme ID {movie_id}...")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        reviews_texto = []
        for item in data.get("results", []):
            content = item.get("content", "")
            # Filtra reviews muito curtas ou vazias
            if len(content) > 10:
                reviews_texto.append(content)
                
        print(f"✅ {len(reviews_texto)} reviews encontradas no TMDB.")
        return reviews_texto

    except Exception as e:
        print(f"⚠️ Erro ao buscar reviews: {e}")
        return []