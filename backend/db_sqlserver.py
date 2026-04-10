import os
import logging
import pymssql
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def buscar_veiculo_por_placa(placa: str):
    """
    Busca dados do veículo no SQL Server corporativo (referencia.dbo.Veiculos)
    usando pymssql para compatibilidade com Vercel.
    """
    host = os.getenv("SQLSERVER_HOST", "bi.bluefleet.com.br")
    port = int(os.getenv("SQLSERVER_PORT", "1433"))
    user = os.getenv("SQLSERVER_USER", "referencia")
    password = os.getenv("SQLSERVER_PASSWORD", "JSoo2iS*hdfbs5f2gdsf")
    db = os.getenv("SQLSERVER_DB", "referencia")

    # Normaliza placa para busca
    placa_limpa = placa.replace("-", "").upper().strip()
    placa_hifen = f"{placa_limpa[:3]}-{placa_limpa[3:]}" if len(placa_limpa) == 7 else placa_limpa

    try:
        conn = pymssql.connect(
            server=host,
            port=port,
            user=user,
            password=password,
            database=db,
            timeout=10
        )
        
        cursor = conn.cursor(as_dict=True)
        query = """
            SELECT TOP 1
                Placa as placa,
                DescricaoModelo as modelo,
                DescricaoFabricante as marca,
                CodigoVeiculo as frota,
                CASE 
                    WHEN DescricaoModelo LIKE '%Bi%Truck%' THEN 'bitruck'
                    ELSE 'simples'
                END as tipo
            FROM Veiculos
            WHERE Placa = %s OR Placa = %s
        """
        cursor.execute(query, (placa_limpa, placa_hifen))
        row = cursor.fetchone()
        
        conn.close()
        return row

    except Exception as e:
        logger.error(f"Erro ao consultar SQL Server via pymssql: {e}")
        return None
