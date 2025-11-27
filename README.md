# **🎬 CinePulse \- Análise de Sentimento Híbrida**

O **CinePulse** é um sistema de análise de sentimentos em críticas de filmes. Ele utiliza uma arquitetura híbrida que combina **Machine Learning Clássico** (para métricas quantitativas rápidas) com **IA Generativa** (para resumos qualitativos detalhados).

## **🚀 Funcionalidades**

* **Busca na Web:** Localiza filmes e críticas automaticamente via API do TMDB.  
* **Motor Híbrido de Classificação:**  
  * 🧠 **Modelo Local (Scikit-Learn):** Classifica críticas em tempo real (\<50ms) usando Naive Bayes treinado em datasets IMDb (Inglês e Português).  
  * ✨ **IA Generativa (Google Gemini):** Lê as críticas e gera um resumo conciso e imparcial dos pontos fortes e fracos em Português.  
* **Interface Web:** Frontend responsivo construído com HTML5 e TailwindCSS.  
* **MLOps:** Pipeline de CI/CD configurado e containerização com Docker.

## **🛠️ Arquitetura do Sistema**

O sistema segue uma arquitetura de microsserviços simplificada:

1. **Frontend:** Cliente Web (Single Page Application).  
2. **API Gateway:** FastAPI orquestra as chamadas.  
3. **Coletor:** Módulo de integração com TMDB.  
4. **Inference Engine:** Carrega modelos .joblib para predição local.  
5. **GenAI Service:** Conecta com Google Gemini 1.5 Flash.

## **📦 Como Rodar**

### **Pré-requisitos**

* Docker (Recomendado) **OU** Python 3.9+  
* Chaves de API (TMDB e Google Gemini) configuradas no arquivo .env.

### **Opção A: Usando Docker (Recomendado)**

1. Construa a imagem:
   ```bash
   docker build -t cinepulse .
   ```

3. Execute o container (injetando as variáveis de ambiente):
   ```bash
   docker run -p 8000:8000 --env-file .env cinepulse
   ```

5. Acesse: http://localhost:8000

### **Opção B: Rodando Localmente (Python)**

1. Crie e ative o ambiente virtual:
   ```bash
   python -m venv venv  
   source venv/bin/activate  # Linux/Mac  
   venv\Scripts\activate   # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

5. Execute o servidor:
   ```bash
   uvicorn src.app:app --reload
   ```

## **🧪 Testes e CI**

O projeto possui testes automatizados para garantir a integridade da API.  
### **Testes Automatizados**

Utilizamos pytest com a técnica de **Mocks** para isolar a lógica de negócio e garantir testes rápidos e determinísticos, sem depender de APIs externas.  
Para rodar os testes localmente:  
```bash
pytest tests/ -v
```

### **Integração Contínua (GitHub Actions)**

O pipeline de CI é acionado a cada *push* ou *pull request*. Ele executa:

1. **Linting:** Verificação de estilo de código (PEP8) com flake8.  
2. **Testes Unitários e de Integração:** Validação completa da API e dos clientes.
