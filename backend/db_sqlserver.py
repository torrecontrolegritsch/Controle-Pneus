import os
import logging
import pymssql
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def buscar_veiculo_por_placa(placa: str):
    """
    Busca dados do veículo no SQL Server corporativo.
    Adicionado suporte a TDS 7.4 e Timeouts para nuvem.
    """
    host = os.getenv("SQLSERVER_HOST", "bi.bluefleet.com.br")
    port = int(os.getenv("SQLSERVER_PORT", "1433"))
    user = os.getenv("SQLSERVER_USER", "referencia")
    password = os.getenv("SQLSERVER_PASSWORD", "JSoo2iS*hdfbs5f2gdsf")
    db = os.getenv("SQLSERVER_DB", "referencia")

    # Normaliza placa
    placa_limpa = placa.replace("-", "").upper().strip()
    placa_hifen = f"{placa_limpa[:3]}-{placa_limpa[3:]}" if len(placa_limpa) == 7 else placa_limpa

    logger.info(f"Iniciando busca SQL para placa: {placa_limpa}")

    try:
        # Tenta conectar com parâmetros otimizados para nuvem
        conn = pymssql.connect(
            server=host,
            user=user,
            password=password,
            database=db,
            port=port,
            login_timeout=15, # Tempo para o login
            timeout=30        # Tempo para a query
        )
        
        cursor = conn.cursor(as_dict=True)
        # Usamos %s para pymssql
        query = "SELECT TOP 1 Placa as placa, Modelo as modelo, Montadora as marca, CAST(IdVeiculo AS VARCHAR) as frota FROM Veiculos WHERE Placa = %s OR Placa = %s"
        
        cursor.execute(query, (placa_limpa, placa_hifen))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            logger.info(f"Veículo encontrado: {row['placa']}")
            # Adiciona o campo 'tipo' baseado no modelo
            row['tipo'] = 'bitruck' if 'BITRUCK' in str(row['modelo']).upper() else 'simples'
            return row
        else:
            logger.warning(f"Nenhum veículo encontrado no SQL Server para {placa_limpa}")
            return None

    except Exception as e:
        logger.error(f"SQL Server inacessível: {e}. Verificando cache...")
        
        # Se estivermos localmente, não tentamos psycopg2 (evita erro de porta bloqueada)
        if os.name == 'nt':
            try:
                # Tenta buscar no SQLite local (veiculos_referencia)
                from db_gestao_pneus import _get_gp_engine
                from sqlalchemy import text
                engine = _get_gp_engine()
                with engine.connect() as conn:
                    query = text("SELECT placa, modelo, marca, frota, tipo FROM veiculos_referencia WHERE UPPER(placa) = :p1 OR UPPER(placa) = :p2")
                    row = conn.execute(query, {"p1": placa_limpa, "p2": placa_hifen}).mappings().first()
                    if row:
                        logger.info("Dados recuperados do cache SQLite local.")
                        return dict(row)
            except Exception as le:
                logger.error(f"Erro ao buscar no cache local: {le}")
            return None

        # Se for no Vercel (Linux), tenta Supabase
        supa_url = os.getenv("SUPABASE_DB_URL")
        if not supa_url: return None
            
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(supa_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            query = "SELECT placa, modelo, marca, frota, tipo FROM veiculos_referencia WHERE UPPER(placa) = %s OR UPPER(placa) = %s"
            cursor.execute(query, (placa_limpa, placa_hifen))
            row = cursor.fetchone()
            conn.close()
            return row
        except Exception as se:
            logger.error(f"Erro ao buscar no cache do Supabase: {se}")
            return None
