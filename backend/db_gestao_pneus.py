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

# Localiza o arquivo .env na raiz do projeto (Pneus/.env)
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    # Tenta carregar do ambiente direto (Vercel)
    load_dotenv()

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

# ── PONTE HTTPS PARA SUPABASE (Contorna Firewall) ─────────────────────────
def _api_request(method, table, params=None, payload=None):
    try:
        supa_key = os.getenv("SUPABASE_KEY")
        if not supa_key: 
            logger.error("!!! SUPABASE_KEY não encontrada !!!")
            return None
            
        # Tenta pegar a URL do Supabase do .env ou usa o ID fixo se falhar
        supa_url = os.getenv("SUPABASE_URL")
        if not supa_url:
            # Se não tiver URL, tenta extrair do ID que já conhecemos
            project_id = "dpvdjldocvdsdgvmnsvu"
            supa_url = f"https://{project_id}.supabase.co"
            
        api_url = f"{supa_url.rstrip('/')}/rest/v1/{table}"
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
            print(f"  [OK] {method} {table} - Status: {response.status_code}")
            if not response.text or response.status_code == 204: 
                # Retorna lista vazia para GET e dict vazio para outros se não houver conteúdo
                return [] if method == "GET" else {}
            res_json = response.json()
            if method == "GET" and isinstance(res_json, list):
                print(f"  [DADOS] {len(res_json)} registros encontrados")
            return res_json
        else:
            print(f"  [ERRO] {method} {table} - Status: {response.status_code} - Resposta: {response.text}")
            from fastapi import HTTPException
            raise HTTPException(status_code=response.status_code, detail=response.text)
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
    if not isinstance(res, list): return []
    for r in res:
        # Proteção contra campos nulos em Joins
        filial_obj = r.get("gp_filiais")
        r["filial_nome"] = filial_obj.get("nome", "") if isinstance(filial_obj, dict) else ""
        
        veiculo_obj = r.get("gp_veiculos")
        r["veiculo_placa"] = veiculo_obj.get("placa", "") if isinstance(veiculo_obj, dict) else ""
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

    # Mapeamento de sinonimos para colunas comuns
    mapping = {
        "numero_fogo": ["numero_fogo", "fogo", "n fogo", "nº fogo", "num fogo", "numero do fogo", "n.fogo"],
        "marca": ["marca", "fabricante"],
        "modelo": ["modelo", "tipo"],
        "medida": ["medida", "dimensao", "tamanho"],
        "dot": ["dot", "data"],
        "vida": ["vida", "v"],
        "valor": ["valor", "preço", "custo", "preco"],
        "sulco_atual": ["sulco_atual", "sulco", "profundidade"],
        "fornecedor": ["fornecedor"],
        "nf": ["nf", "nota fiscal", "nota"],
        "filial": ["filial", "unidade", "deposito"]
    }

    def find_val(row_dict, target_key):
        # Normaliza as chaves do dicionário para comparação
        norm_row = {str(k).strip().lower(): v for k, v in row_dict.items()}
        for syn in mapping.get(target_key, []):
            if syn in norm_row:
                return norm_row[syn]
        return None

    def safe_float(val):
        if val is None or val == "": return 0.0
        try:
            # Converte para string e troca vírgula por ponto
            s_val = str(val).replace(',', '.')
            return float(s_val)
        except:
            return 0.0

    pneus_list = []
    for p_raw in pneus_data:
        f_name = find_val(p_raw, "filial")
        f_id = get_filial_id(f_name)
        
        p_norm = {
            "numero_fogo": str(find_val(p_raw, "numero_fogo") or "").strip().upper(),
            "marca": str(find_val(p_raw, "marca") or "").strip().upper(),
            "modelo": str(find_val(p_raw, "modelo") or "").strip().upper(),
            "medida": str(find_val(p_raw, "medida") or "").strip(),
            "dot": str(find_val(p_raw, "dot") or "").strip(),
            "vida": int(find_val(p_raw, "vida") or 1),
            "valor": safe_float(find_val(p_raw, "valor")),
            "sulco_atual": safe_float(find_val(p_raw, "sulco_atual")),
            "fornecedor": str(find_val(p_raw, "fornecedor") or "").strip(),
            "nf": str(find_val(p_raw, "nf") or "").strip(),
            "filial_id": f_id,
            "status": "estoque",
            "recebido": 1
        }
        
        if p_norm["numero_fogo"] and p_norm["marca"] and p_norm["medida"]:
            pneus_list.append(p_norm)
    
    if not pneus_list:
        return {"count": 0, "error": "Nenhum pneu válido encontrado. Verifique se as colunas obrigatórias estão presentes (Fogo, Marca, Medida)."}

    # Busca pneus existentes para identificar duplicatas (evita contar como novo o que já existe)
    try:
        p_existentes = _api_request("GET", "gp_pneus", params={"select": "numero_fogo"})
        fogos_existentes = {str(p["numero_fogo"]).strip().upper() for p in p_existentes} if isinstance(p_existentes, list) else set()
    except:
        fogos_existentes = set()

    novos_count = sum(1 for p in pneus_list if p["numero_fogo"] not in fogos_existentes)
    atualizados_count = len(pneus_list) - novos_count

    # Divide em lotes de 100
    chunk_size = 100
    for i in range(0, len(pneus_list), chunk_size):
        chunk = pneus_list[i:i + chunk_size]
        _api_request("POST", "gp_pneus", params={"on_conflict": "numero_fogo"}, payload=chunk)
    
    msg = f"Importação concluída! {novos_count} pneus novos adicionados"
    if atualizados_count > 0:
        msg += f" e {atualizados_count} pneus já existentes foram atualizados."
    else:
        msg += "."

    return {"count": len(pneus_list), "novos": novos_count, "atualizados": atualizados_count, "message": msg, "success": True}

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
    # 1. Busca estado atual para saber de onde está saindo
    current = obter_pneu(pneu_id)
    veiculo_id = current.get("veiculo_id")
    posicao = current.get("posicao")
    
    # 2. Atualiza o status do pneu
    new_status = destino if destino in ("descarte", "recapagem") else "estoque"
    f_dest_id = int(filial_destino_id) if filial_destino_id and str(filial_destino_id).isdigit() else None
    
    payload = {"status": new_status, "veiculo_id": None, "posicao": None}
    if f_dest_id: payload["filial_id"] = f_dest_id
    
    _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=payload)
    
    # 3. Registra a movimentação com o contexto completo (de onde saiu -> para onde foi)
    _registrar_movimentacao(
        pneu_id, 
        "remocao", 
        veiculo_id=veiculo_id, 
        posicao=posicao, 
        km_momento=km_momento, 
        observacao=observacao,
        filial_id=f_dest_id
    )
    
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

