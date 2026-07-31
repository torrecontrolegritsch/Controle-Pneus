# 007 — Endpoint /configs/veiculos Sem Autenticação

**Categoria:** Segurança  
**Prioridade:** BAIXA | **Esforço:** S | **Risco:** Baixo | **Confiança:** Alta

## Por que importa

`backend/routers/gestao_pneus.py:130-133`:
```python
@router.get("/configs/veiculos")
def get_vehicle_configs():
    """Retorna configurações de eixos por tipo de veículo."""
    return VEHICLE_CONFIGS
```

Sem `Depends(get_current_user)`. Expõe publicamente as configurações de eixos/posições dos veículos. Não é catastrófico (não são credenciais), mas é informação desnecessária para quem não está autenticado.

## Passos

Em `backend/routers/gestao_pneus.py`:

```python
# ANTES:
@router.get("/configs/veiculos")
def get_vehicle_configs():
    return VEHICLE_CONFIGS

# DEPOIS:
@router.get("/configs/veiculos")
def get_vehicle_configs(current_user: TokenData = Depends(get_current_user)):
    return VEHICLE_CONFIGS
```

### Commit

```
fix: adiciona auth em /configs/veiculos
```

## Critérios de Conclusão

- [ ] `GET /api/gestao-pneus/configs/veiculos` sem token retorna 401
- [ ] Com token válido continua retornando os dados normalmente
- [ ] Frontend (que chama esse endpoint) ainda funciona

## Fora do Escopo

- Cachear a resposta no frontend (ela nunca muda)
