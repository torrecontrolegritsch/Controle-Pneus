<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <h2>Gestão de Reciclagem</h2>
      <div class="toolbar-filters">
        <div class="tab-group">
          <button 
            :class="{ active: tab === 'pendentes' }" 
            @click="tab = 'pendentes'"
          >Pneus Pendentes</button>
          <button 
            :class="{ active: tab === 'lotes' }" 
            @click="tab = 'lotes'"
          >Lotes Enviados</button>
        </div>
        <select v-model="filtroFilial" class="filter-select" @change="loadData">
          <option :value="null">Todas as filiais</option>
          <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>
      </div>
    </div>

    <!-- TAB: PNEUS PENDENTES -->
    <div v-if="tab === 'pendentes'">
      <div class="batch-actions" v-if="selectedIds.length > 0">
        <span class="selection-count">{{ selectedIds.length }} pneus selecionados</span>
        <button class="btn-primary" @click="handleGerarLote">Criar Lote com Selecionados</button>
      </div>

      <AppTable 
        :data="pneusPendentes" 
        :columns="pneuColumns" 
        :loading="loading"
        empty-message="Nenhum pneu aguardando reciclagem"
      >
        <template #select="{ row }">
          <input type="checkbox" :value="row.id" v-model="selectedIds" />
        </template>
        <template #numero_fogo="{ value }">
          <span class="fogo-cell">{{ value }}</span>
        </template>
        <template #vida="{ value }">
          {{ value }}ª vida
        </template>
      </AppTable>
    </div>

    <!-- TAB: LOTES ENVIADOS -->
    <div v-else>
      <div class="reciclagem-stats">
        <div class="stat-card">
          <span class="stat-value">{{ totalLotes }}</span>
          <span class="stat-label">Lotes</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ totalPneus }}</span>
          <span class="stat-label">Total Pneus</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">R$ {{ fmtN(totalValor) }}</span>
          <span class="stat-label">Valor Total</span>
        </div>
      </div>

      <AppTable 
        :data="lotes" 
        :columns="loteColumns" 
        :loading="loading"
        empty-message="Nenhum lote gerado"
      >
        <template #created_at="{ value }">
          {{ formatDate(value) }}
        </template>
        <template #valor_total="{ value }">
          R$ {{ fmtN(value) }}
        </template>
        <template #status="{ value }">
          <span class="status-badge" :class="value">{{ value }}</span>
        </template>
        <template #actions="{ row }">
           <button class="btn-icon" @click="editLote(row)" title="Informar Valor">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1v22m5-18H8.5a3.5 3.5 0 0 0 0 7h7a3.5 3.5 0 0 1 0 7H6"></path></svg>
           </button>
        </template>
      </AppTable>
    </div>

    <!-- Modal Valor Lote -->
    <AppModal v-model="showValorModal" title="Atualizar Valor do Lote">
       <div class="form-group">
          <label>Valor Total Recebido (R$)</label>
          <input type="number" v-model.number="valorLoteForm.valor" step="0.01" />
       </div>
       <template #footer>
          <button class="btn-secondary" @click="showValorModal = false">Cancelar</button>
          <button class="btn-primary" @click="saveValorLote">Salvar</button>
       </template>
    </AppModal>

  </section>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import AppTable from '../ui/AppTable.vue'
import AppModal from '../ui/AppModal.vue'
import * as api from '../../api/gestaoPneus.js'

const props = defineProps({
  filiais: { type: Array, default: () => [] }
})

const tab = ref('pendentes')
const loading = ref(false)
const lotes = ref([])
const pneusPendentes = ref([])
const selectedIds = ref([])
const filtroFilial = ref(null)

const showValorModal = ref(false)
const valorLoteForm = reactive({ lote_id: null, valor: 0 })

const pneuColumns = [
  { key: 'select', label: '', width: '40px' },
  { key: 'numero_fogo', label: 'Fogo' },
  { key: 'marca', label: 'Marca' },
  { key: 'modelo', label: 'Modelo' },
  { key: 'vida', label: 'Vida' },
  { key: 'filial_nome', label: 'Unidade' }
]

