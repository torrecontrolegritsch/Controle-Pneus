<template>
  <div class="sol-root">

    <!-- Header -->
    <div class="sol-header">
      <div>
        <h2 class="sol-title">Solicitações de Pneus</h2>
        <p class="sol-sub">{{ isAdmin ? 'Gerencie as solicitações de todas as filiais' : 'Solicite pneus e acompanhe o status' }}</p>
      </div>
      <button v-if="!isAdmin" class="btn-primary" @click="abrirForm">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Nova Solicitação
      </button>
    </div>

    <!-- Form nova solicitação (operador) -->
    <div v-if="showForm && !isAdmin" class="sol-form-card">
      <h3 class="sol-form-title">Nova Solicitação</h3>
      <div class="sol-form-grid">
        <div class="form-group">
          <label>Medida do Pneu</label>
          <input v-model="form.medida" placeholder="Ex: 295/80R22.5" list="medidas-list" />
          <datalist id="medidas-list">
            <option v-for="m in medidasSugeridas" :key="m" :value="m" />
          </datalist>
        </div>
        <div class="form-group">
          <label>Quantidade</label>
          <input type="number" v-model.number="form.quantidade" min="1" max="99" />
        </div>
        <div class="form-group">
          <label>Motivo</label>
          <select v-model="form.motivo">
            <option value="">— Selecionar —</option>
            <option value="desgaste">Desgaste / Sulco crítico</option>
            <option value="avaria">Avaria / Dano</option>
            <option value="novo_veiculo">Novo veículo</option>
            <option value="reposicao">Reposição de estoque</option>
            <option value="outro">Outro</option>
          </select>
        </div>
        <div class="form-group form-group-full">
          <label>Placa do Veículo <span class="label-optional">(opcional)</span></label>
          <input v-model="form.observacao" placeholder="Ex: ABC-1234 — informe o veículo que precisa do pneu" />
        </div>
      </div>
      <div class="sol-form-actions">
        <button class="btn-secondary" @click="fecharForm">Cancelar</button>
        <button
          class="btn-primary"
          :disabled="!form.medida || !form.motivo || salvando"
          @click="salvarSolicitacao"
        >
          {{ salvando ? 'Enviando...' : 'Enviar Solicitação' }}
        </button>
      </div>
    </div>

    <!-- Filtros -->
    <div class="sol-filters">
      <!-- Status tabs -->
      <div class="sol-status-tabs">
        <button
          v-for="s in statusOpcoes"
          :key="s.value"
          class="sol-status-btn"
          :class="{ active: filtroStatus === s.value }"
          @click="filtroStatus = s.value"
        >
          {{ s.label }}
          <span v-if="contadores[s.value]" class="sol-count" :class="s.countClass">{{ contadores[s.value] }}</span>
        </button>
      </div>

      <!-- Filial filter (admin) -->
      <select v-if="isAdmin" v-model="filtroFilial" class="filter-select">
        <option value="">Todas as filiais</option>
        <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="sol-loading">
      <div class="skeleton-list">
        <div v-for="i in 4" :key="i" class="skeleton-row"></div>
      </div>
    </div>

    <!-- Tabela -->
    <div v-else-if="solicitacoesFiltradas.length" class="sol-table-wrap">
      <table class="sol-table">
        <thead>
          <tr>
            <th>Data</th>
            <th v-if="isAdmin">Filial</th>
            <th>Medida</th>
            <th class="text-center">Qtd</th>
            <th>Motivo</th>
            <th v-if="isAdmin">Placa</th>
            <th v-if="isAdmin">Solicitante</th>
            <th>Status</th>
            <th v-if="!isAdmin">Resposta</th>
            <th v-if="isAdmin" class="text-right">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in solicitacoesFiltradas" :key="s.id">
            <td class="td-data">{{ fmtData(s.criado_em) }}</td>
            <td v-if="isAdmin" class="td-filial">{{ s.filial_nome || '—' }}</td>
            <td><span class="medida-tag-sol">{{ s.medida }}</span></td>
            <td class="text-center"><strong>{{ s.quantidade }}</strong></td>
            <td>{{ motivoLabel(s.motivo) }}</td>
            <td v-if="isAdmin" class="td-placa-sol">
              <span v-if="s.observacao" class="placa-badge">{{ s.observacao }}</span>
              <span v-else class="text-muted">—</span>
            </td>
            <td v-if="isAdmin" class="td-usuario">
              <span class="usuario-nome">{{ s.usuario_nome || '—' }}</span>
              <span class="usuario-email">{{ s.usuario_email || '' }}</span>
            </td>
            <td>
              <span class="sol-status-chip" :class="statusClass(s.status)">
                <span class="chip-dot"></span>{{ statusLabel(s.status) }}
              </span>
            </td>
            <td v-if="!isAdmin" class="td-nota">{{ s.observacao_admin || '—' }}</td>
            <td v-if="isAdmin" class="td-acoes">
              <div class="acoes-wrap">
                <button
                  v-if="s.status === 'pendente'"
                  class="acao-btn acao-analise"
                  title="Marcar em análise"
                  @click="atualizarStatus(s, 'em_analise', '')"
                >Em análise</button>
                <button
                  v-if="s.status !== 'aprovado'"
                  class="acao-btn acao-aprovar"
                  title="Aprovar"
                  @click="abrirNota(s, 'aprovado')"
                >Aprovar</button>
                <button
                  v-if="s.status !== 'recusado'"
                  class="acao-btn acao-recusar"
                  title="Recusar"
                  @click="abrirNota(s, 'recusado')"
                >Recusar</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state">
      <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/></svg>
      <p>{{ filtroStatus === 'todas' ? 'Nenhuma solicitação ainda.' : `Nenhuma solicitação com status "${statusLabel(filtroStatus)}".` }}</p>
    </div>

    <!-- Modal nota admin (Aprovar / Recusar) -->
    <div v-if="showNotaModal" class="modal-overlay" @click.self="showNotaModal = false">
      <div class="modal-box" style="max-width:420px;">
        <h3>{{ acaoNota === 'aprovado' ? 'Aprovar Solicitação' : 'Recusar Solicitação' }}</h3>
        <p class="nota-desc">
          Solicitação de <strong>{{ solSelecionada?.quantidade }}x {{ solSelecionada?.medida }}</strong>
          para <strong>{{ solSelecionada?.filial_nome }}</strong>.
        </p>
        <div class="form-group" style="margin-top:16px;">
          <label>Nota para o solicitante <span class="label-optional">(opcional)</span></label>
          <input v-model="notaAdmin" :placeholder="acaoNota === 'recusado' ? 'Ex: Sem estoque disponível neste momento.' : 'Ex: Pneu será enviado na próxima semana.'" />
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showNotaModal = false">Cancelar</button>
          <button
            class="btn-primary"
            :class="{ 'btn-danger': acaoNota === 'recusado' }"
            :disabled="atualizando"
            @click="confirmarNota"
          >
            {{ atualizando ? 'Salvando...' : (acaoNota === 'aprovado' ? 'Confirmar Aprovação' : 'Confirmar Recusa') }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import * as api from '../../api/gestaoPneus.js'

const props = defineProps({
  filiais: { type: Array, default: () => [] },
  user:    { type: Object, default: () => ({}) },
})

const isAdmin = computed(() => props.user?.role === 'admin' || props.user?.role === 'gerente')

// State
const solicitacoes = ref([])
const loading      = ref(false)
const salvando     = ref(false)
const atualizando  = ref(false)
const showForm     = ref(false)
const filtroStatus = ref('todas')
const filtroFilial = ref('')
const showNotaModal = ref(false)
const solSelecionada = ref(null)
const acaoNota     = ref('')
const notaAdmin    = ref('')

const form = ref({ medida: '', quantidade: 1, motivo: '', observacao: '' })

const statusOpcoes = [
  { value: 'todas',      label: 'Todas',      countClass: '' },
  { value: 'pendente',   label: 'Pendente',   countClass: 'count-pendente' },
  { value: 'em_analise', label: 'Em análise', countClass: 'count-analise' },
  { value: 'aprovado',   label: 'Aprovado',   countClass: 'count-aprovado' },
  { value: 'recusado',   label: 'Recusado',   countClass: 'count-recusado' },
]

const medidasSugeridas = [
  '295/80R22.5', '275/80R22.5', '315/80R22.5',
  '215/75R17.5', '235/75R17.5', '245/70R17.5',
  '275/70R22.5', '385/65R22.5', '1000R20',
]

// Computeds
const contadores = computed(() => {
  const c = { todas: solicitacoes.value.length, pendente: 0, em_analise: 0, aprovado: 0, recusado: 0 }
  for (const s of solicitacoes.value) { if (c[s.status] !== undefined) c[s.status]++ }
  return c
})

const solicitacoesFiltradas = computed(() => {
  let list = solicitacoes.value
  if (filtroStatus.value !== 'todas') list = list.filter(s => s.status === filtroStatus.value)
  if (filtroFilial.value)             list = list.filter(s => s.filial_id === Number(filtroFilial.value))
  return list
})

// Funções
async function carregarSolicitacoes() {
  loading.value = true
  try {
    solicitacoes.value = await api.fetchSolicitacoes()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function abrirForm() {
  form.value = { medida: '', quantidade: 1, motivo: '', observacao: '' }
  showForm.value = true
}
function fecharForm() { showForm.value = false }

async function salvarSolicitacao() {
  if (!form.value.medida || !form.value.motivo) return
  salvando.value = true
  try {
    await api.criarSolicitacao({
      medida:     form.value.medida.trim(),
      quantidade: form.value.quantidade,
      motivo:     form.value.motivo,
      observacao: form.value.observacao,
    })
    showForm.value = false
    await carregarSolicitacoes()
  } catch (e) {
    alert('Erro ao enviar: ' + (e.message || e))
  } finally {
    salvando.value = false
  }
}

function abrirNota(sol, acao) {
  solSelecionada.value = sol
  acaoNota.value = acao
  notaAdmin.value = ''
  showNotaModal.value = true
}

async function confirmarNota() {
  if (!solSelecionada.value) return
  await atualizarStatus(solSelecionada.value, acaoNota.value, notaAdmin.value)
  showNotaModal.value = false
}

async function atualizarStatus(sol, status, nota) {
  atualizando.value = true
  try {
    await api.atualizarSolicitacao(sol.id, { status, observacao_admin: nota || '' })
    await carregarSolicitacoes()
  } catch (e) {
    alert('Erro: ' + (e.message || e))
  } finally {
    atualizando.value = false
  }
}

// Helpers
function fmtData(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

function motivoLabel(m) {
  const map = { desgaste: 'Desgaste', avaria: 'Avaria', novo_veiculo: 'Novo veículo', reposicao: 'Reposição', outro: 'Outro' }
  return map[m] || m || '—'
}

function statusLabel(s) {
  const map = { pendente: 'Pendente', em_analise: 'Em análise', aprovado: 'Aprovado', recusado: 'Recusado', todas: 'Todas' }
  return map[s] || s
}

function statusClass(s) {
  return { 'chip-pendente': s === 'pendente', 'chip-analise': s === 'em_analise', 'chip-aprovado': s === 'aprovado', 'chip-recusado': s === 'recusado' }
}

onMounted(carregarSolicitacoes)
</script>

<style scoped>
.sol-root { padding: 0; }

.sol-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; gap: 16px; }
.sol-title  { font-size: 20px; font-weight: 800; color: #0f172a; margin: 0 0 4px; }
.sol-sub    { font-size: 13px; color: #64748b; margin: 0; }

/* Form card */
.sol-form-card  { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
.sol-form-title { font-size: 15px; font-weight: 700; color: #0f172a; margin: 0 0 16px; }
.sol-form-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-group-full { grid-column: 1 / -1; }
.form-group     { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: .04em; }
.form-group input,
.form-group select { padding: 9px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 13px; outline: none; background: #fff; }
.form-group input:focus,
.form-group select:focus { border-color: #3b82f6; }
.label-optional { font-size: 10px; font-weight: 400; color: #94a3b8; text-transform: none; letter-spacing: 0; }
.sol-form-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 16px; }

/* Filtros */
.sol-filters      { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.sol-status-tabs  { display: flex; gap: 4px; background: #f1f5f9; padding: 4px; border-radius: 10px; }
.sol-status-btn   { padding: 6px 14px; border: none; background: transparent; border-radius: 7px; font-size: 12px; font-weight: 600; color: #64748b; cursor: pointer; transition: all 120ms; display: flex; align-items: center; gap: 6px; white-space: nowrap; }
.sol-status-btn.active { background: #fff; color: #0f172a; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.sol-count        { font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 99px; background: #e2e8f0; color: #475569; }
.count-pendente   { background: #fef3c7; color: #b45309; }
.count-analise    { background: #dbeafe; color: #1d4ed8; }
.count-aprovado   { background: #dcfce7; color: #15803d; }
.count-recusado   { background: #fee2e2; color: #b91c1c; }

/* Tabela */
.sol-table-wrap { overflow-x: auto; border-radius: 12px; border: 1px solid #e2e8f0; }
.sol-table      { width: 100%; border-collapse: collapse; font-size: 13px; }
.sol-table th   { text-align: left; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; color: #94a3b8; padding: 10px 14px; border-bottom: 1px solid #e2e8f0; white-space: nowrap; background: #f8fafc; }
.sol-table td   { padding: 11px 14px; border-bottom: 1px solid #f1f5f9; color: #334155; vertical-align: middle; }
.sol-table tbody tr:last-child td { border-bottom: none; }
.sol-table tbody tr:hover td { background: #f8fafc; }
.text-center { text-align: center; }
.text-right  { text-align: right; }

.td-data    { font-size: 11px; color: #64748b; white-space: nowrap; }
.td-filial  { font-weight: 600; color: #0f172a; }
.td-nota    { font-size: 11px; color: #64748b; max-width: 180px; }
.td-usuario { max-width: 160px; }
.usuario-nome  { display: block; font-weight: 600; font-size: 12px; color: #0f172a; }
.usuario-email { display: block; font-size: 10px; color: #94a3b8; }
.td-acoes { white-space: nowrap; }
.td-placa-sol { white-space: nowrap; }
.placa-badge { font-family: monospace; font-size: 12px; font-weight: 700; background: #f1f5f9; color: #334155; padding: 2px 8px; border-radius: 6px; letter-spacing: .05em; }
.text-muted { color: #94a3b8; font-size: 12px; }

.medida-tag-sol { background: #e0f2fe; color: #0369a1; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 6px; white-space: nowrap; }

/* Status chip */
.sol-status-chip { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 99px; white-space: nowrap; }
.chip-dot        { width: 6px; height: 6px; border-radius: 99px; background: currentColor; flex-shrink: 0; }
.chip-pendente   { background: #fef3c7; color: #b45309; }
.chip-analise    { background: #dbeafe; color: #1d4ed8; }
.chip-aprovado   { background: #dcfce7; color: #15803d; }
.chip-recusado   { background: #fee2e2; color: #b91c1c; }

/* Ações admin */
.acoes-wrap  { display: flex; gap: 6px; justify-content: flex-end; flex-wrap: wrap; }
.acao-btn    { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; border: 1px solid; cursor: pointer; transition: all 120ms; white-space: nowrap; }
.acao-analise { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }
.acao-analise:hover { background: #dbeafe; }
.acao-aprovar { background: #f0fdf4; color: #15803d; border-color: #bbf7d0; }
.acao-aprovar:hover { background: #dcfce7; }
.acao-recusar { background: #fff1f2; color: #be123c; border-color: #fecdd3; }
.acao-recusar:hover { background: #ffe4e6; }

/* Loading skeleton */
.sol-loading   { padding: 8px 0; }
.skeleton-list { display: flex; flex-direction: column; gap: 8px; }
.skeleton-row  { height: 44px; background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%); background-size: 200% 100%; border-radius: 8px; animation: shimmer 1.4s infinite; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* Empty */
.empty-state { text-align: center; padding: 48px 20px; color: #94a3b8; font-size: 14px; display: flex; flex-direction: column; align-items: center; gap: 12px; border: 2px dashed #e2e8f0; border-radius: 12px; margin-top: 8px; }
.empty-state p { margin: 0; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,.55); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(3px); }
.modal-box     { background: #fff; border-radius: 16px; padding: 28px; width: 420px; max-width: 95vw; box-shadow: 0 20px 40px rgba(0,0,0,.2); }
.modal-box h3  { font-size: 18px; font-weight: 800; margin: 0 0 8px; color: #0f172a; }
.nota-desc     { font-size: 13px; color: #475569; margin: 0 0 4px; line-height: 1.5; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
.btn-danger    { background: #be123c !important; border-color: #9f1239 !important; }

/* Botões globais (inline para evitar conflito de scoped) */
.btn-primary   { padding: 9px 18px; background: #1d4ed8; color: #fff; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: background 120ms; }
.btn-primary:hover:not(:disabled) { background: #1e40af; }
.btn-primary:disabled { opacity: .5; cursor: not-allowed; }
.btn-secondary { padding: 9px 18px; background: #fff; color: #334155; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: background 120ms; }
.btn-secondary:hover { background: #f8fafc; }
.filter-select { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 13px; background: #fff; cursor: pointer; }
</style>
