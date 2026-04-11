import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPA_URL = "https://dpvdjldocvdsdgvmnsvu.supabase.co/rest/v1"
SUPA_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type": "application/json"
}

def limpar_tabela(table):
    print(f"Limpando {table}...")
    # O comando DELETE no PostgREST sem filtros apaga tudo se o RLS permitir
    # Usamos o filtro 'id=gt.0' para garantir que pegamos todos os registros
    res = requests.delete(f"{SUPA_URL}/{table}?id=gt.0", headers=HEADERS)
    if res.status_code in [200, 204]:
        print(f"Sucesso! {table} está limpa.")
    else:
        print(f"Erro ao limpar {table}: {res.status_code} - {res.text}")

if __name__ == "__main__":
    if not SUPA_KEY:
        print("Erro: SUPABASE_KEY não encontrada.")
    else:
        # Ordem reversa para não dar erro de chave estrangeira
        limpar_tabela("gp_movimentacoes")
        limpar_tabela("gp_pneus")
        limpar_tabela("gp_veiculos")
        limpar_tabela("gp_filiais")
        print("\n=== BANCO DE DADOS LIMPO! ===")
