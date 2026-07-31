---
status: Pendente
prioridade: CRÍTICA
esforço: M
risco: médio
categoria: Produto — Fundação
dependências: nenhuma (pode rodar junto com 013)
---

# 015 — Máquina de Estados do Pneu com Validação

## Por que isso importa

O campo `status` em `pneus` hoje é uma string livre. Nada impede transições inválidas:
alocar um pneu "em recapagem", sucatar um pneu já descartado, ou mover um "em trânsito"
sem confirmação de recebimento. Dados de status incorretos corrompem o histórico e o CPK.

Com a máquina de estados:
- Cada transição é validada no backend (não no frontend)
- Toda mudança de estado gera log auditável (quem, quando, de onde, para onde, por quê)
- A UI mostra apenas as ações válidas para o estado atual do pneu

## Estados e transições válidas

```
ESTOQUE      → APLICADO (alocar em posição)
ESTOQUE      → EM_TRANSITO (transferência entre filiais)
ESTOQUE      → EM_RECAPAGEM (envio para recapadora)
ESTOQUE      → DESCARTADO (sucata direta do estoque)
APLICADO     → ESTOQUE (remoção normal)
APLICADO     → EM_ANALISE (retirada para análise de dano/garantia)
APLICADO     → DESCARTADO (sucata direto do veículo)
EM_TRANSITO  → ESTOQUE (confirmação de recebimento)
EM_ANALISE   → ESTOQUE (aprovado, volta ao estoque)
EM_ANALISE   → EM_RECAPAGEM (aprovado para recapar)
EM_ANALISE   → DESCARTADO (reprovado)
EM_RECAPAGEM → ESTOQUE (retornou com nova vida)
EM_RECAPAGEM → DESCARTADO (recusado pela recapadora)
```

`DESCARTADO` é estado terminal — sem transições de saída.

## Estado atual

```python
# Sem validação: qualquer valor de status é aceito
# Status observados nos dados: 'estoque', 'em_uso', 'descartado', 'em_transito'
# Não existe tabela de log de mudanças de status
```

## Mudanças necessárias

### A — Enum de status no banco

```sql
CREATE TYPE status_pneu AS ENUM (
  'ESTOQUE', 'APLICADO', 'EM_TRANSITO', 'EM_ANALISE', 'EM_RECAPAGEM', 'DESCARTADO'
);

-- Migração dos valores existentes
UPDATE pneus SET status = 'APLICADO'    WHERE status IN ('em_uso', 'aplicado');
UPDATE pneus SET status = 'ESTOQUE'     WHERE status IN ('estoque', 'disponivel');
UPDATE pneus SET status = 'EM_TRANSITO' WHERE status = 'em_transito';
UPDATE pneus SET status = 'DESCARTADO'  WHERE status IN ('descartado', 'sucata');
UPDATE pneus SET status = 'ESTOQUE'     WHERE status IS NULL;

ALTER TABLE pneus ALTER COLUMN status TYPE status_pneu USING status::status_pneu;
ALTER TABLE pneus ALTER COLUMN status SET DEFAULT 'ESTOQUE';
```

### B — Nova tabela `pneu_status_log`

```sql
CREATE TABLE pneu_status_log (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pneu_id          UUID NOT NULL REFERENCES pneus(id),
  status_anterior  status_pneu,
  status_novo      status_pneu NOT NULL,
  usuario_id       UUID REFERENCES auth.users(id),
  data_hora        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  motivo           TEXT,                   -- ex.: "descarte por corte lateral"
  km_veiculo       INTEGER,
  veiculo_id       UUID REFERENCES veiculos(id)
);
```

### C — Validador de transições no backend

