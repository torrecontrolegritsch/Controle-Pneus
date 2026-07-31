---
status: Pendente
prioridade: ALTA
esforço: S
risco: baixo
categoria: Produto — Operação
dependências: 015 (máquina de estados — DESCARTADO como estado formal)
---

# 017 — Causa Raiz de Descarte Catalogada

## Por que isso importa

Frotas médias perdem 15–25% do orçamento de pneus em descartes antecipados.
Sem saber POR QUÊ o pneu foi descartado, a empresa não tem como atacar o problema:
- Muitos descartes por "subcalibragem" → problema de processo operacional
- Muitos por "corte lateral" → problema de rota ou treinamento do motorista
- Muitos por "desgaste irregular" → problema de alinhamento não feito

Dois trimestres de dados já revelam o padrão dominante. Custo: S.

## Estado atual

Ao arrastar pneu para zona "Sucata" no diagrama, o frontend chama:
```js
// PneusGestao.vue
handleDropOnRemoval('sucata')
// → removerPneu({ pneu_id, veiculo_id, posicao, destino: 'sucata' })
```

Não há campo de motivo. O pneu muda de status sem registro de causa.

## Mudanças necessárias

### A — Enum de causa raiz no banco

```sql
CREATE TYPE causa_descarte AS ENUM (
  'DESGASTE_NATURAL',
  'DESGASTE_IRREGULAR',
  'CORTE_AVARIA',
  'BOLHA_SEPARACAO',
  'DEFEITO_FABRICACAO',
  'SINISTRO',
  'SUBCALIBRAGEM',
  'ENVELHECIMENTO',
  'RECAPE_RECUSADO',
  'OUTROS'
);

ALTER TABLE pneus
  ADD COLUMN IF NOT EXISTS causa_descarte  causa_descarte,
  ADD COLUMN IF NOT EXISTS descarte_obs    TEXT;
```

### B — Modal de confirmação de descarte

Antes de concluir o drop na zona Sucata, abrir modal obrigatório:

```html
<div class="modal-overlay" v-if="showDescarteModal">
  <div class="modal-box">
    <h3>Confirmar Descarte</h3>
    <p class="modal-desc">
      Pneu <strong>{{ descartePneu?.numero_fogo }}</strong>
      será marcado como DESCARTADO. Esta ação não pode ser desfeita.
    </p>

    <div class="form-group">
      <label>Causa do Descarte *</label>
      <select v-model="descarteMotivo" required>
        <option value="">Selecione...</option>
        <option value="DESGASTE_NATURAL">Desgaste natural (vida útil esgotada)</option>
        <option value="DESGASTE_IRREGULAR">Desgaste irregular (problema operacional)</option>
        <option value="CORTE_AVARIA">Corte / Avaria mecânica</option>
        <option value="BOLHA_SEPARACAO">Bolha / Separação de lona</option>
        <option value="DEFEITO_FABRICACAO">Defeito de fabricação</option>
        <option value="SINISTRO">Sinistro / Acidente</option>
        <option value="SUBCALIBRAGEM">Subcalibragem / Pressão incorreta</option>
        <option value="ENVELHECIMENTO">Envelhecimento (DOT vencido)</option>
        <option value="RECAPE_RECUSADO">Recapagem recusada pela borracharia</option>
        <option value="OUTROS">Outros</option>
      </select>
    </div>

    <div class="form-group">
      <label>Observações (opcional)</label>
      <textarea v-model="descarteObs" rows="2" placeholder="Detalhes adicionais..." />
    </div>

    <div class="modal-actions">
      <button @click="showDescarteModal = false" class="btn-secondary">Cancelar</button>
      <button @click="confirmarDescarte" :disabled="!descarteMotivo" class="btn-primary btn-danger">
        Confirmar Descarte
      </button>
    </div>
  </div>
</div>
```

### C — Relatório de descartes por causa (nova aba no Dashboard)

```html
<!-- Tabela de descartes por causa nos últimos 90 dias -->
<div class="card-section">
  <h3>Descartes por Causa (90 dias)</h3>
  <div v-for="item in relatorioDescarte" :key="item.causa" class="causa-row">
    <span class="causa-label">{{ item.causa_label }}</span>
    <div class="causa-bar">
      <div class="causa-fill" :style="{ width: item.pct + '%' }"></div>
    </div>
    <span class="causa-count">{{ item.count }} pneus</span>
  </div>
</div>
```

Endpoint:
```
GET /api/gestao-pneus/relatorios/descartes-por-causa?dias=90&filial_id=
Response: [{ causa, causa_label, count, pct }]
```

## Escopo

**Em escopo:**
- Enum `causa_descarte` e campos na tabela `pneus`
- Modal obrigatório ao sucatar pneu (impede descarte sem causa)
- Endpoint de relatório de descartes por causa
- Visualização de barras horizontais no Dashboard (simples, sem gráfico de biblioteca)

**Fora de escopo:**
- Abertura de garantia ao selecionar "DEFEITO_FABRICACAO" (Fase 6.3 do roadmap)
- Descarte de pneus em estoque (sem veículo) — mesmo modal, `km_veiculo = NULL`

## Critérios de conclusão

- [ ] Enum `causa_descarte` criado no Supabase
- [ ] Modal aparece ao arrastar para zona Sucata (e não ao arrastar para Estoque)
- [ ] Botão "Confirmar Descarte" permanece desabilitado até causa ser selecionada
- [ ] Campo `causa_descarte` preenchido no banco após confirmar
- [ ] Endpoint de relatório retorna dados agrupados por causa
- [ ] Build sem erros

## STOP se

- O Plano 015 ainda não foi executado e `status` não é enum — o endpoint de descarte
  pode aceitar qualquer valor de status; executar 015 antes para garantir que "DESCARTADO"
  seja tratado como estado terminal
