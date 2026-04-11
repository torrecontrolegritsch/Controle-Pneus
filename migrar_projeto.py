import sqlite3
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

SUPA_URL = "https://dpvdjldocvdsdgvmnsvu.supabase.co/rest/v1"
SUPA_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def migrate_table(table_name, sqlite_table):
    print(f"--- Migrando {sqlite_table} -> {table_name} ---")
    conn = sqlite3.connect("backend/gestao_pneus.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {sqlite_table}")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not rows:
            print(f"Tabela {sqlite_table} está vazia localmente.")
            return

        # Limpa IDs para o Supabase gerar novos se necessário, ou mantém se quiser sincronia exata
        # Aqui vamos tentar manter os IDs para não quebrar relacionamentos
        
        # Envia em blocos de 50 para não estourar a API
        for i in range(0, len(rows), 50):
            batch = rows[i:i+50]
            # Remove campos que o SQLite gera e o Postgres pode reclamar
            for item in batch:
                if 'id' in item and table_name == 'gp_filiais':
                     # Para filiais, deixamos o ID para ser a base dos outros
                     pass
            
            res = requests.post(f"{SUPA_URL}/{table_name}", headers=HEADERS, data=json.dumps(batch))
            if res.status_code in [200, 201, 204]:
                print(f"Lote {i//50 + 1} enviado com sucesso!")
            else:
                print(f"Erro no lote {i//50 + 1}: {res.status_code} - {res.text}")
                
    except Exception as e:
        print(f"Erro ao acessar {sqlite_table}: {e}")

if __name__ == "__main__":
    if not SUPA_KEY:
        print("ERRO: SUPABASE_KEY não encontrada no .env")
    else:
        # Ordem importa por causa das chaves estrangeiras
        migrate_table("gp_filiais", "gp_filiais")
        migrate_table("gp_veiculos", "gp_veiculos")
        migrate_table("gp_pneus", "gp_pneus")
        migrate_table("gp_movimentacoes", "gp_movimentacoes")
        print("\n=== MIGRAÇÃO CONCLUÍDA ===")
