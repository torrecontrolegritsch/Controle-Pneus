import os
import sys
import mimetypes
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

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

ERROR_LOAD = None

@app.get("/ping")
def ping():
    return {"status": "online", "message": "servidor ativo na Vercel (api/index.py)"}

@app.get("/api/debug-server")
def debug_server():
    dist_path = os.path.join(BASE_DIR, "frontend", "dist")
    return {
        "status": "rodando",
        "erro_carregamento": str(ERROR_LOAD) if ERROR_LOAD else "Nenhum erro",
        "caminho_atual": os.getcwd(),
        "dist_existe": os.path.exists(dist_path),
        "arquivos_dist": os.listdir(dist_path) if os.path.exists(dist_path) else [],
        "mime_js": mimetypes.guess_type("file.js")[0],
        "mime_css": mimetypes.guess_type("file.css")[0],
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
    # Serve arquivos estáticos que existem na raiz do dist (logo, bg, etc.)
    file_path = os.path.join(dist_path, full_path)
    if full_path and os.path.isfile(file_path):
        return FileResponse(file_path)
    # Fallback para index.html (SPA routing)
    return FileResponse(os.path.join(dist_path, "index.html"))

# Para rodar localmente com python api/index.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
