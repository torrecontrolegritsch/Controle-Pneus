<template>
  <section class="gp-section">

    <!-- Toolbar padrão do sistema -->
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2 class="sec-title">Relatório por Nota Fiscal</h2>
        <p class="sec-subtitle">Rastreie todos os pneus de uma NF — destino, status e histórico de veículo</p>
      </div>
      <button v-if="pneus.length" class="nf-btn-export" @click="exportarCSV">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Exportar CSV
      </button>
    </div>

    <!-- Barra de busca -->
    <div class="nf-search-card">
      <div class="nf-search-row">
        <div class="nf-input-wrap" :class="{ focused: inputFocused }">
          <svg class="nf-input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            v-model="buscaNF"
            class="nf-input"
            placeholder="Digite o número da Nota Fiscal..."
            @keyup.enter="buscar"
            @focus="inputFocused = true"
            @blur="inputFocused = false"
          />
          <button v-if="buscaNF" class="nf-clear" @click="limpar">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <button class="nf-btn-buscar" @click="buscar" :disabled="!buscaNF.trim() || carregando">
          <svg v-if="!carregando" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <span v-else class="nf-spin"></span>
          {{ carregando ? 'Buscando...' : 'Buscar NF' }}
        </button>
      </div>
      <p class="nf-hint" v-if="!buscou">
        Informe o número da NF para ver todos os pneus adquiridos, onde foram instalados e seu status atual.
      </p>
    </div>

    <!-- Carregando -->
    <div v-if="carregando" class="nf-loading">
      <div class="nf-loading-ring"></div>
      <span>Buscando pneus da NF <strong>{{ buscaNF }}</strong>...</span>
    </div>

    <!-- Sem resultados -->
    <div v-else-if="buscou && !pneus.length" class="empty-state">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/></svg>
      <p>Nenhum pneu encontrado para a NF <strong>{{ buscaNF }}</strong>.</p>
      <small>Verifique se o número foi preenchido corretamente no cadastro dos pneus.</small>
    </div>

    <!-- Resultados -->
    <div v-else-if="pneus.length">

      <!-- KPI cards -->
      <div class="nf-kpis">
        <div class="nf-kpi">
          <div class="nf-kpi-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
          </div>
          <div>
            <span class="nf-kpi-num">{{ pneus.length }}</span>
            <span class="nf-kpi-lbl">Pneus na NF</span>
          </div>
        </div>
        <div class="nf-kpi nf-kpi-green">
          <div class="nf-kpi-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <div>
            <span class="nf-kpi-num">R$ {{ fmtN(valorTotal) }}</span>
            <span class="nf-kpi-lbl">Valor Total</span>
          </div>
        </div>
        <div class="nf-kpi nf-kpi-blue">
          <div class="nf-kpi-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <div>
            <span class="nf-kpi-num">{{ filiaisDestino.length }}</span>
            <span class="nf-kpi-lbl">Filiais destino</span>
          </div>
        </div>
        <div class="nf-kpi nf-kpi-purple">
          <div class="nf-kpi-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
          </div>
          <div>
            <span class="nf-kpi-num">{{ veiculosUsando.length }}</span>
            <span class="nf-kpi-lbl">Veículos em uso</span>
          </div>
        </div>
        <div class="nf-kpi nf-kpi-orange">
          <div class="nf-kpi-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8V21H3V8"/><path d="M1 3H23V8H1V3Z"/><path d="M10 12H14"/></svg>
          </div>
          <div>
            <span class="nf-kpi-num">{{ emEstoque }}</span>
            <span class="nf-kpi-lbl">Em estoque</span>
          </div>
        </div>
      </div>

      <!-- Agrupado por filial -->
      <div class="nf-por-filial">
        <div v-for="(grupo, filialNome) in porFilial" :key="filialNome" class="nf-filial-card">
          <div class="nf-filial-header">
            <span class="nf-filial-nome">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
              {{ filialNome }}
            </span>
            <div class="nf-filial-meta">
              <span class="badge badge-blue">{{ grupo.length }} pneu{{ grupo.length !== 1 ? 's' : '' }}</span>
              <span class="nf-filial-valor">R$ {{ fmtN(grupo.reduce((s,p) => s + parseFloat(p.valor||0), 0)) }}</span>
            </div>
          </div>

          <table class="gp-table nf-table">
            <thead>
              <tr>
                <th>N. Fogo</th>
                <th>Marca / Modelo</th>
                <th>Medida</th>
                <th class="tc">Vida</th>
                <th class="tr">Valor</th>
                <th>Status</th>
                <th>Veículo / Posição</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in grupo" :key="p.id">
                <td><strong>{{ p.numero_fogo }}</strong></td>
                <td>
                  {{ p.marca }}
                  <span class="nf-modelo">{{ p.modelo }}</span>
                </td>
                <td>{{ p.medida }}</td>
                <td class="tc"><span class="vida-badge">{{ p.vida }}ª</span></td>
                <td class="tr">R$ {{ fmtN(p.valor) }}</td>
                <td>
                  <span class="badge" :class="statusClass(p.status)">{{ statusLabel(p.status) }}</span>
                </td>
                <td>
                  <!-- Veículo atual (em uso) -->
                  <div v-if="p.veiculo_placa" class="nf-veiculo-atual">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
                    <strong>{{ p.veiculo_placa }}</strong>
                    <span class="nf-pos">— {{ p.posicao || '?' }}</span>
                  </div>
                  <!-- Último veículo (histórico) -->
                  <div v-else-if="p.ultimo_veiculo_placa" class="nf-veiculo-hist">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    <span>{{ p.ultimo_veiculo_placa }}</span>
                    <span class="nf-hist-tag">anterior</span>
                  </div>
                  <!-- Nunca instalado -->
                  <span v-else class="text-muted">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  fetchPneusPorNF: { type: Function, required: true },
})

