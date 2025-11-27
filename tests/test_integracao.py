from fastapi.testclient import TestClient
from unittest.mock import patch
from src.app import app

client = TestClient(app)

# Mockamos as duas funções externas para o teste da API ser rápido e não gastar quota
@patch('src.app.buscar_reviews_tmdb')
@patch('src.app.gerar_resumo_ia')
def test_endpoint_analisar_sucesso(mock_gemini, mock_tmdb):
    # --- 1. Preparar os Mocks ---
    
    # O TMDB falso retorna reviews em ingles e portugues e metadados
    mock_tmdb.return_value = (
        {"en": ["Great movie", "Loved it"], "pt": ["Filme bom"]}, 
        {"titulo_br": "Teste", "titulo_original": "Test", "data_lancamento": "2024", "poster": "url"}
    )
    
    # O Gemini falso retorna um texto fixo
    mock_gemini.return_value = "Resumo de teste gerado com sucesso."

    # --- 2. Fazer a Requisição ---
    payload = {"filme": "Matrix"}
    response = client.post("/analisar", json=payload)

    # --- 3. Validar a Resposta ---
    assert response.status_code == 200
    data = response.json()

    # Verificar estrutura do JSON
    assert data["filme_buscado"] == "Matrix"
    assert "metadados" in data
    assert data["metadados"]["titulo_br"] == "Teste"
    
    # Verificar se calculou alguma nota (mesmo que seja zero se não tiver modelo carregado no ambiente de teste)
    assert "analise_quantitativa" in data
    assert "analise_qualitativa" in data
    assert data["analise_qualitativa"] == "Resumo de teste gerado com sucesso."

@patch('src.app.buscar_reviews_tmdb')
def test_endpoint_analisar_filme_nao_encontrado(mock_tmdb):
    # Simula que o TMDB devolveu None (filme não achado)
    mock_tmdb.return_value = (None, None)

    response = client.post("/analisar", json={"filme": "Filme Fantasma"})
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Filme não encontrado."