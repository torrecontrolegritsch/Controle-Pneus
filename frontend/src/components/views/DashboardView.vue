<template>
  <section class="dash-root">

    <!-- Alertas críticos -->
    <div v-if="totalAlertas > 0" class="dash-alertas">
      <div class="alerta-header">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        <strong>{{ totalAlertas }} pneu{{ totalAlertas > 1 ? 's' : '' }} requer{{ totalAlertas > 1 ? 'em' : '' }} atenção</strong>
        <button class="alerta-toggle" @click="alertasAbertos = !alertasAbertos">
          {{ alertasAbertos ? 'Ocultar' : 'Ver detalhes' }}
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" :style="{ transform: alertasAbertos ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
      </div>

      <div v-if="alertasAbertos" class="alerta-detalhe">
        <div v-if="dash.alertas_sulco?.length" class="alerta-grupo">
          <p class="alerta-grupo-label">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            Sulco crítico (menor que 5 mm) — em uso
          </p>
          <div class="alerta-lista">
            <span v-for="a in dash.alertas_sulco" :key="a.numero_fogo" class="alerta-chip vermelho">
              {{ a.numero_fogo }} · {{ a.sulco_atual }}mm
              <span v-if="a.veiculo_placa" class="chip-sub">{{ a.veiculo_placa }}</span>
            </span>
          </div>
        </div>

        <div v-if="dash.alertas_vida?.length" class="alerta-grupo">
          <p class="alerta-grupo-label">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            Última vida (4ª ou mais) — ativos
          </p>
          <div class="alerta-lista">
            <span v-for="a in dash.alertas_vida" :key="a.numero_fogo" class="alerta-chip laranja">
              {{ a.numero_fogo }} · {{ a.vida }}ª vida
              <span v-if="a.veiculo_placa" class="chip-sub">{{ a.veiculo_placa }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- KPIs -->
    <div v-if="loading" class="dash-kpis">
      <div v-for="i in 5" :key="i" class="kpi-card skeleton"></div>
    </div>
    <div v-else class="dash-kpis">
      <div class="kpi-card">
        <div class="kpi-icon icon-slate">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/></svg>
        </div>
        <div class="kpi-body">
          <span class="kpi-value">{{ dash?.total_pneus ?? 0 }}</span>
          <span class="kpi-label">Total de Pneus</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon icon-blue">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/></svg>
        </div>
        <div class="kpi-body">
          <span class="kpi-value">{{ dash?.em_uso ?? 0 }}</span>
          <span class="kpi-label">Em Uso</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon icon-green">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>
        </div>
        <div class="kpi-body">
          <span class="kpi-value">{{ dash?.em_estoque ?? 0 }}</span>
          <span class="kpi-label">Em Estoque</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon icon-amber">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
        </div>
        <div class="kpi-body">
          <span class="kpi-value">{{ dash?.em_reciclagem ?? 0 }}</span>
          <span class="kpi-label">Reciclagem</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon icon-gold">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
        </div>
        <div class="kpi-body">
          <span class="kpi-value">R$ {{ fmtN(dash?.valor_estoque ?? 0) }}</span>
          <span class="kpi-label">Patrimônio em Estoque</span>
        </div>
      </div>
    </div>

    <!-- Gráficos -->
    <div class="dash-charts">
      <div class="chart-card">
        <h3 class="chart-title">Distribuição por Status</h3>
        <div class="chart-bars">
          <div class="bar-row">
            <span class="bar-label">Em Uso</span>
            <div class="bar-track">
              <div class="bar-fill bar-blue" :style="{ width: pct(dash?.em_uso, dash?.total_pneus) + '%' }"></div>
            </div>
            <span class="bar-count">{{ dash?.em_uso ?? 0 }}</span>
          </div>
          <div class="bar-row">
            <span class="bar-label">Estoque</span>
            <div class="bar-track">
              <div class="bar-fill bar-green" :style="{ width: pct(dash?.em_estoque, dash?.total_pneus) + '%' }"></div>
            </div>
            <span class="bar-count">{{ dash?.em_estoque ?? 0 }}</span>
          </div>
          <div class="bar-row">
            <span class="bar-label">Reciclagem</span>
            <div class="bar-track">
              <div class="bar-fill bar-amber" :style="{ width: pct(dash?.em_reciclagem, dash?.total_pneus) + '%' }"></div>
            </div>
            <span class="bar-count">{{ dash?.em_reciclagem ?? 0 }}</span>
          </div>
          <div class="bar-row">
            <span class="bar-label">Descarte</span>
            <div class="bar-track">
              <div class="bar-fill bar-red" :style="{ width: pct(dash?.descartados, dash?.total_pneus) + '%' }"></div>
            </div>
            <span class="bar-count">{{ dash?.descartados ?? 0 }}</span>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <h3 class="chart-title">Distribuição por Vida Útil</h3>
        <div class="chart-bars">
          <div class="bar-row" v-for="v in [1,2,3,4]" :key="v">
            <span class="bar-label">{{ v }}ª Vida</span>
            <div class="bar-track">
              <div class="bar-fill" :class="v <= 2 ? 'bar-blue' : v === 3 ? 'bar-amber' : 'bar-red'"
                :style="{ width: pct(vidaCount(v), dash?.total_pneus) + '%' }"></div>
            </div>
            <span class="bar-count">{{ vidaCount(v) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Movimentações recentes -->
    <div class="dash-table-card">
      <h3 class="chart-title">Últimas Movimentações</h3>
      <div v-if="loading" class="table-loading">Carregando...</div>
      <table v-else-if="movimentacoes.length" class="mov-table">
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Pneu</th>
            <th>Veículo</th>
            <th>Data</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in movimentacoes" :key="m.id">
            <td><span class="tipo-badge" :class="m.tipo">{{ labelTipo(m.tipo) }}</span></td>
            <td class="cell-fogo">{{ m.numero_fogo || '—' }}</td>
            <td class="cell-placa">{{ m.veiculo_placa || '—' }}</td>
            <td class="cell-data">{{ fmtDate(m.created_at) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="table-empty">Nenhuma movimentação registrada.</p>
    </div>

  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as api from '../../api/gestaoPneus.js'

const dash = ref(null)
const movimentacoes = ref([])
const loading = ref(true)
const alertasAbertos = ref(true)

const totalAlertas = computed(() => {
  if (!dash.value) return 0
  return (dash.value.alertas_sulco?.length ?? 0) + (dash.value.alertas_vida?.length ?? 0)
})

onMounted(async () => {
  try {
    const [d, movs] = await Promise.all([
      api.fetchGPDashboard(),
      api.fetchMovimentacoes({ limit: 12 })
    ])
    dash.value = d
    movimentacoes.value = Array.isArray(movs) ? movs : []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

function fmtN(n) {
  return Number(n || 0).toLocaleString('pt-BR', { maximumFractionDigits: 0 })
}

function pct(val, total) {
  if (!total || !val) return 0
  return Math.max(2, Math.round((val / total) * 100))
}

function vidaCount(vida) {
  return dash.value?.por_vida?.[vida] ?? 0
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('pt-BR')
}

const TIPO_LABEL = {
  alocacao: 'Alocação', remocao: 'Remoção', transferencia: 'Transferência',
  rodizio: 'Rodízio', envio_recicladora: 'Reciclagem', criacao: 'Cadastro'
}
function labelTipo(t) {
  return TIPO_LABEL[t] || t
}
</script>

<style scoped>
.dash-root {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── Alertas ─────────────────────────────────────────────── */
.dash-alertas {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 10px;
  overflow: hidden;
}

.alerta-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #9a3412;
  font-size: 13px;
}

.alerta-header svg { flex-shrink: 0; }
.alerta-header strong { flex: 1; }

.alerta-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: 1px solid #fdba74;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
  color: #9a3412;
  cursor: pointer;
  white-space: nowrap;
}
.alerta-toggle:hover { background: #ffedd5; }

.alerta-detalhe {
  border-top: 1px solid #fed7aa;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alerta-grupo-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #7c3aed;
  margin-bottom: 7px;
}

.alerta-lista {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.alerta-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.alerta-chip.vermelho { background: #fee2e2; color: #991b1b; }
.alerta-chip.laranja  { background: #ffedd5; color: #9a3412; }
.chip-sub {
  font-weight: 400;
  opacity: 0.75;
  font-size: 11px;
}

/* ── KPIs ────────────────────────────────────────────────── */
.dash-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 14px;
}

.kpi-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.kpi-card.skeleton {
  height: 72px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

.kpi-icon {
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-slate { background: #f1f5f9; color: #475569; }
.icon-blue  { background: #dbeafe; color: #1d4ed8; }
.icon-green { background: #dcfce7; color: #15803d; }
.icon-amber { background: #fef3c7; color: #b45309; }
.icon-gold  { background: #fef9c3; color: #a16207; }

.kpi-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.kpi-value {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}
.kpi-label {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Gráficos ────────────────────────────────────────────── */
.dash-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}

.chart-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 18px 20px;
}

.chart-title {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin: 0 0 16px;
}

.chart-bars {
  display: flex;
  flex-direction: column;
  gap: 11px;
}

.bar-row {
  display: grid;
  grid-template-columns: 80px 1fr 36px;
  align-items: center;
  gap: 10px;
}

.bar-label {
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
}

.bar-track {
  height: 7px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
  background: #94a3b8;
}
.bar-blue  { background: #3b82f6; }
.bar-green { background: #22c55e; }
.bar-amber { background: #f59e0b; }
.bar-red   { background: #ef4444; }

.bar-count {
  font-size: 12px;
  font-weight: 600;
  color: #334155;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

/* ── Tabela de movimentações ─────────────────────────────── */
.dash-table-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 18px 20px;
}

.table-loading, .table-empty {
  font-size: 13px;
  color: #94a3b8;
  text-align: center;
  padding: 20px 0;
}

.mov-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.mov-table th {
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
  padding: 0 8px 10px;
  border-bottom: 1px solid #f1f5f9;
}
.mov-table td {
  padding: 9px 8px;
  border-bottom: 1px solid #f8fafc;
  color: #334155;
}
.mov-table tbody tr:last-child td { border-bottom: none; }
.mov-table tbody tr:hover td { background: #f8fafc; }

.cell-fogo  { font-weight: 600; font-variant-numeric: tabular-nums; }
.cell-placa { color: #64748b; }
.cell-data  { color: #94a3b8; white-space: nowrap; }

.tipo-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.tipo-badge.alocacao       { background: #dbeafe; color: #1d4ed8; }
.tipo-badge.remocao        { background: #fee2e2; color: #991b1b; }
.tipo-badge.transferencia  { background: #ede9fe; color: #6d28d9; }
.tipo-badge.rodizio        { background: #d1fae5; color: #065f46; }
.tipo-badge.envio_recicladora { background: #fef3c7; color: #92400e; }
.tipo-badge.criacao        { background: #f1f5f9; color: #475569; }
</style>
