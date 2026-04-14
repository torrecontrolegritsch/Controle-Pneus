import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

# Configuração de Caminhos para Vercel/Local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gestão de Pneus Online", version="1.1.0")

# Ping de Teste Primário
@app.get("/ping")
def ping():
    return {"status": "online", "message": "pong"}

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importação Dinâmica dos Roteadores
try:
    from backend.routers import gestao_pneus
    app.include_router(gestao_pneus.router, prefix="/api/gestao-pneus")
except Exception as e:
    logger.error(f"Erro crítico ao carregar roteadores: {e}")

# Servir Frontend (Static Files)
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
