---
status: Pendente
prioridade: CRÍTICA
esforço: M
risco: baixo
categoria: Produto — Operação
dependências: 013 (km_acumulado para calcular desgaste/km)
---

# 014 — Aferição de Sulco (4 pontos) e Pressão

## Por que isso importa

O sistema registra `sulco_atual` como campo único atualizado manualmente — sem histórico,
sem 4 pontos de medição, sem pressão, sem data da última aferição. Isso impede:
- Detectar desgaste irregular (sinal de desalinhamento, subcalibragem, problema de suspensão)
- Projetar quando o pneu vai atingir o sulco mínimo
- Identificar pneus com risco antes que causem acidente ou descarte antecipado

Os líderes do mercado (Prolog, PneuFit) têm esta como feature central.

## Estado atual

Campo em `pneus`:
```
sulco_atual: NUMERIC — atualizado na remoção/sucata, sem histórico
```

Não existe tabela de aferições. Sem coleta de pressão. Sem 4 pontos.

## Mudanças necessárias

### A — Nova tabela `aferacoes` (Supabase)

```sql
CREATE TABLE aferacoes (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pneu_id          UUID NOT NULL REFERENCES pneus(id),
  veiculo_id       UUID REFERENCES veiculos(id),
  posicao          TEXT,                   -- posição no veículo no momento da aferição
  sulco_externo    NUMERIC(4,1) NOT NULL,  -- mm
  sulco_cent_ext   NUMERIC(4,1) NOT NULL,
  sulco_cent_int   NUMERIC(4,1) NOT NULL,
  sulco_interno    NUMERIC(4,1) NOT NULL,
  pressao_psi      INTEGER,
  hodometro_km     INTEGER,
  km_acumulado_pneu INTEGER,              -- snapshot do km do pneu no momento
  usuario_id       UUID REFERENCES auth.users(id),
  data_hora        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  observacoes      TEXT,
  foto_url         TEXT,

  -- Computed (atualizados por trigger ou backend)
  sulco_medio      NUMERIC(4,1) GENERATED ALWAYS AS (
    (sulco_externo + sulco_cent_ext + sulco_cent_int + sulco_interno) / 4
  ) STORED,
  sulco_minimo     NUMERIC(4,1) GENERATED ALWAYS AS (
    LEAST(sulco_externo, sulco_cent_ext, sulco_cent_int, sulco_interno)
  ) STORED,
  diferenca_ombros NUMERIC(4,1) GENERATED ALWAYS AS (
    ABS(sulco_externo - sulco_interno)
  ) STORED,
  diferenca_centro NUMERIC(4,1) GENERATED ALWAYS AS (
    ABS((sulco_cent_ext + sulco_cent_int)/2 - (sulco_externo + sulco_interno)/2)
  ) STORED
);
```

### B — Classificação de condição (backend/view)

```python
def classificar_condicao(sulco_minimo, sulco_minimo_pneu, pressao, pressao_rec, tolerancia_pct):
    # Sulco
    margem_atencao = sulco_minimo_pneu + 2.0  # 2mm acima do mínimo = atenção
    if sulco_minimo <= sulco_minimo_pneu:
        condicao_sulco = "CRITICO"
    elif sulco_minimo <= margem_atencao:
        condicao_sulco = "ATENCAO"
    else:
        condicao_sulco = "CONFORME"
    
    # Pressão
    if pressao and pressao_rec:
        delta = abs(pressao - pressao_rec) / pressao_rec * 100
        if delta > tolerancia_pct:
            condicao_pressao = "CRITICO" if delta > tolerancia_pct * 1.5 else "ATENCAO"
        else:
            condicao_pressao = "CONFORME"
    else:
        condicao_pressao = None
    
    return max([condicao_sulco, condicao_pressao or "CONFORME"],
               key=lambda c: ["CONFORME","ATENCAO","CRITICO"].index(c))
```

### C — Detecção de padrão de desgaste

```python
def detectar_padrao_desgaste(sulco_ext, sulco_ce, sulco_ci, sulco_int):
    """Retorna causa provável baseada nos 4 pontos."""
    centro = (sulco_ce + sulco_ci) / 2
    ombros = (sulco_ext + sulco_int) / 2
    delta_ombros = abs(sulco_ext - sulco_int)
    
    if ombros < centro - 2:  # ombros muito mais gastos
        return "SUBCALIBRAGEM", "Pressão abaixo do recomendado — desgaste nos dois ombros"
    if centro < ombros - 2:  # centro muito mais gasto
        return "SOBRECALIBRAGEM", "Pressão acima do recomendado — desgaste no centro"
    if delta_ombros > 3:     # um ombro muito mais gasto que o outro
        return "DESALINHAMENTO", "Desgaste em um ombro — verificar alinhamento/cambagem"
    
    return None, None
```

