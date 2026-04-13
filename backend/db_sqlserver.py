import os
import logging
import requests
import json

logger = logging.getLogger(__name__)

def buscar_veiculo_por_placa(placa: str):
    """
    Busca dados do veículo (Placa, Modelo, Marca, Frota).
    1. Primeiro tenta no Supabase (Base já sincronizada/online).
    2. Se não encontrar, e estiver local (Windows), tenta o SQL Server corporativo.
    """
    placa_limpa = placa.replace("-", "").upper().strip()
    placa_hifen = f"{placa_limpa[:3]}-{placa_limpa[3:]}" if len(placa_limpa) == 7 else placa_limpa

    # --- 1. BUSCA NO SUPABASE (Sempre disponível via HTTPS) ---
    try:
        supa_key = os.getenv("SUPABASE_KEY")
        if supa_key:
            api_url = "https://dpvdjldocvdsdgvmnsvu.supabase.co/rest/v1/veiculos_referencia"
            params = {
                "placa": f"in.({placa_limpa},{placa_hifen})",
                "select": "*"
            }
            headers = {"apikey": supa_key, "Authorization": f"Bearer {supa_key}"}
            res = requests.get(api_url, headers=headers, params=params, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                if data:
                    row = data[0]
                    logger.info(f"Veículo {placa_limpa} encontrado no Supabase.")
                    row['tipo'] = 'bitruck' if 'BITRUCK' in str(row.get('modelo','')).upper() else 'simples'
                    return row
    except Exception as e:
        logger.warning(f"Aviso: Falha ao buscar no Supabase: {e}")

    # --- 2. BUSCA NO SQL SERVER (Apenas se estiver em Windows e não encontrou no Supabase) ---
    if os.name == 'nt':
        try:
            import pymssql
            host = os.getenv("SQLSERVER_HOST", "bi.bluefleet.com.br").replace('"', '')
            port_val = os.getenv("SQLSERVER_PORT", "1433").replace('"', '')
            port = int(port_val) if port_val.isdigit() else 1433
            user = os.getenv("SQLSERVER_USER", "referencia").replace('"', '')
            password = os.getenv("SQLSERVER_PASSWORD", "JSoo2iS*hdfbs5f2gdsf").replace('"', '')
            db = os.getenv("SQLSERVER_DB", "referencia").replace('"', '')

            logger.info(f"Buscando {placa_limpa} no SQL Server corporativo...")
            conn = pymssql.connect(server=host, user=user, password=password, database=db, port=port, login_timeout=10, timeout=20)
            cursor = conn.cursor(as_dict=True)
            query = "SELECT TOP 1 Placa as placa, Modelo as modelo, Montadora as marca, CAST(IdVeiculo AS VARCHAR) as frota FROM Veiculos WHERE Placa = %s OR Placa = %s"
            cursor.execute(query, (placa_limpa, placa_hifen))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                logger.info(f"Veículo {placa_limpa} encontrado no SQL Server.")
                row['tipo'] = 'bitruck' if 'BITRUCK' in str(row.get('modelo', '')).upper() else 'simples'
                return row
        except ImportError:
            logger.error("pymssql não instalado. Não foi possível consultar SQL Server.")
        except Exception as e:
            logger.error(f"Erro ao consultar SQL Server corporativo: {e}")
    
    return None
