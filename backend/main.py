import logging
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Garante que o diretório 'backend' esteja no path para a Vercel encontrar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

print("\n" + "#"*60)
print("### INICIANDO GESTÃO DE PNEUS - VERSÃO FIREWALL BYPASS ###")
print(f"### PORTA: {os.getenv('PORT')} | CORS: {os.getenv('CORS_ORIGINS')} ###")
print("#"*60 + "\n")

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

from fastapi.staticfiles import StaticFiles
app.include_router(gestao_pneus.router)

# Monta o frontend (Caminho Absoluto)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dist_path = os.path.join(base_dir, "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/frontend", StaticFiles(directory=dist_path, html=True), name="frontend")
else:
    logger.warning(f"AVISO: Pasta dist não encontrada em {dist_path}")

@app.get("/")
def home():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/frontend/")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8012))
    uvicorn.run(app, host="0.0.0.0", port=port)
