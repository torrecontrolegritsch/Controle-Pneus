
<template>
  <div class="estoque-central">
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2>Estoque Central</h2>
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
        <input type="file" ref="fileInput" style="display: none;" accept=".csv" @change="handleFileUpload" />
        <button class="btn-primary" @click="openPneuForm()">+ Registrar Novo Pneu (NF)</button>
      </div>
    </div>

    <!-- Barra de Ações em Lote -->
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

    <div class="table-responsive" v-if="pneus.length">
      <table class="gp-table">
        <thead>
          <tr>
            <th width="40"><input type="checkbox" :checked="allSelected" @change="toggleSelectAll" /></th>
            <th>N.Fogo</th>
            <th>Marca / Modelo</th>
            <th>Medida</th>
            <th>NF</th>
            <th>Fornecedor</th>
            <th>Valor Unit.</th>
            <th>Data Cadastro</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in pneus" :key="p.id">
            <td><input type="checkbox" v-model="selectedIds" :value="p.id" /></td>
            <td><strong>{{ p.numero_fogo }}</strong></td>
            <td>{{ p.marca }} {{ p.modelo }}</td>
            <td>{{ p.medida }}</td>
            <td>{{ p.nf || '—' }}</td>
            <td>{{ p.fornecedor || '—' }}</td>
            <td><strong>R$ {{ p.valor?.toLocaleString('pt-BR', {minimumFractionDigits: 2}) }}</strong></td>
            <td>{{ new Date(p.criado_em).toLocaleDateString('pt-BR') }}</td>
            <td class="td-actions">
              <button class="btn-sm" @click="openPneuForm(p)">Editar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v8"/><path d="M8 12h8"/></svg>
      <p>Nenhum pneu disponível no Estoque Central para distribuição.</p>
    </div>

    <!-- Modal Cadastro/Edição -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
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
          <button class="btn-secondary" @click="showModal = false">Cancelar</button>
          <button class="btn-primary" @click="savePneu">Salvar Entrada</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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

const pneuForm = ref({
  numero_fogo: '', marca: '', modelo: '', medida: '295/80R22.5', 
  valor: 0, nf: '', fornecedor: '', filial_id: null
})

const centralFilial = computed(() => {
  return props.filiais.find(f => f.nome.toUpperCase().includes('ESTOQUE CENTRAL'))
})

const filiaisDestino = computed(() => {
  return props.filiais.filter(f => f.id !== centralFilial.value?.id && !f.nome.toUpperCase().includes('SUCATA'))
})

const allSelected = computed(() => {
  return pneus.value.length > 0 && selectedIds.value.length === pneus.value.length
})

onMounted(loadData)

async function loadData() {
  if (!centralFilial.value) return
  loading.value = true
  try {
    pneus.value = await api.fetchPneusList({
      status: 'estoque',
      filial_id: centralFilial.value.id
    })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = pneus.value.map(p => p.id)
  }
}

function openPneuForm(p = null) {
  editingPneu.value = p
  if (p) {
    pneuForm.value = { ...p }
  } else {
    pneuForm.value = {
      numero_fogo: '', marca: '', modelo: '', medida: '295/80R22.5', 
      valor: 0, nf: '', fornecedor: '', filial_id: centralFilial.value?.id
    }
  }
  showModal.value = true
}

async function savePneu() {
  try {
    if (editingPneu.value) {
      await api.updatePneu(editingPneu.value.id, pneuForm.value)
    } else {
      await api.createPneu(pneuForm.value)
    }
    showModal.value = false
    loadData()
  } catch (e) {
    alert(e.message)
  }
}

async function distribuirEmLote() {
  if (!filialDestinoId.value || selectedIds.value.length === 0) return
  const filialNome = props.filiais.find(f => f.id === filialDestinoId.value)?.nome
  
  if (!confirm(`Deseja enviar ${selectedIds.value.length} pneus para a filial ${filialNome}?`)) return

  loading.value = true
  try {
    for (const id of selectedIds.value) {
      await api.transferirPneu({
        pneu_id: id,
        filial_destino_id: filialDestinoId.value,
        observacao: 'Distribuição em lote do Estoque Central'
      })
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

function downloadTemplate() {
  const url = api.fetchPneusTemplate()
  window.open(url, '_blank')
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
</script>

<style scoped>
.estoque-central { display: flex; flex-direction: column; gap: 20px; }
.sec-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.toolbar-right { display: flex; gap: 12px; }
.sec-subtitle { font-size: 13px; color: var(--text3); margin-top: 4px; }

.batch-bar {
  background: var(--brand-bg);
  border: 1px solid var(--brand-mid);
  padding: 16px 24px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  box-shadow: var(--shadow-sm);
}
.batch-info { font-size: 14px; color: var(--text); }
.batch-info strong { color: var(--brand); font-size: 16px; }
.batch-actions { display: flex; gap: 12px; align-items: center; }

.gp-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px; }
.gp-table th { background: #F9FAFB; font-weight: 700; color: var(--text3); text-transform: uppercase; letter-spacing: 0.05em; font-size: 11px; padding: 16px; border-bottom: 2px solid var(--border); text-align: left; }
.gp-table td { padding: 16px; border-bottom: 1px solid var(--border); color: var(--text); vertical-align: middle; }
.gp-table tr:hover td { background: #F9FAFB; }

.btn-primary { padding: 10px 20px; background: linear-gradient(180deg, var(--brand) 0%, var(--brand-dark) 100%); color: #fff; border: 1px solid var(--brand-dark); border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 6px -1px rgba(196,18,48,0.2); }
.btn-secondary { padding: 10px 20px; background: #fff; color: var(--text); border: 1px solid var(--s4); border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }
.btn-secondary:hover { background: var(--s3); border-color: var(--text3); }
.btn-sm { padding: 6px 12px; border: 1px solid var(--s4); background: #fff; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; color: var(--text); transition: all 0.2s; }

.filter-select { padding: 10px 14px; border: 1px solid var(--s4); border-radius: 8px; font-size: 13px; font-weight: 500; background: #fff; color: var(--text); min-width: 200px; outline: none; }
.select-premium { border-color: var(--brand-mid); color: var(--brand); font-weight: 600; }

.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px); }
.modal-box { background: #fff; border-radius: 20px; padding: 32px; width: 500px; max-width: 95vw; box-shadow: var(--shadow-float); }
.modal-box h3 { font-size: 20px; font-weight: 800; margin-bottom: 24px; color: var(--text); }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; }

.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; flex: 1; }
.form-group label { font-size: 12px; font-weight: 700; color: var(--text2); text-transform: uppercase; }
.form-group input { padding: 10px 14px; border: 1px solid var(--s4); border-radius: 8px; font-size: 14px; outline: none; }
.form-group input:focus { border-color: var(--brand); }
.form-row { display: flex; gap: 16px; }

.empty-state { text-align: center; padding: 48px; color: var(--text3); border: 2px dashed var(--s2); border-radius: 12px; margin-top: 20px; }

.table-responsive { overflow-x: auto; border-radius: 12px; border: 1px solid var(--border); }
</style>
