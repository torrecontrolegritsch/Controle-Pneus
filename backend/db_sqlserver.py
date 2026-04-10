import os
import pyodbc
import logging
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def get_sqlserver_conn():
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('SQLSERVER_HOST')};"
            f"DATABASE={os.getenv('SQLSERVER_DB')};"
            f"UID={os.getenv('SQLSERVER_USER')};"
            f"PWD={os.getenv('SQLSERVER_PASSWORD')};"
            "Timeout=10;"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        logger.error(f"Erro ao conectar no SQL Server: {e}")
        return None

def buscar_veiculo_por_placa(placa_raw: str):
    """
    Busca veículo no SQL Server. 
    Trata a placa removendo o hífen para bater com o formato do banco (ou vice-versa).
    """
    # Normaliza: ABC1D23 ou ABC-1D23 -> ABC-1D23 (formato comum no SQL)
    placa = placa_raw.strip().upper()
    if len(placa) == 7 and "-" not in placa:
        placa = f"{placa[:3]}-{placa[3:]}"
    
    conn = get_sqlserver_conn()
    if not conn:
        return None
        
    try:
        # Consulta típica baseada na estrutura Bluefleet/Gritsch
        query = """
            SELECT TOP 1 
                LTRIM(RTRIM(Placa)) as placa,
                LTRIM(RTRIM(DescricaoModelo)) as modelo,
                LTRIM(RTRIM(DescricaoMarca)) as marca,
                LTRIM(RTRIM(Prefixo)) as frota,
                CASE 
                    WHEN DescricaoModelo LIKE '%Toco%' THEN 'toco'
                    WHEN DescricaoModelo LIKE '%Truck%' THEN 'truck'
                    WHEN DescricaoModelo LIKE '%Bi%Truck%' THEN 'bitruck'
                    ELSE 'simples'
                END as tipo
            FROM Veiculos
            WHERE Placa = ? OR Placa = ?
        """
        # Tenta com e sem hífen
        placa_sem = placa.replace("-", "")
        df = pd.read_sql(query, conn, params=[placa, placa_sem])
        
        if not df.empty:
            return df.iloc[0].to_dict()
        return None
    except Exception as e:
        logger.error(f"Erro na query SQL Server: {e}")
        return None
    finally:
        conn.close()
