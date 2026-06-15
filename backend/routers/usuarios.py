from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import requests
import logging

from backend.auth import require_admin, TokenData
from backend.config_app import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])

TELAS_VALIDAS = [
    'estoque_central', 'alocacoes', 'veiculos', 'filiais',
    'estoque', 'financeiro', 'sucata', 'recicladora', 'historico', 'relatorio_nf'
]


def _supa_rest(path: str, method: str = "GET", body=None, params: dict = None):
    url = f"{SUPABASE_URL}/rest/v1{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    if params:
        from urllib.parse import urlencode
        url += "?" + urlencode(params)
    return requests.request(method, url, headers=headers, json=body, timeout=15)


def _supa_admin(path: str, method: str = "POST", body=None):
    url = f"{SUPABASE_URL}/auth/v1/admin{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    return requests.request(method, url, headers=headers, json=body, timeout=15)


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    password: str
    role: str = "operador"
    filial_id: Optional[int] = None
    telas: List[str] = []
    ativo: bool = True


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    filial_id: Optional[int] = None
    telas: Optional[List[str]] = None
    ativo: Optional[bool] = None


@router.get("")
def listar_usuarios(current_user: TokenData = Depends(require_admin)):
    res = _supa_rest("/usuarios", params={
        "select": "id,nome,email,role,filial_id,telas,ativo",
        "order": "nome.asc"
    })
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="Erro ao buscar usuários")
    return res.json()


@router.post("")
def criar_usuario(data: UsuarioCreate, current_user: TokenData = Depends(require_admin)):
    telas_validas = [t for t in data.telas if t in TELAS_VALIDAS]

    auth_res = _supa_admin("/users", body={
        "email": data.email,
        "password": data.password,
        "email_confirm": True,
        "user_metadata": {
            "role": data.role,
            "nome": data.nome
        }
    })
    if auth_res.status_code not in (200, 201):
        err_body = auth_res.json()
        err_msg = err_body.get("msg") or err_body.get("message") or err_body.get("error_description") or "Erro ao criar usuário"
        raise HTTPException(status_code=400, detail=err_msg)

    user_id = auth_res.json()["id"]

    insert_res = _supa_rest("/usuarios", "POST", body={
        "id": user_id,
        "nome": data.nome,
        "email": data.email,
        "role": data.role,
        "filial_id": data.filial_id,
        "telas": telas_validas,
        "ativo": data.ativo
    })
    if insert_res.status_code not in (200, 201):
        _supa_admin(f"/users/{user_id}", method="DELETE")
        err_detail = ""
        try:
            err_detail = insert_res.json().get("message") or insert_res.json().get("hint") or ""
        except Exception:
            pass
        if "column" in err_detail.lower() or "does not exist" in err_detail.lower():
            raise HTTPException(status_code=500, detail="Execute a migração SQL no Supabase antes de criar usuários. Acesse o SQL Editor e rode o ALTER TABLE usuarios ADD COLUMN ...")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar usuário no banco: {err_detail or insert_res.text[:200]}")

    return {"id": user_id, "message": "Usuário criado com sucesso"}


@router.put("/{user_id}")
def atualizar_usuario(user_id: str, data: UsuarioUpdate, current_user: TokenData = Depends(require_admin)):
    all_fields = data.model_dump(exclude_unset=True)

    password = all_fields.pop("password", None)
    table_fields = {k: v for k, v in all_fields.items()}

    if "telas" in table_fields and table_fields["telas"] is not None:
        table_fields["telas"] = [t for t in table_fields["telas"] if t in TELAS_VALIDAS]

    if table_fields:
        res = _supa_rest("/usuarios", "PATCH", body=table_fields, params={"id": f"eq.{user_id}"})
        if res.status_code not in (200, 201, 204):
            raise HTTPException(status_code=res.status_code, detail="Erro ao atualizar usuário")

    if password:
        auth_res = _supa_admin(f"/users/{user_id}", method="PUT", body={"password": password})
        if auth_res.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail="Erro ao atualizar senha")

    return {"message": "Usuário atualizado com sucesso"}


@router.delete("/{user_id}")
def deletar_usuario(user_id: str, current_user: TokenData = Depends(require_admin)):
    auth_res = _supa_admin(f"/users/{user_id}", method="DELETE")
    if auth_res.status_code not in (200, 204):
        raise HTTPException(status_code=400, detail="Erro ao deletar usuário")

    _supa_rest("/usuarios", "DELETE", params={"id": f"eq.{user_id}"})

    return {"message": "Usuário deletado com sucesso"}
