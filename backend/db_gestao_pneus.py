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
            "Prefer": "return=representation,resolution=merge-duplicates" if method == "POST" else ""
        }
        
        if method == "GET":
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            # Converte para lista se não for, para suportar upsert do PostgREST
            data = payload if isinstance(payload, list) else [payload]
            response = requests.post(api_url, headers=headers, params=params, data=json.dumps(data), timeout=10)
        elif method == "PATCH":
            response = requests.patch(api_url, headers=headers, params=params, data=json.dumps(payload), timeout=10)
        
        if response.status_code in [200, 201, 204]:
            if not response.text: return True
            res_json = response.json()
            # Se for uma lista (comum no PostgREST com return=representation), retorna o primeiro item se esperado
            return res_json
        else:
            from fastapi import HTTPException
            error_detail = response.text
            try:
                # Tenta extrair mensagem amigável se for JSON
                err_data = response.json()
                if 'message' in err_data: error_detail = err_data['message']
            except: pass
            raise HTTPException(status_code=response.status_code, detail=error_detail)
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
            {"num": 3, "nome": "Eixo 3 - Tração", "tipo": "duplo", "posicoes": ["E3_ESQ_EXT", "E3_ESQ_INT", "E3_DIR_INT", "E3_DIR_EXT"]},
            {"num": 4, "nome": "Eixo 4 - Truck", "tipo": "duplo", "posicoes": ["E4_ESQ_EXT", "E4_ESQ_INT", "E4_DIR_INT", "E4_DIR_EXT"]},
        ],
        "estepes": ["ESTEPE_1", "ESTEPE_2"],
    },
}

def ensure_tables():
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
    f_id = int(filial_id) if filial_id and str(filial_id).isdigit() else None
    payload = {
        "placa": placa.strip().upper().replace("-",""),
        "frota": str(frota).strip(), "modelo": str(modelo).strip(),
        "marca": str(marca).strip(), "tipo": tipo, "filial_id": f_id, "km_atual": float(km_atual or 0)
    }
    res = _api_request("POST", "gp_veiculos", params={"on_conflict": "placa"}, payload=payload)
    return res[0] if res and isinstance(res, list) else (res if res else {})

def atualizar_veiculo(veiculo_id, **kwargs):
    if "filial_id" in kwargs:
         kwargs["filial_id"] = int(kwargs["filial_id"]) if kwargs["filial_id"] and str(kwargs["filial_id"]).isdigit() else None
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
    f_id = int(filial_id) if filial_id and str(filial_id).isdigit() else None
    payload = {
        "numero_fogo": numero_fogo.strip().upper(), "marca": marca.strip(),
        "modelo": modelo.strip(), "medida": medida.strip(), "dot": dot.strip(),
        "valor": float(valor), "vida": int(vida), "filial_id": f_id,
        "sulco_atual": float(sulco_atual), "nf": str(nf).strip(), "fornecedor": str(fornecedor).strip(),
        "status": "estoque"
    }
    res = _api_request("POST", "gp_pneus", params={"on_conflict": "numero_fogo"}, payload=payload)
    return res[0] if res and isinstance(res, list) else (res if res else {})

def importar_pneus_lote(pneus_data):
    """Importa uma lista de pneus em lote para o Supabase."""
    if not pneus_data:
        return {"count": 0, "message": "Nenhum dado recebido"}
    
    # Busca filiais para converter Nome em ID
    filiais = listar_filiais()
    def get_filial_id(nome):
        if not nome: return None
        n = str(nome).strip().upper()
        f = next((x for x in filiais if x["nome"].strip().upper() == n), None)
        return f["id"] if f else None

    # Normaliza dados e garante tipos
    pneus_list = []
    for p_raw in pneus_data:
        # Normaliza chaves (tira espaços e deixa minúsculo)
        p = {str(k).strip().lower(): v for k, v in p_raw.items()}
        
        # Busca f_id (tentando 'filial' ou 'filial_id')
        f_id = get_filial_id(p.get("filial"))
        if not f_id and p.get("filial_id"):
            val_f = str(p.get("filial_id")).strip()
            f_id = int(val_f) if val_f.isdigit() else None

        p_norm = {
            "numero_fogo": str(p.get("numero_fogo", "")).strip().upper(),
            "marca": str(p.get("marca", "")).strip().upper(),
            "modelo": str(p.get("modelo", "")).strip().upper(),
            "medida": str(p.get("medida", "")).strip(),
            "dot": str(p.get("dot", "")).strip(),
            "vida": int(p.get("vida", 1) or 1),
            "valor": float(p.get("valor", 0) or 0),
            "sulco_atual": float(p.get("sulco_atual", 0) or 0),
            "fornecedor": str(p.get("fornecedor", "")).strip(),
            "nf": str(p.get("nf", "")).strip(),
            "filial_id": f_id,
            "status": "estoque",
            "recebido": 1
        }
        
    # Só adiciona se tiver os campos mínimos
        if p_norm["numero_fogo"] and p_norm["marca"] and p_norm["medida"]:
            pneus_list.append(p_norm)
    
    if not pneus_list:
        return {"count": 0, "error": "Nenhum pneu válido encontrado. Verifique se as colunas estão corretas (numero_fogo, marca, medida, etc)."}

    # Divide em lotes de 100 para não estourar payload
    chunk_size = 100
    for i in range(0, len(pneus_list), chunk_size):
        chunk = pneus_list[i:i + chunk_size]
        _api_request("POST", "gp_pneus", params={"on_conflict": "numero_fogo"}, payload=chunk)
    
    return {"count": len(pneus_list), "imported": True}

