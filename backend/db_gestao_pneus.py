"""
Gestão de Pneus — Camada de banco de dados (Versão HTTPS Bypass).
Tabelas: gp_filiais, gp_veiculos, gp_pneus, gp_movimentacoes.
"""
import logging
import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

# Força a busca do .env na pasta raiz do projeto
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

# ── PONTE HTTPS PARA SUPABASE (Contorna Firewall) ─────────────────────────
def _api_request(method, table, params=None, payload=None):
    try:
        supa_key = os.getenv("SUPABASE_KEY")
        if not supa_key: 
            logger.error("!!! SUPABASE_KEY não encontrada !!!")
            return None
        
        api_url = f"https://dpvdjldocvdsdgvmnsvu.supabase.co/rest/v1/{table}"
        headers = {
            "apikey": supa_key,
            "Authorization": f"Bearer {supa_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation" if method == "POST" else ""
        }
        
        if method == "GET":
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=10)
        elif method == "PATCH":
            response = requests.patch(api_url, headers=headers, params=params, data=json.dumps(payload), timeout=10)
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.text else True
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=response.text)
    except Exception as e:
        logger.error(f"Erro na requisição ({table}): {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

# ── CONFIGURAÇÕES ─────────────────────────────────────────────────────────

VEHICLE_CONFIGS = {
    "simples": {
        "nome": "1. Simples",
        "eixos": [
            {"num": 1, "nome": "Eixo 1 - Direção", "tipo": "simples", "posicoes": ["E1_ESQ", "E1_DIR"]},
            {"num": 2, "nome": "Eixo 2 - Traseiro", "tipo": "simples", "posicoes": ["E2_ESQ", "E2_DIR"]},
        ],
        "estepes": ["ESTEPE_1"],
    },
    "toco": {
        "nome": "2. Toco",
        "eixos": [
            {"num": 1, "nome": "Eixo 1 - Direção", "tipo": "simples", "posicoes": ["E1_ESQ", "E1_DIR"]},
            {"num": 2, "nome": "Eixo 2 - Tração", "tipo": "duplo", "posicoes": ["E2_ESQ_EXT", "E2_ESQ_INT", "E2_DIR_INT", "E2_DIR_EXT"]},
        ],
        "estepes": ["ESTEPE_1"],
    },
    "truck": {
        "nome": "3. Truck",
        "eixos": [
            {"num": 1, "nome": "Eixo 1 - Direção", "tipo": "simples", "posicoes": ["E1_ESQ", "E1_DIR"]},
            {"num": 2, "nome": "Eixo 2 - Tração", "tipo": "duplo", "posicoes": ["E2_ESQ_EXT", "E2_ESQ_INT", "E2_DIR_INT", "E2_DIR_EXT"]},
            {"num": 3, "nome": "Eixo 3 - Truck", "tipo": "duplo", "posicoes": ["E3_ESQ_EXT", "E3_ESQ_INT", "E3_DIR_INT", "E3_DIR_EXT"]},
        ],
        "estepes": ["ESTEPE_1"],
    },
    "bitruck": {
        "nome": "4. Bitruck",
        "eixos": [
            {"num": 1, "nome": "Eixo 1 - Direção", "tipo": "simples", "posicoes": ["E1_ESQ", "E1_DIR"]},
            {"num": 2, "nome": "Eixo 2 - Direcional", "tipo": "simples", "posicoes": ["E2_ESQ", "E2_DIR"]},
            {"num": 3, "nome": "Eixo 3 - Tração", "tipo": "duplo", "posicoes": ["E3_ESQ_EXT", "E3_ESQ_INT", "E3_DIR_INT", "E2_DIR_EXT"]},
            {"num": 4, "nome": "Eixo 4 - Truck", "tipo": "duplo", "posicoes": ["E4_ESQ_EXT", "E4_ESQ_INT", "E4_DIR_INT", "E4_DIR_EXT"]},
        ],
        "estepes": ["ESTEPE_1", "ESTEPE_2"],
    },
}

def ensure_tables():
    # Agora controlado pelo SQL Editor do Supabase (Bypass)
    pass

# ── FILIAIS ────────────────────────────────────────────────────────────────

def listar_filiais(apenas_ativas=True):
    params = {"select": "*", "order": "nome"}
    if apenas_ativas: params["ativo"] = "eq.1"
    res = _api_request("GET", "gp_filiais", params=params)
    return res if res else []

def criar_filial(nome, cidade="", estado=""):
    payload = {"nome": nome, "cidade": cidade, "estado": estado}
    res = _api_request("POST", "gp_filiais", payload=payload)
    return res[0] if res else {}

def atualizar_filial(filial_id, nome, cidade="", estado=""):
    payload = {"nome": nome, "cidade": cidade, "estado": estado}
    return _api_request("PATCH", "gp_filiais", params={"id": f"eq.{filial_id}"}, payload=payload)

def desativar_filial(filial_id):
    return _api_request("PATCH", "gp_filiais", params={"id": f"eq.{filial_id}"}, payload={"ativo": 0})

# ── VEÍCULOS ───────────────────────────────────────────────────────────────

def listar_veiculos(filial_id=None, apenas_ativos=True):
    params = {"select": "*,gp_filiais(nome)", "order": "placa"}
    if apenas_ativos: params["ativo"] = "eq.1"
    if filial_id: params["filial_id"] = f"eq.{filial_id}"
    res = _api_request("GET", "gp_veiculos", params=params)
    if not res: return []
    for r in res:
        r["filial_nome"] = r.get("gp_filiais", {}).get("nome", "") if r.get("gp_filiais") else ""
    return res

def criar_veiculo(placa, frota="", modelo="", marca="", tipo="truck", filial_id=None, km_atual=0):
    payload = {
        "placa": placa.strip().upper().replace("-",""),
        "frota": frota.strip(), "modelo": modelo.strip(),
        "marca": marca.strip(), "tipo": tipo, "filial_id": filial_id, "km_atual": float(km_atual)
    }
    res = _api_request("POST", "gp_veiculos", payload=payload)
    return res[0] if res else {}

def atualizar_veiculo(veiculo_id, **kwargs):
    return _api_request("PATCH", "gp_veiculos", params={"id": f"eq.{veiculo_id}"}, payload=kwargs)

def obter_veiculo_com_pneus(veiculo_id):
    params = {"id": f"eq.{veiculo_id}", "select": "*,gp_filiais(nome)"}
    v_res = _api_request("GET", "gp_veiculos", params=params)
    if not v_res: return {}
    veiculo = v_res[0]
    veiculo["filial_nome"] = veiculo.get("gp_filiais", {}).get("nome", "")
    pneus = listar_pneus(veiculo_id=veiculo_id, status="em_uso")
    veiculo["pneus"] = {p["posicao"]: p for p in pneus}
    veiculo["config"] = VEHICLE_CONFIGS.get(veiculo.get("tipo", "truck"), VEHICLE_CONFIGS["truck"])
    return veiculo

def desativar_veiculo(veiculo_id):
    return _api_request("PATCH", "gp_veiculos", params={"id": f"eq.{veiculo_id}"}, payload={"ativo": 0})

# ── PNEUS ──────────────────────────────────────────────────────────────────

def listar_pneus(filial_id=None, status=None, veiculo_id=None):
    params = {"select": "*,gp_filiais(nome),gp_veiculos(placa)", "order": "numero_fogo"}
    if filial_id: params["filial_id"] = f"eq.{filial_id}"
    if status: params["status"] = f"eq.{status}"
    if veiculo_id: params["veiculo_id"] = f"eq.{veiculo_id}"
    res = _api_request("GET", "gp_pneus", params=params)
    if not res: return []
    for r in res:
        r["filial_nome"] = r.get("gp_filiais", {}).get("nome", "")
        r["veiculo_placa"] = r.get("gp_veiculos", {}).get("placa", "")
    return res

def criar_pneu(numero_fogo, marca, medida, filial_id, modelo="", dot="", valor=0.0, vida=1, sulco_atual=0.0, nf="", fornecedor=""):
    payload = {
        "numero_fogo": numero_fogo.strip().upper(), "marca": marca.strip(),
        "modelo": modelo.strip(), "medida": medida.strip(), "dot": dot.strip(),
        "valor": float(valor), "vida": int(vida), "filial_id": filial_id,
        "sulco_atual": float(sulco_atual), "nf": str(nf).strip(), "fornecedor": str(fornecedor).strip(),
        "status": "estoque"
    }
    res = _api_request("POST", "gp_pneus", payload=payload)
    return res[0] if res else {}

def obter_pneu(pneu_id):
    params = {"id": f"eq.{pneu_id}", "select": "*,gp_filiais(nome),gp_veiculos(placa)"}
    res = _api_request("GET", "gp_pneus", params=params)
    if not res: return {}
    p = res[0]
    p["filial_nome"] = p.get("gp_filiais", {}).get("nome", "")
    p["veiculo_placa"] = p.get("gp_veiculos", {}).get("placa", "")
    return p

def atualizar_pneu(pneu_id, **kwargs):
    res = _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=kwargs)
    return res[0] if res and isinstance(res, list) else {}

