<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <h2>Pneus</h2>
      <div class="toolbar-actions">
        <select v-model="filtroStatus" class="filter-select" @change="loadData">
          <option value="">Todos os status</option>
          <option value="em_uso">Em Uso</option>
          <option value="estoque">Estoque</option>
          <option value="reciclagem">Reciclagem</option>
          <option value="descartado">Descartado</option>
        </select>
        <select v-model="filtroFilial" class="filter-select" @change="loadData">
          <option :value="null">Todas as filiais</option>
          <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>
        <button class="btn-primary" @click="showModal = true">+ Novo Pneu</button>
      </div>
    </div>

    <AppTable 
      :data="pneus" 
      :columns="columns" 
      :loading="loading"
      empty-message="Nenhum pneu encontrado"
    >
      <template #numero_fogo="{ value }">
        <span class="fogo-cell">{{ value }}</span>
      </template>
      <template #status="{ value }">
        <span class="status-badge" :class="value">{{ value }}</span>
      </template>
      <template #vida="{ value }">
        <span class="vida-cell">{{ value }}ª vida</span>
      </template>
      <template #sulco_atual="{ value }">
        <div class="sulco-bar">
          <div class="sulco-fill" :style="{ width: (value / 20 * 100) + '%' }" :class="{ warning: value < 5 }"></div>
        </div>
        <span class="sulco-value">{{ value }}mm</span>
      </template>
      <template #actions="{ row }">
        <div class="row-actions">
          <button class="btn-icon" @click="edit(row)" title="Editar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
          </button>
          <button class="btn-icon btn-danger" @click="confirmDelete(row)" title="Excluir">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </button>
        </div>
      </template>
    </AppTable>

    <!-- Modal Form -->
    <AppModal v-model="showModal" :title="editing ? 'Editar Pneu' : 'Novo Pneu'" max-width="500px">
      <form @submit.prevent="save" class="form-stacked">
        <div class="form-row">
          <div class="form-group">
            <label>Número de Fogo</label>
            <input v-model="form.numero_fogo" required placeholder="EX001" />
          </div>
          <div class="form-group">
            <label>Marca</label>
            <input v-model="form.marca" placeholder="Bridgestone" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Modelo</label>
            <input v-model="form.modelo" placeholder="R268" />
          </div>
          <div class="form-group">
            <label>Medida</label>
            <input v-model="form.medida" placeholder="295/80R22.5" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>DOT</label>
            <input v-model="form.dot" placeholder="2024" />
          </div>
          <div class="form-group">
            <label>Vida</label>
            <input v-model.number="form.vida" type="number" min="1" max="5" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Valor (R$)</label>
            <input v-model.number="form.valor" type="number" step="0.01" />
          </div>
          <div class="form-group">
            <label>Sulco Atual (mm)</label>
            <input v-model.number="form.sulco_atual" type="number" step="0.5" />
          </div>
        </div>
        <div class="form-group">
          <label>Filial</label>
          <select v-model="form.filial_id">
            <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
          </select>
        </div>
      </form>
      <template #footer>
        <button type="button" class="btn-secondary" @click="showModal = false">Cancelar</button>
        <button type="submit" class="btn-primary" @click="save">
          {{ editing ? 'Salvar' : 'Criar' }}
        </button>
      </template>
    </AppModal>
  </section>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppTable from '../ui/AppTable.vue'
import AppModal from '../ui/AppModal.vue'
import * as api from '../../api/gestaoPneus.js'

const props = defineProps({
  filiais: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh'])

const loading = ref(false)
const pneus = ref([])
const filtroStatus = ref('')
const filtroFilial = ref(null)
const showModal = ref(false)
const editing = ref(null)
const form = reactive({
  numero_fogo: '', marca: '', modelo: '', medida: '', dot: '', 
  vida: 1, valor: 0, sulco_atual: 16, filial_id: null
})

const columns = [
  { key: 'numero_fogo', label: 'Fogo' },
  { key: 'marca', label: 'Marca' },
  { key: 'modelo', label: 'Modelo' },
  { key: 'medida', label: 'Medida' },
  { key: 'status', label: 'Status' },
  { key: 'vida', label: 'Vida' },
  { key: 'sulco_atual', label: 'Sulco' }
]

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    pneus.value = await api.fetchPneusList({
      status: filtroStatus.value || undefined,
      filial_id: filtroFilial.value
    })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function edit(row) {
  editing.value = row.id
  Object.assign(form, row)
  showModal.value = true
}

async function save() {
  loading.value = true
  try {
    if (editing.value) {
      await api.updatePneu(editing.value, form)
    } else {
      await api.createPneu(form)
    }
    showModal.value = false
    loadData()
    emit('refresh')
  } catch (e) {
    alert(e.message)
  } finally {
    loading.value = false
  }
}

async function confirmDelete(row) {
  if (!confirm(`Excluir ${row.numero_fogo}?`)) return
  loading.value = true
  try {
    await api.updatePneu(row.id, { ativo: 0 })
    loadData()
  } catch (e) {
    alert(e.message)
  } finally {
    loading.value = false
  }
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

.toolbar-actions {
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
  cursor: pointer;
}

.fogo-cell {
  font-weight: 600;
  color: #818cf8;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.em_uso { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.status-badge.estoque { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.status-badge.reciclagem { background: rgba(234, 179, 8, 0.2); color: #eab308; }
.status-badge.descartado { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

.vida-cell {
  color: rgba(255,255,255,0.7);
}

.sulco-bar {
  width: 60px;
  height: 6px;
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
  overflow: hidden;
  display: inline-block;
  vertical-align: middle;
  margin-right: 8px;
}

.sulco-fill {
  height: 100%;
  background: #22c55e;
  border-radius: 3px;
}

.sulco-fill.warning {
  background: #ef4444;
}

.sulco-value {
  color: rgba(255,255,255,0.7);
  font-size: 12px;
}

.row-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.btn-icon {
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(255,255,255,0.05);
  border-radius: 6px;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
}

.btn-icon.btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.form-stacked {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  color: rgba(255,255,255,0.7);
  font-size: 13px;
}

.form-group input, .form-group select {
  padding: 10px 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.btn-primary {
  background: #6366f1;
  color: #fff;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary {
  background: transparent;
  color: rgba(255,255,255,0.7);
  border: 1px solid rgba(255,255,255,0.2);
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
}
</style>