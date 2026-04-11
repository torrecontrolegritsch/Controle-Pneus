"""
Gestão de Pneus — Camada de banco de dados (SQLite local).
Tabelas: gp_filiais, gp_veiculos, gp_pneus, gp_movimentacoes.
Banco: backend/gestao_pneus.db
"""
import logging
import os
import requests
import json
from dotenv import load_dotenv
# Força a busca do .env na pasta raiz do projeto
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, text

# Configuração de Logs para aparecer no Terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

# ── PONTE HTTPS PARA SUPABASE (Contorna Firewall) ─────────────────────────
def _api_request(method, table, params=None, payload=None):
    try:
        supa_key = os.getenv("SUPABASE_KEY")
        if not supa_key: 
            print("!!! ERRO: SUPABASE_KEY não encontrada no .env !!!")
            return None
        
        api_url = f"https://dpvdjldocvdsdgvmnsvu.supabase.co/rest/v1/{table}"
        # print(f"DEBUG: {method} {api_url}") # Útil se quiser ver a URL
        
        headers = {
            "apikey": supa_key,
            "Authorization": f"Bearer {supa_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation" if method == "POST" else ""
        }
        
        if method == "GET":
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            # print(f"DEBUG Payload: {payload}")
            response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=10)
        elif method == "PATCH":
            response = requests.patch(api_url, headers=headers, params=params, data=json.dumps(payload), timeout=10)
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.text else True
        else:
            err_msg = f"ERRO DIRETO DO SUPABASE ({table}): {response.status_code} - {response.text}"
            print("\n" + "!"*60)
            print(err_msg)
            print("!"*60 + "\n")
            return None
    except Exception as e:
        print(f"\n!!! ERRO TÉCNICO NA REQUISIÇÃO ({table}): {e} !!!\n")
        return None

_gp_engine = None

def _get_gp_engine():
    global _gp_engine
    if _gp_engine is None:
        supabase_url = os.getenv("SUPABASE_DB_URL")
        
        if supabase_url:
            logger.info("db_gestao_pneus: Usando Supabase (Modo Online).")
            # Força parâmetros para passar por Firewalls chatos
            if "sslmode" not in supabase_url:
                separator = "&" if "?" in supabase_url else "?"
                supabase_url += f"{separator}sslmode=require"
            
            _gp_engine = create_engine(
                supabase_url, 
                pool_pre_ping=True,
                connect_args={"connect_timeout": 30}
            )
        else:
            logger.error("ERRO: SUPABASE_DB_URL não configurada no ambiente!")
            # Fallback seguro para não quebrar o app completamente, mas avisando que está local
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gestao_pneus.db")
            _gp_engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
            
    return _gp_engine


# ── Configurações de eixos por tipo de veículo ─────────────────────────────

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

# ── Criação das tabelas ────────────────────────────────────────────────────

_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS gp_filiais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        cidade TEXT,
        estado TEXT,
        ativo INTEGER DEFAULT 1,
        criado_em TEXT DEFAULT (datetime('now'))
    )""",
    """CREATE TABLE IF NOT EXISTS gp_veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        placa TEXT NOT NULL UNIQUE,
        frota TEXT,
        modelo TEXT,
        marca TEXT,
        tipo TEXT DEFAULT 'truck',
        km_atual REAL DEFAULT 0,
        filial_id INTEGER REFERENCES gp_filiais(id),
        ativo INTEGER DEFAULT 1,
        criado_em TEXT DEFAULT (datetime('now'))
    )""",
    """CREATE TABLE IF NOT EXISTS gp_pneus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_fogo TEXT NOT NULL UNIQUE,
        marca TEXT NOT NULL,
        modelo TEXT,
        medida TEXT NOT NULL,
        dot TEXT,
        valor REAL DEFAULT 0,
        status TEXT DEFAULT 'estoque',
        vida INTEGER DEFAULT 1,
        filial_id INTEGER REFERENCES gp_filiais(id),
        veiculo_id INTEGER REFERENCES gp_veiculos(id),
        posicao TEXT,
        km_instalacao REAL DEFAULT 0,
        sulco_atual REAL DEFAULT 0,
        km_total REAL DEFAULT 0,
        cpk REAL DEFAULT 0,
        nf TEXT,
        fornecedor TEXT,
        recebido INTEGER DEFAULT 1,
        lote_id INTEGER REFERENCES gp_lotes_reciclagem(id),
        filial_origem_id INTEGER,
        criado_em TEXT DEFAULT (datetime('now', 'localtime')),
        atualizado_em TEXT DEFAULT (datetime('now', 'localtime'))
    )""",
    """CREATE TABLE IF NOT EXISTS gp_movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pneu_id INTEGER REFERENCES gp_pneus(id),
        tipo TEXT NOT NULL,
        filial_origem_id INTEGER REFERENCES gp_filiais(id),
        filial_destino_id INTEGER REFERENCES gp_filiais(id),
        veiculo_id INTEGER REFERENCES gp_veiculos(id),
        posicao TEXT,
        km_momento REAL DEFAULT 0,
        observacao TEXT,
        criado_em TEXT DEFAULT (datetime('now', 'localtime'))
    )""",
    """CREATE TABLE IF NOT EXISTS gp_lotes_reciclagem (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_lote TEXT NOT NULL UNIQUE,
        data_envio TEXT NOT NULL,
        filial_id INTEGER REFERENCES gp_filiais(id),
        status TEXT DEFAULT 'enviado',
        valor_total REAL DEFAULT 0,
        valor_pneu REAL DEFAULT 0,
        criado_em TEXT DEFAULT (datetime('now', 'localtime'))
    )""",
    """CREATE TABLE IF NOT EXISTS veiculos_referencia (
        placa TEXT PRIMARY KEY,
        modelo TEXT,
        marca TEXT,
        frota TEXT,
        tipo TEXT,
        last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
]

