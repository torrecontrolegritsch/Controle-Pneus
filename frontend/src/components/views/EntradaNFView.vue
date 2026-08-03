<template>
  <div class="entrada-nf">

    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2>Entrada de NF</h2>
        <p class="sec-subtitle">Registro de Notas Fiscais e Distribuição Logística</p>
      </div>
      <div class="toolbar-right">
        <button class="btn-secondary" @click="downloadTemplate">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Baixar Modelo
        </button>
        <button class="btn-secondary" @click="triggerImport">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          Importar Estoque
        </button>
        <input type="file" ref="fileInput" style="display:none;" accept=".csv" @change="handleFileUpload" />
        <button class="btn-primary" @click="openPneuForm()">+ Registrar Novo Pneu (NF)</button>
      </div>
    </div>

    <!-- Barra de distribuição em lote -->
    <div v-if="selectedIds.length > 0" class="batch-bar">
      <div class="batch-info">
        <strong>{{ selectedIds.length }}</strong> pneus selecionados
      </div>
      <div class="batch-actions">
        <select v-model="filialDestinoId" class="filter-select select-premium">
          <option :value="null">Selecionar Filial Destino...</option>
          <option v-for="f in filiaisDestino" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>
        <button class="btn-primary" :disabled="!filialDestinoId" @click="distribuirEmLote">
          Confirmar Distribuição em Lote
        </button>
        <button class="btn-secondary" @click="selectedIds = []">Cancelar</button>
      </div>
    </div>

    <!-- Seleção global -->
    <div v-if="pneus.length" class="sel-bar">
      <label class="sel-all">
        <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" />
        <span>Selecionar todos ({{ pneus.length }})</span>
      </label>
      <span class="sel-info" v-if="selectedIds.length">{{ selectedIds.length }} selecionado{{ selectedIds.length > 1 ? 's' : '' }}</span>
    </div>

    <!-- Acordeão por Fornecedor → Mês -->
    <div v-if="gruposFornecedor.length" class="fornecedor-list">
      <div v-for="gf in gruposFornecedor" :key="gf.fornecedor" class="fornecedor-card">
        <div class="forn-header" @click="toggleFornecedor(gf.fornecedor)">
          <div class="forn-header-left">
            <span class="chevron" :class="{ open: expandedFornecedor.has(gf.fornecedor) }">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
            </span>
            <span class="forn-nome">{{ gf.fornecedor }}</span>
            <span class="forn-badge">{{ gf.qtd }} pneu{{ gf.qtd > 1 ? 's' : '' }}</span>
          </div>
          <div class="forn-header-right">
            <span class="forn-valor">R$ {{ fmtN(gf.valor) }}</span>
          </div>
        </div>

        <div v-if="expandedFornecedor.has(gf.fornecedor)" class="forn-body">
          <div v-for="gm in gf.meses" :key="gm.mesKey" class="mes-grupo">
            <div class="mes-header" @click="toggleMes(gf.fornecedor, gm.mesKey)">
              <span class="chevron chevron-sm" :class="{ open: expandedMes.has(gf.fornecedor + '|' + gm.mesKey) }">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
              </span>
              <span class="mes-label">{{ gm.mesLabel }}</span>
              <span class="mes-badge">{{ gm.qtd }} pneu{{ gm.qtd > 1 ? 's' : '' }}</span>
              <span class="mes-valor">R$ {{ fmtN(gm.valor) }}</span>
            </div>

            <div v-if="expandedMes.has(gf.fornecedor + '|' + gm.mesKey)" class="mes-table-wrap">
              <table class="mes-table">
                <thead>
                  <tr>
                    <th width="36"></th>
                    <th>N. Fogo</th>
                    <th>Marca / Modelo</th>
                    <th>Medida</th>
                    <th>NF</th>
                    <th class="text-right">Valor Unit.</th>
                    <th>Entrada</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in gm.pneus" :key="p.id">
                    <td><input type="checkbox" v-model="selectedIds" :value="p.id" /></td>
                    <td><strong class="fogo-tag">{{ p.numero_fogo }}</strong></td>
                    <td class="td-marca">{{ p.marca }} {{ p.modelo }}</td>
                    <td class="td-medida">{{ p.medida }}</td>
                    <td class="td-nf">{{ p.nf || '—' }}</td>
                    <td class="text-right td-valor">R$ {{ fmtN(p.valor) }}</td>
                    <td class="td-data">{{ p.criado_em ? new Date(p.criado_em).toLocaleDateString('pt-BR') : '—' }}</td>
                    <td><button class="btn-sm" @click.stop="openPneuForm(p)">Editar</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v8"/><path d="M8 12h8"/></svg>
      <p>Nenhum pneu cadastrado ainda. Registre o primeiro pneu via NF.</p>
    </div>

    <!-- Modal Cadastro/Edição -->
    <div v-if="showModal" class="modal-overlay" @click.self="fecharModalNF">
      <div class="modal-box">

        <template v-if="!showDistribuirRapido">
          <h3>{{ editingPneu ? 'Editar Pneu' : 'Entrada de Pneu (NF)' }}</h3>
          <div class="form-row">
            <div class="form-group">
              <label>Nº Fogo</label>
              <input v-model="pneuForm.numero_fogo" placeholder="EX: 0001" />
            </div>
            <div class="form-group">
              <label>Nota Fiscal (NF)</label>
              <input v-model="pneuForm.nf" placeholder="000.000.000" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Marca</label>
              <input v-model="pneuForm.marca" />
            </div>
            <div class="form-group">
              <label>Modelo</label>
              <input v-model="pneuForm.modelo" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Medida</label>
              <input v-model="pneuForm.medida" />
            </div>
            <div class="form-group">
              <label>Valor Unitário (R$)</label>
              <input type="number" step="0.01" v-model="pneuForm.valor" />
            </div>
          </div>
          <div class="form-group">
            <label>Fornecedor</label>
            <input v-model="pneuForm.fornecedor" />
          </div>
          <div class="modal-actions">
            <button class="btn-secondary" @click="fecharModalNF">Cancelar</button>
            <button class="btn-primary" @click="savePneu">Salvar Entrada</button>
          </div>
        </template>

        <template v-else>
          <div class="dist-rapida-success">
            <div class="dist-rapida-icon">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/></svg>
            </div>
            <h3 class="dist-rapida-title">Pneu cadastrado!</h3>
            <p class="dist-rapida-sub">Pneu <strong>{{ pneuForm.numero_fogo }}</strong> entrou no Estoque Central.<br>Deseja distribuir para uma filial agora?</p>
          </div>
          <div class="form-group" style="margin-top:16px;">
            <label>Filial de destino</label>
            <select v-model="filialDestinoRapido" class="filter-select" style="width:100%;">
              <option :value="null">— Selecionar filial —</option>
              <option v-for="f in filiaisDestino" :key="f.id" :value="f.id">{{ f.nome }}</option>
            </select>
          </div>
          <div class="modal-actions" style="margin-top:20px;">
            <button class="btn-secondary" @click="fecharModalNF">Finalizar sem distribuir</button>
            <button class="btn-primary" :disabled="!filialDestinoRapido || distribuindoRapido" @click="distribuirRapido">
              {{ distribuindoRapido ? 'Enviando...' : 'Distribuir Agora' }}
            </button>
          </div>
        </template>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import * as api from '../../api/gestaoPneus.js'