def listar_movimentacoes(pneu_id=None, veiculo_id=None, filial_id=None, tipo=None, limit=100):
    params = {"select": "*,gp_pneus(numero_fogo),gp_veiculos(placa)", "order": "id.desc", "limit": str(limit)}
    if pneu_id: params["pneu_id"] = f"eq.{pneu_id}"
    if veiculo_id: params["veiculo_id"] = f"eq.{veiculo_id}"
    if filial_id: params["filial_id"] = f"eq.{filial_id}"
    if tipo: params["tipo"] = f"eq.{tipo}"
    
    res = _api_request("GET", "gp_movimentacoes", params=params)
    if not isinstance(res, list): return []
    
    for r in res:
        # Achata numero_fogo
        pneu_obj = r.get("gp_pneus")
        r["numero_fogo"] = pneu_obj.get("numero_fogo", "—") if isinstance(pneu_obj, dict) else "—"
        
        # Achata veiculo_placa
        veiculo_obj = r.get("gp_veiculos")
        r["veiculo_placa"] = veiculo_obj.get("placa", "") if isinstance(veiculo_obj, dict) else ""
        
    return res

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
    try:
        pneus = listar_pneus()
        veiculos = listar_veiculos()
        
        # Garante que pneus e veiculos sejam listas
        if not isinstance(pneus, list): pneus = []
        if not isinstance(veiculos, list): veiculos = []
        
        return {
            "total_pneus": len(pneus),
            "em_estoque": len([p for p in pneus if str(p.get('status')).lower() == 'estoque']),
            "em_uso": len([p for p in pneus if str(p.get('status')).lower() == 'em_uso']),
            "descartados": len([p for p in pneus if str(p.get('status')).lower() == 'descarte']),
            "total_veiculos": len(veiculos),
            "valor_estoque": sum(float(p.get('valor', 0) or 0) for p in pneus if str(p.get('status')).lower() == 'estoque'),
            "alertas_rodizio": []
        }
    except Exception as e:
        logger.error(f"Falha ao processar dados do dashboard: {e}")
        return {
            "total_pneus": 0, "em_estoque": 0, "em_uso": 0, "descartados": 0, 
            "total_veiculos": 0, "valor_estoque": 0, "alertas_rodizio": [], "error": str(e)
        }