def ensure_tables():
    engine = _get_gp_engine()
    is_postgres = "postgresql" in str(engine.url)
    
    with engine.begin() as conn:
        for stmt in _STATEMENTS:
            final_stmt = stmt
            if is_postgres:
                # Converte sintaxe SQLite para PostgreSQL
                final_stmt = final_stmt.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
                final_stmt = final_stmt.replace("datetime('now')", "CURRENT_TIMESTAMP")
                final_stmt = final_stmt.replace("datetime('now', 'localtime')", "CURRENT_TIMESTAMP")
                final_stmt = final_stmt.replace("AUTOINCREMENT", "") # redundante em serial
            
            try:
                conn.execute(text(final_stmt))
            except Exception as e:
                logger.warning(f"Erro ao executar statement (provavelmente tabela já existe): {e}")
            
        # Migrações suaves (adiciona colunas novas se necessário)
        try: conn.execute(text("ALTER TABLE gp_veiculos ADD COLUMN km_atual REAL DEFAULT 0"))
        except Exception: pass
        try: conn.execute(text("ALTER TABLE gp_pneus ADD COLUMN filial_origem_id INTEGER"))
        except Exception: pass
    logger.info("Gestão Pneus: tabelas SQLite configuradas localmente.")

# ── Helpers ────────────────────────────────────────────────────────────────

def _e():
    return _get_gp_engine()

def _fetch_row(conn, table, row_id):
    row = conn.execute(text(f"SELECT * FROM {table} WHERE id = :id"), {"id": row_id}).mappings().first()
    return dict(row) if row else None

# ── FILIAIS ────────────────────────────────────────────────────────────────

def listar_filiais(apenas_ativas=True):
    print("\n" + "="*50)
    print(">>> EXECUTANDO VERSÃO HTTPS (FIREWALL BYPASS) <<<")
    print("="*50 + "\n")
    params = {"select": "*", "order": "nome"}
    if apenas_ativas: params["ativo"] = "eq.1"
    res = _api_request("GET", "gp_filiais", params=params)
    return res if res else []

def criar_filial(nome, cidade="", estado=""):
    payload = {"nome": nome, "cidade": cidade, "estado": estado}
    res = _api_request("POST", "gp_filiais", payload=payload)
    if not res: raise Exception("O Supabase recusou o salvamento da Filial. Verifique a chave ou se o nome já existe.")
    return res[0] if res else {}

def atualizar_filial(filial_id, nome, cidade="", estado=""):
    with _e().begin() as conn:
        conn.execute(text("UPDATE gp_filiais SET nome=:n, cidade=:c, estado=:e WHERE id=:id"),
                     {"id": filial_id, "n": nome.strip(), "c": cidade.strip(), "e": estado.strip().upper()})
        row = conn.execute(text("SELECT * FROM gp_filiais WHERE id=:id"), {"id": filial_id}).mappings().first()
    return dict(row) if row else {}

def desativar_filial(filial_id):
    with _e().begin() as conn:
        conn.execute(text("UPDATE gp_filiais SET ativo=0 WHERE id=:id"), {"id": filial_id})
    return True

# ── VEÍCULOS ───────────────────────────────────────────────────────────────

