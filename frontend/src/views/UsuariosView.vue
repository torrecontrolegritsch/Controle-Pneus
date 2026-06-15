<template>
  <section class="usr-section">

    <!-- Toolbar -->
    <div class="usr-toolbar">
      <div>
        <h2 class="usr-title">Gerenciamento de Usuários</h2>
        <p class="usr-sub">Controle de acesso — defina quais telas cada usuário pode visualizar</p>
      </div>
      <button class="usr-btn-new" @click="abrirCriar">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Novo Usuário
      </button>
    </div>

    <!-- KPI cards -->
    <div class="usr-kpis">
      <div class="ukpi">
        <div class="ukpi-icon ukpi-blue">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div>
          <span class="ukpi-n">{{ usuarios.length }}</span>
          <span class="ukpi-l">Total de usuários</span>
        </div>
      </div>
      <div class="ukpi">
        <div class="ukpi-icon ukpi-green">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div>
          <span class="ukpi-n">{{ ativos }}</span>
          <span class="ukpi-l">Ativos</span>
        </div>
      </div>
      <div class="ukpi">
        <div class="ukpi-icon ukpi-purple">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>
        </div>
        <div>
          <span class="ukpi-n">{{ admins }}</span>
          <span class="ukpi-l">Administradores</span>
        </div>
      </div>
      <div class="ukpi">
        <div class="ukpi-icon ukpi-orange">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        </div>
        <div>
          <span class="ukpi-n">{{ inativos }}</span>
          <span class="ukpi-l">Inativos</span>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="carregando" class="usr-loading">
      <div class="usr-spinner"></div>
      <span>Carregando usuários...</span>
    </div>

    <!-- Tabela -->
    <div v-else class="usr-card">
      <div class="usr-card-header">
        <span class="usr-card-title">Lista de Usuários</span>
        <span class="usr-count-badge">{{ usuarios.length }} usuário{{ usuarios.length !== 1 ? 's' : '' }}</span>
      </div>

      <div class="usr-table-wrap">
        <table class="usr-table">
          <thead>
            <tr>
              <th>Usuário</th>
              <th>Perfil</th>
              <th>Filial</th>
              <th>Telas autorizadas</th>
              <th class="tc">Status</th>
              <th class="tc">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in usuarios" :key="u.id" class="usr-row">
              <td>
                <div class="usr-cell-user">
                  <div class="usr-avatar" :style="{ background: avatarColor(u) }">
                    {{ avatarLetra(u) }}
                  </div>
                  <div>
                    <div class="usr-nome">{{ u.nome || '—' }}</div>
                    <div class="usr-email">{{ u.email || '—' }}</div>
                  </div>
                </div>
              </td>
              <td>
                <span class="role-badge" :class="`role-${u.role || 'operador'}`">
                  {{ roleLabel(u.role) }}
                </span>
              </td>
              <td>
                <span class="filial-tag">{{ filialNome(u.filial_id) }}</span>
              </td>
              <td>
                <div class="telas-cell">
                  <span v-if="u.role === 'admin'" class="tela-chip tela-admin">Todas as telas</span>
                  <template v-else-if="u.telas && u.telas.length">
                    <span v-for="t in u.telas.slice(0, 3)" :key="t" class="tela-chip">{{ telaLabel(t) }}</span>
                    <span v-if="u.telas.length > 3" class="tela-mais">+{{ u.telas.length - 3 }}</span>
                  </template>
                  <span v-else class="tela-nenhuma">Sem acesso</span>
                </div>
              </td>
              <td class="tc">
                <span class="status-dot" :class="u.ativo !== false ? 'dot-ativo' : 'dot-inativo'">
                  {{ u.ativo !== false ? 'Ativo' : 'Inativo' }}
                </span>
              </td>
              <td class="tc">
                <div class="usr-actions">
                  <button class="act-btn act-edit" @click="abrirEditar(u)" title="Editar">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    Editar
                  </button>
                  <button class="act-btn act-del" @click="confirmarDeletar(u)" title="Excluir">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="!usuarios.length">
              <td colspan="6" class="usr-empty">
                <div class="usr-empty-inner">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                  <p>Nenhum usuário cadastrado</p>
                  <span>Clique em "+ Novo Usuário" para começar</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ===== MODAL ===== -->
    <Teleport to="body">
      <div v-if="showModal" class="usr-overlay" @click.self="fecharModal">
        <div class="usr-modal">

          <!-- Header do modal -->
          <div class="modal-hdr">
            <div class="modal-hdr-icon" :class="editando ? 'hdr-edit' : 'hdr-new'">
              <svg v-if="!editando" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </div>
            <div>
              <h3 class="modal-title">{{ editando ? 'Editar Usuário' : 'Novo Usuário' }}</h3>
              <p class="modal-sub">{{ editando ? 'Atualize os dados e permissões' : 'Preencha os dados para criar o acesso' }}</p>
            </div>
            <button class="modal-close" @click="fecharModal">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <!-- Corpo -->
          <div class="modal-body">

            <!-- Bloco: Dados pessoais -->
            <div class="form-block">
              <div class="form-block-title">
                <span class="fb-num">1</span> Dados do usuário
              </div>
              <div class="fb-row">
                <div class="fb-group">
                  <label class="fb-label">Nome completo <span class="req">*</span></label>
                  <input class="fb-input" v-model="form.nome" placeholder="Ex: João Silva" />
                </div>
                <div class="fb-group">
                  <label class="fb-label">E-mail <span class="req">*</span></label>
                  <input class="fb-input" v-model="form.email" type="email" placeholder="usuario@empresa.com" :disabled="!!editando" :class="{ 'fb-disabled': !!editando }" />
                </div>
              </div>
              <div class="fb-row">
                <div class="fb-group">
                  <label class="fb-label">{{ editando ? 'Nova senha (deixe em branco para não alterar)' : 'Senha *' }}</label>
                  <input class="fb-input" v-model="form.password" type="password" placeholder="••••••••" />
                </div>
                <div class="fb-group">
                  <label class="fb-label">Status</label>
                  <div class="fb-toggle-wrap">
                    <label class="fb-toggle">
                      <input type="checkbox" v-model="form.ativo" />
                      <span class="fb-slider"></span>
                    </label>
                    <span class="fb-toggle-label" :class="form.ativo ? 'tl-ativo' : 'tl-inativo'">
                      {{ form.ativo ? 'Usuário ativo' : 'Usuário inativo' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Bloco: Perfil e filial -->
            <div class="form-block">
              <div class="form-block-title">
                <span class="fb-num">2</span> Perfil e filial
              </div>
              <div class="fb-row">
                <div class="fb-group">
                  <label class="fb-label">Perfil de acesso</label>
                  <div class="role-selector">
                    <label
                      v-for="r in roles"
                      :key="r.value"
                      class="role-opt"
                      :class="{ 'role-opt-active': form.role === r.value, [`role-opt-${r.value}`]: form.role === r.value }"
                    >
                      <input type="radio" :value="r.value" v-model="form.role" style="display:none" />
                      <span class="role-opt-icon" v-html="r.icon"></span>
                      <div>
                        <span class="role-opt-name">{{ r.label }}</span>
                        <span class="role-opt-desc">{{ r.desc }}</span>
                      </div>
                    </label>
                  </div>
                </div>
                <div class="fb-group">
                  <label class="fb-label">Filial vinculada</label>
                  <select class="fb-select" v-model="form.filial_id">
                    <option :value="null">Nenhuma (acesso geral)</option>
                    <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
                  </select>
                  <p class="fb-hint">Define a filial padrão do operador</p>
                </div>
              </div>
            </div>

            <!-- Bloco: Telas -->
            <div class="form-block" v-if="form.role !== 'admin'">
              <div class="form-block-title">
                <span class="fb-num">3</span> Telas autorizadas
                <span class="telas-count">{{ form.telas.length }}/{{ TELAS.length }} selecionadas</span>
              </div>
              <div class="telas-grid">
                <label
                  v-for="t in TELAS"
                  :key="t.id"
                  class="tela-opt"
                  :class="{ 'tela-opt-on': form.telas.includes(t.id) }"
                >
                  <input type="checkbox" :value="t.id" v-model="form.telas" style="display:none" />
                  <span class="tela-opt-check">
                    <svg v-if="form.telas.includes(t.id)" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                  </span>
                  <span v-html="t.icon" class="tela-opt-icon"></span>
                  <span class="tela-opt-name">{{ t.label }}</span>
                </label>
              </div>
              <div class="telas-actions">
                <button type="button" class="ta-btn" @click="form.telas = TELAS.map(t => t.id)">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                  Selecionar tudo
                </button>
                <button type="button" class="ta-btn ta-clear" @click="form.telas = []">Limpar seleção</button>
              </div>
            </div>

            <div class="form-block admin-notice" v-else>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              Administradores têm acesso completo a todas as telas do sistema automaticamente.
            </div>

          </div>

          <!-- Footer do modal -->
          <div class="modal-footer">
            <button class="mf-cancel" @click="fecharModal">Cancelar</button>
            <button class="mf-save" @click="salvar" :disabled="salvando || !formValido">
              <div v-if="salvando" class="btn-spinner"></div>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
              {{ salvando ? 'Salvando...' : editando ? 'Salvar alterações' : 'Criar usuário' }}
            </button>
          </div>

        </div>
      </div>
    </Teleport>

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
  { id: 'estoque_central', label: 'Estoque Central', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>' },
  { id: 'alocacoes',      label: 'Alocações',      icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>' },
  { id: 'veiculos',       label: 'Frota',           icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>' },
  { id: 'filiais',        label: 'Unidades',        icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
  { id: 'estoque',        label: 'Estoque (Filial)', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8V21H3V8"/><path d="M1 3H23V8H1V3Z"/><path d="M10 12H14"/></svg>' },
  { id: 'financeiro',     label: 'Financeiro',      icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>' },
  { id: 'sucata',         label: 'Sucata',          icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>' },
  { id: 'recicladora',    label: 'Reciclagem',      icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 20V9c0-2 2-3 4-3s4 1 4 3v11"/><path d="M14 20V5c0-2 2-3 4-3s4 1 4 3v15"/><path d="M2 20h20"/></svg>' },
  { id: 'historico',      label: 'Histórico',       icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' },
  { id: 'relatorio_nf',   label: 'Relatório NF',    icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>' },
]

const roles = [
  { value: 'operador', label: 'Operador', desc: 'Acesso às telas autorizadas', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  { value: 'gerente',  label: 'Gerente',  desc: 'Acesso geral + usuários',    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
  { value: 'admin',    label: 'Admin',    desc: 'Controle total do sistema',   icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>' },
]

const usuarios = ref([])
const carregando = ref(false)
const showModal = ref(false)
const salvando = ref(false)
const editando = ref(null)

const formVazio = () => ({ nome: '', email: '', password: '', role: 'operador', filial_id: null, telas: [], ativo: true })
const form = ref(formVazio())

const ativos   = computed(() => usuarios.value.filter(u => u.ativo !== false).length)
const inativos = computed(() => usuarios.value.filter(u => u.ativo === false).length)
const admins   = computed(() => usuarios.value.filter(u => u.role === 'admin' || u.role === 'gerente').length)

const formValido = computed(() => {
  if (!form.value.nome.trim()) return false
  if (!editando.value && !form.value.email.trim()) return false
  if (!editando.value && !form.value.password) return false
  return true
})

async function carregar() {
  carregando.value = true
  try { usuarios.value = await fetchUsuarios() }
  catch (e) { props.showToast(e.message || 'Erro ao carregar usuários', 'error') }
  finally { carregando.value = false }
}

function abrirCriar() {
  editando.value = null
  form.value = formVazio()
  showModal.value = true
}

function abrirEditar(u) {
  editando.value = u
  form.value = { nome: u.nome || '', email: u.email || '', password: '', role: u.role || 'operador', filial_id: u.filial_id || null, telas: [...(u.telas || [])], ativo: u.ativo !== false }
  showModal.value = true
}

function fecharModal() { showModal.value = false; editando.value = null }

async function salvar() {
  salvando.value = true
  try {
    const telas = form.value.role === 'admin' ? [] : form.value.telas
    if (editando.value) {
      const payload = { nome: form.value.nome, role: form.value.role, filial_id: form.value.filial_id, telas, ativo: form.value.ativo }
      if (form.value.password) payload.password = form.value.password
      await updateUsuario(editando.value.id, payload)
      props.showToast('Usuário atualizado!')
    } else {
      const res = await createUsuario({ nome: form.value.nome, email: form.value.email, password: form.value.password, role: form.value.role, filial_id: form.value.filial_id, telas, ativo: form.value.ativo })
      const emailMsg = res?.email_enviado ? ' — E-mail de boas-vindas enviado!' : ''
      props.showToast(`Usuário criado com sucesso!${emailMsg}`)
    }
    fecharModal()
    await carregar()
  } catch (e) {
    props.showToast(e.message || 'Erro ao salvar', 'error')
  } finally { salvando.value = false }
}

async function confirmarDeletar(u) {
  if (!confirm(`Excluir "${u.nome || u.email}"?\nEsta ação não pode ser desfeita.`)) return
  try { await deleteUsuario(u.id); props.showToast('Usuário excluído!'); await carregar() }
  catch (e) { props.showToast(e.message || 'Erro ao excluir', 'error') }
}

const CORES = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444','#06b6d4','#84cc16']
function avatarColor(u) { return CORES[(u.nome || u.email || '').charCodeAt(0) % CORES.length] }
function avatarLetra(u) { return ((u.nome || u.email || '?')[0]).toUpperCase() }
function filialNome(id) { return id ? (props.filiais.find(f => f.id === id)?.nome || `#${id}`) : '—' }
function roleLabel(r) { return { admin: 'Admin', gerente: 'Gerente', operador: 'Operador' }[r] || 'Operador' }
function telaLabel(id) { return TELAS.find(t => t.id === id)?.label || id }

onMounted(carregar)
</script>

<style scoped>
/* ===================== SECTION ===================== */
.usr-section { padding: 0; display: flex; flex-direction: column; gap: 20px; }

/* ===================== TOOLBAR ===================== */
.usr-toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.usr-title { font-size: 20px; font-weight: 700; color: #1e293b; margin: 0 0 4px; }
.usr-sub   { font-size: 13px; color: #94a3b8; margin: 0; }
.usr-btn-new {
  display: flex; align-items: center; gap: 7px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white; border: none; border-radius: 10px;
  font-size: 13px; font-weight: 600; cursor: pointer;
  box-shadow: 0 2px 8px rgba(59,130,246,.35);
  transition: all .2s; white-space: nowrap;
}
.usr-btn-new:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(59,130,246,.45); }

/* ===================== KPI CARDS ===================== */
.usr-kpis { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; }
.ukpi {
  display: flex; align-items: center; gap: 14px;
  background: white; border: 1px solid #e2e8f0;
  border-radius: 12px; padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.ukpi-icon {
  width: 44px; height: 44px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.ukpi-blue   { background: #eff6ff; color: #3b82f6; }
.ukpi-green  { background: #f0fdf4; color: #16a34a; }
.ukpi-purple { background: #f5f3ff; color: #7c3aed; }
.ukpi-orange { background: #fff7ed; color: #ea580c; }
.ukpi-n { display: block; font-size: 24px; font-weight: 700; color: #1e293b; line-height: 1.1; }
.ukpi-l { display: block; font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: .5px; margin-top: 2px; }

/* ===================== LOADING ===================== */
.usr-loading { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 60px 0; color: #94a3b8; font-size: 14px; }
.usr-spinner { width: 24px; height: 24px; border: 3px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ===================== CARD / TABELA ===================== */
.usr-card { background: white; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.usr-card-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid #f1f5f9;
  background: #f8fafc;
}
.usr-card-title { font-size: 14px; font-weight: 600; color: #1e293b; }
.usr-count-badge { background: #e2e8f0; color: #64748b; font-size: 11px; font-weight: 600; border-radius: 20px; padding: 2px 10px; }
.usr-table-wrap { overflow-x: auto; }
.usr-table { width: 100%; border-collapse: collapse; }
.usr-table thead th {
  padding: 11px 16px; text-align: left;
  font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .5px;
  color: #94a3b8; background: #f8fafc; border-bottom: 1px solid #f1f5f9;
}
.usr-table .tc { text-align: center; }
.usr-row td { padding: 14px 16px; border-bottom: 1px solid #f8fafc; vertical-align: middle; }
.usr-row:last-child td { border-bottom: none; }
.usr-row:hover td { background: #fafbff; }

/* User cell */
.usr-cell-user { display: flex; align-items: center; gap: 10px; }
.usr-avatar {
  width: 36px; height: 36px; border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; color: white; flex-shrink: 0;
}
.usr-nome  { font-size: 13px; font-weight: 600; color: #1e293b; }
.usr-email { font-size: 11px; color: #94a3b8; margin-top: 1px; }

/* Role badges */
.role-badge { display: inline-block; font-size: 11px; font-weight: 600; border-radius: 6px; padding: 3px 10px; }
.role-admin    { background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }
.role-gerente  { background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe; }
.role-operador { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }

/* Filial tag */
.filial-tag { font-size: 12px; color: #64748b; }

/* Telas cell */
.telas-cell { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
.tela-chip { font-size: 10px; background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; border-radius: 4px; padding: 2px 7px; white-space: nowrap; }
.tela-admin { background: #f5f3ff; color: #7c3aed; border-color: #ddd6fe; }
.tela-mais  { font-size: 11px; color: #94a3b8; }
.tela-nenhuma { font-size: 12px; color: #ef4444; }

/* Status dot */
.status-dot { font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; }
.dot-ativo   { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.dot-inativo { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }

/* Action buttons */
.usr-actions { display: flex; align-items: center; justify-content: center; gap: 6px; }
.act-btn {
  display: flex; align-items: center; gap: 5px;
  border: 1px solid #e2e8f0; background: white; border-radius: 7px;
  font-size: 11px; font-weight: 500; color: #64748b;
  padding: 5px 10px; cursor: pointer; transition: all .15s;
}
.act-edit:hover { background: #eff6ff; border-color: #3b82f6; color: #2563eb; }
.act-del { padding: 5px 8px; }
.act-del:hover { background: #fef2f2; border-color: #ef4444; color: #dc2626; }

/* Empty state */
.usr-empty td { padding: 60px 20px !important; }
.usr-empty-inner { display: flex; flex-direction: column; align-items: center; gap: 8px; color: #94a3b8; }
.usr-empty-inner p { margin: 0; font-size: 15px; font-weight: 500; color: #64748b; }
.usr-empty-inner span { font-size: 12px; }

/* ===================== MODAL OVERLAY ===================== */
.usr-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(15, 23, 42, .55);
  backdrop-filter: blur(3px);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.usr-modal {
  background: white; border-radius: 16px;
  width: 680px; max-width: 100%;
  max-height: 90vh; overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,.25);
  display: flex; flex-direction: column;
}

/* Modal header */
.modal-hdr {
  display: flex; align-items: center; gap: 14px;
  padding: 20px 24px; border-bottom: 1px solid #f1f5f9;
  position: sticky; top: 0; background: white; z-index: 1; border-radius: 16px 16px 0 0;
}
.modal-hdr-icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.hdr-new  { background: #eff6ff; color: #3b82f6; }
.hdr-edit { background: #f5f3ff; color: #7c3aed; }
.modal-title { font-size: 16px; font-weight: 700; color: #1e293b; margin: 0 0 2px; }
.modal-sub { font-size: 12px; color: #94a3b8; margin: 0; }
.modal-close {
  margin-left: auto; width: 32px; height: 32px; border-radius: 8px;
  border: 1px solid #e2e8f0; background: white; cursor: pointer; color: #94a3b8;
  display: flex; align-items: center; justify-content: center; transition: all .15s;
  flex-shrink: 0;
}
.modal-close:hover { background: #fef2f2; color: #ef4444; border-color: #fecaca; }

/* Modal body */
.modal-body { padding: 20px 24px; display: flex; flex-direction: column; gap: 4px; }

/* Form blocks */
.form-block {
  border: 1px solid #f1f5f9; border-radius: 12px;
  padding: 16px; margin-bottom: 12px; background: #fafbff;
}
.form-block-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .6px; color: #64748b; margin-bottom: 14px;
}
.fb-num {
  width: 20px; height: 20px; border-radius: 50%;
  background: #3b82f6; color: white;
  font-size: 10px; font-weight: 700; display: flex; align-items: center; justify-content: center;
}
.telas-count { margin-left: auto; font-size: 11px; color: #3b82f6; background: #eff6ff; padding: 2px 8px; border-radius: 10px; text-transform: none; font-weight: 600; }
.fb-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.fb-group { display: flex; flex-direction: column; gap: 5px; }
.fb-label { font-size: 12px; font-weight: 600; color: #475569; }
.req { color: #ef4444; }
.fb-input, .fb-select {
  padding: 9px 12px; border: 1.5px solid #e2e8f0; border-radius: 8px;
  font-size: 13px; color: #1e293b; outline: none; background: white;
  transition: border-color .15s;
}
.fb-input:focus, .fb-select:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,.1); }
.fb-disabled { background: #f8fafc; color: #94a3b8; cursor: not-allowed; }
.fb-hint { font-size: 11px; color: #94a3b8; margin: 0; }

/* Toggle */
.fb-toggle-wrap { display: flex; align-items: center; gap: 10px; padding: 9px 0; }
.fb-toggle { position: relative; width: 40px; height: 22px; flex-shrink: 0; }
.fb-toggle input { display: none; }
.fb-slider {
  position: absolute; inset: 0; background: #cbd5e1; border-radius: 11px; cursor: pointer; transition: background .2s;
}
.fb-slider::after {
  content: ''; position: absolute; top: 3px; left: 3px;
  width: 16px; height: 16px; background: white; border-radius: 50%; transition: left .2s;
}
.fb-toggle input:checked + .fb-slider { background: #22c55e; }
.fb-toggle input:checked + .fb-slider::after { left: 21px; }
.fb-toggle-label { font-size: 13px; font-weight: 600; }
.tl-ativo   { color: #16a34a; }
.tl-inativo { color: #dc2626; }

/* Role selector */
.role-selector { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.role-opt {
  display: flex; align-items: center; gap: 8px;
  border: 1.5px solid #e2e8f0; border-radius: 9px; padding: 10px 12px;
  cursor: pointer; background: white; transition: all .15s;
}
.role-opt:hover { border-color: #94a3b8; }
.role-opt-active { border-color: #3b82f6 !important; background: #eff6ff; }
.role-opt-gerente { border-color: #8b5cf6 !important; background: #f5f3ff; }
.role-opt-admin   { border-color: #f59e0b !important; background: #fffbeb; }
.role-opt-icon { color: #94a3b8; flex-shrink: 0; }
.role-opt-active .role-opt-icon { color: #3b82f6; }
.role-opt-gerente .role-opt-icon { color: #8b5cf6; }
.role-opt-admin   .role-opt-icon { color: #f59e0b; }
.role-opt-name { display: block; font-size: 12px; font-weight: 600; color: #1e293b; }
.role-opt-desc { display: block; font-size: 10px; color: #94a3b8; margin-top: 1px; }

/* Telas grid */
.telas-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(155px, 1fr)); gap: 7px; margin-bottom: 10px; }
.tela-opt {
  display: flex; align-items: center; gap: 8px;
  border: 1.5px solid #e2e8f0; border-radius: 8px; padding: 9px 10px;
  cursor: pointer; background: white; transition: all .15s; font-size: 12px; color: #475569;
}
.tela-opt:hover { border-color: #3b82f6; }
.tela-opt-on { border-color: #3b82f6; background: #eff6ff; color: #2563eb; }
.tela-opt-check {
  width: 16px; height: 16px; border-radius: 4px; flex-shrink: 0;
  border: 1.5px solid #e2e8f0; display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.tela-opt-on .tela-opt-check { background: #3b82f6; border-color: #3b82f6; }
.tela-opt-icon { color: #94a3b8; flex-shrink: 0; }
.tela-opt-on .tela-opt-icon { color: #3b82f6; }
.tela-opt-name { font-size: 12px; }

.telas-actions { display: flex; gap: 10px; }
.ta-btn {
  display: flex; align-items: center; gap: 5px;
  background: #eff6ff; color: #3b82f6; border: 1px solid #bfdbfe;
  border-radius: 7px; padding: 5px 12px; font-size: 11px; font-weight: 600; cursor: pointer; transition: all .15s;
}
.ta-btn:hover { background: #dbeafe; }
.ta-clear { background: white; color: #94a3b8; border-color: #e2e8f0; }
.ta-clear:hover { background: #fef2f2; color: #ef4444; border-color: #fecaca; }

.admin-notice {
  display: flex; align-items: center; gap: 10px;
  font-size: 13px; color: #3b82f6; background: #eff6ff !important; border-color: #bfdbfe !important;
}

/* Modal footer */
.modal-footer {
  display: flex; align-items: center; justify-content: flex-end; gap: 10px;
  padding: 16px 24px; border-top: 1px solid #f1f5f9;
  position: sticky; bottom: 0; background: white; border-radius: 0 0 16px 16px;
}
.mf-cancel {
  padding: 9px 20px; border: 1.5px solid #e2e8f0; background: white;
  border-radius: 9px; font-size: 13px; font-weight: 500; color: #64748b; cursor: pointer; transition: all .15s;
}
.mf-cancel:hover { background: #f8fafc; }
.mf-save {
  display: flex; align-items: center; gap: 7px;
  padding: 9px 22px; background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white; border: none; border-radius: 9px;
  font-size: 13px; font-weight: 600; cursor: pointer;
  box-shadow: 0 2px 8px rgba(59,130,246,.35); transition: all .2s;
}
.mf-save:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(59,130,246,.45); }
.mf-save:disabled { opacity: .55; cursor: not-allowed; transform: none; }
.btn-spinner { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,.35); border-top-color: white; border-radius: 50%; animation: spin .7s linear infinite; }

@media (max-width: 600px) {
  .fb-row { grid-template-columns: 1fr; }
  .role-selector { grid-template-columns: 1fr; }
  .telas-grid { grid-template-columns: 1fr 1fr; }
  .usr-kpis { grid-template-columns: 1fr 1fr; }
}
</style>
