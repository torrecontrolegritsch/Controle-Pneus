<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <h2>Movimentações</h2>
      <div class="toolbar-filters">
        <select v-model="filtroTipo" class="filter-select" @change="loadData">
          <option value="">Todos os tipos</option>
          <option value="alocacao">Alocação</option>
          <option value="remocao">Remoção</option>
          <option value="transferencia">Transferência</option>
        </select>
        <input v-model="search" placeholder="Buscar..." class="search-input" @input="loadData" />
      </div>
    </div>

    <AppTable 
      :data="filteredMovimentacoes" 
      :columns="columns" 
      :loading="loading"
      :has-actions="false"
      empty-message="Nenhuma movimentação"
    >
      <template #tipo="{ value }">
        <span class="tipo-badge" :class="value">{{ value }}</span>
      </template>
      <template #numero_fogo="{ value }">
        <span class="fogo-cell">{{ value }}</span>
      </template>
      <template #created_at="{ value }">
        {{ formatDate(value) }}
      </template>
      <template #km_total="{ value }">
        {{ Number(value || 0).toLocaleString('pt-BR') }} km
      </template>
    </AppTable>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppTable from '../ui/AppTable.vue'
import * as api from '../../api/gestaoPneus.js'

const loading = ref(false)
const movimentacoes = ref([])
const filtroTipo = ref('')
const search = ref('')

const columns = [
  { key: 'tipo', label: 'Tipo' },
  { key: 'numero_fogo', label: 'Pneu' },
  { key: 'created_at', label: 'Data' },
  { key: 'km_total', label: 'KM' },
  { key: 'observacao', label: 'Observação' }
]

const filteredMovimentacoes = computed(() => {
  let result = movimentacoes.value
  if (filtroTipo.value) {
    result = result.filter(m => m.tipo === filtroTipo.value)
  }
  if (search.value) {
    const s = search.value.toLowerCase()
    result = result.filter(m => 
      m.numero_fogo?.toLowerCase().includes(s) ||
      m.observacao?.toLowerCase().includes(s)
    )
  }
  return result
})

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    movimentacoes.value = await api.fetchMovimentacoes({ limit: 100 })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleString('pt-BR')
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

.filter-select, .search-input {
  padding: 10px 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
}

.search-input {
  width: 200px;
}

.tipo-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.tipo-badge.alocacao { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.tipo-badge.remocao { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.tipo-badge.transferencia { background: rgba(168, 85, 247, 0.2); color: #a855f7; }

.fogo-cell {
  font-weight: 600;
  color: #818cf8;
}
</style>