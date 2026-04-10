import pyodbc
import os
import sys
from dotenv import load_dotenv

# Carrega do local correto
load_dotenv('backend/.env')

def test_conn():
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('SQLSERVER_HOST')};"
            f"DATABASE={os.getenv('SQLSERVER_DB')};"
            f"UID={os.getenv('SQLSERVER_USER')};"
            f"PWD={os.getenv('SQLSERVER_PASSWORD')};"
            "Timeout=10;"
        )
        print(f"Tentando conectar em: {os.getenv('SQLSERVER_HOST')}")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("Conexão OK! Listando todas as tabelas do banco para encontrar a correta...")
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tabelas encontradas: {tables}")
        
        # Procura por algo parecido com veículos
        pneus_related = [t for t in tables if 'veic' in t.lower() or 'pneu' in t.lower()]
        print(f"\nTabelas que parecem ser o que buscamos: {pneus_related}")
        
        # Teste de busca com placa
        print("\nTestando busca da placa 'ABC1D23' (exemplo)...")
        # Vamos listar as 5 primeiras placas para ver o formato
        cursor.execute("SELECT TOP 5 Placa FROM referencia.dbo.Veículos")
        placas = [row[0] for row in cursor.fetchall()]
        print(f"Exemplos de placas no banco: {placas}")
        
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    test_conn()