def alocar_pneu(pneu_id, veiculo_id, posicao, km_instalacao=0, observacao=""):
    payload = {"status": "em_uso", "veiculo_id": veiculo_id, "posicao": posicao, "km_instalacao": float(km_instalacao)}
    _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=payload)
    _registrar_movimentacao(pneu_id, "alocacao", veiculo_id=veiculo_id, posicao=posicao, km_momento=km_instalacao, observacao=observacao)
    return obter_pneu(pneu_id)

def remover_pneu(pneu_id, destino="estoque", km_momento=0, observacao="", filial_destino_id=None):
    new_status = destino if destino in ("descarte", "recapagem") else "estoque"
    payload = {"status": new_status, "veiculo_id": None, "posicao": None}
    if filial_destino_id: payload["filial_id"] = filial_destino_id
    _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=payload)
    _registrar_movimentacao(pneu_id, "remocao", km_momento=km_momento, observacao=observacao)
    return obter_pneu(pneu_id)

def _registrar_movimentacao(pneu_id, tipo, **kw):
    payload = {
        "pneu_id": pneu_id, "tipo": tipo,
        "veiculo_id": kw.get("veiculo_id"),
        "posicao": kw.get("posicao"),
        "km_momento": float(kw.get("km_momento", 0)),
        "observacao": kw.get("observacao", "")
    }
    return _api_request("POST", "gp_movimentacoes", payload=payload)

