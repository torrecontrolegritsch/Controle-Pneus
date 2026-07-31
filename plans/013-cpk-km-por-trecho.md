---
status: Pendente
prioridade: CRÍTICA
esforço: M
risco: médio
categoria: Produto — Fundação
dependências: nenhuma
---

# 013 — KM por Trecho + CPK Básico (Fundação)

## Por que isso importa

`km_total` no cadastro do pneu é um campo manual — subestimado ou zerado para a maioria
dos pneus em uso. Sem km acumulado calculado automaticamente por cada trecho rodado,
é impossível calcular CPK (custo por quilômetro), que é a métrica central para decidir:
qual pneu comprar, se vale recapar, qual veículo desgasta mais pneu.

Todo o restante do roadmap (aferição, OS, dashboard de CPK) depende desta base.

## Estado atual

```js
// gestaoPneus.js linha 143-145
export const alocarPneu = (data) => post(`${P}/alocar`, data)
export const removerPneu = (data) => post(`${P}/remover`, data)
export const rodizioPneu = (data) => post(`${P}/rodizio`, data)
```

O payload atual de `alocarPneu` não inclui hodômetro obrigatório.
O payload de `removerPneu` não captura km de saída.
O campo `km_total` em `pneus` existe mas não é calculado automaticamente.

## Mudanças necessárias

### A — Nova tabela `pneu_aplicacoes` (Supabase)

```sql
CREATE TABLE pneu_aplicacoes (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pneu_id       UUID NOT NULL REFERENCES pneus(id),
  veiculo_id    UUID NOT NULL REFERENCES veiculos(id),
  posicao       TEXT NOT NULL,             -- ex.: "1ESQ", "2TDIE"
  km_entrada    INTEGER NOT NULL,          -- hodômetro do veículo ao alocar
  km_saida      INTEGER,                   -- hodômetro ao remover (NULL = ainda aplicado)
  km_parcial    INTEGER GENERATED ALWAYS AS (km_saida - km_entrada) STORED,
  usuario_id    UUID REFERENCES auth.users(id),
  data_entrada  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  data_saida    TIMESTAMPTZ,
  motivo_saida  TEXT                       -- 'rodizio', 'remocao', 'sucata', 'recapagem'
);
```

### B — View calculada `pneus_km_acumulado`

```sql
CREATE VIEW pneus_km_acumulado AS
SELECT
  pneu_id,
  SUM(COALESCE(km_parcial, 0)) AS km_acumulado,
  COUNT(*) AS num_aplicacoes
FROM pneu_aplicacoes
GROUP BY pneu_id;
```

### C — Enriquecer `pneus` com campos de custo

```sql
ALTER TABLE pneus
  ADD COLUMN IF NOT EXISTS valor_aquisicao   NUMERIC(10,2),
  ADD COLUMN IF NOT EXISTS fornecedor        TEXT,
  ADD COLUMN IF NOT EXISTS dot               TEXT,        -- ex.: "2248" (semana/ano)
  ADD COLUMN IF NOT EXISTS sulco_original_mm NUMERIC(4,1) DEFAULT 16.0,
  ADD COLUMN IF NOT EXISTS sulco_minimo_mm   NUMERIC(4,1) DEFAULT 3.0,
  ADD COLUMN IF NOT EXISTS pressao_rec_psi   INTEGER,
  ADD COLUMN IF NOT EXISTS vidas_maximas     INTEGER DEFAULT 3;
```

### D — Backend: hodômetro obrigatório em alocar/remover

Endpoint `POST /api/gestao-pneus/alocar` — adicionar ao body:
```json
{ "pneu_id": "...", "veiculo_id": "...", "posicao": "1ESQ", "km_hodometro": 125430 }
```
Validação: `km_hodometro >= veiculos.km_atual` (não aceitar valor menor sem justificativa).
Ao alocar: inserir em `pneu_aplicacoes(km_entrada = km_hodometro)` e atualizar `veiculos.km_atual`.

Endpoint `POST /api/gestao-pneus/remover` — adicionar ao body:
```json
{ "pneu_id": "...", "km_hodometro": 128000, "motivo": "rodizio" }
```
Ao remover: fechar `pneu_aplicacoes` (km_saida = km_hodometro, data_saida = now()).
Atualizar `pneus.km_total` com soma de km_acumulado de todas as vidas.

### E — Cálculo de CPK exposto na API

```python
# Endpoint GET /api/gestao-pneus/pneus/{id}/cpk
def get_cpk(pneu_id):
    pneu = fetch_pneu(pneu_id)
    km = fetch_km_acumulado(pneu_id)
    custo_total = (pneu.valor_aquisicao or 0) + fetch_custos_recapagem(pneu_id)
    if km > 0:
        cpk = custo_total / km  # R$/km
    else:
        cpk = None
    return { "km_acumulado": km, "custo_total": custo_total, "cpk": cpk }
```

### F — Frontend: campo hodômetro no modal de alocação/remoção

No modal de confirmar alocação (PneusGestao.vue):
```html
<div class="form-group">
  <label>Hodômetro atual do veículo (km) *</label>
  <input type="number" v-model="hodometroInput" placeholder="ex.: 125.430"
         :min="veiculoDetail.km_atual" required />
  <small v-if="hodometroInput < veiculoDetail.km_atual" class="field-warn">
    Valor menor que o último registrado ({{ veiculoDetail.km_atual.toLocaleString('pt-BR') }} km)
  </small>
</div>
```

## Escopo

**Em escopo:**
- Tabela `pneu_aplicacoes` e view `pneus_km_acumulado` no Supabase
- Campos de enriquecimento do pneu (valor, DOT, sulco original/mínimo, pressão, vidas máximas)
- Hodômetro obrigatório nos endpoints alocar, remover e rodizio
- Endpoint `/pneus/{id}/cpk`
- Campo hodômetro no modal de alocação do frontend

**Fora de escopo:**
- Dashboard de CPK comparativo (Plano 021)
- Custo de recapagem no CPK (depende Plano 018)
- Validação de hodômetro via telemetria (Plano 023)

## Critérios de conclusão

- [ ] Tabela `pneu_aplicacoes` criada no Supabase com RLS adequada
- [ ] `km_parcial` calculado corretamente em ao menos 5 alocações de teste
- [ ] Modal de alocação tem campo hodômetro obrigatório e valida valor mínimo
- [ ] Endpoint `/pneus/{id}/cpk` retorna CPK > 0 para pneus com km_acumulado > 0
- [ ] Build sem erros

## STOP se

- O banco não permite `GENERATED ALWAYS AS` — substituir por trigger ou calcular no backend
- O hodômetro do veículo no banco está zerado para mais de 50% da frota — checar antes de
  tornar obrigatório, e implementar migração com valor padrão ou flag `km_nao_informado`
