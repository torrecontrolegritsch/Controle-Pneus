import logging
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Garante que o diretório 'backend' esteja no path para a Vercel encontrar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

from routers import gestao_pneus

app = FastAPI(
    title="Gestão de Pneus - Gritsch",
    description="Módulo Standalone de Controle de Pneus",
    version="1.1.0",
)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gestao_pneus.router)

@app.get("/")
def home():
    return {"message": "Gestão de Pneus Online", "version": "1.1.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
