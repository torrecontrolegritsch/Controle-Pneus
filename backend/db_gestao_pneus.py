"""
Gestão de Pneus — Camada de banco de dados (SQLite local).
Tabelas: gp_filiais, gp_veiculos, gp_pneus, gp_movimentacoes.
Banco: backend/gestao_pneus.db
"""
import logging
import os
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

_gp_engine = None

def _get_gp_engine():
    global _gp_engine
    if _gp_engine is None:
        # Tenta usar Supabase se estiver configurado
        supabase_url = os.getenv("SUPABASE_DB_URL")
        if supabase_url and "SUA_SENHA_AQUI" not in supabase_url:
            logger.info("db_gestao_pneus: Usando Supabase (PostgreSQL) como banco de dados.")
            _gp_engine = create_engine(supabase_url)
        else:
            logger.info("db_gestao_pneus: Usando SQLite local.")
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
    sql = "SELECT * FROM gp_filiais"
    if apenas_ativas:
        sql += " WHERE ativo = 1"
    sql += " ORDER BY nome"
    with _e().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql)).mappings().all()]

def criar_filial(nome, cidade="", estado=""):
    with _e().begin() as conn:
        conn.execute(text("INSERT INTO gp_filiais (nome, cidade, estado) VALUES (:n, :c, :e)"),
                     {"n": nome.strip(), "c": cidade.strip(), "e": estado.strip().upper()})
        row = conn.execute(text("SELECT * FROM gp_filiais WHERE id = last_insert_rowid()")).mappings().first()
    return dict(row)

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
    sql = "SELECT v.*, f.nome as filial_nome FROM gp_veiculos v LEFT JOIN gp_filiais f ON v.filial_id=f.id WHERE 1=1"
    params = {}
    if apenas_ativos:
        sql += " AND v.ativo=1"
    if filial_id:
        sql += " AND v.filial_id=:fid"
        params["fid"] = filial_id
    sql += " ORDER BY v.placa"
    with _e().connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
        result = []
        for r in rows:
            d = dict(r)
            cnt = conn.execute(text("SELECT COUNT(*) as total FROM gp_pneus WHERE veiculo_id=:vid AND status='em_uso'"),
                               {"vid": d["id"]}).mappings().first()
            cfg = VEHICLE_CONFIGS.get(d.get("tipo", "truck"), VEHICLE_CONFIGS["truck"])
            d["pneus_alocados"] = cnt["total"] if cnt else 0
            d["total_posicoes"] = sum(len(e["posicoes"]) for e in cfg["eixos"]) + len(cfg["estepes"])
            result.append(d)
    return result

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

# ── PNEUS ──────────────────────────────────────────────────────────────────

def listar_pneus(filial_id=None, status=None, veiculo_id=None):
    sql = """SELECT p.*, f.nome as filial_nome, v.placa as veiculo_placa,
                    fo.nome as filial_origem_nome
             FROM gp_pneus p 
             LEFT JOIN gp_filiais f ON p.filial_id=f.id
             LEFT JOIN gp_filiais fo ON p.filial_origem_id=fo.id
             LEFT JOIN gp_veiculos v ON p.veiculo_id=v.id WHERE 1=1"""
    params = {}
    if filial_id:
        sql += " AND p.filial_id=:fid"; params["fid"] = filial_id
    if status:
        sql += " AND p.status=:st"; params["st"] = status
    if veiculo_id:
        sql += " AND p.veiculo_id=:vid"; params["vid"] = veiculo_id
    sql += " ORDER BY p.numero_fogo"
    with _e().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings().all()]

def criar_pneu(numero_fogo, marca, medida, filial_id, modelo="", dot="", valor=0.0, vida=1, sulco_atual=0.0, nf="", fornecedor=""):
    with _e().begin() as conn:
        conn.execute(text("""
            INSERT INTO gp_pneus (numero_fogo, marca, modelo, medida, dot, valor, vida, filial_id, sulco_atual, nf, fornecedor)
            VALUES (:nfog, :ma, :mo, :med, :d, :val, :vi, :fi, :su, :nf, :forn)
        """), {
            "nfog": numero_fogo.strip(), "ma": marca.strip(), "mo": modelo.strip(), "med": medida.strip(),
            "d": dot.strip(), "val": float(valor), "vi": int(vida), "fi": filial_id, "su": float(sulco_atual),
            "nf": str(nf).strip(), "fornecedor": str(fornecedor).strip()
        })
        row = conn.execute(text("SELECT * FROM gp_pneus WHERE id=last_insert_rowid()")).mappings().first()
        pneu_id = row["id"]
    _registrar_movimentacao(pneu_id, "entrada_estoque", filial_destino_id=filial_id, observacao="Pneu cadastrado no estoque")
    return dict(row)

