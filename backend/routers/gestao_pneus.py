"""
Gestão de Pneus — Endpoints REST.
Prefixo: /api/gestao-pneus
"""
import logging
import csv
import io
from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException, File, UploadFile, Response, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.auth import get_current_user, TokenData, require_admin, require_operador

try:
    from backend.db_gestao_pneus import (
        ensure_tables, VEHICLE_CONFIGS, listar_filiais, criar_filial, atualizar_filial, desativar_filial,
        listar_veiculos, criar_veiculo, atualizar_veiculo, obter_veiculo_com_pneus, desativar_veiculo,
        listar_pneus, criar_pneu, atualizar_pneu, obter_pneu, alocar_pneu, remover_pneu, transferir_pneu,
        mover_pneu_veiculo, listar_movimentacoes, obter_dashboard, confirmar_recebimento,
        enviar_para_recicladora, listar_lotes_reciclagem, atualizar_valor_lote_reciclagem,
        obter_relatorio_financeiro_reciclagem, importar_pneus_lote, criar_lote_reciclagem
    )
except ImportError:
    from db_gestao_pneus import (
        ensure_tables, VEHICLE_CONFIGS, listar_filiais, criar_filial, atualizar_filial, desativar_filial,
        listar_veiculos, criar_veiculo, atualizar_veiculo, obter_veiculo_com_pneus, desativar_veiculo,
        listar_pneus, criar_pneu, atualizar_pneu, obter_pneu, alocar_pneu, remover_pneu, transferir_pneu,
        mover_pneu_veiculo, listar_movimentacoes, obter_dashboard, confirmar_recebimento,
        enviar_para_recicladora, listar_lotes_reciclagem, atualizar_valor_lote_reciclagem,
        obter_relatorio_financeiro_reciclagem, importar_pneus_lote, criar_lote_reciclagem
    )
try:
    from backend.db_sqlserver import buscar_veiculo_por_placa, sincronizar_todos_do_sql
except ImportError:
    try:
        from db_sqlserver import buscar_veiculo_por_placa, sincronizar_todos_do_sql
    except ImportError:
        def buscar_veiculo_por_placa(placa): return None
        def sincronizar_todos_do_sql(limite=5000): return {"ok": False, "erro": "Modulo db_sqlserver nao encontrado."}
        logger.warning("Aviso: Modulo db_sqlserver nao encontrado. Busca e sincronizacao desativadas.")

logger = logging.getLogger(__name__)

router = APIRouter(tags=["gestao-pneus"])

@router.get("/ping")
def ping():
    return {"status": "online", "message": "pong"}

# ── Endpoints Públicos (sem auth) ────────────────────────────────────────────────
@router.get("/configs/veiculos")
def get_vehicle_configs():
    return VEHICLE_CONFIGS

# Garante que as tabelas existam ao importar o módulo
# try:
#     ensure_tables()
# except Exception as e:
#     logger.error(f"Falha ao criar tabelas Gestão Pneus: {e}")


# ── Pydantic Models ────────────────────────────────────────────────────────

class FilialIn(BaseModel):
    nome: str
    cidade: str = ""
    estado: str = ""

class VeiculoIn(BaseModel):
    placa: str
    frota: str = ""
    modelo: str = ""
    marca: str = ""
    tipo: str = "truck"
    filial_id: Optional[int] = None
    km_atual: Optional[float] = None

class PneuIn(BaseModel):
    numero_fogo: str
    marca: str
    modelo: str = ""
    medida: str
    dot: str = ""
    valor: float = 0
    vida: int = 1
    filial_id: int
    sulco_atual: float = 0
    nf: str = ""
    fornecedor: str = ""

class PneuUpdate(BaseModel):
    numero_fogo: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    medida: Optional[str] = None
    dot: Optional[str] = None
    valor: Optional[float] = None
    vida: Optional[int] = None
    status: Optional[str] = None
    filial_id: Optional[int] = None
    sulco_atual: Optional[float] = None
    nf: Optional[str] = None
    fornecedor: Optional[str] = None

class AlocarIn(BaseModel):
    pneu_id: int
    veiculo_id: int
    posicao: str
    km_instalacao: float = 0
    observacao: str = ""

