import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

# Garante que a raiz do projeto está no PATH (estamos dentro da pasta /api)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gestão de Pneus Online", version="1.1.0")

ERROR_LOAD = None

@app.get("/ping")
def ping():
    return {"status": "online", "message": "servidor ativo na Vercel (api/index.py)"}

@app.get("/api/debug-server")
def debug_server():
    return {
        "status": "rodando",
        "erro_carregamento": str(ERROR_LOAD) if ERROR_LOAD else "Nenhum erro",
        "caminho_atual": os.getcwd(),
        "arquivos_raiz": os.listdir(BASE_DIR),
        "sys_path": sys.path
    }

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importação dos roteadores
try:
    from backend.routers import gestao_pneus
    app.include_router(gestao_pneus.router, prefix="/api/gestao-pneus")
except Exception as e:
    ERROR_LOAD = e
    logger.error(f"FALHA NO CARREGAMENTO: {e}")

# Servir Frontend
dist_path = os.path.join(BASE_DIR, "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/frontend", StaticFiles(directory=dist_path, html=True), name="frontend")

@app.get("/")
def home():
    return RedirectResponse(url="/frontend/")

# Para rodar localmente com python api/index.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
