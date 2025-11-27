import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def gerar_resumo_ia(reviews_ingles, nome_filme):
    """
    Envia as reviews em inglês para o Gemini e pede um resumo em Português.
    """
    if not GEMINI_API_KEY:
        return "Erro: Chave do Gemini não configurada."
    
    if not reviews_ingles:
        return "Não há reviews suficientes para gerar um resumo."

    try:
        # Configura o modelo
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')

        # Prepara o prompt (texto limitado a 10 reviews para não estourar tokens)
        reviews_concatenadas = "\n\n".join(reviews_ingles[:10])

        prompt = f"""
        Atue como um crítico de cinema do sistema CinePulse.
        Analise as seguintes opiniões de usuários (que estão em inglês) sobre o filme "{nome_filme}".
        
        --- INÍCIO DAS REVIEWS ---
        {reviews_concatenadas}
        --- FIM DAS REVIEWS ---
        
        Tarefa:
        1. Identifique o sentimento geral (se amaram ou odiaram).
        2. Liste os principais pontos positivos mencionados.
        3. Liste os principais pontos negativos mencionados.
        4. Escreva um veredito final resumido em um parágrafo em PORTUGUÊS DO BRASIL.
        """

        print("🤖 Perguntando ao Gemini...")
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"⚠️ Erro no Gemini: {e}")
        return "O sistema de IA está indisponível no momento."