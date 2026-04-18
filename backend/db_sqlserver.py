import os
import logging
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env
BASE_DIR = Path(__file__).parent.parent
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPA_TABLE = "veiculos_referencia"


def _get_supa_headers():
    supa_key = os.getenv("SUPABASE_KEY")
    if not supa_key:
        return None
    return {
        "apikey": supa_key,
        "Authorization": f"Bearer {supa_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }


def _salvar_no_supabase(dados: dict):
    """
    Faz upsert de um veículo na tabela veiculos_referencia do Supabase.
    Chamado automaticamente quando um veículo é encontrado no SQL Server.
    Garante que futuras buscas (inclusive no Vercel) já encontrem via Supabase.
    """
    headers = _get_supa_headers()
    if not headers:
        return

    payload = {
        "placa": dados.get("placa", "").upper().replace("-", ""),
        "modelo": dados.get("modelo", ""),
        "marca": dados.get("marca", ""),
        "frota": str(dados.get("frota", "")),
        "km_atual": float(dados.get("km_atual") or 0),
        "filial_nome": str(dados.get("filial_nome", "") or "").strip()
    }

    try:
        api_url = f"{SUPABASE_URL}/rest/v1/{SUPA_TABLE}"
        res = requests.post(
            api_url,
            headers=headers,
            params={"on_conflict": "placa"},
            data=json.dumps([payload]),
            timeout=8,
        )
        if res.status_code in [200, 201]:
            logger.info(f"Veiculo {payload['placa']} salvo/atualizado no Supabase (cache).")
        else:
            logger.warning(f"Falha ao salvar cache no Supabase: {res.status_code} - {res.text[:200]}")
    except Exception as e:
        logger.warning(f"Erro ao salvar cache no Supabase: {e}")


def buscar_veiculo_por_placa(placa: str):
    """
    Busca dados do veículo AO VIVO direto do SQL Server Corporativo.
    Garante que os dados (Odômetro e Filial) estejam sempre 100% atualizados,
    sem depender de sincronismo de cache. Funciona no Vercel via pytds.
    """
    placa_limpa = placa.replace("-", "").upper().strip()
    placa_hifen = f"{placa_limpa[:3]}-{placa_limpa[3:]}" if len(placa_limpa) == 7 else placa_limpa

    # --- BUSCA DIRETA NO SQL SERVER ---
    try:
        import pytds

        host = os.getenv("SQLSERVER_HOST")
        port_val = os.getenv("SQLSERVER_PORT", "1433").replace('"', "")
        port = int(port_val) if port_val.isdigit() else 1433
        user = os.getenv("SQLSERVER_USER")
        password = os.getenv("SQLSERVER_PASSWORD")
        db = os.getenv("SQLSERVER_DB")
        
        if not all([host, user, password, db]):
            logger.warning("SQL Server credentials não configuradas")
            return None

        logger.info(f"Buscando {placa_limpa} ao vivo no SQL Server corporativo...")
        conn = pytds.connect(
            server=host, user=user, password=password,
            database=db, port=port, login_timeout=5, timeout=10,
        )
        cursor = conn.cursor()
        query = (
            "SELECT TOP 1 Placa as placa, Modelo as modelo, Montadora as marca, "
            "CAST(IdVeiculo AS VARCHAR) as frota, "
            "ISNULL(OdometroConfirmado, 0) as km_atual, "
            "FilialOperacional as filial_nome "
            "FROM Veiculos WHERE Placa = %s OR Placa = %s"
        )
        cursor.execute(query, (placa_limpa, placa_hifen))
        row = cursor.fetchone()
        
        if row:
            # Transforma array em dict
            columns = [col[0].lower() for col in cursor.description]
            row_dict = dict(zip(columns, row))
            
            logger.info(f"Veiculo {placa_limpa} retornado pelo SQL Server.")
            row_dict["tipo"] = "bitruck" if "BITRUCK" in str(row_dict.get("modelo", "")).upper() else "simples"
            row_dict["fonte"] = "sqlserver"
            
            conn.close()
            return row_dict
            
        conn.close()

    except ImportError:
        logger.warning("pytds nao instalado. Driver puro de SQL indisponivel.")
    except Exception as e:
        logger.warning(f"SQL Server inacessivel ou erro de query: {e}")

    # Fallback silencioso não existe mais: só retorna None. Cuidamos do fallback do sistema no router.
    return None


def sincronizar_todos_do_sql(limite: int = 5000) -> dict:
    """
    Busca todos os veículos do SQL Server e faz upsert em lote no Supabase.
    Deve ser executado localmente — popula o Supabase para que o Vercel funcione.
    """
    try:
        import pymssql
    except ImportError:
        return {"ok": False, "erro": "pymssql nao instalado. Execute em ambiente Windows local."}

    headers = _get_supa_headers()
    if not headers:
        return {"ok": False, "erro": "SUPABASE_KEY nao configurada."}

    try:
        host = os.getenv("SQLSERVER_HOST")
        port_val = os.getenv("SQLSERVER_PORT", "1433").replace('"', "")
        port = int(port_val) if port_val.isdigit() else 1433
        user = os.getenv("SQLSERVER_USER")
        password = os.getenv("SQLSERVER_PASSWORD")
        db = os.getenv("SQLSERVER_DB")
        
        if not all([host, user, password, db]):
            return {"ok": False, "erro": "SQL Server credentials não configuradas."}

        logger.info("Conectando ao SQL Server para sincronizacao em lote...")
        conn = pymssql.connect(
            server=host, user=user, password=password,
            database=db, port=port, login_timeout=10, timeout=60,
        )
        cursor = conn.cursor(as_dict=True)
        cursor.execute(
            f"SELECT TOP {limite} Placa as placa, Modelo as modelo, Montadora as marca, "
            f"CAST(IdVeiculo AS VARCHAR) as frota, "
            f"ISNULL(OdometroConfirmado, 0) as km_atual, "
            f"FilialOperacional as filial_nome "
            f"FROM Veiculos WHERE Placa IS NOT NULL AND Placa != '' ORDER BY IdVeiculo DESC"
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {"ok": False, "erro": "Nenhum veiculo encontrado no SQL Server."}

        # Prepara payload para o Supabase
        payload = []
        for r in rows:
            placa = str(r.get("placa", "")).upper().replace("-", "").strip()
            if not placa:
                continue
            payload.append({
                "placa": placa,
                "modelo": str(r.get("modelo", "") or "").strip(),
                "marca": str(r.get("marca", "") or "").strip(),
                "frota": str(r.get("frota", "") or "").strip(),
                "km_atual": float(r.get("km_atual") or 0),
                "filial_nome": str(r.get("filial_nome", "") or "").strip()
            })

        # Envia em lotes de 200 para o Supabase
        api_url = f"{SUPABASE_URL}/rest/v1/{SUPA_TABLE}"
        total_ok = 0
        erros = 0
        chunk_size = 200

        for i in range(0, len(payload), chunk_size):
            chunk = payload[i: i + chunk_size]
            try:
                res = requests.post(
                    api_url,
                    headers=headers,
                    params={"on_conflict": "placa"},
                    data=json.dumps(chunk),
                    timeout=30,
                )
                if res.status_code in [200, 201]:
                    total_ok += len(chunk)
                    logger.info(f"Lote {i // chunk_size + 1}: {len(chunk)} veiculos sincronizados.")
                else:
                    erros += len(chunk)
                    logger.error(f"Erro no lote {i // chunk_size + 1}: {res.status_code} - {res.text[:200]}")
            except Exception as e:
                erros += len(chunk)
                logger.error(f"Falha no lote {i // chunk_size + 1}: {e}")

        return {
            "ok": True,
            "total_sql": len(rows),
            "sincronizados": total_ok,
            "erros": erros,
            "mensagem": f"{total_ok} veiculos sincronizados para o Supabase com sucesso!",
        }

    except Exception as e:
        logger.error(f"Erro na sincronizacao em lote: {e}")
        return {"ok": False, "erro": str(e)}
