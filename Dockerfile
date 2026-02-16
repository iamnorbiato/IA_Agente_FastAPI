# Dockerfile
FROM python:3.11-slim

# Instala dependências de sistema necessárias para psycopg2 e ferramentas de rede
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Camada de cache para dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# O código será montado via volume em desenvolvimento, 
# mas deixamos o COPY para quando você quiser buildar a imagem final
COPY ./src /app/src

# Variável de ambiente para garantir que o Python não gere arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]