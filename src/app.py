from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib
import os
from .tmdb_client import buscar_reviews_tmdb
from .gemini_client import gerar_resumo_ia

# Inicializa a API
app = FastAPI(
    title="CinePulse API",
    description="API de Análise de Sentimento de Filmes (Híbrida)",
    version="1.0.0"
)

# Serve arquivos estáticos (frontend)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# --- Configuração do Modelo Local ---
# Tenta carregar o modelo treinado na PoC
CAMINHO_MODELO = "models/sentiment_pipeline.joblib"
pipeline = None

if os.path.exists(CAMINHO_MODELO):
    try:
        pipeline = joblib.load(CAMINHO_MODELO)
        print("Modelo Local carregado com sucesso!")
    except Exception as e:
        print(f"Erro ao carregar modelo: {e}")
else:
    print("AVISO: Arquivo .joblib não encontrado em 'models/'. A classificação local não funcionará.")

# --- Estrutura de Dados da Requisição ---
class AnaliseRequest(BaseModel):
    filme: str

# --- Rotas da API ---

# Rota Home (Serve o HTML)
@app.get("/")
def home():
    return FileResponse('src/static/index.html')


@app.post("/analisar")
def analisar_filme(request: AnaliseRequest):
    nome_filme = request.filme
    print(f"Recebida solicitação para: {nome_filme}")

    # 1. Buscar Reviews no TMDB
    reviews = buscar_reviews_tmdb(nome_filme)
    
    if not reviews:
        raise HTTPException(status_code=404, detail="Filme não encontrado ou sem reviews suficientes.")

    # 2. Classificação com Modelo Local (Se disponível)
    resultado_local = {"positivos": 0, "negativos": 0, "nota_media": 0}
    
    if pipeline:
        print("⚡ Classificando reviews com modelo local...")
        predicoes = pipeline.predict(reviews)
        
        positivos = sum(1 for p in predicoes if p == 'positive')
        negativos = sum(1 for p in predicoes if p == 'negative')
        total = positivos + negativos
        
        aprovacao = (positivos / total * 100) if total > 0 else 0
        
        resultado_local = {
            "positivos": positivos,
            "negativos": negativos,
            "nota_media": round(aprovacao, 1)
        }

    # 3. Resumo com IA Generativa (Gemini)
    resumo = gerar_resumo_ia(reviews, nome_filme)

    return {
        "filme": nome_filme,
        "analise_quantitativa": resultado_local,
        "analise_qualitativa": resumo
    }