from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib
import os
from src.tmdb_client import buscar_reviews_tmdb
from src.gemini_client import gerar_resumo_ia

# Inicializa a aplicação FastAPI com título e versão
app = FastAPI(title="CinePulse API", version="2.1.0")

# Monta o diretório de arquivos estáticos (CSS, JS, imagens)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# --- CARREGAR MODELOS DE ANÁLISE DE SENTIMENTO ---
# Caminhos para os modelos pré-treinados em inglês e português
CAMINHO_EN = "models/sentiment_pipeline.joblib"
CAMINHO_PT = "models/sentiment_pipeline_pt.joblib"

# Variáveis globais para armazenar os modelos carregados
pipeline_en = None
pipeline_pt = None

# Tenta carregar os modelos de arquivo
try:
    if os.path.exists(CAMINHO_EN): 
        pipeline_en = joblib.load(CAMINHO_EN)
    if os.path.exists(CAMINHO_PT): 
        pipeline_pt = joblib.load(CAMINHO_PT)
    print("✅ Modelos carregados!")
except Exception as e:
    # Se houver erro ao carregar, exibe um aviso mas não para a aplicação
    print(f"⚠️ Erro modelos: {e}")

# Define a estrutura de dados esperada nas requisições POST
class AnaliseRequest(BaseModel):
    filme: str

# Rota raiz - retorna a página HTML principal
@app.get("/")
def home():
    return FileResponse('src/static/index.html')

# Rota principal de análise - recebe o nome do filme e retorna análise completa
@app.post("/analisar")
def analisar_filme(request: AnaliseRequest):
    nome_busca = request.filme
    
    # 1. BUSCA BILÍNGUE - Obtém reviews em inglês e português + metadados do filme
    reviews_dict, metadata = buscar_reviews_tmdb(nome_busca)
    
    # Verifica se encontrou reviews em algum idioma
    if not reviews_dict or (len(reviews_dict['en']) == 0 and len(reviews_dict['pt']) == 0):
        raise HTTPException(status_code=404, detail="Filme não encontrado.")

    # 2. CLASSIFICAÇÃO COM "DUAL ENGINE" - Analisa sentimento em ambos idiomas
    total_pos = 0  # Contador de reviews positivos
    total_neg = 0  # Contador de reviews negativos
    
    # Classifica reviews em inglês usando o modelo treinado em inglês
    if pipeline_en and reviews_dict['en']:
        preds = pipeline_en.predict(reviews_dict['en'])
        total_pos += sum(1 for p in preds if p == 'positive')
        total_neg += sum(1 for p in preds if p == 'negative')

    # Classifica reviews em português usando o modelo treinado em português
    if pipeline_pt and reviews_dict['pt']:
        preds = pipeline_pt.predict(reviews_dict['pt'])
        # Trata variações de rótulos do modelo (positive/pos/1 e negative/neg/0)
        total_pos += sum(1 for p in preds if str(p).lower() in ['positive', 'pos', '1'])
        total_neg += sum(1 for p in preds if str(p).lower() in ['negative', 'neg', '0'])

    # Calcula a taxa de aprovação em porcentagem
    total = total_pos + total_neg
    aprovacao = (total_pos / total * 100) if total > 0 else 0

    # 3. ANÁLISE QUALITATIVA COM IA - Gera resumo contextual usando Gemini
    # Monta nome oficial com título em português e original para melhor contexto
    nome_oficial = f"{metadata['titulo_br']} ({metadata['titulo_original']})"
    # Combina todas as reviews em um único texto para análise
    todas_reviews = reviews_dict['en'] + reviews_dict['pt']
    # Gera resumo AI-powered sobre sentimentos e tendências
    resumo = gerar_resumo_ia(todas_reviews, nome_oficial)

    # Retorna resposta estruturada com análises quantitativa e qualitativa
    return {
        "filme_buscado": nome_busca,
        "metadados": metadata,
        "analise_quantitativa": {
            "positivos": total_pos,          # Número de reviews positivos
            "negativos": total_neg,          # Número de reviews negativos
            "nota_media": round(aprovacao, 1)  # Porcentagem de aprovação (0-100)
        },
        "analise_qualitativa": resumo       # Resumo textual gerado por IA
    }