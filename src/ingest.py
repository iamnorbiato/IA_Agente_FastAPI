import os
import pandas as pd
from sqlalchemy import create_engine, text

def run_ingestion():
    db_url = os.getenv("DATABASE_URL")
    # O arquivo que serve de "fonte da verdade" para o que deve ser processado
    list_file_path = "/app/data/ingestion/files.lst"
    base_path = "/app/data/ingestion/"
    
    if not db_url:
        print("❌ Erro: DATABASE_URL não configurada.")
        return

    if not os.path.exists(list_file_path):
        print(f"❌ Erro: Lista de arquivos não encontrada em {list_file_path}")
        return

    engine = create_engine(db_url)
    
    # Lendo a lista de arquivos (ignora linhas vazias e comentários)
    with open(list_file_path, 'r') as f:
        files = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not files:
        print("ℹ️ Nenhum arquivo listado para processamento.")
        return

    for file_name in files:
        full_path = os.path.join(base_path, file_name)
        
        try:
            print(f"📂 Processando: {full_path}")
            if not os.path.exists(full_path):
                print(f"⚠️ Arquivo físico não encontrado: {full_path}")
                continue

            df = pd.read_parquet(full_path)
            table_name = file_name.split('.')[0] # Nome da tabela = nome do arquivo
            
            print(f"🚀 Inserindo {len(df)} registros em '{table_name}'...")
            with engine.connect() as conn:
                df.to_sql(table_name, conn, if_exists='append', index=False)
                conn.execute(text("COMMIT"))
            print(f"✅ {file_name} processado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro em {file_name}: {e}")

if __name__ == "__main__":
    run_ingestion()