import os
import logging

logger = logging.getLogger(__name__)

def buscar_veiculo_por_placa(placa: str):
    """
    Busca dados do veículo.
    Neutralizado para Deploy Vercel (evita erros de importação de drivers nativos).
    """
    # Se estivermos na Vercel (Linux), não tentamos SQL Server direto
    if os.name != 'nt':
        logger.warning("### SQL SERVER BYPASS (AMBIENTE CLOUD) ###")
        return None

    try:
        import pymssql
        host = os.getenv("SQLSERVER_HOST", "bi.bluefleet.com.br")
        port = int(os.getenv("SQLSERVER_PORT", "1433"))
        user = os.getenv("SQLSERVER_USER", "referencia")
        password = os.getenv("SQLSERVER_PASSWORD", "JSoo2iS*hdfbs5f2gdsf")
        db = os.getenv("SQLSERVER_DB", "referencia")

        placa_limpa = placa.replace("-", "").upper().strip()
        placa_hifen = f"{placa_limpa[:3]}-{placa_limpa[3:]}" if len(placa_limpa) == 7 else placa_limpa

        conn = pymssql.connect(
            server=host, user=user, password=password,
            database=db, port=port, login_timeout=15, timeout=30
        )
        cursor = conn.cursor(as_dict=True)
        query = "SELECT TOP 1 Placa as placa, Modelo as modelo, Montadora as marca, CAST(IdVeiculo AS VARCHAR) as frota FROM Veiculos WHERE Placa = %s OR Placa = %s"
        cursor.execute(query, (placa_limpa, placa_hifen))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            row['tipo'] = 'bitruck' if 'BITRUCK' in str(row['modelo']).upper() else 'simples'
            return row
        return None
    except Exception as e:
        logger.error(f"Erro SQL Server: {e}")
        return None
