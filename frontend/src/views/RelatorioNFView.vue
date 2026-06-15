<template>
  <section class="nfr-page">

    <!-- Hero de busca -->
    <div class="nfr-hero">
      <div class="nfr-hero-text">
        <h2 class="nfr-title">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          Rastreio por Nota Fiscal
        </h2>
        <p class="nfr-subtitle">Localize todos os pneus de uma NF, seus destinos e status atual na frota</p>
      </div>

      <div class="nfr-search-wrap">
        <div class="nfr-search-box" :class="{ focused: inputFocused, 'has-value': buscaNF }">
          <svg class="nfr-search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            v-model="buscaNF"
            class="nfr-input"
            placeholder="Digite o número da Nota Fiscal..."
            @keyup.enter="buscar"
            @focus="inputFocused = true"
            @blur="inputFocused = false"
          />
          <button
            v-if="buscaNF"
            class="nfr-clear"
            @click="buscaNF = ''; pneus = []; buscou = false"
            title="Limpar"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <button class="nfr-btn-buscar" @click="buscar" :disabled="!buscaNF.trim() || carregando">
          <svg v-if="!carregando" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <span class="nfr-spinner" v-else></span>
          {{ carregando ? 'Buscando...' : 'Buscar NF' }}
        </button>

        <button v-if="pneus.length" class="nfr-btn-csv" @click="exportarCSV">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Exportar CSV
        </button>
      </div>

      <p class="nfr-dica" v-if="!buscou && !carregando">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        Informe o número da NF para rastrear todos os pneus adquiridos — instalados, em estoque ou sucateados.
      </p>
    </div>

    <!-- Carregando -->
    <div v-if="carregando" class="nfr-loading">
      <div class="nfr-loading-ring"></div>
      <span>Consultando pneus da NF <strong>{{ buscaNF }}</strong>...</span>
    </div>

    <!-- Sem resultados -->
    <div v-else-if="buscou && !pneus.length" class="nfr-empty">
      <div class="nfr-empty-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
      </div>
      <h3>NF não encontrada</h3>
      <p>Nenhum pneu registrado com a NF <strong>{{ buscaNF }}</strong>.</p>
      <small>Verifique se o número foi informado corretamente no cadastro.</small>
    </div>

    <!-- Resultados -->
    <div v-else-if="pneus.length" class="nfr-results">

      <!-- Cabeçalho dos resultados -->
      <div class="nfr-results-header">
        <div class="nfr-results-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
          NF <strong>{{ buscaNF }}</strong> encontrada — {{ pneus.length }} pneus rastreados
        </div>
      </div>

      <!-- KPI cards -->
      <div class="nfr-kpis">
        <div class="nfr-kpi">
          <div class="nfr-kpi-icon nfr-kpi-gray">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
          </div>
          <div class="nfr-kpi-body">
            <span class="nfr-kpi-num">{{ pneus.length }}</span>
            <span class="nfr-kpi-lbl">Pneus na NF</span>
          </div>
        </div>
        <div class="nfr-kpi nfr-kpi-accent-green">
          <div class="nfr-kpi-icon nfr-kpi-green">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <div class="nfr-kpi-body">
            <span class="nfr-kpi-num">R$ {{ fmtN(valorTotal) }}</span>
            <span class="nfr-kpi-lbl">Valor Total NF</span>
          </div>
        </div>
        <div class="nfr-kpi nfr-kpi-accent-blue">
          <div class="nfr-kpi-icon nfr-kpi-blue">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <div class="nfr-kpi-body">
            <span class="nfr-kpi-num">{{ filiaisDestino.length }}</span>
            <span class="nfr-kpi-lbl">Filiais destino</span>
          </div>
        </div>
        <div class="nfr-kpi nfr-kpi-accent-purple">
          <div class="nfr-kpi-icon nfr-kpi-purple">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
          </div>
          <div class="nfr-kpi-body">
            <span class="nfr-kpi-num">{{ veiculosUsando.length }}</span>
            <span class="nfr-kpi-lbl">Veículos em uso</span>
          </div>
        </div>
        <div class="nfr-kpi nfr-kpi-accent-orange">
          <div class="nfr-kpi-icon nfr-kpi-orange">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8V21H3V8"/><path d="M1 3H23V8H1V3Z"/><path d="M10 12H14"/></svg>
          </div>
          <div class="nfr-kpi-body">
            <span class="nfr-kpi-num">{{ emEstoque }}</span>
            <span class="nfr-kpi-lbl">Em estoque</span>
          </div>
        </div>
      </div>

      <!-- Agrupado por filial -->
      <div class="nfr-por-filial">
        <div
          v-for="(grupo, filialNome) in porFilial"
          :key="filialNome"
          class="nfr-filial-bloco"
        >
          <div class="nfr-filial-header">
            <div class="nfr-filial-info">
              <div class="nfr-filial-avatar">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
              </div>
              <span class="nfr-filial-nome">{{ filialNome }}</span>
            </div>
            <div class="nfr-filial-meta">
              <span class="nfr-filial-badge">{{ grupo.length }} pneu{{ grupo.length !== 1 ? 's' : '' }}</span>
              <span class="nfr-filial-valor">R$ {{ fmtN(grupo.reduce((s,p) => s + parseFloat(p.valor||0), 0)) }}</span>
            </div>
          </div>

          <div class="nfr-table-wrap">
            <table class="nfr-table">
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
                <tr v-for="p in grupo" :key="p.id" class="nfr-row">
                  <td><span class="nfr-fogo">{{ p.numero_fogo }}</span></td>
                  <td>
                    <span class="nfr-marca">{{ p.marca }}</span>
                    <span class="nfr-modelo">{{ p.modelo }}</span>
                  </td>
                  <td><span class="nfr-medida">{{ p.medida }}</span></td>
                  <td class="tc"><span class="nfr-vida">{{ p.vida }}ª</span></td>
                  <td class="tr nfr-valor-cell">R$ {{ fmtN(p.valor) }}</td>
                  <td>
                    <span class="badge" :class="statusClass(p.status)">{{ statusLabel(p.status) }}</span>
                  </td>
                  <td>
                    <div v-if="p.veiculo_placa" class="nfr-veiculo">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/></svg>
                      <strong>{{ p.veiculo_placa }}</strong>
                      <span class="nfr-pos">{{ p.posicao || '?' }}</span>
                    </div>
                    <span v-else class="nfr-estoque-tag">
                      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8V21H3V8"/><path d="M1 3H23V8H1V3Z"/></svg>
                      Em estoque
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
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

