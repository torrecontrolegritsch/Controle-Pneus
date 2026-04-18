"""
Configuração centralizada da aplicação.
NUNCA deve ter valores hardcoded - sempre ler do ambiente.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env
BASE_DIR = Path(__file__).parent.parent
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)

# ==================== SUPABASE ====================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    # 1. Tenta extrair do DB_URL (comum em setups que usam porta 443)
    db_url = os.getenv("SUPABASE_DB_URL")
    if db_url and "postgres." in db_url:
        try:
            ref = db_url.split("postgres.")[1].split(":")[0]
            SUPABASE_URL = f"https://{ref}.supabase.co"
        except:
            pass
            
    # 2. Tenta do Project ID explícito
    if not SUPABASE_URL:
        project_id = os.getenv("SUPABASE_PROJECT_ID")
        if project_id:
            SUPABASE_URL = f"https://{project_id}.supabase.co"
        else:
            # Não lança erro aqui para permitir que o app inicie mas falhe nos endpoints específicos com erro amigável
            SUPABASE_URL = None

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY não configurado")

# ==================== SQL SERVER ====================
SQLSERVER_HOST = os.getenv("SQLSERVER_HOST")
SQLSERVER_PORT = os.getenv("SQLSERVER_PORT", "1433")
SQLSERVER_USER = os.getenv("SQLSERVER_USER")
SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD")
SQLSERVER_DB = os.getenv("SQLSERVER_DB")

# ==================== JWT ====================
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY não configurado")

# ==================== APP ====================
APP_NAME = os.getenv("APP_NAME", "Gestao de Pneus")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
PORT = int(os.getenv("PORT", "8015"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")