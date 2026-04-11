import pymssql

def test_connection():
    print("--- INICIANDO TESTE DE CONEXÃO LIMPO ---")
    host = "bi.bluefleet.com.br"
    user = "referencia"
    password = "JSoo2iS*hdfbs5f2gdsf"
    db = "referencia"
    
    try:
        conn = pymssql.connect(
            server=host,
            user=user,
            password=password,
            database=db,
            timeout=15
        )
        print("CONEXAO OK!")
        conn.close()
    except Exception as e:
        print("ERRO DE CONEXAO:")
        print(str(e))

if __name__ == "__main__":
    test_connection()