def listar_veiculos(filial_id=None, apenas_ativos=True):
    params = {"select": "*,gp_filiais(nome)", "order": "placa"}
    if apenas_ativos: params["ativo"] = "eq.1"
    if filial_id: params["filial_id"] = f"eq.{filial_id}"
    res = _api_request("GET", "gp_veiculos", params=params)
    if not res: return []
    # Converte retorno para o formato que o frontend espera
    for r in res:
        r["filial_nome"] = r.get("gp_filiais", {}).get("nome", "") if r.get("gp_filiais") else ""
        cfg = VEHICLE_CONFIGS.get(r.get("tipo", "truck"), VEHICLE_CONFIGS["truck"])
        r["total_posicoes"] = sum(len(e["posicoes"]) for e in cfg["eixos"]) + len(cfg["estepes"])
    return res

def criar_veiculo(placa, frota="", modelo="", marca="", tipo="truck", filial_id=None, km_atual=0):
    with _e().begin() as conn:
        conn.execute(text("INSERT INTO gp_veiculos (placa, frota, modelo, marca, tipo, filial_id, km_atual) VALUES (:p,:f,:m,:ma,:t,:fi,:km)"),
                     {"p": placa.strip().upper().replace("-",""), "f": frota.strip(), "m": modelo.strip(),
                      "ma": marca.strip(), "t": tipo, "fi": filial_id, "km": float(km_atual)})
        row = conn.execute(text("SELECT * FROM gp_veiculos WHERE id=last_insert_rowid()")).mappings().first()
    return dict(row)

def atualizar_veiculo(veiculo_id, **kwargs):
    sets, params = [], {"id": veiculo_id}
    allowed = ["placa", "frota", "modelo", "marca", "tipo", "filial_id", "km_atual"]
    for key in allowed:
        if key in kwargs and kwargs[key] is not None:
            val = kwargs[key]
            if key == "placa": val = str(val).strip().upper().replace("-","")
            elif isinstance(val, str): val = val.strip()
            sets.append(f"{key}=:{key}")
            params[key] = val
    if not sets:
        return {}
    with _e().begin() as conn:
        conn.execute(text(f"UPDATE gp_veiculos SET {','.join(sets)} WHERE id=:id"), params)
        row = conn.execute(text("SELECT * FROM gp_veiculos WHERE id=:id"), {"id": veiculo_id}).mappings().first()
    return dict(row) if row else {}

def obter_veiculo_com_pneus(veiculo_id):
    with _e().connect() as conn:
        vrow = conn.execute(text("SELECT v.*, f.nome as filial_nome FROM gp_veiculos v LEFT JOIN gp_filiais f ON v.filial_id=f.id WHERE v.id=:id"),
                            {"id": veiculo_id}).mappings().first()
        if not vrow:
            return {}
        veiculo = dict(vrow)
        prows = conn.execute(text("SELECT * FROM gp_pneus WHERE veiculo_id=:vid AND status='em_uso' ORDER BY posicao"),
                             {"vid": veiculo_id}).mappings().all()
        pneus_map = {dict(p)["posicao"]: dict(p) for p in prows}
    cfg = VEHICLE_CONFIGS.get(veiculo.get("tipo", "truck"), VEHICLE_CONFIGS["truck"])
    veiculo["config"] = cfg
    veiculo["pneus"] = pneus_map
    return veiculo

def desativar_veiculo(veiculo_id):
    with _e().begin() as conn:
        conn.execute(text("UPDATE gp_veiculos SET ativo=0 WHERE id=:id"), {"id": veiculo_id})
    return True

def criar_veiculo(placa, frota="", modelo="", marca="", tipo="truck", filial_id=None, km_atual=0):
    payload = {
        "placa": placa.strip().upper().replace("-",""),
        "frota": frota.strip(), "modelo": modelo.strip(),
        "marca": marca.strip(), "tipo": tipo, "filial_id": filial_id, "km_atual": float(km_atual)
    }
    res = _api_request("POST", "gp_veiculos", payload=payload)
    if not res: raise Exception("O Supabase recusou o salvamento do Veículo. Verifique se a placa já existe.")
    return res[0] if res else {}

# ── PNEUS ──────────────────────────────────────────────────────────────────

