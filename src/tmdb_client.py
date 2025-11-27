import requests
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (TMDB_API_KEY)
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def buscar_dados_filme(nome_filme):
    """
    Busca o filme pelo nome usando o endpoint de busca da TMDB.
    Estratégia:
      1. Tenta buscar em pt-BR primeiro (útil para títulos em português).
      2. Se não encontrar, faz fallback para en-US.
    Retorna:
      - dicionário com dados do primeiro resultado encontrado, ou
      - None se não houver chave de API ou nenhum resultado.
    Observações:
      - Timeout curto (5s) para não travar a aplicação.
      - Exclui resultados para adultos.
    """
    # Se a chave de API não estiver definida, não tenta a requisição
    if not TMDB_API_KEY:
        return None

    url = "https://api.themoviedb.org/3/search/movie"

    # 1) Tentativa principal: busca em português (pt-BR)
    try:
        print(f"🔎 Buscando '{nome_filme}' em PT-BR...")
        params_pt = {
            "api_key": TMDB_API_KEY,
            "query": nome_filme,
            "page": 1,
            "language": "pt-BR",
            "include_adult": "false"
        }
        resp = requests.get(url, params=params_pt, timeout=5)
        data = resp.json()
        # Retorna o primeiro resultado se houver
        if data.get("results"):
            return data["results"][0]
    except Exception:
        # Falha silenciosa aqui; será tentado fallback em inglês
        pass

    # 2) Fallback: busca em inglês (en-US)
    try:
        print(f"🔎 Buscando '{nome_filme}' em EN-US...")
        params_en = {
            "api_key": TMDB_API_KEY,
            "query": nome_filme,
            "page": 1,
            "language": "en-US",
            "include_adult": "false"
        }
        resp = requests.get(url, params=params_en, timeout=5)
        data = resp.json()
        if data.get("results"):
            return data["results"][0]
    except Exception:
        # Se também falhar aqui, retorna None
        pass

    return None

def buscar_reviews_tmdb(nome_filme):
    """
    Retorna uma tuple (reviews_dict, metadados):
      - reviews_dict: {'en': [...], 'pt': [...]}, listas de textos de reviews filtradas
      - metadados: dicionário com título, título original, ano de lançamento e poster

    Fluxo:
      1. Usa buscar_dados_filme para obter o ID do filme.
      2. Consulta o endpoint /movie/{id}/reviews para en-US e pt-BR.
      3. Filtra reviews muito curtas (<= 10 caracteres) para evitar ruído.
      4. Retorna dicionário com listas possivelmente vazias e os metadados.
    """
    filme = buscar_dados_filme(nome_filme)
    if not filme:
        return None, None

    movie_id = filme['id']

    # Monta metadados que serão úteis no front-end
    metadados = {
        "titulo_br": filme.get('title'),                     # título traduzido / exibido pela TMDB
        "titulo_original": filme.get('original_title'),      # título original
        "data_lancamento": filme.get('release_date', '')[:4],# apenas o ano (YYYY) quando disponível
        "poster": filme.get('poster_path')                   # caminho da imagem (usar base_url da TMDB quando necessário)
    }

    # Endpoint para reviews do filme
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews"
    resultado = {"en": [], "pt": []}

    print(f"🌍 Filme encontrado: {metadados['titulo_br']} (ID: {movie_id})")

    # 1) Busca reviews em inglês (en-US)
    try:
        params_en = {"api_key": TMDB_API_KEY, "language": "en-US"}
        data_en = requests.get(url, params=params_en, timeout=5).json()
        # Mantém apenas reviews com mais de 10 caracteres
        resultado["en"] = [r['content'] for r in data_en.get("results", []) if len(r.get('content', '')) > 10]
    except Exception:
        # Em caso de erro de rede/JSON, mantém lista vazia
        pass

    # 2) Busca reviews em português (pt-BR)
    try:
        params_pt = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
        data_pt = requests.get(url, params=params_pt, timeout=5).json()
        resultado["pt"] = [r['content'] for r in data_pt.get("results", []) if len(r.get('content', '')) > 10]
    except Exception:
        # Em caso de erro, mantém lista vazia
        pass

    return resultado, metadados