const buscaNF = ref('')
const pneus = ref([])
const carregando = ref(false)
const buscou = ref(false)
const inputFocused = ref(false)

async function buscar() {
  const nf = buscaNF.value.trim()
  if (!nf) return
  carregando.value = true
  buscou.value = false
  pneus.value = []
  try {
    pneus.value = await props.fetchPneusPorNF(nf)
  } finally {
    carregando.value = false
    buscou.value = true
  }
}

function limpar() {
  buscaNF.value = ''
  pneus.value = []
  buscou.value = false
}

const valorTotal    = computed(() => pneus.value.reduce((s, p) => s + parseFloat(p.valor || 0), 0))
const filiaisDestino = computed(() => [...new Set(pneus.value.map(p => p.filial_nome).filter(Boolean))])
const veiculosUsando = computed(() => [...new Set(pneus.value.filter(p => p.veiculo_placa).map(p => p.veiculo_placa))])
const emEstoque     = computed(() => pneus.value.filter(p => p.status === 'estoque').length)

const porFilial = computed(() => {
  const mapa = {}
  for (const p of pneus.value) {
    const nome = p.filial_nome || 'Filial não informada'
    if (!mapa[nome]) mapa[nome] = []
    mapa[nome].push(p)
  }
  return mapa
})

function statusLabel(s) {
  return { estoque: 'Estoque', em_uso: 'Em Uso', sucata: 'Sucata', reciclagem: 'Reciclagem', recapagem: 'Recapagem' }[s] || s || '—'
}
function statusClass(s) {
  return { estoque: 'badge-green', em_uso: 'badge-blue', sucata: 'badge-red', reciclagem: 'badge-yellow', recapagem: 'badge-purple' }[s] || ''
}
function fmtN(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function exportarCSV() {
  const sep = ';'
  const header = ['NF','N. Fogo','Marca','Modelo','Medida','Vida','DOT','Valor','Status','Filial','Filial Origem','Veiculo Atual','Ultimo Veiculo','Posicao','Fornecedor']
  const rows = pneus.value.map(p => [
    buscaNF.value, p.numero_fogo||'', p.marca||'', p.modelo||'',
    p.medida||'', p.vida||'', p.dot||'',
    String(p.valor||0).replace('.',','), statusLabel(p.status),
    p.filial_nome||'', p.filial_origem_nome||'',
    p.veiculo_placa||'', p.ultimo_veiculo_placa||'',
    p.posicao||'', p.fornecedor||'',
  ])
  const csv = [header,...rows].map(r=>r.map(c=>`"${String(c).replace(/"/g,'""')}"`).join(sep)).join('\r\n')
  const blob = new Blob(['﻿'+csv],{type:'text/csv;charset=utf-8;'})
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `relatorio_nf_${buscaNF.value}_${new Date().toISOString().slice(0,10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
/* ── Search card ── */
.nf-search-card {
  background: white;
  border: 1px solid var(--s2, #e2e8f0);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}

.nf-search-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.nf-input-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1.5px solid var(--s2, #e2e8f0);
  border-radius: 8px;
  padding: 0 12px;
  background: #f8fafc;
  transition: border-color .2s, background .2s;
}
.nf-input-wrap.focused {
  border-color: var(--brand, #3b82f6);
  background: #fff;
}

.nf-input-icon { color: #94a3b8; flex-shrink: 0; }
.nf-input-wrap.focused .nf-input-icon { color: var(--brand, #3b82f6); }

.nf-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: var(--text1, #1e293b);
  padding: 13px 0;
}
.nf-input::placeholder { color: #94a3b8; }

.nf-clear {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 3px;
  display: flex;
  border-radius: 4px;
  transition: color .15s;
}
.nf-clear:hover { color: #64748b; }

.nf-spin {
  width: 13px; height: 13px;
  border: 2px solid rgba(255,255,255,.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .7s linear infinite;
  display: inline-block;
}

.nf-hint {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text3, #94a3b8);
}

/* ── Loading ── */
.nf-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 48px 20px;
  justify-content: center;
  color: #64748b;
  font-size: 14px;
}
.nf-loading-ring {
  width: 28px; height: 28px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--brand, #3b82f6);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}

/* ── KPIs ── */
.nf-kpis {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.nf-kpi {
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  border: 1px solid var(--s2, #e2e8f0);
  border-radius: 10px;
  padding: 14px 18px;
  flex: 1;
  min-width: 140px;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}

.nf-kpi-icon {
  width: 36px; height: 36px;
  background: #f1f5f9;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #64748b;
  flex-shrink: 0;
}
.nf-kpi-green .nf-kpi-icon  { background: #f0fdf4; color: #16a34a; }
.nf-kpi-blue  .nf-kpi-icon  { background: #eff6ff; color: #2563eb; }
.nf-kpi-purple .nf-kpi-icon { background: #f5f3ff; color: #7c3aed; }
.nf-kpi-orange .nf-kpi-icon { background: #fff7ed; color: #ea580c; }

.nf-kpi-green  { border-top: 3px solid #22c55e; }
.nf-kpi-blue   { border-top: 3px solid #3b82f6; }
.nf-kpi-purple { border-top: 3px solid #8b5cf6; }
.nf-kpi-orange { border-top: 3px solid #f97316; }

.nf-kpi-num {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--text1, #1e293b);
  line-height: 1.1;
}
.nf-kpi-lbl {
  display: block;
  font-size: 11px;
  color: var(--text3, #94a3b8);
  text-transform: uppercase;
  letter-spacing: .4px;
  margin-top: 2px;
}

/* ── Por filial ── */
.nf-por-filial { display: flex; flex-direction: column; gap: 14px; }

.nf-filial-card {
  background: white;
  border: 1px solid var(--s2, #e2e8f0);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}

.nf-filial-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f8fafc;
  border-bottom: 1px solid var(--s2, #e2e8f0);
}
.nf-filial-nome {
  display: flex;
  align-items: center;
  gap: 7px;
  font-weight: 600;
  color: var(--text1, #1e293b);
  font-size: 14px;
}
.nf-filial-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nf-filial-valor {
  font-size: 13px;
  font-weight: 700;
  color: #16a34a;
}

/* ── Tabela ── */
.nf-table { margin: 0; }
.nf-table td, .nf-table th { padding: 9px 12px; }

.nf-modelo { font-size: 12px; color: var(--text3, #94a3b8); margin-left: 4px; }

.vida-badge {
  display: inline-block;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 11px;
  padding: 2px 7px;
  color: var(--text2, #475569);
  font-weight: 600;
}

/* Veículo em uso */
.nf-veiculo-atual {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text1, #1e293b);
  font-size: 13px;
}
.nf-pos { font-size: 11px; color: var(--text3, #94a3b8); }

/* Último veículo (histórico) */
.nf-veiculo-hist {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: #64748b;
}
.nf-hist-tag {
  font-size: 10px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1px 6px;
  color: #94a3b8;
  font-weight: 500;
}

.tc { text-align: center; }
.tr { text-align: right; }
.text-muted { color: var(--text3, #94a3b8); font-size: 12px; }

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Botões profissionais ── */
.nf-btn-buscar {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 0 22px;
  height: 44px;
  background: linear-gradient(180deg, #c41230 0%, #a50f28 100%);
  color: #fff;
  border: 1px solid #8b0c22;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 700;
  letter-spacing: .2px;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 1px 3px rgba(196,18,48,.25), inset 0 1px 0 rgba(255,255,255,.12);
  transition: box-shadow .15s, transform .15s, opacity .15s;
}
.nf-btn-buscar:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(196,18,48,.35), inset 0 1px 0 rgba(255,255,255,.12);
  transform: translateY(-1px);
}
.nf-btn-buscar:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: inset 0 2px 4px rgba(0,0,0,.15);
}
.nf-btn-buscar:disabled {
  opacity: .5;
  cursor: not-allowed;
}

.nf-btn-export {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 0 18px;
  height: 38px;
  background: #fff;
  color: #374151;
  border: 1.5px solid #d1d5db;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0,0,0,.06);
  transition: background .15s, border-color .15s, box-shadow .15s, transform .15s;
}
.nf-btn-export:hover {
  background: #f9fafb;
  border-color: #9ca3af;
  box-shadow: 0 2px 6px rgba(0,0,0,.1);
  transform: translateY(-1px);
}
.nf-btn-export:active {
  transform: translateY(0);
  box-shadow: inset 0 1px 3px rgba(0,0,0,.08);
}
.nf-btn-export svg { color: #6b7280; }
</style>
