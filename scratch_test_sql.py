import os
import logging
from dotenv import load_dotenv

# Configura log para ver o erro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega .env
load_dotenv()

def test_sqlserver():
    placa = "ABC1234" # Placa de teste
    placa_limpa = placa.replace("-", "").upper().strip()
    placa_hifen = f"{placa_limpa[:3]}-{placa_limpa[3:]}" if len(placa_limpa) == 7 else placa_limpa

    print("--- TESTANDO CONEXÃO SQL SERVER ---")
    try:
        import pymssql
        host = os.getenv("SQLSERVER_HOST", "bi.bluefleet.com.br")
        # Remove aspas se existirem (alguns .env vêm com elas)
        host = host.replace('"', '').replace("'", "")
        
        port_str = os.getenv("SQLSERVER_PORT", "1433")
        port = int(port_str.replace('"', ''))
        
        user = os.getenv("SQLSERVER_USER", "referencia").replace('"', '')
        password = os.getenv("SQLSERVER_PASSWORD", "JSoo2iS*hdfbs5f2gdsf").replace('"', '')
        db = os.getenv("SQLSERVER_DB", "referencia").replace('"', '')

        print(f"Tentando conectar em {host}:{port} com user {user}...")
        
        conn = pymssql.connect(
            server=host, 
            user=user, 
            password=password, 
            database=db, 
            port=port, 
            login_timeout=15, 
            timeout=30
        )
        cursor = conn.cursor(as_dict=True)
        query = "SELECT TOP 1 Placa as placa, Modelo as modelo, Montadora as marca, CAST(IdVeiculo AS VARCHAR) as frota FROM Veiculos WHERE Placa = %s OR Placa = %s"
        cursor.execute(query, (placa_limpa, placa_hifen))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            print(f"Sucesso! Veículo encontrado: {row}")
        else:
            print("Conexão OK, mas veículo não encontrado.")
            
    except ImportError:
        print("ERRO: pymssql não está instalado!")
    except Exception as e:
        print(f"ERRO DE CONEXÃO: {e}")

if __name__ == "__main__":
    test_sqlserver()
