
import os
import requests
import json
from dotenv import load_dotenv

# Carrega as chaves
load_dotenv()
supa_key = os.getenv("SUPABASE_KEY")
api_url = "https://dpvdjldocvdsdgvmnsvu.supabase.co/rest/v1/gp_pneus"

headers = {
    "apikey": supa_key,
    "Authorization": f"Bearer {supa_key}",
    "Content-Type": "application/json"
}

print("--- DIAGNÓSTICO DE BANCO DE DADOS ---")
try:
    # 1. Verifica quantos pneus existem no total
    res = requests.get(api_url, headers=headers, params={"select": "count"}, timeout=10)
    print(f"Total de registros na tabela gp_pneus: {res.text}")
    
    # 2. Lista os últimos 5 para ver os campos
    res_list = requests.get(api_url, headers=headers, params={"select": "*", "limit": "5", "order": "id.desc"}, timeout=10)
    if res_list.status_code == 200:
        pneus = res_list.json()
        print(f"Últimos pneus cadastrados: {len(pneus)}")
        for p in pneus:
            print(f"- Fogo: {p.get('numero_fogo')} | Status: {p.get('status')} | Recebido: {p.get('recebido')}")
    else:
        print(f"Erro ao listar: {res_list.status_code} - {res_list.text}")
        
except Exception as e:
    print(f"Erro no diagnóstico: {e}")
