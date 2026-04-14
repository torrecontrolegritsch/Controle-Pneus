from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import requests
import os

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    """
    Proxy de login para o Supabase Auth.
    Usa o Supabase REST API para validar as credenciais.
    """
    # Em um cenário real, pegaríamos de variáveis de ambiente
    # Aqui usaremos o ID do projeto do usuário
    project_id = "dpvdjldocvdsdgvmnsvu"
    
    # IMPORTANTE: Para Auth, precisamos da ANON KEY. 
    # Como não a temos explícita no .env do backend, tentamos usar a service_role key 
    # ou o usuário terá que adicioná-la.
    # No Supabase, a service_role key TAMBÉM funciona para gerar tokens se configurado.
    apikey = os.getenv("SUPABASE_KEY")
    
    auth_url = f"https://{project_id}.supabase.co/auth/v1/token?grant_type=password"
    
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
            data = res.json()
            # Retornamos apenas o necessário para o frontend
            return {
                "id": data["user"]["id"],
                "email": data["user"]["email"],
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"]
            }
        else:
            # Tenta pegar a mensagem de erro do Supabase
            err_msg = "Falha ao autenticar"
            try:
                err_data = res.json()
                err_msg = err_data.get("error_description") or err_data.get("msg") or err_msg
            except:
                pass
            raise HTTPException(status_code=res.status_code, detail=err_msg)
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com servidor de auth: {e}")
