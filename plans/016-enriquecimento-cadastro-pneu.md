---
status: Pendente
prioridade: ALTA
esforço: S
risco: baixo
categoria: Produto — Fundação
dependências: nenhuma (pode rodar junto com 013)
---

# 016 — Enriquecimento do Cadastro do Pneu

## Por que isso importa

O cadastro atual de pneus tem os campos mínimos para rastrear onde o pneu está,
mas não tem os dados necessários para calcular CPK, detectar subcalibragem, ou comparar
marcas/modelos. Campos como DOT, pressão recomendada e sulco original são coletados
na compra e não mudam — são os mais baratos de adicionar e os que mais desbloqueiam.

## Campos atuais (inferidos do frontend/API)

`numero_fogo`, `marca`, `medida`, `sulco_atual`, `km_total`, `vida`, `status`,
`nf`, `filial_id`, `recebido`, `placa_atual` (via join)

## Campos a adicionar

```sql
ALTER TABLE pneus
  ADD COLUMN IF NOT EXISTS dot               TEXT,
    -- formato "SSSA AA" = semana (3 dig) + ano (2 dig), ex.: "2248" = semana 22 de 2048
    -- ou o número de série completo do fabricante

  ADD COLUMN IF NOT EXISTS modelo            TEXT,
    -- modelo/linha do fabricante, ex.: "XZE2+" (Michelin), "G580" (Goodyear)

  ADD COLUMN IF NOT EXISTS banda             TEXT,
    -- código da banda de recapagem quando tipo = 'recapado'

  ADD COLUMN IF NOT EXISTS tipo_pneu         TEXT DEFAULT 'novo',
    -- 'novo' | 'recapado' | 'remoldado'

  ADD COLUMN IF NOT EXISTS vidas_maximas     INTEGER DEFAULT 3,
    -- número máximo de vidas previstas para esse modelo

  ADD COLUMN IF NOT EXISTS sulco_original_mm NUMERIC(4,1) DEFAULT 16.0,
    -- sulco quando novo (necessário para calcular % de desgaste)

  ADD COLUMN IF NOT EXISTS sulco_minimo_mm   NUMERIC(4,1) DEFAULT 3.0,
    -- sulco de descarte (default DENATRAN, configurável por filial)

  ADD COLUMN IF NOT EXISTS pressao_rec_psi   INTEGER,
    -- pressão recomendada em PSI para este pneu neste veículo

  ADD COLUMN IF NOT EXISTS pressao_tol_pct   INTEGER DEFAULT 10,
    -- tolerância aceita em % acima/abaixo da pressão recomendada

  ADD COLUMN IF NOT EXISTS valor_aquisicao   NUMERIC(10,2),
    -- custo de compra, base para CPK

  ADD COLUMN IF NOT EXISTS fornecedor        TEXT,
    -- nome do fornecedor / distribuidora

  ADD COLUMN IF NOT EXISTS data_vencimento_garantia DATE;
    -- data de validade da garantia do fabricante
```

## Frontend: formulário de pneu (modal de cadastro/edição)

Adicionar ao formulário existente de criação/edição de pneu em PneusGestao.vue:

```html
<!-- Nova seção: Especificações técnicas -->
<div class="form-section-title">Especificações Técnicas</div>
<div class="form-row">
  <div class="form-group">
    <label>Modelo</label>
    <input v-model="formPneu.modelo" placeholder="ex.: XZE2+, G580" />
  </div>
  <div class="form-group">
    <label>DOT / Série</label>
    <input v-model="formPneu.dot" placeholder="ex.: 2248" maxlength="20" />
  </div>
</div>
<div class="form-row">
  <div class="form-group">
    <label>Tipo</label>
    <select v-model="formPneu.tipo_pneu">
      <option value="novo">Novo</option>
      <option value="recapado">Recapado</option>
      <option value="remoldado">Remoldado</option>
    </select>
  </div>
  <div class="form-group" v-if="formPneu.tipo_pneu === 'recapado'">
    <label>Banda de Recapagem</label>
    <input v-model="formPneu.banda" placeholder="ex.: Regresso II" />
  </div>
</div>
<div class="form-row">
  <div class="form-group">
    <label>Sulco Original (mm)</label>
    <input type="number" v-model.number="formPneu.sulco_original_mm" step="0.1" min="0" />
  </div>
  <div class="form-group">
    <label>Sulco Mínimo de Descarte (mm)</label>
    <input type="number" v-model.number="formPneu.sulco_minimo_mm" step="0.1" min="0" />
  </div>
  <div class="form-group">
    <label>Pressão Rec. (PSI)</label>
    <input type="number" v-model.number="formPneu.pressao_rec_psi" />
  </div>
</div>

<!-- Nova seção: Financeiro -->
<div class="form-section-title">Dados Financeiros</div>
<div class="form-row">
  <div class="form-group">
    <label>Valor de Aquisição (R$)</label>
    <input type="number" v-model.number="formPneu.valor_aquisicao" step="0.01" min="0" />
  </div>
  <div class="form-group">
    <label>Fornecedor</label>
    <input v-model="formPneu.fornecedor" placeholder="Distribuidora..." />
  </div>
</div>
```

## Template de importação CSV

Atualizar o template de importação para incluir os novos campos opcionais:
`numero_fogo,marca,medida,modelo,dot,tipo_pneu,banda,sulco_original_mm,sulco_minimo_mm,pressao_rec_psi,valor_aquisicao,fornecedor,nf,filial_nome`

Os campos novos são opcionais na importação — `NOT NULL` só para `numero_fogo`, `marca`, `medida`.

## Escopo

**Em escopo:**
- Colunas SQL listadas acima com `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`
- Formulário de cadastro/edição com as novas seções
- Template de importação CSV atualizado

**Fora de escopo:**
- Configuração de sulco mínimo por filial (refinamento futuro)
- Indexação de sulco/pressão por marca (Plano 021)

## Critérios de conclusão

- [ ] `ALTER TABLE` executado sem erro; dados existentes preservados
- [ ] Formulário de cadastro renderiza os novos campos sem quebrar layout
- [ ] Cadastro de pneu com `valor_aquisicao` e `sulco_original_mm` persiste via API
- [ ] Template CSV baixado inclui cabeçalhos novos
- [ ] Build sem erros

## STOP se

- A API de criação de pneu usa schema Pydantic fixo — adicionar os campos no schema antes
  de migrar o banco, senão os dados enviados serão ignorados silenciosamente
