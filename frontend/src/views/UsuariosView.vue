<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2 class="sec-title">Gerenciamento de Usuários</h2>
        <p class="sec-subtitle">Crie usuários e defina quais telas cada um pode acessar</p>
      </div>
      <div class="toolbar-right">
        <button class="btn-primary" @click="abrirCriar">+ Novo Usuário</button>
      </div>
    </div>

    <!-- Spinner -->
    <div v-if="carregando" class="loading-spinner-wrap">
      <div class="loading-spinner"></div>
    </div>

    <!-- Tabela de usuários -->
    <div v-else class="table-card">
      <table class="gp-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>E-mail</th>
            <th>Perfil</th>
            <th>Filial</th>
            <th>Telas liberadas</th>
            <th class="text-center">Status</th>
            <th class="text-center">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in usuarios" :key="u.id">
            <td><strong>{{ u.nome || '—' }}</strong></td>
            <td><span class="text-muted">{{ u.email || '—' }}</span></td>
            <td>
              <span class="badge" :class="u.role === 'admin' ? 'badge-blue' : u.role === 'gerente' ? 'badge-purple' : 'badge-gray'">
                {{ roleLabel(u.role) }}
              </span>
            </td>
            <td>{{ filialNome(u.filial_id) }}</td>
            <td>
              <span v-if="u.role === 'admin'" class="text-muted" style="font-size:12px;">Todas (admin)</span>
              <span v-else-if="!u.telas || !u.telas.length" class="text-muted" style="font-size:12px;">Nenhuma</span>
              <span v-else>
                <span
                  v-for="t in (u.telas || []).slice(0, 3)"
                  :key="t"
                  class="badge badge-green"
                  style="margin-right:3px;margin-bottom:2px;font-size:10px;"
                >{{ telaLabel(t) }}</span>
                <span v-if="(u.telas || []).length > 3" class="badge badge-gray" style="font-size:10px;">+{{ u.telas.length - 3 }}</span>
              </span>
            </td>
            <td class="text-center">
              <span class="badge" :class="u.ativo !== false ? 'badge-green' : 'badge-red'">
                {{ u.ativo !== false ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="text-center">
              <div class="action-btns">
                <button class="btn-icon btn-edit" @click="abrirEditar(u)" title="Editar">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                </button>
                <button class="btn-icon btn-delete" @click="confirmarDeletar(u)" title="Excluir">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!usuarios.length">
            <td colspan="7" class="text-center" style="padding:40px;color:var(--text3,#94a3b8);">
              Nenhum usuário cadastrado
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MODAL CRIAR/EDITAR -->
    <div v-if="showModal" class="modal-overlay" @click.self="fecharModal">
      <div class="modal-box modal-usuarios">
        <h3>{{ editando ? 'Editar Usuário' : 'Novo Usuário' }}</h3>

        <div class="form-row">
          <div class="form-group">
            <label>Nome completo</label>
            <input v-model="form.nome" placeholder="Ex: João Silva" />
          </div>
          <div class="form-group">
            <label>E-mail</label>
            <input v-model="form.email" type="email" placeholder="usuario@empresa.com" :disabled="!!editando" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>{{ editando ? 'Nova Senha (deixe em branco para não alterar)' : 'Senha' }}</label>
            <input v-model="form.password" type="password" placeholder="••••••••" :required="!editando" />
          </div>
          <div class="form-group">
            <label>Perfil</label>
            <select v-model="form.role" class="select-premium">
              <option value="operador">Operador</option>
              <option value="gerente">Gerente</option>
              <option value="admin">Administrador</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Filial vinculada</label>
            <select v-model="form.filial_id" class="select-premium">
              <option :value="null">Nenhuma (acesso geral)</option>
              <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
            </select>
          </div>
          <div class="form-group" style="display:flex;align-items:center;gap:10px;padding-top:24px;">
            <label class="toggle-label">
              <input type="checkbox" v-model="form.ativo" />
              <span class="toggle-slider"></span>
              Usuário ativo
            </label>
          </div>
        </div>

        <!-- Telas autorizadas (só aparece para não-admin) -->
        <div v-if="form.role !== 'admin'" class="telas-section">
          <label class="telas-title">Telas autorizadas</label>
          <p class="telas-hint">Selecione quais telas este usuário pode acessar</p>
          <div class="telas-grid">
            <label v-for="t in TELAS" :key="t.id" class="tela-check">
              <input type="checkbox" :value="t.id" v-model="form.telas" />
              <span class="tela-nome">{{ t.label }}</span>
            </label>
          </div>
          <div class="telas-quick">
            <button type="button" class="btn-link" @click="form.telas = TELAS.map(t => t.id)">Selecionar tudo</button>
            <button type="button" class="btn-link" @click="form.telas = []">Limpar</button>
          </div>
        </div>
        <div v-else class="telas-section telas-admin-info">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          Administradores têm acesso a todas as telas automaticamente.
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="fecharModal">Cancelar</button>
          <button class="btn-primary" @click="salvar" :disabled="salvando || !formValido">
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchUsuarios, createUsuario, updateUsuario, deleteUsuario } from '../api/gestaoPneus.js'

const props = defineProps({
  filiais: { type: Array, default: () => [] },
  showToast: { type: Function, required: true },
})

const TELAS = [
  { id: 'estoque_central', label: 'Estoque Central' },
  { id: 'alocacoes', label: 'Alocações' },
  { id: 'veiculos', label: 'Frota' },
  { id: 'filiais', label: 'Unidades' },
  { id: 'estoque', label: 'Estoque (Filial)' },
  { id: 'financeiro', label: 'Financeiro' },
  { id: 'sucata', label: 'Sucata' },
  { id: 'recicladora', label: 'Reciclagem' },
  { id: 'historico', label: 'Histórico' },
  { id: 'relatorio_nf', label: 'Relatório NF' },
]

const usuarios = ref([])
const carregando = ref(false)
const showModal = ref(false)
const salvando = ref(false)
const editando = ref(null)

const formVazio = () => ({
  nome: '',
  email: '',
  password: '',
  role: 'operador',
  filial_id: null,
  telas: [],
  ativo: true,
})

const form = ref(formVazio())

const formValido = computed(() => {
  if (!form.value.nome.trim()) return false
  if (!editando.value && !form.value.email.trim()) return false
  if (!editando.value && !form.value.password) return false
  return true
})

async function carregar() {
  carregando.value = true
  try {
    usuarios.value = await fetchUsuarios()
  } catch (e) {
    props.showToast(e.message || 'Erro ao carregar usuários', 'error')
  } finally {
    carregando.value = false
  }
}

function abrirCriar() {
  editando.value = null
  form.value = formVazio()
  showModal.value = true
}

function abrirEditar(u) {
  editando.value = u
  form.value = {
    nome: u.nome || '',
    email: u.email || '',
    password: '',
    role: u.role || 'operador',
    filial_id: u.filial_id || null,
    telas: [...(u.telas || [])],
    ativo: u.ativo !== false,
  }
  showModal.value = true
}

function fecharModal() {
  showModal.value = false
  editando.value = null
}

async function salvar() {
  salvando.value = true
  try {
    if (editando.value) {
      const payload = {
        nome: form.value.nome,
        role: form.value.role,
        filial_id: form.value.filial_id,
        telas: form.value.role === 'admin' ? [] : form.value.telas,
        ativo: form.value.ativo,
      }
      if (form.value.password) payload.password = form.value.password
      await updateUsuario(editando.value.id, payload)
      props.showToast('Usuário atualizado com sucesso!')
    } else {
      await createUsuario({
        nome: form.value.nome,
        email: form.value.email,
        password: form.value.password,
        role: form.value.role,
        filial_id: form.value.filial_id,
        telas: form.value.role === 'admin' ? [] : form.value.telas,
        ativo: form.value.ativo,
      })
      props.showToast('Usuário criado com sucesso!')
    }
    fecharModal()
    await carregar()
  } catch (e) {
    props.showToast(e.message || 'Erro ao salvar usuário', 'error')
  } finally {
    salvando.value = false
  }
}

async function confirmarDeletar(u) {
  if (!confirm(`Excluir o usuário "${u.nome || u.email}"?\nEsta ação não pode ser desfeita.`)) return
  try {
    await deleteUsuario(u.id)
    props.showToast('Usuário excluído!')
    await carregar()
  } catch (e) {
    props.showToast(e.message || 'Erro ao excluir', 'error')
  }
}

function filialNome(id) {
  if (!id) return '—'
  return props.filiais.find(f => f.id === id)?.nome || `Filial #${id}`
}

function roleLabel(role) {
  return { admin: 'Admin', gerente: 'Gerente', operador: 'Operador' }[role] || role || 'Operador'
}

function telaLabel(id) {
  return TELAS.find(t => t.id === id)?.label || id
}

onMounted(carregar)
</script>

<style scoped>
.modal-usuarios {
  width: 680px;
  max-width: 96vw;
  max-height: 90vh;
  overflow-y: auto;
}

.telas-section {
  border: 1px solid var(--s2, #e2e8f0);
  border-radius: 10px;
  padding: 16px;
  margin-top: 4px;
  margin-bottom: 16px;
  background: #f8fafc;
}

.telas-title {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text1, #1e293b);
  margin-bottom: 4px;
}

.telas-hint {
  font-size: 12px;
  color: var(--text3, #94a3b8);
  margin: 0 0 12px;
}

.telas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 8px;
}

.tela-check {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text2, #475569);
  background: white;
  border: 1px solid var(--s2, #e2e8f0);
  border-radius: 6px;
  padding: 8px 10px;
  transition: border-color .15s;
}

.tela-check:hover { border-color: var(--brand, #3b82f6); }
.tela-check input { accent-color: var(--brand, #3b82f6); }
.tela-nome { font-size: 12px; }

.telas-quick {
  display: flex;
  gap: 12px;
  margin-top: 10px;
}

.btn-link {
  background: none;
  border: none;
  padding: 0;
  color: var(--brand, #3b82f6);
  font-size: 12px;
  cursor: pointer;
  text-decoration: underline;
}

.telas-admin-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #3b82f6;
  background: #eff6ff;
  border-color: #bfdbfe;
}

.action-btns { display: flex; gap: 6px; justify-content: center; }

.btn-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--s2, #e2e8f0);
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all .15s;
}

.btn-edit:hover { background: #eff6ff; border-color: #3b82f6; color: #3b82f6; }
.btn-delete:hover { background: #fef2f2; border-color: #ef4444; color: #ef4444; }

.toggle-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text2, #475569);
  user-select: none;
}

.toggle-label input[type="checkbox"] { display: none; }

.toggle-slider {
  width: 36px;
  height: 20px;
  background: #cbd5e1;
  border-radius: 10px;
  position: relative;
  transition: background .2s;
  flex-shrink: 0;
}

.toggle-slider::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 14px;
  height: 14px;
  background: white;
  border-radius: 50%;
  transition: left .2s;
}

.toggle-label input:checked + .toggle-slider { background: #22c55e; }
.toggle-label input:checked + .toggle-slider::after { left: 19px; }

.loading-spinner-wrap { display: flex; justify-content: center; padding: 60px 0; }
.loading-spinner {
  width: 36px; height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--brand, #3b82f6);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.text-muted { color: var(--text3, #94a3b8); font-size: 13px; }
.text-center { text-align: center; }
</style>
