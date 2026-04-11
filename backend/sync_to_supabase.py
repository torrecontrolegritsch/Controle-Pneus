import os
import sqlite3
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Configurações do Supabase (obtidas do seu .env)
# Extraímos o ID do projeto da URL ou usamos o que já sabemos
PROJECT_ID = "dpvdjldocvdsdgvmnsvu"
SUPA_URL = f"https://{PROJECT_ID}.supabase.co/rest/v1"
SUPA_KEY = os.getenv("SUPABASE_KEY") # Precisamos da KEY de serviço ou anon

def sync_table(table_name):
    print(f"Sincronizando tabela {table_name}...")
    
    # 1. Lê dados do SQLite local
    db_path = os.path.join(os.path.dirname(__file__), "gestao_pneus.db")
    if not os.path.exists(db_path):
        print("Arquivo de banco local não encontrado.")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not rows:
            print(f"Tabela {table_name} está vazia localmente.")
            return

        # 2. Envia para o Supabase via HTTPS (Porta 443 - Bypassa o Firewall)
        headers = {
            "apikey": SUPA_KEY,
            "Authorization": f"Bearer {SUPA_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

        # Remove campos que o Supabase gera sozinho ou que dão conflito
        for r in rows:
            if 'criado_em' in r: del r['criado_em']
            if 'atualizado_em' in r: del r['atualizado_em']

        response = requests.post(f"{SUPA_URL}/{table_name}", headers=headers, data=json.dumps(rows))
        
        if response.status_code in [200, 201, 204]:
            print(f"✅ {table_name}: {len(rows)} registros sincronizados com sucesso!")
        else:
            print(f"❌ Erro ao sincronizar {table_name}: {response.text}")

    except Exception as e:
        print(f"Erro na tabela {table_name}: {e}")

if __name__ == "__main__":
    if not SUPA_KEY:
        print("ERRO: SUPABASE_KEY não encontrada no .env. Por favor, adicione-a.")
    else:
        # Lista de tabelas para sincronizar
        tabelas = ["gp_filiais", "gp_veiculos", "gp_pneus", "gp_movimentacoes"]
        for t in tabelas:
            sync_table(t)
        print("\nSincronização concluída!")