def atualizar_pneu(pneu_id, **kwargs):
    allowed = ["numero_fogo", "marca", "modelo", "medida", "dot", "valor", "vida", "sulco_atual", "nf", "fornecedor"]
    sets, params = [], {"id": pneu_id}
    for key in allowed:
        if key in kwargs and kwargs[key] is not None:
            val = kwargs[key]
            if key == "numero_fogo": val = str(val).strip().upper()
            elif isinstance(val, str): val = val.strip()
            sets.append(f"{key}=:{key}")
            params[key] = val
    sets.append("atualizado_em=datetime('now')")
    with _e().begin() as conn:
        conn.execute(text(f"UPDATE gp_pneus SET {','.join(sets)} WHERE id=:id"), params)
        row = conn.execute(text("SELECT * FROM gp_pneus WHERE id=:id"), {"id": pneu_id}).mappings().first()
    return dict(row) if row else {}

def obter_pneu(pneu_id):
    with _e().connect() as conn:
        row = conn.execute(text("""SELECT p.*, f.nome as filial_nome, fo.nome as filial_origem_nome, v.placa as veiculo_placa
                                   FROM gp_pneus p 
                                   LEFT JOIN gp_filiais f ON p.filial_id=f.id
                                   LEFT JOIN gp_filiais fo ON p.filial_origem_id=fo.id
                                   LEFT JOIN gp_veiculos v ON p.veiculo_id=v.id WHERE p.id=:id"""),
                           {"id": pneu_id}).mappings().first()
    return dict(row) if row else {}

def alocar_pneu(pneu_id, veiculo_id, posicao, km_instalacao=0, observacao=""):
    with _e().begin() as conn:
        veiculo = conn.execute(text("SELECT * FROM gp_veiculos WHERE id=:id"), {"id": veiculo_id}).mappings().first()
        if not veiculo: raise ValueError("Veículo não encontrado")
        
        conn.execute(text("""UPDATE gp_pneus SET status='em_uso', veiculo_id=:vid, posicao=:pos,
                             km_instalacao=:km, filial_id=:fid, recebido=1, atualizado_em=datetime('now') WHERE id=:id"""),
                     {"id": pneu_id, "vid": veiculo_id, "pos": posicao, "km": km_instalacao, "fid": veiculo["filial_id"]})
        
        _registrar_movimentacao(pneu_id, "alocacao", conn=conn, veiculo_id=veiculo_id, posicao=posicao,
                                km_momento=km_instalacao, filial_destino_id=veiculo["filial_id"],
                                observacao=observacao or f"Pneu alocado na posição {posicao}")
    return obter_pneu(pneu_id)

def remover_pneu(pneu_id, destino="estoque", km_momento=0, observacao="", filial_destino_id=None):
    with _e().begin() as conn:
        pneu = conn.execute(text("SELECT * FROM gp_pneus WHERE id=:id"), {"id": pneu_id}).mappings().first()
        if not pneu: raise ValueError("Pneu não encontrado")
        
        new_status = destino if destino in ("descarte", "recapagem") else "estoque"
        km_inst = pneu["km_instalacao"] or 0
        km_momento = float(km_momento)
        km_rodado_etapa = km_momento - km_inst if km_momento > km_inst else 0
        km_total_novo = (pneu.get("km_total") or 0) + km_rodado_etapa
        
        fid = filial_destino_id if filial_destino_id else pneu["filial_id"]
        
        conn.execute(text("""UPDATE gp_pneus SET status=:st, veiculo_id=NULL, posicao=NULL, filial_id=:fid, 
                             km_total=:kmt, recebido=0, atualizado_em=datetime('now') WHERE id=:id"""),
                     {"id": pneu_id, "st": new_status, "fid": fid, "kmt": km_total_novo})
        
        _registrar_movimentacao(pneu_id, "remocao", conn=conn, veiculo_id=pneu["veiculo_id"], posicao=pneu["posicao"],
                                km_momento=km_momento, filial_origem_id=pneu["filial_id"], filial_destino_id=fid,
                                observacao=f"Removido com {km_rodado_etapa}km rodados. " + observacao)
    return obter_pneu(pneu_id)

