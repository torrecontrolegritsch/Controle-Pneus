import sqlite3
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

SUPA_URL = "https://dpvdjldocvdsdgvmnsvu.supabase.co/rest/v1/veiculos_referencia"
SUPA_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def sincronizar_referencias():
    print("Sincronizando banco de placas com o Supabase...")
    # Tenta ler do banco de KPIS se existir, ou do próprio gestao_pneus.db
    db_path = "backend/gestao_pneus.db" 
    
    if not os.path.exists(db_path):
        print("Banco de dados local não encontrado.")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Se você tiver uma tabela de referência, usamos ela. 
        # Se não, usamos as placas que você já cadastrou.
        cursor.execute("SELECT placa, modelo, marca, frota, tipo FROM gp_veiculos")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not rows:
            print("Nenhum veículo local para sincronizar.")
            return

        res = requests.post(SUPA_URL, headers=HEADERS, data=json.dumps(rows))
        if res.status_code in [200, 201, 204]:
            print(f"Sucesso! {len(rows)} veículos sincronizados para busca automática.")
        else:
            print(f"Erro na sincronização: {res.status_code} - {res.text}")
                
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    sincronizar_referencias()
