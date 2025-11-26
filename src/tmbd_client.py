import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse

# Headers padrão para fingir que somos um navegador e não ser bloqueado
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

def buscar_link_filme(nome_filme):
    """
    Passo 1: Busca o filme no AdoroCinema e retorna o link do primeiro resultado.
    """
    print(f"🔎 Buscando filme: '{nome_filme}' no AdoroCinema...")
    
    # Codifica o nome para URL (ex: "Duna 2" vira "Duna+2")
    nome_codificado = urllib.parse.quote_plus(nome_filme)
    url_busca = f"https://www.adorocinema.com/pesquisar/?q={nome_codificado}"
    
    try:
        # Pausa aleatória para evitar bloqueio
        time.sleep(random.uniform(0.5, 1.0))
        
        response = requests.get(url_busca, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"❌ Erro na busca: Status {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Pega o primeiro resultado que seja um link de filme
        # A classe 'meta-title-link' geralmente é o título do resultado
        resultado = soup.find('a', class_='meta-title-link')
        
        if resultado:
            link_relativo = resultado['href'] # ex: /filmes/filme-293253/
            # Garante que temos o link completo
            if not link_relativo.startswith('http'):
                link_completo = f"https://www.adorocinema.com{link_relativo}"
            else:
                link_completo = link_relativo
                
            print(f"✅ Filme encontrado: {resultado.get_text(strip=True)}")
            print(f"🔗 Link: {link_completo}")
            return link_completo
        else:
            print("❌ Nenhum filme encontrado com esse nome.")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao buscar filme: {e}")
        return None

def buscar_criticas_por_nome(nome_filme):
    """
    Função Principal: Recebe o nome, acha o link e baixa as críticas.
    """
    # 1. Acha o link
    url_filme = buscar_link_filme(nome_filme)
    
    if not url_filme:
        return []
    
    # 2. Ajusta o link para a página de críticas
    # Se o link for .../filmes/filme-123/, adiciona 'criticas/'
    if "/criticas/" not in url_filme:
        url_filme = url_filme.rstrip('/')
        url_criticas = f"{url_filme}/criticas/"
    else:
        url_criticas = url_filme
        
    # 3. Baixa as críticas (lógica original)
    print(f"⬇️ Baixando críticas de: {url_criticas}")
    
    try:
        time.sleep(random.uniform(0.5, 1.0))
        response = requests.get(url_criticas, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        reviews_divs = soup.find_all('div', class_='content-txt review-card-content')

        lista_reviews = []
        for div in reviews_divs:
            texto = div.get_text(strip=True)
            if len(texto) > 30: # Filtra spam
                lista_reviews.append(texto)
                
            if len(lista_reviews) >= 10: # Limite de 10
                break
        
        print(f"🎉 Sucesso! {len(lista_reviews)} críticas coletadas.")
        return lista_reviews

    except Exception as e:
        print(f"Erro ao baixar críticas: {e}")
        return []

# --- TESTE RÁPIDO (Rode este arquivo para testar) ---
if __name__ == "__main__":
    # Teste com um nome de filme
    nome = "O Auto da Compadecida"
    reviews = buscar_criticas_por_nome(nome)
    
    print(f"\n--- Resultado para '{nome}' ---")
    for i, rev in enumerate(reviews[:3]):
        print(f"Review #{i+1}: {rev[:100]}...")