from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import requests
import os
from datetime import timedelta
import logging
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env
BASE_DIR = Path(__file__).parent.parent.parent
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)

from backend.auth import (
    create_access_token, verify_password, get_current_user, 
    TokenData, get_password_hash, pwd_context
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Auth"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = "operador"
    filial_id: int = None

@router.post("/login")
def login(req: LoginRequest):
    """
    Autentica o usuário e retorna token JWT.
    Primeiro verifica no Supabase Auth, depois gera token local.
    """
    if not SUPABASE_KEY or not SUPABASE_URL:
        raise HTTPException(status_code=500, detail="Serviço não configurado")
    
    # Extrai project_id da URL
    project_id = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
    auth_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    apikey = SUPABASE_KEY
    
    headers = {
        "apikey": apikey,
        "Content-Type": "application/json"
    }
    
    payload = {
        "email": req.email,
        "password": req.password
    }
    
    try:
        res = requests.post(auth_url, headers=headers, json=payload, timeout=10)
        
        if res.status_code == 200:
            supa_data = res.json()
            user_id = supa_data["user"]["id"]
            email = supa_data["user"]["email"]
            role = supa_data["user"].get("user_metadata", {}).get("role", "operador")
            
            user_url = f"{SUPABASE_URL}/rest/v1/usuarios?id=eq.{user_id}"
            user_res = requests.get(user_url, headers={"apikey": apikey, "Authorization": f"Bearer {apikey}"})
            filial_id = None
            if user_res.status_code == 200 and user_res.json():
                user_data = user_res.json()[0]
                filial_id = user_data.get("filial_id")
            
            access_token = create_access_token({
                "user_id": user_id,
                "email": email,
                "role": role,
                "filial_id": filial_id
            })
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "email": email,
                    "role": role,
                    "filial_id": filial_id
                }
            }
        else:
            err_msg = "Falha ao autenticar"
            try:
                err_data = res.json()
                err_msg = err_data.get("error_description") or err_data.get("msg") or err_msg
            except:
                pass
            raise HTTPException(status_code=res.status_code, detail=err_msg)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na autenticação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão com servidor de auth: {e}")

@router.post("/register")
def register(req: RegisterRequest):
    """
    Registra novo usuário no Supabase Auth.
    """
    if not SUPABASE_KEY or not SUPABASE_URL:
        raise HTTPException(status_code=500, detail="Serviço não configurado")
    
    project_id = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
    auth_url = f"{SUPABASE_URL}/auth/v1/signup"
    
    headers = {
        "apikey": apikey,
        "Content-Type": "application/json"
    }
    
    payload = {
        "email": req.email,
        "password": req.password,
        "data": {
            "role": req.role,
            "filial_id": req.filial_id
        }
    }
    
    try:
        res = requests.post(auth_url, headers=headers, json=payload, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            return {
                "id": data.get("id"),
                "email": req.email,
                "message": "Usuário registrado com sucesso"
            }
        else:
            err_msg = "Falha ao registrar"
            try:
                err_data = res.json()
                err_msg = err_data.get("error_description") or err_data.get("msg") or err_msg
            except:
                pass
            raise HTTPException(status_code=res.status_code, detail=err_msg)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro no registro: {e}")
        raise HTTPException(status_code=500, detail=f"Erro de conexão: {e}")

@router.get("/me")
def get_me(current_user: TokenData = Depends(get_current_user)):
    """
    Retorna dados do usuário atual autenticado.
    """
    return {
        "id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role,
        "filial_id": current_user.filial_id
    }
