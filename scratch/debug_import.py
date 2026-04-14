import requests
import csv
import io

BASE_URL = "http://localhost:8015/api/gestao-pneus"

def test_import():
    # Cria um CSV fake na memória
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["numero_fogo", "marca", "medida", "filial"])
    writer.writerow(["TESTE001", "MICHELIN", "295/80", "MATRIZ"])
    
    csv_content = output.getvalue()
    files = {'file': ('test.csv', csv_content, 'text/csv')}
    
    print(f"Enviando teste para {BASE_URL}/pneus/importar...")
    try:
        response = requests.post(f"{BASE_URL}/pneus/importar", files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {response.json()}")
    except Exception as e:
        print(f"Erro na conexão: {e}")

if __name__ == "__main__":
    test_import()