class RemoverIn(BaseModel):
    pneu_id: int
    destino: str = "estoque"  # estoque | descarte | recapagem
    filial_destino_id: Optional[int] = None
    km_momento: float = 0
    observacao: str = ""

class TransferirIn(BaseModel):
    pneu_id: int
    filial_destino_id: int
    observacao: str = ""


# ── CONFIGS ────────────────────────────────────────────────────────────────

@router.get("/configs/veiculos")
def get_vehicle_configs():
    """Retorna configurações de eixos por tipo de veículo."""
    return VEHICLE_CONFIGS


# ── FILIAIS ────────────────────────────────────────────────────────────────

@router.get("/filiais")
def get_filiais(current_user: TokenData = Depends(get_current_user)):
    return listar_filiais()

@router.post("/filiais")
def post_filial(body: FilialIn, current_user: TokenData = Depends(require_admin)):
    try:
        return criar_filial(body.nome, body.cidade, body.estado)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/filiais/{filial_id}")
def put_filial(filial_id: int, body: FilialIn, current_user: TokenData = Depends(require_admin)):
    result = atualizar_filial(filial_id, body.nome, body.cidade, body.estado)
    if not result:
        raise HTTPException(status_code=404, detail="Filial não encontrada")
    return result

@router.delete("/filiais/{filial_id}")
def delete_filial(filial_id: int, current_user: TokenData = Depends(require_admin)):
    desativar_filial(filial_id)
    return {"ok": True}


# ── VEÍCULOS ───────────────────────────────────────────────────────────────

@router.get("/veiculos")
def get_veiculos(filial_id: Optional[int] = Query(None), current_user: TokenData = Depends(get_current_user)):
    return listar_veiculos(filial_id=filial_id)

