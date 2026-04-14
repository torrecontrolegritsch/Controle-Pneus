import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

# Configura o log para vermos o erro caso falte algo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Garante que a raiz do projeto está no PATH para Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

load_dotenv()

app = FastAPI(title="Gestão de Pneus Online", version="1.1.0")

ERROR_LOAD = None

# Ping de Teste
@app.get("/api/ping")
def ping():
    return {"status": "online", "message": "servidor ativo"}

# Rota de Diagnóstico (Lanterna)
@app.get("/api/debug-server")
def debug_server():
    return {
        "status": "rodando",
        "erro_carregamento": str(ERROR_LOAD) if ERROR_LOAD else "Nenhum erro",
        "caminho_atual": os.getcwd(),
        "arquivos_raiz": os.listdir('.'),
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

# Importação dos roteadores com captura de erro para debug
try:
    from backend.routers import gestao_pneus
    app.include_router(gestao_pneus.router, prefix="/api/gestao-pneus")
    logger.info("Roteadores carregados!")
except Exception as e:
    ERROR_LOAD = e
    logger.error(f"FALHA NO CARREGAMENTO: {e}")

# Frontend
dist_path = os.path.join(BASE_DIR, "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/frontend", StaticFiles(directory=dist_path, html=True), name="frontend")

@app.get("/")
def home():
    return RedirectResponse(url="/frontend/")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8015))
    uvicorn.run(app, host="0.0.0.0", port=port)
