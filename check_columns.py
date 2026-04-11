import pymssql

def check_schema():
    host = "bi.bluefleet.com.br"
    user = "referencia"
    password = "JSoo2iS*hdfbs5f2gdsf"
    db = "referencia"
    
    try:
        conn = pymssql.connect(server=host, user=user, password=password, database=db)
        cursor = conn.cursor()
        print("Buscando colunas da tabela Veiculos...")
        cursor.execute("SELECT TOP 1 * FROM Veiculos")
        columns = [column[0] for column in cursor.description]
        print("COLUNAS ENCONTRADAS:")
        print(columns)
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_schema()
