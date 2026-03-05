#G:\Learning\IA\IA_Agente_FastAPI\src\ingest.py
import os
import pandas as pd
from sqlalchemy import create_engine, text

def run_ingestion():
    db_url = os.getenv("DATABASE_URL")
    list_file_path = "/app/data/ingestion/files.lst"
    base_path = "/app/data/ingestion/"
    
    if not db_url:
        print("Erro: DATABASE_URL nao configurada.")
        return

    if not os.path.exists(list_file_path):
        print(f"Erro: Lista de arquivos nao encontrada em {list_file_path}")
        return

    try:
        engine = create_engine(db_url)
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return
    
    with open(list_file_path, 'r') as f:
        files = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not files:
        print("Nenhum arquivo listado para processamento.")
        return

    for file_name in files:
        full_path = os.path.join(base_path, file_name)
        
        try:
            print(f"Processando: {full_path}")
            if not os.path.exists(full_path):
                print(f"Arquivo fisico nao encontrado: {full_path}")
                continue

            # Leitura do arquivo Parquet
            df = pd.read_parquet(full_path)

            # Conversao de tipos complexos (numpy.ndarray) para lista Python
            # Necessario para compatibilidade com o driver do PostgreSQL
            for col in df.columns:
                if isinstance(df[col].iloc[0], (list, pd.Series, type(pd.Series().values))):
                    print(f"Ajustando formato da coluna: {col}")
                    df[col] = df[col].apply(lambda x: x.tolist() if hasattr(x, "tolist") else x)
            
            table_name = file_name.split('.')[0]
            
            print(f"Inserindo {len(df)} registros na tabela '{table_name}'...")
            
            # Utilizando 'replace' se a tabela estiver corrompida, 
            # ou 'append' para manter dados existentes.
            with engine.connect() as conn:
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                conn.execute(text("COMMIT"))
                
            print(f"Arquivo {file_name} processado com sucesso.")
            
        except Exception as e:
            print(f"Erro ao processar {file_name}: {e}")

if __name__ == "__main__":
    run_ingestion()