### D — Endpoint backend

```
POST /api/gestao-pneus/aferacoes
Body: { pneu_id, veiculo_id, posicao, sulco_externo, sulco_cent_ext, sulco_cent_int,
        sulco_interno, pressao_psi, hodometro_km, observacoes }
Response: { id, condicao, padrao_desgaste, descricao_padrao, sulco_medio, sulco_minimo,
            desgaste_mm_por_1000km (se houver aferição anterior com km), vida_restante_km }

GET /api/gestao-pneus/pneus/{id}/aferacoes
Response: lista cronológica de aferições do pneu
```

### E — Frontend: Modal de aferição

Acessível via clique no pneu no diagrama (PneusGestao.vue, aba Alocações):

```html
<!-- Modal de aferição — disparado ao clicar em pneu ocupado no diagrama -->
<div class="modal-overlay" v-if="showAferacaoModal">
  <div class="modal-box">
    <h3>Aferição — Pneu {{ aferacaoPneu?.numero_fogo }}</h3>
    
    <div class="sulco-grid">
      <!-- 4 inputs de sulco dispostos como o perfil do pneu -->
      <div class="sulco-diagram">
        <input v-model.number="af.sulco_externo"  class="sulco-inp" placeholder="Ext" />
        <input v-model.number="af.sulco_cent_ext" class="sulco-inp" placeholder="C.Ext" />
        <input v-model.number="af.sulco_cent_int" class="sulco-inp" placeholder="C.Int" />
        <input v-model.number="af.sulco_interno"  class="sulco-inp" placeholder="Int" />
      </div>
      <div class="pneu-perfil-visual"><!-- SVG ilustrativo do perfil --></div>
    </div>
    
    <div class="form-row">
      <div class="form-group">
        <label>Pressão (PSI)</label>
        <input type="number" v-model.number="af.pressao_psi" placeholder="ex.: 120" />
      </div>
      <div class="form-group">
        <label>Hodômetro (km)</label>
        <input type="number" v-model.number="af.hodometro_km" />
      </div>
    </div>
    
    <!-- Resultado em tempo real -->
    <div v-if="aferacaoResultPreview" class="aferacao-resultado"
         :class="'resultado-' + aferacaoResultPreview.condicao.toLowerCase()">
      <strong>{{ aferacaoResultPreview.condicao }}</strong>
      <span v-if="aferacaoResultPreview.padrao_desgaste">
        · {{ aferacaoResultPreview.descricao_padrao }}
      </span>
    </div>
    
    <div class="modal-actions">
      <button @click="showAferacaoModal = false" class="btn-secondary">Cancelar</button>
      <button @click="salvarAferacao" class="btn-primary">Registrar Aferição</button>
    </div>
  </div>
</div>
```

O `aferacaoResultPreview` é um `computed` que classifica os valores localmente antes do save.

### F — Atualizar `sulco_atual` do pneu após aferição

Ao salvar aferição, o backend deve atualizar `pneus.sulco_atual = sulco_minimo` da nova aferição,
mantendo o campo existente compatível com a tela de estoque.

## Escopo

**Em escopo:**
- Tabela `aferacoes` no Supabase
- Endpoints `POST` e `GET` de aferições
- Modal de aferição no diagrama do veículo (aba Alocações)
- Classificação de condição e detecção de padrão de desgaste no backend
- Atualização de `sulco_atual` após cada aferição

**Fora de escopo:**
- Fluxo de aferição em massa (Fase 3.4 do roadmap — tela mobile sequencial)
- Cronograma de inspeção / alertas de atraso (Plano 019)
- Geração automática de OS (Plano 020)
- Foto do pneu (implementar sem o campo foto por ora; `foto_url` fica NULL)

## Critérios de conclusão

- [ ] Tabela `aferacoes` criada no Supabase
- [ ] `sulco_medio` e `sulco_minimo` computed corretamente para ao menos 10 aferições
- [ ] Modal de aferição abre ao clicar em pneu no diagrama e salva via API
- [ ] Pneu com sulco_minimo <= sulco_minimo_pneu recebe condicao = "CRITICO"
- [ ] `sulco_atual` do pneu atualizado após aferição (visível na tela de estoque)
- [ ] Build sem erros

## STOP se

- A tabela `pneus` não tem `sulco_minimo_mm` (depende Plano 013 adicionar esse campo)
- A API de aferição retornar 401 sem o header Authorization — verificar RLS do Supabase
