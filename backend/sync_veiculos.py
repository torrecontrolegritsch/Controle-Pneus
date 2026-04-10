import os
import logging
import pymssql
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SYNC")

def sync():
    # 1. Configurações SQL Server
    sql_host = os.getenv("SQLSERVER_HOST", "bi.bluefleet.com.br")
    sql_user = os.getenv("SQLSERVER_USER", "referencia")
    sql_pass = os.getenv("SQLSERVER_PASSWORD", "JSoo2iS*hdfbs5f2gdsf")
    sql_db = os.getenv("SQLSERVER_DB", "referencia")

    # 2. Configurações Supabase (PostgreSQL)
    supa_url = os.getenv("SUPABASE_DB_URL")
    if not supa_url:
        logger.error("SUPABASE_DB_URL não configurado no .env")
        return

    try:
        # --- BUSCANDO DADOS NO SQL SERVER ---
        logger.info(f"Conectando ao SQL Server em {sql_host}...")
        sql_conn = pymssql.connect(server=sql_host, user=sql_user, password=sql_pass, database=sql_db)
        sql_cursor = sql_conn.cursor(as_dict=True)
        
        sql_query = """
            SELECT 
                Placa as placa,
                DescricaoModelo as modelo,
                DescricaoFabricante as marca,
                CodigoVeiculo as frota,
                CASE 
                    WHEN DescricaoModelo LIKE '%Bi%Truck%' THEN 'bitruck'
                    ELSE 'simples'
                END as tipo
            FROM Veiculos
            WHERE Placa IS NOT NULL
        """
        sql_cursor.execute(sql_query)
        veiculos = sql_cursor.fetchall()
        sql_conn.close()
        logger.info(f"Sucesso! {len(veiculos)} veículos encontrados no SQL Server.")

        # --- ENVIANDO PARA O SUPABASE ---
        logger.info("Conectando ao Supabase (PostgreSQL)...")
        supa_conn = psycopg2.connect(supa_url)
        supa_cursor = supa_conn.cursor()

        # Prepara os dados para inserção em lote
        data_to_insert = [
            (v['placa'], v['modelo'], v['marca'], v['frota'], v['tipo'])
            for v in veiculos
        ]

        # Limpa tabela ou faz Upsert. Vamos fazer Upsert para não apagar nada útil.
        upsert_query = """
            INSERT INTO veiculos_referencia (placa, modelo, marca, frota, tipo)
            VALUES %s
            ON CONFLICT (placa) DO UPDATE SET
                modelo = EXCLUDED.modelo,
                marca = EXCLUDED.marca,
                frota = EXCLUDED.frota,
                tipo = EXCLUDED.tipo,
                last_sync = CURRENT_TIMESTAMP
        """
        
        execute_values(supa_cursor, upsert_query, data_to_insert)
        supa_conn.commit()
        supa_cursor.close()
        supa_conn.close()
        
        logger.info("✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO NO SUPABASE!")

    except Exception as e:
        logger.error(f"ERRO DURANTE SINCRONIZAÇÃO: {e}")

if __name__ == "__main__":
    sync()