const loteColumns = [
  { key: 'id', label: 'Lote' },
  { key: 'data_envio', label: 'Data Envio' },
  { key: 'filial_origem_nome', label: 'Filial' },
  { key: 'qtd_pneus', label: 'Qtd' },
  { key: 'valor_total', label: 'Valor' },
  { key: 'actions', label: 'Ações' }
]

const totalLotes = computed(() => lotes.value.length)
const totalPneus = computed(() => lotes.value.reduce((sum, l) => sum + (l.pneus?.length || 0), 0))
const totalValor = computed(() => lotes.value.reduce((sum, l) => sum + (l.valor_total || 0), 0))

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    if (tab.value === 'lotes') {
      lotes.value = await api.fetchLotesReciclagem({ filial_id: filtroFilial.value })
    } else {
      // Pneus que estão em reciclagem mas não têm lote_id
      const all = await api.fetchPneusList({ status: 'reciclagem', filial_id: filtroFilial.value })
      pneusPendentes.value = all.filter(p => !p.lote_id)
      selectedIds.value = []
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function handleGerarLote() {
  if (selectedIds.value.length === 0) return
  if (!confirm(`Deseja gerar um lote com ${selectedIds.value.length} pneus?`)) return
  
  loading.value = true
  try {
    const fId = filtroFilial.value || (pneusPendentes.value.length > 0 ? pneusPendentes.value[0].filial_id : 1)
    await api.criarLoteReciclagem({ pneu_ids: selectedIds.value, filial_id: fId })
    tab.value = 'lotes'
    loadData()
  } catch (e) {
    alert(e.message)
  } finally {
    loading.value = false
  }
}

function editLote(lote) {
  valorLoteForm.lote_id = lote.id
  valorLoteForm.valor = lote.valor_total
  showValorModal.value = true
}

async function saveValorLote() {
  loading.value = true
  try {
    await api.atualizarValorLote({ lote_id: valorLoteForm.lote_id, valor_total: valorLoteForm.valor })
    showValorModal.value = false
    loadData()
  } catch (e) {
    alert(e.message)
  } finally {
    loading.value = false
  }
}

function fmtN(n) {
  return Number(n || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('pt-BR')
}
</script>

<style scoped>
.sec-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.sec-toolbar h2 {
  margin: 0;
  color: #fff;
  font-size: 20px;
}

.toolbar-filters {
  display: flex;
  align-items: center;
  gap: 16px;
}

.tab-group {
  display: flex;
  background: rgba(255,255,255,0.05);
  padding: 4px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.1);
}

.tab-group button {
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: rgba(255,255,255,0.6);
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.tab-group button.active {
  background: #6366f1;
  color: #fff;
}

.filter-select {
  padding: 8px 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
}

.reciclagem-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: #1e1e3f;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
  align-items: center;
  border: 1px solid rgba(255,255,255,0.05);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #818cf8;
}

.stat-label {
  font-size: 13px;
  color: rgba(255,255,255,0.6);
  margin-top: 4px;
}

.batch-actions {
  background: rgba(99, 102, 241, 0.1);
  padding: 12px 20px;
  border-radius: 12px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.selection-count {
  color: #818cf8;
  font-weight: 600;
}

.btn-primary {
  background: #6366f1;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary {
  background: transparent;
  color: #fff;
  border: 1px solid rgba(255,255,255,0.2);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.fogo-cell {
  font-weight: 600;
  color: #818cf8;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.form-group label { color: rgba(255,255,255,0.7); font-size: 13px; }
.form-group input { 
  background: rgba(255,255,255,0.05); 
  border: 1px solid rgba(255,255,255,0.1); 
  padding: 10px; 
  border-radius: 6px; 
  color: #fff; 
}

.btn-icon {
  background: rgba(99, 102, 241, 0.1);
  border: none;
  color: #818cf8;
  padding: 6px;
  border-radius: 4px;
  cursor: pointer;
}
</style>