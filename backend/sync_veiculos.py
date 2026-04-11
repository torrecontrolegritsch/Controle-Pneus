import os
import logging
import pymssql
import requests
import json
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SYNC_HTTPS")

def sync():
    # 1. Configurações SQL Server
    sql_host = "bi.bluefleet.com.br"
    sql_user = "referencia"
    sql_pass = "JSoo2iS*hdfbs5f2gdsf"
    sql_db = "referencia"

    # 2. Configurações Supabase API (Pula o Firewall da porta 5432)
    supa_url = "https://dpvdjldocvdsdgvmnsvu.supabase.co"
    supa_key = os.getenv("SUPABASE_KEY")
    
    # Endpoint da tabela via REST
    api_url = f"{supa_url}/rest/v1/veiculos_referencia"

    try:
        # --- BUSCANDO DADOS NO SQL SERVER ---
        logger.info(f"Conectando ao SQL Server em {sql_host}...")
        sql_conn = pymssql.connect(server=sql_host, user=sql_user, password=sql_pass, database=sql_db)
        sql_cursor = sql_conn.cursor(as_dict=True)
        
        sql_query = """
            SELECT TOP 5000
                Placa as placa,
                Modelo as modelo,
                Montadora as marca,
                CAST(IdVeiculo AS VARCHAR) as frota,
                CASE 
                    WHEN Modelo LIKE '%Bi%Truck%' THEN 'bitruck'
                    ELSE 'simples'
                END as tipo
            FROM Veiculos
            WHERE Placa IS NOT NULL
            ORDER BY IdVeiculo DESC
        """
        sql_cursor.execute(sql_query)
        veiculos = sql_cursor.fetchall()
        sql_conn.close()
        logger.info(f"Sucesso! {len(veiculos)} veículos lidos do SQL Server.")

        # --- ENVIANDO PARA O SUPABASE VIA HTTPS (PORTA 443) ---
        headers = {
            "apikey": supa_key,
            "Authorization": f"Bearer {supa_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates" # Isso faz o Upsert automático!
        }

        logger.info("Enviando dados para o Supabase via HTTPS (bypass firewall)...")
        # Envia em lotes de 500 para não estourar o limite da API
        batch_size = 500
        for i in range(0, len(veiculos), batch_size):
            batch = veiculos[i:i+batch_size]
            response = requests.post(api_url, headers=headers, data=json.dumps(batch))
            
            if response.status_code in [200, 201]:
                logger.info(f"Lote {i//batch_size + 1} enviado com sucesso ({len(batch)} veículos).")
            else:
                logger.error(f"Erro no lote {i//batch_size + 1}: {response.text}")
                break

        logger.info("✅ PROCESSO CONCLUÍDO!")

    except Exception as e:
        logger.error(f"ERRO: {e}")

if __name__ == "__main__":
    sync()
