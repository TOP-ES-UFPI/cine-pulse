import pytest
from unittest.mock import patch, MagicMock
from src.tmdb_client import buscar_id_filme
from src.gemini_client import gerar_resumo_ia

# --- TESTE 1: TMDB Client (Com Mock) ---
# O @patch substitui o 'requests.get' por uma função falsa durante o teste
@patch('src.tmdb_client.requests.get')
def test_buscar_id_filme_sucesso(mock_get):
    # 1. Configurar o cenário (O que a API falsa deve devolver?)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {"id": 12345, "title": "Filme Teste", "original_title": "Test Movie"}
        ]
    }
    mock_get.return_value = mock_response

    # 2. Executar a função
    movie_id = buscar_id_filme("Filme Teste")

    # 3. Verificar (Assert)
    assert movie_id == 12345 # O ID deve ser o que definimos no mock

@patch('src.tmdb_client.requests.get')
def test_buscar_id_filme_nao_encontrado(mock_get):
    # Cenário: API retorna lista vazia
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response

    result = buscar_id_filme("Filme Inexistente 999")
    assert result is None

# --- TESTE 2: Gemini Client (Com Mock) ---
@patch('src.gemini_client.genai.GenerativeModel')
def test_gerar_resumo_ia(mock_model_class):
    # 1. Configurar o Mock do Gemini
    mock_model_instance = mock_model_class.return_value
    mock_response = MagicMock()
    mock_response.text = "Este é um resumo gerado por teste."
    mock_model_instance.generate_content.return_value = mock_response

    # 2. Executar
    reviews = ["Filme bom", "Gostei"]
    resultado = gerar_resumo_ia(reviews, "Filme Teste")

    # 3. Verificar
    assert resultado == "Este é um resumo gerado por teste."
    # Verifica se o modelo foi chamado com um prompt (qualquer prompt)
    mock_model_instance.generate_content.assert_called_once()