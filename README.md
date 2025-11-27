# 🎬 Cine Pulse - Painel de Avaliações de Filmes

Sistema completo de gerenciamento e análise de avaliações de filmes com insights gerados por IA usando a API do Google Gemini.

## 📋 Visão Geral

Cine Pulse é uma aplicação full-stack que permite:
- ✨ Criar, ler, atualizar e excluir avaliações de filmes (CRUD completo)
- 📊 Visualizar estatísticas agregadas por filme
- 🤖 Gerar análises detalhadas usando IA (Gemini 2.0 Flash)
- 🔍 Buscar e filtrar avaliações
- 📈 Acompanhar distribuição de sentimentos

## 📸 Preview da Interface

![Dashboard do Cine Pulse](backend/docs/{7BE681BC-0330-48BA-B99E-14BCAE835284}.png)
*Dashboard principal com busca de filmes, cards clicáveis e análise AI*

## 🚀 Stack Tecnológico

### Frontend
- **React 18** com Vite
- **React Router v6** para navegação
- **Bootstrap 5** para estilização
- **Axios** para requisições HTTP
- **Bootstrap Icons** para ícones

### Backend
- **Python Flask** como framework web
- **SQLAlchemy** para ORM
- **PostgreSQL** como banco de dados
- **Flask-CORS** para habilitar CORS
- **Google Gemini 2.5 Flash API** para análise de IA

### Design
- **Tema "Dark Cinematic"** com paleta escura e acentos dourados
- **Fonte Outfit** do Google Fonts
- Interface moderna e premium

## 📦 Instalação

### Pré-requisitos

