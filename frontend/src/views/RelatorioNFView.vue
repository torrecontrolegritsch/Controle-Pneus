<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2 class="sec-title">Relatório por Nota Fiscal</h2>
        <p class="sec-subtitle">Rastreie todos os pneus de uma NF e seus destinos (frota / filial)</p>
      </div>
    </div>

    <!-- Barra de busca -->
    <div class="nf-search-card">
      <div class="nf-search-row">
        <input
          v-model="buscaNF"
          class="nf-input"
          placeholder="Ex: 12345 — Digite o número da Nota Fiscal..."
          @keyup.enter="buscar"
        />
        <button class="btn-primary" @click="buscar" :disabled="!buscaNF.trim() || carregando">
          <span v-if="carregando">Buscando...</span>
          <span v-else>🔍 Buscar NF</span>
        </button>
        <button v-if="pneus.length" class="btn-csv" @click="exportarCSV" title="Exportar relatório em CSV">
          ⬇ Exportar CSV
        </button>
      </div>
      <p class="nf-hint" v-if="!buscou">
        Informe o número da NF para ver quais pneus foram adquiridos, onde foram instalados e para quais filiais foram enviados.
      </p>
    </div>

    <!-- Spinner -->
    <div v-if="carregando" class="loading-spinner-wrap">
      <div class="loading-spinner"></div>
    </div>

    <!-- Sem resultados -->
    <div v-else-if="buscou && !pneus.length" class="empty-state">
      <span style="font-size:40px;">📋</span>
      <p>Nenhum pneu encontrado para a NF <strong>{{ buscaNF }}</strong>.</p>
      <small>Verifique se o número foi preenchido corretamente no cadastro dos pneus.</small>
    </div>

    <!-- Resultados -->
    <div v-else-if="pneus.length">

      <!-- Cards de resumo -->
      <div class="nf-resumo">
        <div class="nr-card">
          <span class="nr-num">{{ pneus.length }}</span>
          <span class="nr-label">Pneus na NF</span>
        </div>
        <div class="nr-card nr-green">
          <span class="nr-num">R$ {{ fmtN(valorTotal) }}</span>
          <span class="nr-label">Valor Total</span>
        </div>
        <div class="nr-card nr-blue">
          <span class="nr-num">{{ filiaisDestino.length }}</span>
          <span class="nr-label">Filiais destino</span>
        </div>
        <div class="nr-card nr-purple">
          <span class="nr-num">{{ veiculosUsando.length }}</span>
          <span class="nr-label">Veículos em uso</span>
        </div>
        <div class="nr-card nr-orange">
          <span class="nr-num">{{ emEstoque }}</span>
          <span class="nr-label">Em estoque</span>
        </div>
      </div>

      <!-- Agrupado por filial -->
      <div class="nf-por-filial">
        <div
          v-for="(grupo, filialNome) in porFilial"
          :key="filialNome"
          class="nf-filial-card"
        >
          <div class="nf-filial-header">
            <span class="nf-filial-nome">🏢 {{ filialNome }}</span>
            <span class="badge badge-blue">{{ grupo.length }} pneus</span>
          </div>
          <table class="gp-table nf-table-inner">
            <thead>
              <tr>
                <th>N. Fogo</th>
                <th>Marca / Modelo</th>
                <th>Medida</th>
                <th class="text-center">Vida</th>
                <th class="text-right">Valor</th>
                <th>Status</th>
                <th>Veículo / Posição</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in grupo" :key="p.id">
                <td><strong>{{ p.numero_fogo }}</strong></td>
                <td>{{ p.marca }} <span style="font-size:12px;color:var(--text3)">{{ p.modelo }}</span></td>
                <td>{{ p.medida }}</td>
                <td class="text-center">
                  <span class="vida-badge">{{ p.vida }}ª</span>
                </td>
                <td class="text-right">R$ {{ fmtN(p.valor) }}</td>
                <td>
                  <span class="badge" :class="statusClass(p.status)">{{ statusLabel(p.status) }}</span>
                </td>
                <td>
                  <span v-if="p.veiculo_placa">
                    <strong>{{ p.veiculo_placa }}</strong>
                    <span style="font-size:12px;color:var(--text3)"> — {{ p.posicao || '?' }}</span>
                  </span>
                  <span v-else class="text-muted">Em estoque</span>
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
  const m = { estoque: 'Estoque', em_uso: 'Em Uso', sucata: 'Sucata', reciclagem: 'Reciclagem', recapagem: 'Recapagem' }
  return m[s] || s || '—'
}

