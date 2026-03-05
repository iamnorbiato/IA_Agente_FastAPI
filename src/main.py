#G:\Meu Drive\Projetos\IA\IA_Agente_FastAPI\src\main.py
import os
import torch
from fastapi import FastAPI, Query, HTTPException
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer

# CRÍTICO: Limita threads para evitar que o Docker Desktop derrube a conexão
torch.set_num_threads(1)

app = FastAPI(title="Agente IA FastAPI - Estável")

DATABASE_URL = os.getenv("DATABASE_URL")
MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
SQL_FILE_PATH = os.getenv("SQL_SEARCH_FILE", "/app/src/sql/vector_search.sql")

# Inicialização global do modelo
try:
    print(f"Carregando modelo: {MODEL_NAME} em modo CPU...")
    model = SentenceTransformer(MODEL_NAME, device="cpu")
except Exception as e:
    print(f"ERRO CRÍTICO AO CARREGAR MODELO: {e}")
    model = None

# Engine do SQLAlchemy com pre-ping para evitar 'Connection Closed'
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def load_sql_file(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo SQL ausente: {path}")
    with open(path, 'r') as f:
        return f.read()

@app.get("/search")
def search(query: str = Query(..., min_length=3), limit: int = 5):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo de IA não carregado no container")
    
    try:
        # Gera o embedding sem gradiente para economizar memória
        with torch.no_grad():
            query_embedding = model.encode(query, convert_to_tensor=False).tolist()
        
        query_sql = load_sql_file(SQL_FILE_PATH)
        
        with engine.connect() as conn:
            results = conn.execute(
                text(query_sql), 
                {"embedding": str(query_embedding), "limit": limit}
            )
            # Retorna as linhas mapeadas dinamicamente
            return {"query": query, "results": [dict(row._mapping) for row in results]}
    except Exception as e:
        print(f"ERRO NA EXECUÇÃO DA BUSCA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Modo de compatibilidade máxima para Docker Desktop
    uvicorn.run("main:app", host="0.0.0.0", port=8000, loop="asyncio", http="h11")