@router.post("/veiculos")
def post_veiculo(body: VeiculoIn, current_user: TokenData = Depends(get_current_user)):
    try:
        return criar_veiculo(
            placa=body.placa, frota=body.frota, modelo=body.modelo,
            marca=body.marca, tipo=body.tipo, filial_id=body.filial_id,
            km_atual=body.km_atual or 0,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/veiculos/{veiculo_id}")
def get_veiculo_detail(veiculo_id: int, current_user: TokenData = Depends(get_current_user)):
    result = obter_veiculo_com_pneus(veiculo_id)
    if not result:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return result

@router.put("/veiculos/{veiculo_id}")
def put_veiculo(veiculo_id: int, body: VeiculoIn, current_user: TokenData = Depends(get_current_user)):
    update_data = dict(placa=body.placa, frota=body.frota, modelo=body.modelo,
                   marca=body.marca, tipo=body.tipo, filial_id=body.filial_id)
    if body.km_atual is not None:
        update_data["km_atual"] = body.km_atual
    result = atualizar_veiculo(veiculo_id, **update_data)
    if result is None or result is False:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return result or {"ok": True}

@router.delete("/veiculos/{veiculo_id}")
def delete_veiculo(veiculo_id: int, current_user: TokenData = Depends(require_admin)):
    try:
        desativar_veiculo(veiculo_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── PNEUS ──────────────────────────────────────────────────────────────────

@router.get("/pneus")
def get_pneus(
    filial_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    veiculo_id: Optional[int] = Query(None),
    current_user: TokenData = Depends(get_current_user),
):
    return listar_pneus(filial_id=filial_id, status=status, veiculo_id=veiculo_id)

@router.post("/pneus")
def post_pneu(body: PneuIn, current_user: TokenData = Depends(get_current_user)):
    try:
        return criar_pneu(
            numero_fogo=body.numero_fogo, marca=body.marca, modelo=body.modelo,
            medida=body.medida, dot=body.dot, valor=body.valor,
            vida=body.vida, filial_id=body.filial_id, sulco_atual=body.sulco_atual,
            nf=body.nf, fornecedor=body.fornecedor
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pneus/template")
def get_pneus_template(current_user: TokenData = Depends(get_current_user)):
    """Gera um CSV modelo para importação de pneus."""
    try:
        output = io.StringIO()
        # Adiciona BOM para o Excel identificar como UTF-8
        output.write('\ufeff')
        
        writer = csv.writer(output, delimiter=';')
        
        # 1. Header
        writer.writerow([
            "numero_fogo", "dot", "marca", "modelo", "medida", 
            "vida", "valor", "sulco_atual", "fornecedor", "nf", "filial"
        ])
        
        # 2. Exemplo
        writer.writerow([
            "EX001", "2024", "BRIDGESTONE", "R268", "295/80R22.5", 
            "1", "2500.00", "16.5", "FORNECEDOR X", "12345", "MATRIZ"
        ])
        
        # 3. Informações de apoio
        writer.writerow([])
        writer.writerow(["--- LISTA DE FILIAIS CADASTRADAS (Use exatamente o nome abaixo) ---"])
        try:
            f_list = listar_filiais()
            for f in f_list:
                writer.writerow([f["nome"]])
        except:
             writer.writerow(["Erro ao carregar filiais online"])

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=modelo_importacao_pneus.csv",
                "Content-Type": "text/csv; charset=utf-8-sig"
            }
        )
    except Exception as e:
        logger.error(f"Erro ao gerar template: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/pneus/importar")
async def post_importar_pneus(file: UploadFile = File(...), current_user: TokenData = Depends(get_current_user)):
    """Recebe um CSV e importa os pneus em massa."""
    try:
        content = await file.read()
        decoded = content.decode('utf-8-sig').splitlines()
        
        header_line = decoded[0]
        delimiter = ';' if ';' in header_line else ','
        
        reader = csv.DictReader(decoded, delimiter=delimiter)
        pneus_data = []
        for row in reader:
            pneus_data.append(row)
            
        return importar_pneus_lote(pneus_data)
    except Exception as e:
        logger.error(f"Erro na importação CSV: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao processar CSV: {str(e)}")

@router.get("/pneus/{pneu_id}")
def get_pneu_detail(pneu_id: int):
    result = obter_pneu(pneu_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pneu não encontrado")
    return result

@router.put("/pneus/{pneu_id}")
def put_pneu(pneu_id: int, body: PneuUpdate):
    result = atualizar_pneu(pneu_id, **body.dict(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="Pneu não encontrado")
    return result

@router.post("/confirmar-recebimento", tags=["operacoes"])
def post_confirmar_recebimento(body: dict):
    pneu_id = body.get("pneu_id")
    if not pneu_id:
        raise HTTPException(status_code=400, detail="pneu_id é obrigatório")
    confirmar_recebimento(pneu_id)
    return {"ok": True}


@router.post("/rodizio")
def post_rodizio(body: dict):
    mover_pneu_veiculo(
        veiculo_id=body["veiculo_id"],
        pos_origem=body["pos_origem"],
        pos_destino=body["pos_destino"],
        observacao=body.get("observacao", ""),
        km_momento=body.get("km_momento")
    )
    return {"ok": True}


# ── OPERAÇÕES ──────────────────────────────────────────────────────────────

@router.post("/alocar")
def post_alocar(body: AlocarIn, current_user: TokenData = Depends(require_operador)):
    try:
        return alocar_pneu(
            pneu_id=body.pneu_id, veiculo_id=body.veiculo_id,
            posicao=body.posicao, km_instalacao=body.km_instalacao,
            observacao=body.observacao,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/remover")
def post_remover(body: RemoverIn, current_user: TokenData = Depends(require_operador)):
    try:
        return remover_pneu(
            pneu_id=body.pneu_id, destino=body.destino,
            km_momento=body.km_momento, observacao=body.observacao,
filial_destino_id=body.filial_destino_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/transferir")
def post_transferir(body: TransferirIn, current_user: TokenData = Depends(require_operador)):
    try:
        return transferir_pneu(
            pneu_id=body.pneu_id, filial_destino_id=body.filial_destino_id,
            observacao=body.observacao,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── MOVIMENTAÇÕES ──────────────────────────────────────────────────────────

@router.get("/movimentacoes")
def get_movimentacoes(
    pneu_id: Optional[int] = Query(None),
    veiculo_id: Optional[int] = Query(None),
    filial_id: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None),
    limit: int = Query(100),
    current_user: TokenData = Depends(get_current_user),
):
    return listar_movimentacoes(
        pneu_id=pneu_id, veiculo_id=veiculo_id,
        filial_id=filial_id, tipo=tipo, limit=limit,
    )


# ── DASHBOARD ──────────────────────────────────────────────────────────────

@router.get("/dashboard")
def get_dashboard(current_user: TokenData = Depends(get_current_user)):
    try:
        return obter_dashboard()
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ── RECICLAGEM ─────────────────────────────────────────────────────────────

@router.post("/reciclagem/enviar", tags=["operacoes"])
def post_enviar_reciclagem(body: dict):
    try:
        return enviar_para_recicladora(
            pneu_id=body["pneu_id"],
            data_envio=body["data_envio"],
            observacao=body.get("observacao", "")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reciclagem/lotes")
def get_lotes_reciclagem(filial_id: Optional[int] = Query(None)):
    return listar_lotes_reciclagem(filial_id=filial_id)

@router.get("/reciclagem/aguardando")
def get_pneus_aguardando_lote(filial_id: Optional[int] = Query(None)):
    return listar_pneus_aguardando_lote(filial_id=filial_id)

@router.post("/reciclagem/atualizar-valor")
def post_atualizar_valor_lote(body: dict):
    try:
        return atualizar_valor_lote_reciclagem(lote_id=body["lote_id"], valor_total=body["valor_total"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reciclagem/criar-lote")
def post_criar_lote_reciclagem(body: dict, current_user: TokenData = Depends(get_current_user)):
    try:
        return criar_lote_reciclagem(pneu_ids=body["pneu_ids"], filial_id=body["filial_id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reciclagem/relatorio-financeiro")
def get_relatorio_financeiro_reciclagem(mes: Optional[str] = Query(None), filial_id: Optional[int] = Query(None)):
    return obter_relatorio_financeiro_reciclagem(mes=mes, filial_id=filial_id)




# ── BUSCA EXTERNA (SQL SERVER) ──────────────────────────────────────────────

@router.get("/busca-veiculo-sql/{placa}")
def get_busca_veiculo_sql(placa: str):
    """Busca dados de um veiculo pela placa em 3 fontes (prioridade): Supabase → SQL Server → Sistema."""
    try:
        placa_limpa = placa.replace("-", "").upper().strip()

        # 1. Tenta buscar na referência (Supabase ou SQL Server corporativo)
        result = buscar_veiculo_por_placa(placa_limpa)

        # 2. Fallback: veículos já cadastrados no sistema de pneus (gp_veiculos)
        if not result:
            veiculos_locais = listar_veiculos(apenas_ativos=False)
            v_existente = next(
                (v for v in veiculos_locais if v['placa'].replace("-", "").upper() == placa_limpa),
                None
            )
            if v_existente:
                result = {
                    "placa": v_existente['placa'],
                    "modelo": v_existente['modelo'],
                    "marca": v_existente['marca'],
                    "frota": v_existente['frota'],
                    "tipo": v_existente['tipo'],
                    "fonte": "sistema"
                }

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Veiculo nao encontrado. Verifique a placa ou preencha os dados manualmente."
            )

        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao buscar placa: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao consultar banco de veiculos")

# ── SINCRONIZAÇÃO SQL SERVER → SUPABASE ─────────────────────────────────────

@router.post("/sincronizar-veiculos-sql")
def post_sincronizar_veiculos(limite: int = 5000):
    """
    Sincroniza todos os veiculos do SQL Server corporativo para o Supabase.
    Execute apenas localmente (requer pymssql e acesso ao SQL Server).
    Apos a sincronizacao, o Vercel (producao) encontrara os veiculos via Supabase.
    """
    try:
        resultado = sincronizar_todos_do_sql(limite=limite)
        if not resultado.get("ok"):
            raise HTTPException(status_code=503, detail=resultado.get("erro", "Sincronizacao falhou."))
        return resultado
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro na sincronizacao: {e}")
        raise HTTPException(status_code=500, detail=str(e))

