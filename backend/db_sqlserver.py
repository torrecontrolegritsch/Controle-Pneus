import os
import logging
import requests
import json

logger = logging.getLogger(__name__)

def buscar_veiculo_por_placa(placa: str):
    """
    Busca dados do veículo.
    Se estiver na nuvem (Vercel), busca na tabela veiculos_referencia do Supabase via REST.
    Se estiver local, tenta SQL Server corporativo.
    """
    placa_limpa = placa.replace("-", "").upper().strip()
    placa_hifen = f"{placa_limpa[:3]}-{placa_limpa[3:]}" if len(placa_limpa) == 7 else placa_limpa

    # MODO NUVEM: Busca via API REST do Supabase (Tabela veiculos_referencia)
    if os.name != 'nt':
        try:
            supa_key = os.getenv("SUPABASE_KEY")
            api_url = f"https://dpvdjldocvdsdgvmnsvu.supabase.co/rest/v1/veiculos_referencia"
            params = {
                "placa": f"in.({placa_limpa},{placa_hifen})",
                "select": "*"
            }
            headers = {"apikey": supa_key, "Authorization": f"Bearer {supa_key}"}
            res = requests.get(api_url, headers=headers, params=params, timeout=10)
            
            if res.status_code == 200 and res.json():
                row = res.json()[0]
                row['tipo'] = 'bitruck' if 'BITRUCK' in str(row.get('modelo','')).upper() else 'simples'
                return row
            return None
        except Exception as e:
            logger.error(f"Erro busca Supabase: {e}")
            return None

    # MODO LOCAL: SQL Server Corporativo
    try:
        import pymssql
        host = os.getenv("SQLSERVER_HOST", "bi.bluefleet.com.br")
        port = int(os.getenv("SQLSERVER_PORT", "1433"))
        user = os.getenv("SQLSERVER_USER", "referencia")
        password = os.getenv("SQLSERVER_PASSWORD", "JSoo2iS*hdfbs5f2gdsf")
        db = os.getenv("SQLSERVER_DB", "referencia")

        conn = pymssql.connect(server=host, user=user, password=password, database=db, port=port, login_timeout=15, timeout=30)
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
