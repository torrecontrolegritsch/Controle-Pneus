import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env')

db_url = os.getenv('SUPABASE_DB_URL')

def setup_db():
    if not db_url:
        print("Erro: SUPABASE_DB_URL não encontrada.")
        return

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        print("--- Verificando/Adicionando coluna km_atual em veiculos_referencia ---")
        cur.execute("""
            ALTER TABLE veiculos_referencia 
            ADD COLUMN IF NOT EXISTS km_atual float8 DEFAULT 0;
        """)
        
        print("--- Limpando veículos sem frota em gp_veiculos ---")
        # Deletar veículos que não tem frota preenchida (vazios ou null) e que não tem pneus atrelados
        # Primeiro verificamos quantos são
        cur.execute("SELECT count(*) FROM gp_veiculos WHERE (frota IS NULL OR frota = '')")
        count = cur.fetchone()[0]
        print(f"Total de veículos sem frota: {count}")
        
        if count > 0:
            # Deleta apenas os que não tem movimentações ou pneus vinculados (segurança)
            cur.execute("""
                DELETE FROM gp_veiculos 
                WHERE (frota IS NULL OR frota = '') 
                AND id NOT IN (SELECT DISTINCT veiculo_id FROM gp_pneus WHERE veiculo_id IS NOT NULL)
                AND id NOT IN (SELECT DISTINCT veiculo_id FROM gp_movimentacoes WHERE veiculo_id IS NOT NULL)
            """)
            deleted = cur.rowcount
            print(f"Veículos excluídos: {deleted}")

        conn.commit()
        cur.close()
        conn.close()
        print("Concluído com sucesso!")

    except Exception as e:
        print(f"Erro ao executar comandos SQL: {e}")

if __name__ == "__main__":
    setup_db()
