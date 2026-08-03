<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2>Histórico de Movimentações</h2>
        <p class="sec-subtitle">Registro cronológico de todas as operações de pneus</p>
      </div>
      <div class="toolbar-right">
        <div class="search-box-pill">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input v-model="searchMov" placeholder="Buscar Placa ou N. Fogo..." />
        </div>
        <select v-model="filtroTipoMov" @change="loadMovs" class="filter-select">
          <option value="">Todos os tipos</option>
          <option value="entrada_estoque">Entrada Estoque</option>
          <option value="alocacao">Alocação</option>
          <option value="remocao">Remoção</option>
          <option value="descarte">Descarte</option>
          <option value="recebimento_sucata">Confirmação Sucata</option>
          <option value="transferencia">Transferência</option>
          <option value="recapagem">Recapagem</option>
          <option value="rodizio">Rodízio / Troca</option>
        </select>
      </div>
    </div>

    <div class="timeline-container" v-if="filteredMovs.length">
      <div v-for="m in filteredMovs" :key="m.id" class="timeline-item">
        <div class="tl-date">
          <span class="tl-day" v-if="m.data_hora">{{ new Date(m.data_hora).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) }}</span>
          <span class="tl-time" v-if="m.data_hora">{{ new Date(m.data_hora).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', hour12: false }) }}</span>
          <span class="tl-day" v-else>—</span>
        </div>

        <div class="tl-icon-box" :class="movClass(m.tipo)" v-html="movIcon(m.tipo)"></div>

        <div class="tl-content">
          <div class="tl-header">
            <span class="tl-type">{{ movLabel(m.tipo) }}</span>
            <span class="tl-pneu">Pneu: <strong>{{ m.numero_fogo || '—' }}</strong></span>
          </div>

          <div class="tl-details">
            <div v-if="m.veiculo_placa" class="tl-detail-item">
              <span class="tl-label">Veículo</span>
              <span class="tl-val">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:4px;vertical-align:middle"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><path d="M10 9h4"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
                {{ m.veiculo_placa }}
              </span>
            </div>
            <div v-if="m.posicao" class="tl-detail-item">
              <span class="tl-label">Posição</span>
              <span class="tl-val">{{ posLabel(m.posicao, m.veiculo_tipo) }}</span>
            </div>
            <div v-if="m.km_momento" class="tl-detail-item">
              <span class="tl-label">KM Momento</span>
              <span class="tl-val">{{ Number(m.km_momento).toLocaleString('pt-BR') }} km</span>
            </div>
          </div>

          <div v-if="m.observacao" class="tl-obs">
            <span class="obs-icon">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </span>
            {{ m.observacao }}
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:16px"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      <p>Nenhuma movimentação encontrada com os filtros atuais.</p>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchMovimentacoes } from '../../api/gestaoPneus.js'

const movs = ref([])
const filtroTipoMov = ref('')
const searchMov = ref('')

const filteredMovs = computed(() => {
  if (!searchMov.value) return movs.value
  const s = searchMov.value.toLowerCase()
  return movs.value.filter(m =>
    (m.numero_fogo && m.numero_fogo.toLowerCase().includes(s)) ||
    (m.veiculo_placa && m.veiculo_placa.toLowerCase().includes(s)) ||
    (m.observacao && m.observacao.toLowerCase().includes(s))
  )
})

async function loadMovs() {
  try { movs.value = await fetchMovimentacoes({ tipo: filtroTipoMov.value }) } catch(e) { console.error(e) }
}

const movLabel = (t) => ({ entrada_estoque: 'Entrada', alocacao: 'Alocação', remocao: 'Remoção', descarte: 'Descarte', transferencia: 'Transferência', recapagem: 'Recapagem', recebimento_sucata: 'Confirmação Sucata', rodizio: 'Rodízio / Troca' }[t] || t)
const movClass = (t) => ({ entrada_estoque: 'badge-green', alocacao: 'badge-blue', remocao: 'badge-yellow', descarte: 'badge-red', transferencia: 'badge-purple', recapagem: 'badge-yellow', recebimento_sucata: 'badge-green', rodizio: 'badge-purple' }[t] || '')
const movIcon = (t) => {
  const icons = {
    entrada_estoque: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m3 16 4 4 4-4"/><path d="M7 20V4"/><rect x="12" y="4" width="8" height="8" rx="1"/><path d="M12 18h8"/></svg>`,
    alocacao: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><path d="M10 9h4"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>`,
    remocao: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`,
    descarte: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>`,
    transferencia: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 11V7a5 5 0 0 1 10 0v4"/><path d="M11 21a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V13a2 2 0 0 0-2-2h-6a2 2 0 0 0-2 2v8Z"/></svg>`,
    recapagem: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v4"/><path d="m16.2 4.2 2.8 2.8"/><path d="M12 18v4"/><path d="m4.9 19.1 2.8-2.8"/><path d="M2 12h4"/><path d="m4.2 16.2 2.8-2.8"/><path d="M18 12h4"/><path d="m19.1 4.9-2.8 2.8"/></svg>`,
    recebimento_sucata: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`,
    rodizio: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>`
  }
  return icons[t] || `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`
}

const posLabel = (pos, type = null) => {
  if (!pos) return '—'
  const labels = { E1_ESQ: '1º Dianteiro LE', E1_DIR: '1º Dianteiro LD', E2_ESQ: '2º Dianteiro LE', E2_DIR: '2º Dianteiro LD', ESTEPE_1: 'Estepe 1', ESTEPE_2: 'Estepe 2' }
  if (labels[pos]) return labels[pos]
  const isBitruck = type === 'bitruck'
  if (pos.startsWith('E2')) return isBitruck ? (pos.includes('ESQ') ? '2º Dianteiro LE' : '2º Dianteiro LD') : 'Tração ' + (pos.includes('ESQ') ? 'LE ' : 'LD ') + (pos.includes('INT') ? 'Int' : 'Fora')
  if (pos.startsWith('E3')) return (isBitruck ? 'Tração ' : 'Truck ') + (pos.includes('ESQ') ? 'LE ' : 'LD ') + (pos.includes('INT') ? 'Int' : 'Fora')
  if (pos.startsWith('E4')) return 'Truck ' + (pos.includes('ESQ') ? 'LE ' : 'LD ') + (pos.includes('INT') ? 'Int' : 'Fora')
  return pos
}

onMounted(loadMovs)
</script>

<style scoped>
.search-box-pill {
  display: flex; align-items: center; gap: 8px;
  background: var(--surface-1); padding: 6px 14px;
  border-radius: 20px; border: 1px solid var(--ink-200); width: 280px;
}
.search-box-pill input { background: transparent; border: none; outline: none; font-size: 13px; width: 100%; color: var(--ink-900); }
.search-box-pill svg { color: var(--ink-300); flex-shrink: 0; }

.timeline-container { display: flex; flex-direction: column; gap: 2px; padding: 20px 0; max-width: 900px; margin: 0 auto; }
.timeline-item { display: flex; gap: 24px; padding: 16px; border-radius: 12px; transition: all 0.2s; position: relative; }
.timeline-item:hover { background: var(--surface-1); }
.timeline-item::before { content: ''; position: absolute; left: 95px; top: 0; bottom: 0; width: 2px; background: var(--ink-200); z-index: 1; }
.timeline-item:first-child::before { top: 20px; }
.timeline-item:last-child::before { bottom: 20px; }

.tl-date { width: 60px; display: flex; flex-direction: column; align-items: flex-end; flex-shrink: 0; }
.tl-day { font-size: 14px; font-weight: 800; color: var(--ink-900); }
.tl-time { font-size: 11px; color: var(--ink-300); font-weight: 600; }

.tl-icon-box {
  width: 42px; height: 42px; border-radius: 50%; background: var(--surface-0);
  border: 2px solid var(--ink-200); display: flex; align-items: center; justify-content: center;
  z-index: 2; position: relative; flex-shrink: 0; box-shadow: var(--shadow-sm);
}

.tl-content { flex: 1; background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: 12px; padding: 16px; box-shadow: var(--shadow-sm); }
.tl-header { display: flex; justify-content: space-between; margin-bottom: 12px; align-items: center; }
.tl-type { font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--ink-900); }
.tl-pneu { font-size: 13px; color: var(--ink-600); }

.tl-details { display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 12px; }
.tl-detail-item { display: flex; flex-direction: column; gap: 2px; }
.tl-label { font-size: 10px; font-weight: 700; color: var(--ink-300); text-transform: uppercase; }
.tl-val { font-size: 13px; font-weight: 600; color: var(--ink-900); display: flex; align-items: center; }

.tl-obs { background: var(--surface-1); padding: 10px 14px; border-radius: 8px; font-size: 12px; color: var(--ink-600); display: flex; align-items: center; gap: 8px; font-style: italic; }
.obs-icon { font-style: normal; }
</style>
