<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <h2>Filiais</h2>
      <button class="btn-primary" @click="openForm()">+ Nova Filial</button>
    </div>

    <AppTable 
      :data="filiais" 
      :columns="columns" 
      :loading="loading"
      empty-message="Nenhuma filial encontrada"
    >
      <template #nome="{ value, row }">
        <span class="filial-name">{{ value }}</span>
        <span v-if="row.ativo === 0" class="badge badge-red">Inativa</span>
      </template>
      <template #estado="{ value }">
        <span class="estado-badge">{{ value }}</span>
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
    <AppModal v-model="showModal" :title="editing ? 'Editar Filial' : 'Nova Filial'" max-width="400px">
      <form @submit.prevent="save" class="form-stacked">
        <div class="form-group">
          <label>Nome</label>
          <input v-model="form.nome" required placeholder="Ex: GRITSCH - Matriz" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Cidade</label>
            <input v-model="form.cidade" placeholder="Cidade" />
          </div>
          <div class="form-group">
            <label>Estado</label>
            <input v-model="form.estado" placeholder="UF" maxlength="2" />
          </div>
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
const showModal = ref(false)
const editing = ref(null)
const form = reactive({ nome: '', cidade: '', estado: '' })

const columns = [
  { key: 'nome', label: 'Nome' },
  { key: 'cidade', label: 'Cidade' },
  { key: 'estado', label: 'UF', width: '80px' }
]

function openForm(row = null) {
  editing.value = row?.id || null
  form.nome = row?.nome || ''
  form.cidade = row?.cidade || ''
  form.estado = row?.estado || ''
  showModal.value = true
}

async function save() {
  loading.value = true
  try {
    if (editing.value) {
      await api.updateFilial(editing.value, form)
    } else {
      await api.createFilial(form)
    }
    showModal.value = false
    emit('refresh')
  } catch (e) {
    alert(e.message)
  } finally {
    loading.value = false
  }
}

async function confirmDelete(row) {
  if (!confirm(`Excluir ${row.nome}?`)) return
  loading.value = true
  try {
    await api.deleteFilial(row.id)
    emit('refresh')
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

.filial-name {
  font-weight: 500;
}

.estado-badge {
  display: inline-block;
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  padding: 2px 8px;
  border-radius: 4px;
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

.form-group input {
  padding: 10px 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #818cf8;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 100px;
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