def listar_movimentacoes(pneu_id=None, veiculo_id=None, filial_id=None, tipo=None, limit=50):
    params = {"select": "*,gp_pneus(numero_fogo)", "order": "id.desc", "limit": str(limit)}
    if pneu_id: params["pneu_id"] = f"eq.{pneu_id}"
    res = _api_request("GET", "gp_movimentacoes", params=params)
    return res if res else []

def confirmar_recebimento(pneu_id):
    return _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload={"recebido": 1})

def transferir_pneu(pneu_id, filial_destino_id, observacao=""):
    _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload={"filial_id": filial_destino_id, "recebido": 0})
    _registrar_movimentacao(pneu_id, "transferencia", filial_destino_id=filial_destino_id, observacao=observacao)
    return obter_pneu(pneu_id)

def mover_pneu_veiculo(veiculo_id, pos_origem, pos_destino, observacao="", km_momento=0):
    return True # Implementar logica de troca se necessario

def enviar_para_recicladora(pneu_id, data_envio, observacao=''):
    payload = {"status": "reciclagem", "data_envio_reciclagem": data_envio, "observacao_reciclagem": observacao}
    return _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=payload)

def listar_lotes_reciclagem(filial_id=None): return []
def atualizar_valor_lote_reciclagem(lote_id, valor_total): return True
def obter_relatorio_financeiro_reciclagem(mes=None, filial_id=None): return []

def obter_dashboard():
    pneus = listar_pneus()
    veiculos = listar_veiculos()
    return {
        "total_pneus": len(pneus),
        "em_estoque": len([p for p in pneus if p['status'] == 'estoque']),
        "em_uso": len([p for p in pneus if p['status'] == 'em_uso']),
        "descartados": len([p for p in pneus if p['status'] == 'descarte']),
        "total_veiculos": len(veiculos),
        "valor_estoque": sum(p.get('valor', 0) for p in pneus if p['status'] == 'estoque'),
        "alertas_rodizio": []
    }