const props = defineProps({
  filiais: { type: Array, default: () => [] }
})

const loading = ref(false)
const pneus = ref([])
const selectedIds = ref([])
const filialDestinoId = ref(null)
const showModal = ref(false)
const editingPneu = ref(null)
const fileInput = ref(null)
const expandedFornecedor = ref(new Set())
const expandedMes = ref(new Set())
const showDistribuirRapido = ref(false)
const filialDestinoRapido = ref(null)
const pneuRecemCriadoId = ref(null)
const distribuindoRapido = ref(false)

const pneuForm = ref({
  numero_fogo: '', marca: '', modelo: '', medida: '295/80R22.5',
  valor: 0, nf: '', fornecedor: '', filial_id: null
})

const centralFilial = computed(() =>
  props.filiais.find(f => f.nome.toUpperCase().includes('ESTOQUE CENTRAL'))
)

const filiaisDestino = computed(() =>
  props.filiais.filter(f => f.id !== centralFilial.value?.id && !f.nome.toUpperCase().includes('SUCATA'))
)

const allSelected = computed(() =>
  pneus.value.length > 0 && selectedIds.value.length === pneus.value.length
)

const gruposFornecedor = computed(() => {
  const mapa = {}
  for (const p of pneus.value) {
    const forn = (p.fornecedor || 'Sem Fornecedor').trim()
    if (!mapa[forn]) mapa[forn] = {}
    let mesKey = 'sem-data', mesLabel = 'Sem data'
    if (p.criado_em) {
      const d = new Date(p.criado_em)
      mesKey = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}`
      mesLabel = d.toLocaleString('pt-BR', { month: 'long', year: 'numeric' })
      mesLabel = mesLabel.charAt(0).toUpperCase() + mesLabel.slice(1)
    }
    if (!mapa[forn][mesKey]) mapa[forn][mesKey] = { mesKey, mesLabel, pneus: [] }
    mapa[forn][mesKey].pneus.push(p)
  }
  return Object.entries(mapa)
    .map(([fornecedor, mesesMap]) => {
      const meses = Object.values(mesesMap)
        .sort((a, b) => b.mesKey.localeCompare(a.mesKey))
        .map(gm => ({ ...gm, qtd: gm.pneus.length, valor: gm.pneus.reduce((s, p) => s + parseFloat(p.valor || 0), 0) }))
      return { fornecedor, meses, qtd: meses.reduce((s, m) => s + m.qtd, 0), valor: meses.reduce((s, m) => s + m.valor, 0) }
    })
    .sort((a, b) => b.qtd - a.qtd)
})

onMounted(loadData)

watch(centralFilial, (nova, antiga) => {
  if (nova && !antiga) loadData()
})

async function loadData() {
  if (!centralFilial.value) return
  loading.value = true
  try {
    pneus.value = await api.fetchPneusList({ status: 'estoque', filial_id: centralFilial.value.id })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function toggleSelectAll() {
  selectedIds.value = allSelected.value ? [] : pneus.value.map(p => p.id)
}

function toggleFornecedor(nome) {
  const s = new Set(expandedFornecedor.value)
  if (s.has(nome)) s.delete(nome)
  else s.add(nome)
  expandedFornecedor.value = s
}

function toggleMes(fornecedor, mesKey) {
  const key = `${fornecedor}|${mesKey}`
  const s = new Set(expandedMes.value)
  if (s.has(key)) s.delete(key)
  else s.add(key)
  expandedMes.value = s
}

function openPneuForm(p = null) {
  editingPneu.value = p
  pneuForm.value = p
    ? { ...p }
    : { numero_fogo: '', marca: '', modelo: '', medida: '295/80R22.5', valor: 0, nf: '', fornecedor: '', filial_id: centralFilial.value?.id }
  showModal.value = true
}

async function savePneu() {
  try {
    if (editingPneu.value) {
      await api.updatePneu(editingPneu.value.id, pneuForm.value)
      showModal.value = false
      loadData()
    } else {
      const criado = await api.createPneu(pneuForm.value)
      pneuRecemCriadoId.value = criado?.id ?? null
      filialDestinoRapido.value = null
      showDistribuirRapido.value = true
      loadData()
    }
  } catch (e) {
    alert(e.message)
  }
}

async function distribuirRapido() {
  if (!filialDestinoRapido.value || !pneuRecemCriadoId.value) return
  distribuindoRapido.value = true
  try {
    await api.transferirPneu({ pneu_id: pneuRecemCriadoId.value, filial_destino_id: filialDestinoRapido.value, observacao: 'Distribuição imediata via cadastro de NF' })
    loadData()
  } catch (e) {
    alert('Erro ao distribuir: ' + e.message)
  } finally {
    distribuindoRapido.value = false
    showModal.value = false
    showDistribuirRapido.value = false
    pneuRecemCriadoId.value = null
  }
}

function fecharModalNF() {
  showModal.value = false
  showDistribuirRapido.value = false
  pneuRecemCriadoId.value = null
  filialDestinoRapido.value = null
}

async function distribuirEmLote() {
  if (!filialDestinoId.value || !selectedIds.value.length) return
  const filialNome = props.filiais.find(f => f.id === filialDestinoId.value)?.nome
  if (!confirm(`Deseja enviar ${selectedIds.value.length} pneus para ${filialNome}?`)) return
  loading.value = true
  try {
    for (const id of selectedIds.value) {
      await api.transferirPneu({ pneu_id: id, filial_destino_id: filialDestinoId.value, observacao: 'Distribuição em lote do Estoque Central' })
    }
    selectedIds.value = []
    filialDestinoId.value = null
    loadData()
    alert('Pneus distribuídos com sucesso!')
  } catch (e) {
    alert('Erro na distribuição: ' + e.message)
  } finally {
    loading.value = false
  }
}

async function downloadTemplate() {
  await api.fetchPneusTemplate()
}

function triggerImport() {
  fileInput.value.click()
}

async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await api.importPneusCsv(formData, centralFilial.value?.id)
    alert(res.message || 'Importação concluída!')
    loadData()
  } catch (e) {
    alert('Erro: ' + e.message)
  } finally {
    event.target.value = ''
  }
}

function fmtN(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.entrada-nf { display: flex; flex-direction: column; gap: 16px; flex: 1; overflow-y: auto; min-height: 0; padding: 16px 20px; }

.sec-toolbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
.toolbar-right { display: flex; gap: 8px; flex-wrap: wrap; }
.sec-subtitle { font-size: 13px; color: var(--text3); margin-top: 4px; }

.batch-bar { background: #eff6ff; border: 1px solid #bfdbfe; padding: 16px 24px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.batch-info { font-size: 14px; color: #1e40af; }
.batch-info strong { font-size: 16px; }
.batch-actions { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }

.sel-bar { display: flex; align-items: center; gap: 16px; padding: 10px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 13px; color: #64748b; }
.sel-all { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.sel-info { font-weight: 600; color: var(--brand, #c41230); }

.fornecedor-list { display: flex; flex-direction: column; gap: 8px; }
.fornecedor-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; }

.forn-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; cursor: pointer; user-select: none; transition: background .15s; }
.forn-header:hover { background: #f8fafc; }
.forn-header-left { display: flex; align-items: center; gap: 10px; }
.forn-header-right { display: flex; align-items: center; }

.forn-nome { font-size: 14px; font-weight: 700; color: #1e293b; }
.forn-badge { background: #f1f5f9; color: #64748b; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 20px; }
.forn-valor { font-size: 14px; font-weight: 700; color: #15803d; }

.chevron { display: flex; align-items: center; color: #94a3b8; transition: transform .2s; }
.chevron.open { transform: rotate(90deg); color: var(--brand, #c41230); }
.chevron-sm { color: #cbd5e1; }

.forn-body { border-top: 1px solid #f1f5f9; }
.mes-grupo { border-bottom: 1px solid #f8fafc; }
.mes-grupo:last-child { border-bottom: none; }

.mes-header { display: flex; align-items: center; gap: 10px; padding: 10px 18px 10px 36px; cursor: pointer; background: #fafafa; transition: background .15s; }
.mes-header:hover { background: #f1f5f9; }
.mes-label { font-size: 13px; font-weight: 600; color: #334155; flex: 1; }
.mes-badge { background: #eff6ff; color: #1d4ed8; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 20px; }
.mes-valor { font-size: 12px; color: #64748b; font-weight: 500; min-width: 100px; text-align: right; }

.mes-table-wrap { overflow-x: auto; }
.mes-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.mes-table th { background: #f9fafb; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; color: #94a3b8; padding: 8px 12px; border-bottom: 1px solid #e2e8f0; text-align: left; white-space: nowrap; }
.mes-table td { padding: 10px 12px; border-bottom: 1px solid #f8fafc; color: #334155; vertical-align: middle; }
.mes-table tbody tr:last-child td { border-bottom: none; }
.mes-table tbody tr:hover td { background: #f8fafc; }

.fogo-tag { font-weight: 700; color: #1e293b; font-size: 13px; }
.td-marca { color: #475569; }
.td-medida { font-family: Consolas, monospace; font-size: 11px; color: #64748b; white-space: nowrap; }
.td-nf { color: #15803d; font-size: 11px; }
.td-valor { font-weight: 600; color: #1e293b; white-space: nowrap; }
.td-data { color: #94a3b8; white-space: nowrap; font-size: 11px; }

.btn-primary { padding: 10px 20px; background: linear-gradient(180deg, var(--brand) 0%, var(--brand-dark) 100%); color: #fff; border: 1px solid var(--brand-dark); border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.btn-primary:hover { transform: translateY(-1px); }
.btn-primary:disabled { opacity: .5; cursor: not-allowed; transform: none; }
.btn-secondary { padding: 10px 20px; background: #fff; color: var(--text); border: 1px solid var(--s4); border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.btn-secondary:hover { background: var(--s3); }
.btn-sm { padding: 6px 12px; border: 1px solid var(--s4); background: #fff; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; color: var(--text); }

.filter-select { padding: 10px 14px; border: 1px solid var(--s4); border-radius: 8px; font-size: 13px; background: #fff; color: var(--text); min-width: 200px; outline: none; }
.select-premium { border-color: var(--brand-mid); color: var(--brand); font-weight: 600; }

.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,.6); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px); }
.modal-box { background: #fff; border-radius: 20px; padding: 32px; width: 500px; max-width: 95vw; box-shadow: 0 25px 50px rgba(0,0,0,.25); }
.modal-box h3 { font-size: 20px; font-weight: 800; margin-bottom: 24px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; }

.dist-rapida-success { text-align: center; padding: 8px 0 4px; }
.dist-rapida-icon { margin-bottom: 12px; }
.dist-rapida-title { font-size: 20px; font-weight: 800; color: #0f172a; margin: 0 0 8px; }
.dist-rapida-sub { font-size: 14px; color: #475569; line-height: 1.5; margin: 0; }

.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; flex: 1; }
.form-group label { font-size: 12px; font-weight: 700; color: var(--text2); text-transform: uppercase; }
.form-group input { padding: 10px 14px; border: 1px solid var(--s4); border-radius: 8px; font-size: 14px; outline: none; }
.form-group input:focus { border-color: var(--brand); }
.form-row { display: flex; gap: 16px; }

.text-right { text-align: right; }
.empty-state { text-align: center; padding: 48px; color: var(--text3); border: 2px dashed var(--s2); border-radius: 12px; }
</style>
