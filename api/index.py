import os
import sys
import mimetypes
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Garante tipos MIME corretos em ambientes Lambda/Linux mínimos
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/javascript', '.mjs')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/html', '.html')
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/svg+xml', '.svg')

# Garante que a raiz do projeto está no PATH (estamos dentro da pasta /api)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gestão de Pneus Online", version="1.1.0")

# Rate limiting (proteção contra força bruta)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/ping")
def ping():
    return {"status": "online"}

# CORS — sem wildcard: usa domínio configurado ou restringe ao Vercel
_cors_raw = os.getenv("CORS_ORIGINS")
if not _cors_raw:
    logger.warning("CORS_ORIGINS não configurado — usando domínio Vercel padrão")
    _cors_raw = "https://controle-pneus-six.vercel.app"
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importação dos roteadores (API routes registradas ANTES do catch-all)
from backend.routers import gestao_pneus, auth
from backend.routers import usuarios
app.include_router(gestao_pneus.router, prefix="/api/gestao-pneus")
app.include_router(auth.router)
app.include_router(usuarios.router)

# Servir assets estáticos (JS, CSS) do dist commitado
dist_path = os.path.join(BASE_DIR, "frontend", "dist")
assets_path = os.path.join(dist_path, "assets")

if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# SPA catch-all: serve index.html para qualquer rota não-API
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    if not os.path.exists(dist_path):
        return {"error": "Frontend nao encontrado. Execute npm run build no diretorio frontend/."}
    file_path = os.path.join(dist_path, full_path)
    if full_path and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(dist_path, "index.html"))

# Para rodar localmente com python api/index.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
