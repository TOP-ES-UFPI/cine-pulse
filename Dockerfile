# 1. Usa uma imagem base do Python (leve e rápida)
FROM python:3.9-slim

# 2. Cria uma pasta de trabalho dentro do container
WORKDIR /app

# 3. Copia o arquivo de requisitos para dentro do container
COPY requirements.txt .

# 4. Instala as bibliotecas necessárias
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia TODO o resto do seu projeto (códigos, modelo .joblib, etc) para dentro
COPY . .

# 6. Avisa que o container vai usar a porta 8000
EXPOSE 8000

# 7. O comando que roda a API quando o container liga
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]