const valorTotal = computed(() => pneus.value.reduce((s, p) => s + parseFloat(p.valor || 0), 0))
const filiaisDestino = computed(() => [...new Set(pneus.value.map(p => p.filial_nome).filter(Boolean))])
const veiculosUsando = computed(() => [...new Set(pneus.value.filter(p => p.veiculo_placa).map(p => p.veiculo_placa))])
const emEstoque = computed(() => pneus.value.filter(p => p.status === 'estoque').length)

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
  const header = ['NF', 'N. Fogo', 'Marca', 'Modelo', 'Medida', 'Vida', 'DOT', 'Valor', 'Status', 'Filial', 'Filial Origem', 'Veiculo', 'Posicao', 'Fornecedor']
  const rows = pneus.value.map(p => [
    buscaNF.value, p.numero_fogo || '', p.marca || '', p.modelo || '',
    p.medida || '', p.vida || '', p.dot || '',
    String(p.valor || 0).replace('.', ','), statusLabel(p.status),
    p.filial_nome || '', p.filial_origem_nome || '',
    p.veiculo_placa || '', p.posicao || '', p.fornecedor || '',
  ])
  const csv = [header, ...rows]
    .map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(sep))
    .join('\r\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `relatorio_nf_${buscaNF.value}_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.nfr-page { padding: 0; display: flex; flex-direction: column; gap: 20px; }

/* ── Hero ── */
.nfr-hero {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border-radius: 16px;
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.nfr-hero-text { margin-bottom: 4px; }

.nfr-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 6px;
}

.nfr-subtitle {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

.nfr-search-wrap {
  display: flex;
  gap: 10px;
  align-items: center;
}

.nfr-search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.08);
  border: 1.5px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  padding: 0 14px;
  transition: border-color .2s, background .2s;
}
.nfr-search-box.focused {
  border-color: #3b82f6;
  background: rgba(59,130,246,0.08);
}
.nfr-search-box.has-value { border-color: rgba(255,255,255,0.25); }

