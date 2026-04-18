<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <h2>Reciclagem</h2>
      <div class="toolbar-filters">
        <select v-model="filtroFilial" class="filter-select" @change="loadData">
          <option :value="null">Todas as filiais</option>
          <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>
      </div>
    </div>

    <div class="reciclagem-stats">
      <div class="stat-card">
        <span class="stat-value">{{ totalLotes }}</span>
        <span class="stat-label">Lotes Enviados</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ totalPneus }}</span>
        <span class="stat-label">Pneus</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">R$ {{ fmtN(totalValor) }}</span>
        <span class="stat-label">Valor Total</span>
      </div>
    </div>

    <AppTable 
      :data="lotes" 
      :columns="columns" 
      :loading="loading"
      empty-message="Nenhum lote"
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
    </AppTable>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppTable from '../ui/AppTable.vue'
import * as api from '../../api/gestaoPneus.js'

const props = defineProps({
  filiais: { type: Array, default: () => [] }
})

const loading = ref(false)
const lotes = ref([])
const filtroFilial = ref(null)

const columns = [
  { key: 'id', label: 'Lote' },
  { key: 'created_at', label: 'Data' },
  { key: 'filial_nome', label: 'Filial' },
  { key: 'qtd_pneus', label: 'Qtd' },
  { key: 'valor_total', label: 'Valor' },
  { key: 'status', label: 'Status' }
]

const totalLotes = computed(() => lotes.value.length)
const totalPneus = computed(() => lotes.value.reduce((sum, l) => sum + (l.qtd_pneus || 0), 0))
const totalValor = computed(() => lotes.value.reduce((sum, l) => sum + (l.valor_total || 0), 0))

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    lotes.value = await api.fetchLotesReciclagem({ filial_id: filtroFilial.value })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function fmtN(n) {
  return Number(n || 0).toLocaleString('pt-BR', { maximumFractionDigits: 0 })
}

function formatDate(date) {
  if (!date) return ''
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
  gap: 12px;
}

.filter-select {
  padding: 10px 12px;
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
  align-items: center;
  min-width: 120px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #eab308;
}

.stat-label {
  font-size: 13px;
  color: rgba(255,255,255,0.6);
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-badge.pendente { background: rgba(234, 179, 8, 0.2); color: #eab308; }
.status-badge.aprovado { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.status-badge.pago { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
</style>