- Node.js 18+ e npm
- Python 3.8+
- PostgreSQL 12+
- Chave de API do Google Gemini ([obtenha aqui](https://makersuite.google.com/app/apikey))

### 1. Clone o Repositório

```bash
cd "C:\Users\Paulo\Documents\topico software\aplicacao"
```

### 2. Configurar Backend

```bash
cd backend

# Criar ambiente virtual (opcional mas recomendado)
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install flask flask-sqlalchemy flask-cors python-dotenv requests tqdm

# Criar arquivo .env com suas configurações
# Exemplo de .env:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5433/movie_reviews_db
# GEMINI_API_KEY=sua_chave_api_aqui
```

### 3. Configurar Banco de Dados

```bash
# Certifique-se de que o PostgreSQL está rodando na porta 5433
# Crie o banco de dados (se não existir)
# psql -U postgres
# CREATE DATABASE movie_reviews_db;

# Inicializar e popular o banco de dados
python init_database.py
```

### 4. Configurar Frontend

```bash
cd ../frontend

# Instalar dependências (já feito)
npm install

# O Vite já está configurado para fazer proxy para http://localhost:5000
```

## 🎯 Executando a Aplicação

### Iniciar Backend

```bash
cd backend
python movie_review_app.py
```

O servidor Flask estará rodando em `http://localhost:5000`

### Iniciar Frontend

```bash
cd frontend
npm run dev
```

O aplicativo React estará disponível em `http://localhost:3000`

## 📱 Funcionalidades Principais

### 1. Dashboard (Início)
- **Busca de Filmes**: Campo de pesquisa em tempo real para filtrar filmes por nome
- Visualize todos os filmes como cards clicáveis
- Veja estatísticas: nota média (escala 0-10), contagem de avaliações, distribuição de sentimentos
- **Cards Clicáveis**: Clique em qualquer card para ver detalhes do filme
- Botão "Gerar Resumo AI" abre modal com análise detalhada
- Botão "Adicionar Avaliação" com pré-preenchimento do título do filme

### 2. Detalhes do Filme
- **Nova Página**: Visualize todas as avaliações de um filme específico
- Lista completa de reviews com notas, sentimentos e spoilers
- Botões para voltar ao dashboard ou adicionar nova avaliação
- Sistema de estrelas ajustado (0-10 convertido para escala de 5 estrelas)

### 3. Todas as Avaliações
- Lista de todas as avaliações individuais
- Busca por filme, avaliador ou conteúdo
- Filtros por sentimento (Positivo/Negativo/Neutro)
- Ordenação (Mais recente, Maior/Menor nota, A-Z)
- Botões de Editar e Excluir
- Sistema de estrelas corrigido (ratings de 10 pontos exibidos como 5 estrelas)

### 4. Adicionar/Editar Avaliação
- Formulário simplificado (campos de sentimento/confiança são auto-gerados)
- Seletor visual de estrelas (escala de 1-5)
- Toggle de spoiler
- **UX Melhorado**: Campo de título do filme pode ser pré-preenchido
- Review ID gerado automaticamente (oculto do usuário)
- Validação em português

### 5. Análise AI (Gemini 2.5 Flash)
A análise gerada pela IA inclui:
- **Resumo Executivo**: Visão geral da recepção do filme
- **Análise Quantitativa**: Padrões estatísticos
- **Aspectos Positivos**: O que os espectadores amaram (com citações)
- **Aspectos Negativos**: Principais críticas (com citações)
- **Mergulho Profundo no Sentimento**: Análise detalhada de cada grupo
- **Segmentação de Audiência**: Quem gostou e quem não gostou
- **Análise de Conteúdo**: Temas discutidos, spoilers, padrões
- **Utilidade e Credibilidade**: Avaliadores mais confiáveis
- **Veredicto Final**: Recomendações por tipo de espectador
- **Principais Conclusões**: Insights chave

## 🔑 Configuração da API Gemini

1. Obtenha sua chave de API em: https://makersuite.google.com/app/apikey
2. Configure de uma das formas:
   - **Opção 1**: Adicione ao arquivo `.env` no backend:
     ```
     GEMINI_API_KEY=sua_chave_aqui
     ```
   - **Opção 2**: Insira diretamente no frontend quando solicitado (será salvo no localStorage)

## 📊 Estrutura do Banco de Dados

### Tabela: `movie_reviews`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| review_id | String (PK) | ID único da avaliação |
| reviewer | String | Nome do avaliador |
| movie | String | Título do filme |
| rating | Integer | Nota de 1-5 |
| review_summary | Text | Resumo da avaliação |
| review_date | String | Data da avaliação |
| spoiler_tag | Integer | 0=Não, 1=Sim |
| review_detail | Text | Avaliação detalhada |
| helpful_from | String | Votos úteis (de) |
| helpful_to | String | Votos úteis (total) |
| source_movie | String | Fonte do filme |
| predicted_sentiment | String | positivo/negativo/neutro |
| prediction_confidence | Float | Confiança (0-1) |

## 🛠️ Desenvolvimento

### Estrutura de Diretórios

```
aplicacao/
├── backend/
│   ├── dataset_portugues_aplicacao_with_predictions.json
│   ├── init_database.py          # Script de inicialização do DB
│   ├── movie_review_app.py       # Aplicação Flask principal
│   └── .env                       # Variáveis de ambiente
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx              # Barra de navegação
│   │   │   ├── MovieReviewsList.jsx    # Dashboard com cards de filmes
│   │   │   ├── MovieDetail.jsx         # Página de detalhes do filme
│   │   │   ├── MovieReviewsPage.jsx    # Lista de todas as reviews
│   │   │   └── MovieReviewForm.jsx     # Formulário add/edit
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

### API Endpoints

#### Reviews
- `GET /api/reviews` - Lista todas as avaliações
- `GET /api/reviews/<id>` - Obter avaliação específica
- `POST /api/reviews` - Criar nova avaliação
- `PUT /api/reviews/<id>` - Atualizar avaliação
- `DELETE /api/reviews/<id>` - Excluir avaliação

#### AI Analysis
- `POST /api/summarize` - Gerar análise AI
  ```json
  {
    "movie_title": "Nome do Filme",
    "reviews": [...],
    "analysis_params": {
      "sentiment_filter": "all",
      "sort_order": "helpful",
      "total_reviews": 100
    },
    "api_key": "sua_chave_gemini" // opcional se configurado no .env
  }
  ```

## 🎨 Personalização

### Cores (App.css)
```css
:root {
  --primary-color: #6366f1;
  --secondary-color: #8b5cf6;
  --success-color: #10b981;
  --danger-color: #ef4444;
  --warning-color: #f59e0b;
}
```

### Proxy do Vite (vite.config.js)
Se seu backend estiver em porta diferente, atualize:
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000', // Altere aqui
      changeOrigin: true
    }
  }
}
```

## 🐛 Solução de Problemas

### Backend não conecta ao banco
- Verifique se o PostgreSQL está rodando
- Confirme credenciais no DATABASE_URL
- Teste a conexão: `psql -U postgres -h localhost -p 5433`

### Erro de CORS
- Certifique-se de que Flask-CORS está instalado
- Verifique se `CORS(app)` está no `movie_review_app.py`

### Frontend não carrega dados
- Verifique se o backend está rodando em localhost:5000
- Abra DevTools (F12) e veja Console/Network para erros
- Verifique o proxy no vite.config.js

### Análise AI não funciona
- Confirme que a chave de API do Gemini é válida
- Verifique limites de quota da API
- Veja logs no console do backend para erros detalhados

## 📝 Notas Importantes

- **Idioma**: Toda a interface está em Português (pt-BR)
- **AI**: As análises são geradas em português pela instrução explícita no prompt
- **Dataset**: Contém ~38MB de avaliações de filmes em português
- **Performance**: A análise AI pode levar 10-30 segundos dependendo do número de avaliações

## 🤝 Contribuindo

Sinta-se à vontade para reportar bugs ou sugerir melhorias!

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais.

---

**Desenvolvido com ❤️ usando React, Flask e Gemini AI**