```python
TRANSICOES_VALIDAS = {
    "ESTOQUE":      {"APLICADO", "EM_TRANSITO", "EM_RECAPAGEM", "DESCARTADO"},
    "APLICADO":     {"ESTOQUE", "EM_ANALISE", "DESCARTADO"},
    "EM_TRANSITO":  {"ESTOQUE"},
    "EM_ANALISE":   {"ESTOQUE", "EM_RECAPAGEM", "DESCARTADO"},
    "EM_RECAPAGEM": {"ESTOQUE", "DESCARTADO"},
    "DESCARTADO":   set(),  # terminal
}

def validar_transicao(status_atual: str, status_novo: str):
    permitidos = TRANSICOES_VALIDAS.get(status_atual, set())
    if status_novo not in permitidos:
        raise HTTPException(
            status_code=422,
            detail=f"Transição inválida: {status_atual} → {status_novo}. "
                   f"Permitidas: {', '.join(permitidos) or 'nenhuma'}"
        )

def mudar_status(pneu_id, status_novo, usuario_id, motivo=None, km_veiculo=None, veiculo_id=None):
    pneu = get_pneu(pneu_id)
    validar_transicao(pneu.status, status_novo)
    
    # Log antes de mudar
    insert_status_log(pneu_id, pneu.status, status_novo, usuario_id, motivo, km_veiculo, veiculo_id)
    
    # Mudar status
    update_pneu_status(pneu_id, status_novo)
    
    return pneu_id
```

Todos os endpoints existentes (`alocar`, `remover`, `transferir`, `confirmar-recebimento`)
devem passar por `mudar_status()` em vez de fazer `UPDATE pneus SET status = '...'` direto.

### D — Endpoint GET do histórico de status

```
GET /api/gestao-pneus/pneus/{id}/historico-status
Response: lista cronológica de { status_anterior, status_novo, usuario_nome, data_hora, motivo }
```

### E — Frontend: linha do tempo do pneu

No modal de detalhe do pneu (ou nova aba "Histórico" no diagrama):

```html
<div class="timeline">
  <div v-for="log in historicoStatus" :key="log.id" class="tl-item">
    <div class="tl-dot" :class="'tl-' + log.status_novo.toLowerCase()"></div>
    <div class="tl-body">
      <span class="tl-status">{{ log.status_novo }}</span>
      <span class="tl-meta">{{ log.usuario_nome }} · {{ fmtDate(log.data_hora) }}</span>
      <span v-if="log.motivo" class="tl-motivo">{{ log.motivo }}</span>
    </div>
  </div>
</div>
```

### F — Ações visíveis por estado

No diagrama e na tela de estoque, mostrar apenas ações válidas para o estado atual:
```js
const acoesDisponiveis = computed(() => {
  const mapa = {
    ESTOQUE:      ['alocar', 'transferir', 'sucatar'],
    APLICADO:     ['remover', 'analise'],
    EM_TRANSITO:  ['confirmar_recebimento'],
    EM_ANALISE:   ['aprovar', 'enviar_recapagem', 'sucatar'],
    EM_RECAPAGEM: ['confirmar_retorno', 'sucatar'],
    DESCARTADO:   [],
  }
  return mapa[pneuSelecionado.value?.status] ?? []
})
```

## Escopo

**Em escopo:**
- Enum `status_pneu` e migração de dados existentes
- Tabela `pneu_status_log`
- Validador de transições chamado em todos os endpoints de operação
- Endpoint GET de histórico de status
- Linha do tempo no frontend (modal simples, não uma tela nova)
- Ações visíveis filtradas por estado no diagrama

**Fora de escopo:**
- Motivo de descarte catalogado (Plano 017 — detalhamento da causa raiz)
- Fluxo de recapagem completo (Plano 018)
- Alertas automáticos por estado (Plano 022)

## Critérios de conclusão

- [ ] Enum `status_pneu` criado e dados migrados sem perda
- [ ] Tentativa de transição inválida retorna HTTP 422 com mensagem clara
- [ ] `pneu_status_log` tem ao menos 1 registro para cada operação de mudança de status
- [ ] Endpoint histórico-status retorna lista ordenada por data_hora DESC
- [ ] Linha do tempo visível no frontend ao clicar num pneu
- [ ] Build sem erros

## STOP se

- Mais de 5% dos pneus têm status que não mapeia para o enum — analisar os valores
  distintos com `SELECT status, COUNT(*) FROM pneus GROUP BY status` antes de migrar
- A migração falhar por constraint — rodar com `ALTER TABLE ... USING status::text::status_pneu`
  e verificar os valores que não convertem
