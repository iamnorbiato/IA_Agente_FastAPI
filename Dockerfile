#G:\IA\IA_Agente_FastAPI\Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependências de sistema para Postgres e compilação
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências primeiro para aproveitar cache
COPY requirements.txt .

# Instala Torch CPU (leve) e demais libs
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Comando de inicialização
CMD ["python", "src/main.py"]