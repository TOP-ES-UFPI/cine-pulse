import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def gerar_resumo_ia(reviews_ingles, nome_filme):
    """
    Envia as reviews em inglês para o Gemini 1.5 Flash e pede um resumo 
    conciso e impessoal em Português.
    """
    if not GEMINI_API_KEY:
        return "Erro: Chave do Gemini não configurada."
    
    if not reviews_ingles:
        return "Não há reviews suficientes para gerar um resumo."

    try:
        # Configura a chave
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Limita o contexto para não gastar tokens demais
        reviews_concatenadas = "\n\n".join(reviews_ingles[:15]) 

        # --- O SEGREDO ESTÁ AQUI: PROMPT RESTRITIVO ---
        prompt = f"""
        Analise as seguintes opiniões de usuários (extraídas do TMDB) sobre o filme "{nome_filme}".
        
        --- DADOS (REVIEWS EM INGLÊS) ---
        {reviews_concatenadas}
        --- FIM DOS DADOS ---
        
        Instruções OBRIGATÓRIAS:
        1. Escreva um único parágrafo de no máximo 8 linhas.
        2. O tom deve ser IMPESSOAL e JORNALÍSTICO (Nunca use "eu", "nós", "nosso", "crítico").
        3. Não invente fatos. Baseie-se APENAS no texto acima.
        4. Sintetize o consenso geral, destacando pontos fortes e fracos recorrentes.
        5. Finalize OBRIGATORIAMENTE com a seguinte frase exata: "(Resumo gerado por IA com base em análises do site TMDB)."
        
        Responda em Português do Brasil.
        """

        print(f"🤖 Enviando para Gemini 2.5 Flash...")
        response = model.generate_content(prompt)
        
        return response.text

    except Exception as e:
        print(f"⚠️ Erro no Gemini: {e}")
        return "O sistema de IA está indisponível no momento."