.nfr-search-icon { color: #64748b; flex-shrink: 0; }
.nfr-search-box.focused .nfr-search-icon { color: #3b82f6; }

.nfr-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #f1f5f9;
  font-size: 15px;
  padding: 13px 0;
  min-width: 0;
}
.nfr-input::placeholder { color: #475569; }

.nfr-clear {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  border-radius: 4px;
  transition: color .2s;
}
.nfr-clear:hover { color: #94a3b8; }

.nfr-btn-buscar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 13px 22px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background .2s, transform .1s;
}
.nfr-btn-buscar:hover:not(:disabled) { background: #2563eb; transform: translateY(-1px); }
.nfr-btn-buscar:disabled { opacity: .5; cursor: not-allowed; transform: none; }

.nfr-spinner {
  width: 15px; height: 15px;
  border: 2px solid rgba(255,255,255,.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .7s linear infinite;
}

.nfr-btn-csv {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 13px 18px;
  background: rgba(22,163,74,0.15);
  color: #4ade80;
  border: 1.5px solid rgba(22,163,74,0.3);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all .2s;
}
.nfr-btn-csv:hover { background: rgba(22,163,74,0.25); border-color: #4ade80; }

.nfr-dica {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #475569;
  margin: 0;
}

/* ── Loading ── */
.nfr-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 60px 20px;
  color: #64748b;
  font-size: 14px;
}
.nfr-loading-ring {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin .8s linear infinite;
}

/* ── Empty ── */
.nfr-empty {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  text-align: center;
  padding: 64px 40px;
}
.nfr-empty-icon {
  width: 72px; height: 72px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 20px;
  color: #94a3b8;
}
.nfr-empty h3 { font-size: 17px; font-weight: 600; color: #1e293b; margin: 0 0 8px; }
.nfr-empty p { font-size: 14px; color: #64748b; margin: 0 0 6px; }
.nfr-empty small { font-size: 12px; color: #94a3b8; }

/* ── Results ── */
.nfr-results { display: flex; flex-direction: column; gap: 16px; }

.nfr-results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nfr-results-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #22c55e;
  font-weight: 600;
  background: rgba(34,197,94,0.08);
  border: 1px solid rgba(34,197,94,0.2);
  padding: 6px 14px;
  border-radius: 8px;
}

/* ── KPIs ── */
.nfr-kpis {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}
@media (max-width: 900px) { .nfr-kpis { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 600px) { .nfr-kpis { grid-template-columns: repeat(2, 1fr); } }

.nfr-kpi {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px 18px;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
  transition: box-shadow .2s;
}
.nfr-kpi:hover { box-shadow: 0 4px 12px rgba(0,0,0,.08); }

.nfr-kpi-accent-green { border-left: 3px solid #22c55e; }
.nfr-kpi-accent-blue  { border-left: 3px solid #3b82f6; }
.nfr-kpi-accent-purple{ border-left: 3px solid #8b5cf6; }
.nfr-kpi-accent-orange{ border-left: 3px solid #f97316; }

.nfr-kpi-icon {
  width: 38px; height: 38px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.nfr-kpi-gray   { background: #f1f5f9; color: #64748b; }
.nfr-kpi-green  { background: rgba(34,197,94,0.1); color: #16a34a; }
.nfr-kpi-blue   { background: rgba(59,130,246,0.1); color: #2563eb; }
.nfr-kpi-purple { background: rgba(139,92,246,0.1); color: #7c3aed; }
.nfr-kpi-orange { background: rgba(249,115,22,0.1); color: #ea580c; }

.nfr-kpi-body { display: flex; flex-direction: column; gap: 2px; }
.nfr-kpi-num {
  font-size: 19px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1;
}
.nfr-kpi-lbl {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: #94a3b8;
  font-weight: 500;
}

/* ── Por Filial ── */
.nfr-por-filial { display: flex; flex-direction: column; gap: 14px; }

.nfr-filial-bloco {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,.05);
}

.nfr-filial-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: linear-gradient(to right, #f8fafc, #fff);
  border-bottom: 1px solid #e2e8f0;
}

.nfr-filial-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.nfr-filial-avatar {
  width: 30px; height: 30px;
  background: #e2e8f0;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #64748b;
}
.nfr-filial-nome { font-size: 14px; font-weight: 600; color: #1e293b; }

.nfr-filial-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nfr-filial-badge {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
}
.nfr-filial-valor {
  font-size: 13px;
  font-weight: 700;
  color: #16a34a;
}

/* ── Tabela ── */
.nfr-table-wrap { overflow-x: auto; }
.nfr-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.nfr-table thead tr {
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}
.nfr-table th {
  padding: 10px 14px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .4px;
  color: #64748b;
  text-align: left;
}
.nfr-row {
  border-bottom: 1px solid #f1f5f9;
  transition: background .15s;
}
.nfr-row:last-child { border-bottom: none; }
.nfr-row:hover { background: #f8fafc; }
.nfr-table td { padding: 10px 14px; color: #334155; vertical-align: middle; }

.nfr-fogo { font-weight: 600; color: #1e293b; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.nfr-marca { font-weight: 600; color: #1e293b; display: block; }
.nfr-modelo { font-size: 11px; color: #94a3b8; display: block; }
.nfr-medida { font-size: 12px; font-family: monospace; color: #475569; }
.nfr-vida {
  display: inline-block;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  font-size: 11px;
  padding: 2px 7px;
  color: #475569;
  font-weight: 600;
}
.nfr-valor-cell { font-weight: 600; color: #15803d; font-size: 13px; }

.nfr-veiculo {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #374151;
}
.nfr-veiculo strong { font-size: 13px; }
.nfr-pos { font-size: 11px; color: #94a3b8; }

.nfr-estoque-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #94a3b8;
}

.tc { text-align: center; }
.tr { text-align: right; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