def transferir_pneu(pneu_id, filial_destino_id, observacao=""):
    with _e().begin() as conn:
        pneu = conn.execute(text("SELECT filial_id FROM gp_pneus WHERE id=:id"), {"id": pneu_id}).mappings().first()
        conn.execute(text("UPDATE gp_pneus SET filial_id=:fid, recebido=0, atualizado_em=datetime('now') WHERE id=:id"),
                     {"id": pneu_id, "fid": filial_destino_id})
        _registrar_movimentacao(pneu_id, "transferencia", conn=conn, filial_origem_id=pneu["filial_id"],
                                filial_destino_id=filial_destino_id, observacao=observacao)
    return obter_pneu(pneu_id)

def mover_pneu_veiculo(veiculo_id, pos_origem, pos_destino, observacao="", km_momento=0):
    with _e().begin() as conn:
        p_orig = conn.execute(text("SELECT id FROM gp_pneus WHERE veiculo_id=:vid AND posicao=:pos"),
                              {"vid": veiculo_id, "pos": pos_origem}).mappings().first()
        p_dest = conn.execute(text("SELECT id FROM gp_pneus WHERE veiculo_id=:vid AND posicao=:pos"),
                              {"vid": veiculo_id, "pos": pos_destino}).mappings().first()
        
        if p_orig:
            conn.execute(text("UPDATE gp_pneus SET posicao=:pos WHERE id=:id"), {"pos": pos_destino, "id": p_orig["id"]})
            _registrar_movimentacao(p_orig["id"], "rodizio", conn=conn, veiculo_id=veiculo_id, posicao=pos_destino, 
                                    km_momento=float(km_momento), observacao=f"Rodízio: {pos_origem} -> {pos_destino}")
        if p_dest:
            conn.execute(text("UPDATE gp_pneus SET posicao=:pos WHERE id=:id"), {"pos": pos_origem, "id": p_dest["id"]})
            _registrar_movimentacao(p_dest["id"], "rodizio", conn=conn, veiculo_id=veiculo_id, posicao=pos_origem, 
                                    km_momento=float(km_momento), observacao=f"Rodízio: {pos_destino} -> {pos_origem}")
    return True

# ── HISTÓRICO ──────────────────────────────────────────────────────────────

def _registrar_movimentacao(pneu_id, tipo, conn=None, **kw):
    stmt = text("""INSERT INTO gp_movimentacoes (pneu_id,tipo,filial_origem_id,filial_destino_id,veiculo_id,posicao,km_momento,observacao)
                   VALUES (:pid,:tp,:fo,:fd,:vid,:pos,:km,:obs)""")
    params = {"pid": pneu_id, "tp": tipo, "fo": kw.get("filial_origem_id"), "fd": kw.get("filial_destino_id"),
              "vid": kw.get("veiculo_id"), "pos": kw.get("posicao"), "km": kw.get("km_momento", 0),
              "obs": kw.get("observacao", "")}
    if conn: conn.execute(stmt, params)
    else:
        with _e().begin() as conn: conn.execute(stmt, params)

def listar_movimentacoes(pneu_id=None, veiculo_id=None, filial_id=None, tipo=None, limit=100):
    sql = """SELECT m.*, p.numero_fogo, p.marca as pneu_marca, p.medida as pneu_medida,
                    fo.nome as filial_origem_nome, fd.nome as filial_destino_nome, 
                    v.placa as veiculo_placa
             FROM gp_movimentacoes m
             LEFT JOIN gp_pneus p ON m.pneu_id=p.id
             LEFT JOIN gp_filiais fo ON m.filial_origem_id=fo.id
             LEFT JOIN gp_filiais fd ON m.filial_destino_id=fd.id
             LEFT JOIN gp_veiculos v ON m.veiculo_id=v.id WHERE 1=1"""
    params = {}
    if pneu_id: sql += " AND m.pneu_id=:pid"; params["pid"] = pneu_id
    if veiculo_id: sql += " AND m.veiculo_id=:vid"; params["vid"] = veiculo_id
    if filial_id: sql += " AND (m.filial_origem_id=:fid OR m.filial_destino_id=:fid)"; params["fid"] = filial_id
    if tipo: sql += " AND m.tipo=:tp"; params["tp"] = tipo
    sql += " ORDER BY m.id DESC LIMIT :lim"
    params["lim"] = limit
    with _e().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings().all()]