def obter_pneu(pneu_id):
    params = {"id": f"eq.{pneu_id}", "select": "*,gp_filiais(nome),gp_veiculos(placa)"}
    res = _api_request("GET", "gp_pneus", params=params)
    if not res: return {}
    p = res[0]
    p["filial_nome"] = p.get("gp_filiais", {}).get("nome", "")
    p["veiculo_placa"] = p.get("gp_veiculos", {}).get("placa", "")
    return p

def atualizar_pneu(pneu_id, **kwargs):
    if "filial_id" in kwargs:
         kwargs["filial_id"] = int(kwargs["filial_id"]) if kwargs["filial_id"] and str(kwargs["filial_id"]).isdigit() else None
    res = _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=kwargs)
    return res[0] if res and isinstance(res, list) else {}

def alocar_pneu(pneu_id, veiculo_id, posicao, km_instalacao=0, observacao=""):
    payload = {"status": "em_uso", "veiculo_id": veiculo_id, "posicao": posicao, "km_instalacao": float(km_instalacao)}
    _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=payload)
    _registrar_movimentacao(pneu_id, "alocacao", veiculo_id=veiculo_id, posicao=posicao, km_momento=km_instalacao, observacao=observacao)
    return obter_pneu(pneu_id)

def remover_pneu(pneu_id, destino="estoque", km_momento=0, observacao="", filial_destino_id=None):
    new_status = destino if destino in ("descarte", "recapagem") else "estoque"
    f_dest_id = int(filial_destino_id) if filial_destino_id and str(filial_destino_id).isdigit() else None
    payload = {"status": new_status, "veiculo_id": None, "posicao": None}
    if f_dest_id: payload["filial_id"] = f_dest_id
    _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=payload)
    _registrar_movimentacao(pneu_id, "remocao", km_momento=km_momento, observacao=observacao)
    return obter_pneu(pneu_id)

def _registrar_movimentacao(pneu_id, tipo, **kw):
    f_id = int(kw.get("filial_id")) if kw.get("filial_id") and str(kw.get("filial_id")).isdigit() else None
    payload = {
        "pneu_id": pneu_id, "tipo": tipo,
        "veiculo_id": kw.get("veiculo_id"),
        "posicao": kw.get("posicao"),
        "km_momento": float(kw.get("km_momento", 0)),
        "observacao": kw.get("observacao", ""),
        "filial_destino_id": f_id
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
    f_dest_id = int(filial_destino_id) if filial_destino_id and str(filial_destino_id).isdigit() else None
    _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload={"filial_id": f_dest_id, "recebido": 0})
    _registrar_movimentacao(pneu_id, "transferencia", filial_id=f_dest_id, observacao=observacao)
    return obter_pneu(pneu_id)

def mover_pneu_veiculo(veiculo_id, pos_origem, pos_destino, observacao="", km_momento=0):
    return True

def enviar_para_recicladora(pneu_id, data_envio, observacao=''):
    payload = {"status": "reciclagem", "data_envio_reciclagem": data_envio, "observacao_reciclagem": observacao}
    return _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=payload)

def listar_lotes_reciclagem(filial_id=None):
    # Por enquanto retorna vazio pois não temos tabela de lotes, 
    # mas poderíamos agrupar os pneus em status 'reciclagem'
    return []

def atualizar_valor_lote_reciclagem(lote_id, valor_total):
    return True

def obter_relatorio_financeiro_reciclagem(mes=None, filial_id=None):
    # Busca pneus que estão em reciclagem
    params = {"status": "eq.reciclagem", "select": "*,gp_filiais(nome)"}
    if filial_id:
        params["filial_id"] = f"eq.{filial_id}"
    
    pneus = _api_request("GET", "gp_pneus", params=params)
    if not pneus or not isinstance(pneus, list):
        return {"resumo_filiais": [], "detalhes": [], "total_geral": 0}
    
    # Filtrar por mês se fornecido (YYYY-MM)
    if mes:
        pneus = [p for p in pneus if p.get('data_envio_reciclagem') and p['data_envio_reciclagem'].startswith(mes)]
    
    resumo = {}
    total_geral = 0
    
    for p in pneus:
        f_nome = p.get('gp_filiais', {}).get('nome') if p.get('gp_filiais') else 'Sem Filial'
        valor = float(p.get('valor_arrecadado', 0) or 0)
        
        total_geral += valor
        if f_nome not in resumo:
            resumo[f_nome] = {"nome": f_nome, "pneus": 0, "total": 0}
        resumo[f_nome]["pneus"] += 1
        resumo[f_nome]["total"] += valor
        
    return {
        "resumo_filiais": list(resumo.values()),
        "detalhes": pneus,
        "total_geral": total_geral
    }

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