def listar_pneus(filial_id=None, status=None, veiculo_id=None):
    params = {"select": "*,gp_filiais(nome),gp_veiculos(placa)", "order": "numero_fogo"}
    if filial_id: params["filial_id"] = f"eq.{filial_id}"
    if status: params["status"] = f"eq.{status}"
    if veiculo_id: params["veiculo_id"] = f"eq.{veiculo_id}"
    res = _api_request("GET", "gp_pneus", params=params)
    if not res: return []
    for r in res:
        r["filial_nome"] = r.get("gp_filiais", {}).get("nome", "") if r.get("gp_filiais") else ""
        r["veiculo_placa"] = r.get("gp_veiculos", {}).get("placa", "") if r.get("gp_veiculos") else ""
    return res

def criar_pneu(numero_fogo, marca, medida, filial_id, modelo="", dot="", valor=0.0, vida=1, sulco_atual=0.0, nf="", fornecedor=""):
    payload = {
        "numero_fogo": numero_fogo.strip().upper(), "marca": marca.strip(),
        "modelo": modelo.strip(), "medida": medida.strip(), "dot": dot.strip(),
        "valor": float(valor), "vida": int(vida), "filial_id": filial_id,
        "sulco_atual": float(sulco_atual), "nf": str(nf).strip(), "fornecedor": str(fornecedor).strip()
    }
    res = _api_request("POST", "gp_pneus", payload=payload)
    if not res: raise Exception("O Supabase recusou o salvamento do Pneu. Verifique se o Nº Fogo já existe.")
    return res[0] if res else {}

def atualizar_pneu(pneu_id, **kwargs):
    res = _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=kwargs)
    return res[0] if res and isinstance(res, list) else {}

def obter_pneu(pneu_id):
    params = {"id": f"eq.{pneu_id}", "select": "*,gp_filiais(nome),gp_veiculos(placa)"}
    res = _api_request("GET", "gp_pneus", params=params)
    if res:
        p = res[0]
        p["filial_nome"] = p.get("gp_filiais", {}).get("nome", "")
        p["veiculo_placa"] = p.get("gp_veiculos", {}).get("placa", "")
        return p
    return {}

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
    if veiculo_id: params["veiculo_id"] = f"eq.{veiculo_id}"
    if filial_id: params["filial_id"] = f"eq.{filial_id}"
    if tipo: params["tipo"] = f"eq.{tipo}"
    res = _api_request("GET", "gp_movimentacoes", params=params)
    return res if res else []

def confirmar_recebimento(pneu_id):
    return _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload={"recebido": 1})

def transferir_pneu(pneu_id, filial_destino_id, observacao=""):
    _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload={"filial_id": filial_destino_id, "recebido": 0})
    _registrar_movimentacao(pneu_id, "transferencia", filial_destino_id=filial_destino_id, observacao=observacao)
    return obter_pneu(pneu_id)

def mover_pneu_veiculo(veiculo_id, pos_origem, pos_destino, observacao="", km_momento=0):
    # Lógica de rodízio via API
    res = _api_request("GET", "gp_pneus", params={"veiculo_id": f"eq.{veiculo_id}"})
    p_orig = next((p for p in res if p["posicao"] == pos_origem), None) if res else None
    p_dest = next((p for p in res if p["posicao"] == pos_destino), None) if res else None
    
    if p_orig:
        _api_request("PATCH", "gp_pneus", params={"id": f"eq.{p_orig['id']}"}, payload={"posicao": pos_destino})
        _registrar_movimentacao(p_orig['id'], "rodizio", veiculo_id=veiculo_id, posicao=pos_destino, km_momento=km_momento, observacao=f"Rodizio: {pos_origem}->{pos_destino}")
    if p_dest:
        _api_request("PATCH", "gp_pneus", params={"id": f"eq.{p_dest['id']}"}, payload={"posicao": pos_origem})
        _registrar_movimentacao(p_dest['id'], "rodizio", veiculo_id=veiculo_id, posicao=pos_origem, km_momento=km_momento, observacao=f"Rodizio: {pos_destino}->{pos_origem}")
    return True

def enviar_para_recicladora(pneu_id, data_envio, observacao=''):
    payload = {"status": "reciclagem", "data_envio_reciclagem": data_envio, "observacao_reciclagem": observacao}
    return _api_request("PATCH", "gp_pneus", params={"id": f"eq.{pneu_id}"}, payload=payload)

def listar_lotes_reciclagem(filial_id=None):
    return [] # Implementação futura se necessário

def atualizar_valor_lote_reciclagem(lote_id, valor_total):
    return True

def obter_relatorio_financeiro_reciclagem(mes=None, filial_id=None):
    return []

def obter_dashboard():
    return {
        "total_pneus": 0, "em_estoque": 0, "em_uso": 0,
        "descartados": 0, "total_veiculos": 0,
        "valor_estoque": 0, "alertas_rodizio": []
    }
