<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2>Lotes de Reciclagem</h2>
        <p class="sec-subtitle">Acompanhamento de pneus enviados para descarte/compra</p>
      </div>
    </div>

    <!-- Pneus aguardando lote — agrupados por medida -->
    <div v-if="pneusAguardando.length > 0" class="aguardando-lote-box">
      <div class="box-header">
        <div class="title-group">
          <h3>Pneus em Espera ({{ pneusAguardando.length }})</h3>
          <p>Agrupados por medida. Clique em "Gerar Lote" em cada grupo para enviar à reciclagem.</p>
        </div>
      </div>

      <div v-for="grupo in gruposPorMedida" :key="grupo.medida" class="medida-group">
        <div class="medida-group-header">
          <div class="medida-group-info">
            <span class="medida-badge">{{ grupo.medida || 'Sem Medida' }}</span>
            <span class="medida-count">{{ grupo.pneus.length }} pneu(s)</span>
          </div>
          <button class="btn-primary btn-sm-lote" @click="gerarLotePorMedida(grupo)">
            Gerar Lote ({{ grupo.pneus.length }})
          </button>
        </div>
        <div class="aguardando-grid">
          <div
            v-for="p in grupo.pneus" :key="p.id"
            class="pneu-selection-card"
            :class="{ selected: selected.includes(p.id) }"
            @click="toggleSelection(p.id)"
          >
            <div class="selection-indicator">
              <div class="check-circle">
                <svg v-if="selected.includes(p.id)" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
            </div>
            <div class="pneu-brief">
              <span class="pneu-fogo">{{ p.numero_fogo }}</span>
              <span class="pneu-model">{{ p.marca }} {{ p.modelo }}</span>
              <span class="pneu-medida">{{ p.medida || '—' }}</span>
              <span class="pneu-origin">{{ p.filial_origem_nome }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="pneusAguardando.length > 0 && lotes.length > 0" class="section-divider">
      <span>Lotes já Processados</span>
    </div>

    <!-- Lista de lotes -->
    <div class="lotes-container">
      <div v-for="l in lotes" :key="l.id" class="lote-card">
        <div class="lote-header">
          <div class="lote-title">
            <span class="lote-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8V21H3V8"/><path d="M1 3H23V8H1V3Z"/><path d="M10 12H14"/></svg>
            </span>
            <div class="lote-names">
              <h3>{{ l.numero_lote }}</h3>
              <span class="lote-date">Envio: {{ new Date(l.data_envio).toLocaleDateString('pt-BR') }}</span>
            </div>
          </div>
          <div class="lote-finance">
            <div class="finance-item" v-if="l.valor_total > 0">
              <span class="lbl">Total Lote:</span>
              <span class="val">{{ l.valor_total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}</span>
            </div>
            <div class="finance-item" v-if="l.valor_pneu > 0">
              <span class="lbl">Por Pneu:</span>
              <span class="val">{{ l.valor_pneu.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}</span>
            </div>
            <button class="btn-lote-valor" @click="openValorModal(l)" style="margin-right:8px">
              {{ l.valor_total > 0 ? 'Editar Valor' : 'Informar Valor' }}
            </button>
            <button class="btn-lote-valor" @click="imprimirLote(l)" style="background:var(--surface-1);border-color:var(--ink-300)">
              Relatório
            </button>
          </div>
        </div>
        <div class="lote-pneus">
          <div class="table-responsive">
            <table class="gp-table mini">
              <thead>
                <tr>
                  <th>N. Fogo</th>
                  <th>Marca/Modelo</th>
                  <th>Medida</th>
                  <th>Filial Origem</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in l.pneus" :key="p.id">
                  <td><strong>{{ p.numero_fogo }}</strong></td>
                  <td>{{ p.marca }} {{ p.modelo }}</td>
                  <td>{{ p.medida || '—' }}</td>
                  <td>{{ p.filial_origem_nome || 'N/A' }}</td>
                  <td><span class="badge badge-purple">Reciclagem</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div v-if="!lotes.length" class="empty-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:12px"><path d="M21 8V21H3V8"/><path d="M1 3H23V8H1V3Z"/><path d="M10 12H14"/></svg>
        <p>Nenhum lote de reciclagem encontrado</p>
      </div>
    </div>

    <!-- Modal: Valor do Lote -->
    <div v-if="showValorModal" class="modal-overlay" @click.self="showValorModal = false">
      <div class="modal-box">
        <h3>Informar Valor do Lote</h3>
        <p>Lote: <strong>{{ valorCtx?.numero_lote }}</strong></p>
        <p style="font-size:13px;color:var(--ink-600);margin-top:4px">
          O valor total será dividido entre os <strong>{{ valorCtx?.pneus.length }} pneus</strong> do lote.
        </p>
        <div class="form-group" style="margin-top:16px">
          <label>Valor Total Recebido (R$)</label>
          <input type="number" v-model="valorForm.valor_total" step="0.01" />
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showValorModal = false">Cancelar</button>
          <button class="btn-primary" @click="salvarValor">Salvar Valor</button>
        </div>
      </div>
    </div>

    <!-- Manifesto de impressão (oculto na tela) -->
    <div id="printable-lote" class="print-only" v-if="loteImpressao">
      <div class="pm-header">
        <div class="pm-logo-cell">
          <img src="/logo.jpg" alt="Gritsch" class="pm-logo" />
          <span class="pm-system-label">CONTROLE DE PNEUS</span>
        </div>
        <div class="pm-company-cell">
          <div class="pm-company-name">TRANSPORTES GRITSCH LTDA</div>
          <div class="pm-company-info">RUA FRANCISCO NUNES, 1990 — PRADO VELHO</div>
          <div class="pm-company-info">80215-202 — CURITIBA / PR</div>
          <div class="pm-company-info">Fone: (41) 3072-1100 &nbsp;|&nbsp; pneus@gritsch.com.br</div>
        </div>
        <div class="pm-title-cell">
          <div class="pm-title-main">MANIFESTO</div>
          <div class="pm-title-main">DE ENVIO</div>
          <div class="pm-title-sub">RECICLAGEM DE PNEUS</div>
        </div>
      </div>
      <div class="pm-meta">
        <div class="pm-meta-item">
          <span class="pm-meta-label">LOTE</span>
          <span class="pm-meta-value">{{ loteImpressao.numero_lote }}</span>
        </div>
        <div class="pm-meta-item">
          <span class="pm-meta-label">DATA DE ENVIO</span>
          <span class="pm-meta-value">{{ new Date(loteImpressao.data_envio).toLocaleDateString('pt-BR') }}</span>
        </div>
        <div class="pm-meta-item">
          <span class="pm-meta-label">QUANTIDADE</span>
          <span class="pm-meta-value">{{ loteImpressao.pneus.length }} pneu(s)</span>
        </div>
      </div>
      <table class="pm-table">
        <thead>
          <tr>
            <th style="width:18%">N. FOGO</th>
            <th style="width:42%">MARCA / MODELO</th>
            <th style="width:20%">MEDIDA</th>
            <th style="width:20%">OBSERVAÇÃO</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(p, i) in loteImpressao.pneus" :key="p.id" :class="i % 2 === 0 ? 'pm-tr-even' : ''">
            <td><strong>{{ p.numero_fogo }}</strong></td>
            <td>{{ p.marca }} {{ p.modelo }}</td>
            <td>{{ p.medida || '—' }}</td>
            <td></td>
          </tr>
        </tbody>
      </table>
      <div class="pm-signatures">
        <div class="pm-sig-block">
          <div class="pm-sig-line"></div>
          <p class="pm-sig-label">Responsável Gritsch — Expedição</p>
          <p class="pm-sig-sub">Nome / Matrícula</p>
        </div>
        <div class="pm-sig-block">
          <div class="pm-sig-line"></div>
          <p class="pm-sig-label">Responsável Recicladora — Recebimento</p>
          <p class="pm-sig-sub">Nome Legível / RG</p>
        </div>
      </div>
      <div class="pm-footer">
        Documento gerado em {{ new Date().toLocaleString('pt-BR') }} — Sistema Torre de Controle Gritsch
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchLotesReciclagem, fetchPneusAguardandoLote, criarLoteReciclagem, atualizarValorLote } from '../../api/gestaoPneus.js'

const emit = defineEmits(['refresh'])

const lotes = ref([])
const pneusAguardando = ref([])
const selected = ref([])

const gruposPorMedida = computed(() => {
  const map = new Map()
  for (const p of pneusAguardando.value) {
    const key = p.medida || ''
    if (!map.has(key)) map.set(key, [])
    map.get(key).push(p)
  }
  return [...map.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([medida, pneus]) => ({ medida, pneus }))
})

const showValorModal = ref(false)
const valorCtx = ref(null)
const valorForm = ref({ valor_total: 0 })
const loteImpressao = ref(null)

async function loadLotes() {
  try {
    lotes.value = await fetchLotesReciclagem()
    pneusAguardando.value = await fetchPneusAguardandoLote()
  } catch(e) { console.error(e) }
}

function toggleSelection(id) {
  const idx = selected.value.indexOf(id)
  if (idx > -1) selected.value.splice(idx, 1)
  else selected.value.push(id)
}

async function gerarLote() {
  if (selected.value.length === 0) return
  try {
    await criarLoteReciclagem({
      pneu_ids: selected.value,
      filial_id: pneusAguardando.value[0]?.filial_id || 1
    })
    alert(`Lote gerado com sucesso!`)
    selected.value = []
    await loadLotes()
    emit('refresh')
  } catch(e) { alert(e.message) }
}

async function gerarLotePorMedida(grupo) {
  const ids = grupo.pneus.map(p => p.id)
  if (ids.length === 0) return
  try {
    await criarLoteReciclagem({
      pneu_ids: ids,
      filial_id: grupo.pneus[0]?.filial_id || 1
    })
    alert(`Lote de ${grupo.medida || 'sem medida'} gerado com sucesso!`)
    selected.value = selected.value.filter(id => !ids.includes(id))
    await loadLotes()
    emit('refresh')
  } catch(e) { alert(e.message) }
}

function openValorModal(lote) {
  valorCtx.value = lote
  valorForm.value = { valor_total: lote.valor_total || 0 }
  showValorModal.value = true
}

async function salvarValor() {
  try {
    await atualizarValorLote({ lote_id: valorCtx.value.id, valor_total: valorForm.value.valor_total })
    showValorModal.value = false
    await loadLotes()
  } catch(e) { alert(e.message) }
}

function imprimirLote(lote) {
  loteImpressao.value = lote
  setTimeout(() => {
    window.print()
    loteImpressao.value = null
  }, 300)
}

onMounted(loadLotes)
</script>

<style scoped>
.aguardando-lote-box { background: var(--surface-1); border: 1px solid var(--ink-200); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
.box-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 16px; }
.title-group h3 { font-size: 15px; font-weight: 700; color: var(--ink-900); margin: 0 0 4px; }
.title-group p  { font-size: 13px; color: var(--ink-600); margin: 0; }

.aguardando-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
.pneu-selection-card { background: var(--surface-0); border: 2px solid var(--ink-200); border-radius: 10px; padding: 14px; cursor: pointer; transition: all 0.2s; display: flex; gap: 12px; align-items: flex-start; }
.pneu-selection-card:hover { border-color: var(--brand-600); }
.pneu-selection-card.selected { border-color: var(--brand-900); background: var(--brand-100); }
.selection-indicator { flex-shrink: 0; }
.check-circle { width: 22px; height: 22px; border-radius: 50%; border: 2px solid var(--ink-300); display: flex; align-items: center; justify-content: center; background: var(--surface-0); transition: all 0.2s; }
.selected .check-circle { background: var(--brand-900); border-color: var(--brand-900); color: white; }
.medida-group { margin-bottom: 20px; }
.medida-group-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: var(--surface-2); border: 1px solid var(--ink-200); border-radius: 8px; margin-bottom: 10px; }
.medida-group-info { display: flex; align-items: center; gap: 10px; }
.medida-badge { font-size: 13px; font-weight: 800; color: var(--brand-900); background: var(--brand-100); padding: 3px 10px; border-radius: 6px; letter-spacing: 0.03em; }
.medida-count { font-size: 12px; color: var(--ink-600); }
.btn-sm-lote { padding: 6px 14px; font-size: 12px; font-weight: 600; background: var(--brand-900); color: #fff; border: none; border-radius: 7px; cursor: pointer; transition: opacity 0.2s; }
.btn-sm-lote:hover { opacity: 0.85; }

.pneu-brief { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.pneu-fogo { font-size: 13px; font-weight: 800; color: var(--ink-900); }
.pneu-model { font-size: 11px; color: var(--ink-600); }
.pneu-medida { font-size: 11px; font-weight: 700; color: var(--brand-900); }
.pneu-origin { font-size: 10px; color: var(--ink-300); }

.section-divider { display: flex; align-items: center; gap: 16px; margin: 24px 0; }
.section-divider::before, .section-divider::after { content: ''; flex: 1; height: 1px; background: var(--ink-200); }
.section-divider span { font-size: 12px; font-weight: 700; color: var(--ink-300); text-transform: uppercase; letter-spacing: 0.06em; white-space: nowrap; }

.lotes-container { display: flex; flex-direction: column; gap: 16px; }
.lote-card { background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: 12px; overflow: hidden; box-shadow: var(--shadow-sm); }
.lote-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 18px 20px; border-bottom: 1px solid var(--ink-200); background: var(--surface-1); flex-wrap: wrap; }
.lote-title { display: flex; align-items: center; gap: 14px; }
.lote-icon { width: 42px; height: 42px; background: var(--brand-100); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: var(--brand-900); flex-shrink: 0; }
.lote-names h3 { font-size: 15px; font-weight: 800; margin: 0 0 2px; color: var(--ink-900); }
.lote-date { font-size: 12px; color: var(--ink-600); }
.lote-finance { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.finance-item { display: flex; flex-direction: column; gap: 2px; }
.finance-item .lbl { font-size: 10px; text-transform: uppercase; font-weight: 700; color: var(--ink-300); }
.finance-item .val { font-size: 14px; font-weight: 800; color: var(--status-ok); }
.lote-pneus { padding: 0; }
.btn-lote-valor { padding: 8px 14px; background: var(--surface-0); border: 1px solid var(--brand-900); color: var(--brand-900); border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: all 0.2s; }
.btn-lote-valor:hover { background: var(--brand-100); }
.mini th, .mini td { padding: 10px 14px; }

/* Print */
.print-only { display: none; }
@media print {
  body > * { display: none !important; }
  #printable-lote { display: block !important; font-family: Arial, sans-serif; font-size: 11pt; color: #000; padding: 20mm; }
  .pm-header { display: grid; grid-template-columns: auto 1fr auto; gap: 20px; border-bottom: 2px solid #000; padding-bottom: 14px; margin-bottom: 14px; align-items: center; }
  .pm-logo { height: 50px; width: auto; }
  .pm-system-label { font-size: 9pt; font-weight: 700; display: block; margin-top: 4px; color: #555; }
  .pm-company-name { font-size: 13pt; font-weight: 700; }
  .pm-company-info { font-size: 9pt; color: #444; }
  .pm-title-cell { text-align: right; }
  .pm-title-main { font-size: 18pt; font-weight: 900; line-height: 1.1; }
  .pm-title-sub { font-size: 9pt; color: #555; margin-top: 4px; }
  .pm-meta { display: flex; gap: 40px; margin-bottom: 16px; padding: 12px 16px; border: 1px solid #ccc; border-radius: 4px; }
  .pm-meta-label { display: block; font-size: 8pt; font-weight: 700; text-transform: uppercase; color: #888; }
  .pm-meta-value { display: block; font-size: 12pt; font-weight: 700; }
  .pm-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
  .pm-table th { background: #1a1a1a; color: #fff; padding: 8px 10px; text-align: left; font-size: 9pt; }
  .pm-table td { padding: 7px 10px; border-bottom: 1px solid #e5e5e5; font-size: 10pt; }
  .pm-tr-even td { background: #f9f9f9; }
  .pm-signatures { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; margin-top: 40px; }
  .pm-sig-line { border-top: 1px solid #000; margin-bottom: 8px; }
  .pm-sig-label { font-size: 10pt; font-weight: 700; margin: 0 0 2px; }
  .pm-sig-sub { font-size: 9pt; color: #555; margin: 0; }
  .pm-footer { margin-top: 30px; text-align: center; font-size: 8pt; color: #888; border-top: 1px solid #e5e5e5; padding-top: 8px; }
}
</style>
