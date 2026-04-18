<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <h2>Veículos</h2>
      <div class="toolbar-filters">
        <select v-model="filialFilter" class="filter-select" @change="loadData">
          <option :value="null">Todas as filiais</option>
          <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>
        <button class="btn-primary" @click="openForm()">+ Novo Veículo</button>
      </div>
    </div>

    <AppTable 
      :data="veiculos" 
      :columns="columns" 
      :loading="loading"
      empty-message="Nenhum veículo encontrado"
    >
      <template #placa="{ value }">
        <span class="placa-cell">{{ value }}</span>
      </template>
      <template #frota="{ value }">
        <span class="frota-cell">#{{ value }}</span>
      </template>
      <template #tipo="{ value }">
        <span class="tipo-badge">{{ value }}</span>
      </template>
      <template #km_atual="{ value }">
        <span class="km-cell">{{ Number(value || 0).toLocaleString('pt-BR') }} km</span>
      </template>
      <template #actions="{ row }">
        <div class="row-actions">
          <button class="btn-icon" @click="openForm(row)" title="Editar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
          </button>
          <button class="btn-icon btn-danger" @click="confirmDelete(row)" title="Excluir">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </button>
        </div>
      </template>
    </AppTable>

    <!-- Modal Form -->
    <AppModal v-model="showModal" :title="editing ? 'Editar Veículo' : 'Novo Veículo'" max-width="500px">
      <form @submit.prevent="save" class="form-stacked">
        <div class="form-row">
          <div class="form-group">
            <label>Placa</label>
            <input v-model="form.placa" required placeholder="ABC-1234" />
          </div>
          <div class="form-group">
            <label>Frota</label>
            <input v-model="form.frota" placeholder="Número da frota" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Marca</label>
            <input v-model="form.marca" placeholder="Mercedes, Volvo..." />
          </div>
          <div class="form-group">
            <label>Modelo</label>
            <input v-model="form.modelo" placeholder="Actros, FH..." />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Tipo</label>
            <select v-model="form.tipo">
              <option value="simples">Simples</option>
              <option value="bitruck">Bi-Truck</option>
              <option value="bitrem">Bi-Trem</option>
              <option value="truck">Truck</option>
            </select>
          </div>
          <div class="form-group">
            <label>KM Atual</label>
            <input v-model.number="form.km_atual" type="number" placeholder="0" />
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
import { ref, reactive } from 'vue'
import AppTable from '../ui/AppTable.vue'
import AppModal from '../ui/AppModal.vue'
import * as api from '../../api/gestaoPneus.js'

const props = defineProps({
  filiais: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh'])

const loading = ref(false)
const veiculos = ref([])
const filialFilter = ref(null)
const showModal = ref(false)
const editing = ref(null)
const form = reactive({
  placa: '', frota: '', marca: '', modelo: '', tipo: 'simples', km_atual: 0, filial_id: null
})

const columns = [
  { key: 'placa', label: 'Placa' },
  { key: 'frota', label: 'Frota' },
  { key: 'marca', label: 'Marca' },
  { key: 'modelo', label: 'Modelo' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'km_atual', label: 'KM' }
]

async function loadData() {
  loading.value = true
  try {
    veiculos.value = await api.fetchVeiculos({ filial_id: filialFilter.value })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openForm(row = null) {
  editing.value = row?.id || null
  form.placa = row?.placa || ''
  form.frota = row?.frota || ''
  form.marca = row?.marca || ''
  form.modelo = row?.modelo || ''
  form.tipo = row?.tipo || 'simples'
  form.km_atual = row?.km_atual || 0
  form.filial_id = row?.filial_id || props.filiais[0]?.id
  showModal.value = true
}

async function save() {
  loading.value = true
  try {
    if (editing.value) {
      await api.updateVeiculo(editing.value, form)
    } else {
      await api.createVeiculo(form)
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
  if (!confirm(`Excluir ${row.placa}?`)) return
  loading.value = true
  try {
    await api.deleteVeiculo(row.id)
    loadData()
  } catch (e) {
    alert(e.message)
  } finally {
    loading.value = false
  }
}

defineExpose({ loadData })
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
  cursor: pointer;
}

.placa-cell {
  font-weight: 600;
  color: #818cf8;
}

.frota-cell {
  color: rgba(255,255,255,0.6);
}

.tipo-badge {
  display: inline-block;
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.km-cell {
  font-family: monospace;
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

.form-group input:focus, .form-group select:focus {
  outline: none;
  border-color: #818cf8;
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

.btn-primary:hover {
  background: #818cf8;
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