# ── DASHBOARD KPIs ─────────────────────────────────────────────────────────

def obter_dashboard():
    with _e().connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM gp_pneus")).scalar() or 0
        estoque = conn.execute(text("SELECT COUNT(*) FROM gp_pneus WHERE status='estoque'")).scalar() or 0
        em_uso = conn.execute(text("SELECT COUNT(*) FROM gp_pneus WHERE status='em_uso'")).scalar() or 0
        descartados = conn.execute(text("SELECT COUNT(*) FROM gp_pneus WHERE status='descarte'")).scalar() or 0
        veiculos = conn.execute(text("SELECT COUNT(*) FROM gp_veiculos WHERE ativo=1")).scalar() or 0
        val_estoque = conn.execute(text("SELECT COALESCE(SUM(valor),0) FROM gp_pneus WHERE status='estoque'")).scalar() or 0
        
        pneus_uso = conn.execute(text("""SELECT p.numero_fogo, p.km_instalacao, v.placa, v.km_atual, p.posicao
                                         FROM gp_pneus p JOIN gp_veiculos v ON p.veiculo_id = v.id
                                         WHERE p.status='em_uso'""")).mappings().all()

    alertas = []
    for p in pneus_uso:
        rodado = float(p["km_atual"] or 0) - float(p["km_instalacao"] or 0)
        if rodado >= 7000:
            alertas.append({
                "numero_fogo": p["numero_fogo"], "placa": p["placa"],
                "posicao": p["posicao"], "km_rodado": rodado, "limite": 7000
            })
            
    return {
        "total_pneus": total, "em_estoque": estoque, "em_uso": em_uso,
        "descartados": descartados, "total_veiculos": veiculos,
        "valor_estoque": float(val_estoque), "alertas_rodizio": alertas
    }

def confirmar_recebimento(pneu_id):
    with _e().begin() as conn:
        conn.execute(text("UPDATE gp_pneus SET recebido=1, atualizado_em=datetime('now') WHERE id=:id"), {"id": pneu_id})
    return True

# ── RECICLAGEM ─────────────────────────────────────────────────────────────

def enviar_para_recicladora(pneu_id, data_envio, observacao=''):
    with _e().begin() as conn:
        pneu = conn.execute(text("SELECT * FROM gp_pneus WHERE id=:id"), {"id": pneu_id}).mappings().first()
        numero_lote = f"LOTE-{data_envio.replace('-', '')}"
        lote = conn.execute(text("SELECT id FROM gp_lotes_reciclagem WHERE numero_lote=:n"), {"n": numero_lote}).mappings().first()
        if not lote:
            res = conn.execute(text("INSERT INTO gp_lotes_reciclagem (numero_lote, data_envio, filial_id) VALUES (:n, :d, :f)"),
                             {"n": numero_lote, "d": data_envio, "f": pneu["filial_id"]})
            lote_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()
        else: lote_id = lote["id"]
        conn.execute(text("UPDATE gp_pneus SET status='reciclagem', lote_id=:lid WHERE id=:id"), {"lid": lote_id, "id": pneu_id})
    return True

def listar_lotes_reciclagem(filial_id=None):
    sql = "SELECT l.*, f.nome as filial_nome FROM gp_lotes_reciclagem l JOIN gp_filiais f ON l.filial_id=f.id"
    if filial_id: sql += " WHERE l.filial_id=:fid"
    with _e().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), {"fid": filial_id} if filial_id else {}).mappings().all()]

def atualizar_valor_lote_reciclagem(lote_id, valor_total):
    with _e().begin() as conn:
        conn.execute(text("UPDATE gp_lotes_reciclagem SET valor_total=:val, status='finalizado' WHERE id=:id"),
                     {"val": float(valor_total), "id": lote_id})
    return True

def obter_relatorio_financeiro_reciclagem(mes=None, filial_id=None):
    # Simplificado para local
    return []