function statusClass(s) {
  const m = { estoque: 'badge-green', em_uso: 'badge-blue', sucata: 'badge-red', reciclagem: 'badge-yellow', recapagem: 'badge-purple' }
  return m[s] || ''
}

function fmtN(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function exportarCSV() {
  const sep = ';'
  const header = ['NF', 'N. Fogo', 'Marca', 'Modelo', 'Medida', 'Vida', 'DOT', 'Valor', 'Status', 'Filial', 'Filial Origem', 'Veiculo', 'Posicao', 'Fornecedor']
  const rows = pneus.value.map(p => [
    buscaNF.value,
    p.numero_fogo || '',
    p.marca || '',
    p.modelo || '',
    p.medida || '',
    p.vida || '',
    p.dot || '',
    String(p.valor || 0).replace('.', ','),
    statusLabel(p.status),
    p.filial_nome || '',
    p.filial_origem_nome || '',
    p.veiculo_placa || '',
    p.posicao || '',
    p.fornecedor || '',
  ])

  const csv = [header, ...rows]
    .map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(sep))
    .join('\r\n')

  const bom = '﻿'
  const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `relatorio_nf_${buscaNF.value}_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.nf-search-card {
  background: white;
  border: 1px solid var(--s2, #e2e8f0);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}

.nf-search-row {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.nf-input {
  flex: 1;
  min-width: 260px;
  padding: 10px 16px;
  border: 1.5px solid var(--s2, #e2e8f0);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text1, #1e293b);
  outline: none;
  transition: border-color .2s;
}
.nf-input:focus { border-color: var(--brand, #3b82f6); }

.btn-csv {
  padding: 9px 18px;
  background: #16a34a;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background .2s;
  white-space: nowrap;
}
.btn-csv:hover { background: #15803d; }

.nf-hint {
  margin-top: 10px;
  font-size: 13px;
  color: var(--text3, #94a3b8);
}

.nf-resumo {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.nr-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid var(--s2, #e2e8f0);
  border-radius: 10px;
  padding: 14px 20px;
  flex: 1;
  min-width: 130px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
  text-align: center;
}

.nr-card.nr-green  { border-top: 3px solid #22c55e; }
.nr-card.nr-blue   { border-top: 3px solid #3b82f6; }
.nr-card.nr-purple { border-top: 3px solid #8b5cf6; }
.nr-card.nr-orange { border-top: 3px solid #f97316; }

.nr-num {
  font-size: 22px;
  font-weight: 700;
  color: var(--text1, #1e293b);
  display: block;
  line-height: 1.2;
}

.nr-label {
  font-size: 11px;
  color: var(--text3, #94a3b8);
  text-transform: uppercase;
  letter-spacing: .5px;
  margin-top: 2px;
}

.nf-por-filial { display: flex; flex-direction: column; gap: 16px; }

.nf-filial-card {
  background: white;
  border: 1px solid var(--s2, #e2e8f0);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}

.nf-filial-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f8fafc;
  border-bottom: 1px solid var(--s2, #e2e8f0);
}

.nf-filial-nome { font-weight: 600; color: var(--text1, #1e293b); }

.nf-table-inner { margin: 0; }
.nf-table-inner td, .nf-table-inner th { padding: 8px 12px; }

.vida-badge {
  display: inline-block;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 11px;
  padding: 1px 6px;
  color: var(--text2, #475569);
}

.text-muted { color: var(--text3, #94a3b8); font-size: 12px; }
.text-center { text-align: center; }
.text-right  { text-align: right; }

.loading-spinner-wrap { display: flex; justify-content: center; padding: 60px 0; }
.loading-spinner {
  width: 36px; height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--brand, #3b82f6);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text3, #94a3b8);
}
.empty-state p { margin-top: 12px; font-size: 16px; }
</style>
