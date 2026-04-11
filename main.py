import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Carrega variáveis
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tenta carregar os roteadores
try:
    from backend.routers import gestao_pneus
except ImportError:
    # Fallback se estiver rodando de dentro da pasta backend
    sys.path.append(os.path.join(os.getcwd(), "backend"))
    from routers import gestao_pneus

app = FastAPI(title="Gestão de Pneus Online", version="1.1.0")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(gestao_pneus.router)

# Frontend
dist_path = os.path.join(os.getcwd(), "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/frontend", StaticFiles(directory=dist_path, html=True), name="frontend")

@app.get("/")
def home():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/frontend/")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8015))
    uvicorn.run(app, host="0.0.0.0", port=port)
