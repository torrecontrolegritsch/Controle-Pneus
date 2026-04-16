# -*- coding: utf-8 -*-
"""
Script de Sincronizacao SQL Server -> Supabase
===============================================
Execute este script localmente (Windows, com acesso ao SQL Server corporativo)
para popular a tabela 'veiculos_referencia' no Supabase com todos os veiculos.

Apos a sincronizacao, o Vercel (producao) conseguira encontrar os veiculos
normalmente via Supabase, sem precisar de acesso direto ao SQL Server.

Uso:
    python sincronizar_sql_supabase.py
    python sincronizar_sql_supabase.py --limite 10000
"""

import os
import sys
import json
import argparse
import logging

# Carrega variaveis de ambiente do .env
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Sincroniza veiculos do SQL Server para o Supabase.")
    parser.add_argument("--limite", type=int, default=10000, help="Limite de veiculos (padrao: 10000)")
    args = parser.parse_args()

    # Verifica pymssql
    try:
        import pymssql
    except ImportError:
        print("\n[ERRO] pymssql nao instalado. Execute: pip install pymssql")
        sys.exit(1)

    # Verifica requests
    try:
        import requests
    except ImportError:
        print("\n[ERRO] requests nao instalado. Execute: pip install requests")
        sys.exit(1)

    supa_key = os.getenv("SUPABASE_KEY")
    if not supa_key:
        print("\n[ERRO] SUPABASE_KEY nao encontrada no .env")
        sys.exit(1)

    host = os.getenv("SQLSERVER_HOST", "bi.bluefleet.com.br").replace('"', "")
    port_val = os.getenv("SQLSERVER_PORT", "1433").replace('"', "")
    port = int(port_val) if port_val.isdigit() else 1433
    user = os.getenv("SQLSERVER_USER", "referencia").replace('"', "")
    password = os.getenv("SQLSERVER_PASSWORD", "JSoo2iS*hdfbs5f2gdsf").replace('"', "")
    db = os.getenv("SQLSERVER_DB", "referencia").replace('"', "")

    print(f"\n[INFO] Conectando ao SQL Server: {host}:{port}...")
    try:
        conn = pymssql.connect(
            server=host, user=user, password=password,
            database=db, port=port, login_timeout=10, timeout=60,
        )
    except Exception as e:
        print(f"\n[ERRO] Falha ao conectar no SQL Server: {e}")
        sys.exit(1)

    print(f"[OK] Conexao estabelecida! Buscando ate {args.limite} veiculos...")
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        f"SELECT TOP {args.limite} "
        f"Placa as placa, Modelo as modelo, Montadora as marca, CAST(IdVeiculo AS VARCHAR) as frota, "
        f"ISNULL(OdometroConfirmado, 0) as km_atual "
        f"FROM Veiculos WHERE Placa IS NOT NULL AND Placa != '' ORDER BY IdVeiculo DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\n[AVISO] Nenhum veiculo encontrado no SQL Server.")
        sys.exit(0)

    print(f"[INFO] {len(rows)} veiculos encontrados. Preparando envio para o Supabase...")

    # Prepara payload — desduplicando por placa (sem hifens) para evitar erros de constraint
    seen = set()
    payload = []
    for r in rows:
        placa = str(r.get("placa", "")).upper().replace("-", "").strip()
        if not placa or len(placa) < 6 or placa in seen:
            continue
        seen.add(placa)
        payload.append({
            "placa": placa,
            "modelo": str(r.get("modelo", "") or "").strip(),
            "marca": str(r.get("marca", "") or "").strip(),
            "frota": str(r.get("frota", "") or "").strip(),
            "km_atual": float(r.get("km_atual") or 0)
        })

    print(f"[INFO] {len(payload)} veiculos unicos apos remocao de duplicatas.")

    supa_url = "https://dpvdjldocvdsdgvmnsvu.supabase.co/rest/v1/veiculos_referencia"
    headers = {
        "apikey": supa_key,
        "Authorization": f"Bearer {supa_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }

    total_ok = 0
    erros = 0
    chunk_size = 200

    for i in range(0, len(payload), chunk_size):
        chunk = payload[i: i + chunk_size]
        lote_num = i // chunk_size + 1
        total_lotes = (len(payload) + chunk_size - 1) // chunk_size

        try:
            res = requests.post(
                supa_url,
                headers=headers,
                params={"on_conflict": "placa"},
                data=json.dumps(chunk),
                timeout=30,
            )
            if res.status_code in [200, 201, 204]:
                total_ok += len(chunk)
                print(f"  [OK] Lote {lote_num}/{total_lotes}: {len(chunk)} veiculos sincronizados")
            else:
                erros += len(chunk)
                print(f"  [ERRO] Lote {lote_num}/{total_lotes}: Status {res.status_code} - {res.text[:150]}")
        except Exception as e:
            erros += len(chunk)
            print(f"  [ERRO] Lote {lote_num}/{total_lotes}: {e}")

    print(f"\n{'=' * 55}")
    print(f"[RESULTADO] Sincronizacao concluida!")
    print(f"   Total no SQL Server : {len(rows)}")
    print(f"   Sincronizados OK    : {total_ok}")
    print(f"   Erros               : {erros}")
    print(f"\n[INFO] O Vercel agora conseguira encontrar esses veiculos via Supabase.")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    main()
