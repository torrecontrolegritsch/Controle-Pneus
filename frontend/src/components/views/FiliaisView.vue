<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2>Filiais</h2>
        <p class="sec-subtitle">Cadastro e configuração das unidades operacionais</p>
      </div>
      <div class="toolbar-right">
        <button class="btn-primary" @click="openForm()">+ Nova Filial</button>
      </div>
    </div>

    <div class="table-responsive">
      <table class="gp-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Cidade</th>
            <th style="text-align:center;width:80px">UF</th>
            <th style="text-align:center;width:80px">Status</th>
            <th style="text-align:center;width:100px">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in filiais" :key="f.id" :class="{ 'row-disabled': f.ativo === 0 }">
            <td><strong>{{ f.nome }}</strong></td>
            <td>{{ f.cidade || '—' }}</td>
            <td style="text-align:center">
              <span v-if="f.estado" class="estado-badge">{{ f.estado }}</span>
              <span v-else style="color:var(--ink-300)">—</span>
            </td>
            <td style="text-align:center">
              <span class="badge" :class="f.ativo === 0 ? 'badge-red' : 'badge-green'">
                {{ f.ativo === 0 ? 'Inativa' : 'Ativa' }}
              </span>
            </td>
            <td>
              <div class="td-actions" style="justify-content:center">
                <button class="btn-sm" @click="openForm(f)" title="Editar">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  Editar
                </button>
                <button class="btn-sm btn-danger" @click="doDelete(f)" title="Excluir">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!filiais.length">
            <td colspan="5" style="text-align:center;padding:40px;color:var(--ink-300)">Nenhuma filial cadastrada</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box" style="width:420px">
        <h3>{{ editId ? 'Editar Filial' : 'Nova Filial' }}</h3>
        <div class="form-group">
          <label>Nome</label>
          <input v-model="form.nome" placeholder="Ex: GRITSCH — Matriz" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Cidade</label>
            <input v-model="form.cidade" placeholder="Cidade" />
          </div>
          <div class="form-group" style="max-width:100px">
            <label>UF</label>
            <input v-model="form.estado" placeholder="PR" maxlength="2" style="text-transform:uppercase" />
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showModal = false">Cancelar</button>
          <button class="btn-primary" :disabled="loading" @click="save">
            {{ editId ? 'Salvar' : 'Criar' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { updateFilial, createFilial, deleteFilial } from '../../api/gestaoPneus.js'

const props = defineProps({ filiais: { type: Array, default: () => [] } })
const emit = defineEmits(['refresh'])

const loading = ref(false)
const showModal = ref(false)
const editId = ref(null)
const form = ref({ nome: '', cidade: '', estado: '' })

function openForm(row = null) {
  editId.value = row?.id || null
  form.value = { nome: row?.nome || '', cidade: row?.cidade || '', estado: row?.estado || '' }
  showModal.value = true
}

async function save() {
  if (!form.value.nome) return
  loading.value = true
  try {
    if (editId.value) await updateFilial(editId.value, form.value)
    else await createFilial(form.value)
    showModal.value = false
    emit('refresh')
  } catch(e) { alert(e.message) } finally { loading.value = false }
}

async function doDelete(row) {
  if (!confirm(`Excluir a filial "${row.nome}"?`)) return
  loading.value = true
  try {
    await deleteFilial(row.id)
    emit('refresh')
  } catch(e) { alert(e.message) } finally { loading.value = false }
}
</script>

<style scoped>
.estado-badge { display: inline-block; background: var(--brand-100); color: var(--brand-900); padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; }
</style>
