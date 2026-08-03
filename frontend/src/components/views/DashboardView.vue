<template>
  <section class="dash-root">

    <!-- Alertas críticos -->
    <div v-if="totalAlertas > 0" class="dash-alertas">
      <div class="alerta-header">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        <span class="alerta-titulo">{{ totalAlertas }} pneu{{ totalAlertas > 1 ? 's' : '' }} requer{{ totalAlertas > 1 ? 'em' : '' }} atenção imediata</span>
        <button class="alerta-toggle" @click="alertasAbertos = !alertasAbertos">
          {{ alertasAbertos ? 'Recolher' : 'Expandir' }}
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :style="{ transform: alertasAbertos ? 'rotate(180deg)' : 'none', transition: 'transform 0.12s' }"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
      </div>

      <div v-if="alertasAbertos" class="alerta-detalhe">
        <div v-if="dash.alertas_sulco?.length" class="alerta-grupo">
          <p class="alerta-grupo-label">Sulco crítico · menor que 5 mm · em uso</p>
          <div class="alerta-lista">
            <span v-for="a in dash.alertas_sulco" :key="a.numero_fogo" class="alerta-chip chip-critico">
              {{ a.numero_fogo }} · {{ a.sulco_atual }}mm
              <span v-if="a.veiculo_placa" class="chip-sub">{{ a.veiculo_placa }}</span>
            </span>
          </div>
        </div>

        <div v-if="dash.alertas_vida?.length" class="alerta-grupo">
          <p class="alerta-grupo-label">Última vida · 4ª ou mais · ativos</p>
          <div class="alerta-lista">
            <span v-for="a in dash.alertas_vida" :key="a.numero_fogo" class="alerta-chip chip-alerta">
              {{ a.numero_fogo }} · {{ a.vida }}ª vida
              <span v-if="a.veiculo_placa" class="chip-sub">{{ a.veiculo_placa }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- KPI strip -->
    <div v-if="loading" class="kpi-strip kpi-skeleton">
      <div v-for="i in 5" :key="i" class="kpi-cell kpi-skel-cell"></div>
    </div>
    <div v-else class="kpi-strip">
      <div class="kpi-cell">
        <span class="kpi-lbl">Total de Pneus</span>
        <span class="kpi-val">{{ dash?.total_pneus ?? 0 }}</span>
      </div>
      <div class="kpi-cell">
        <span class="kpi-lbl">Em Uso</span>
        <span class="kpi-val">{{ dash?.em_uso ?? 0 }}</span>
      </div>
      <div class="kpi-cell">
        <span class="kpi-lbl">Em Estoque</span>
        <span class="kpi-val">{{ dash?.em_estoque ?? 0 }}</span>
      </div>
      <div class="kpi-cell">
        <span class="kpi-lbl">Reciclagem</span>
        <span class="kpi-val">{{ dash?.em_reciclagem ?? 0 }}</span>
      </div>
      <div class="kpi-cell kpi-cell-last">
        <span class="kpi-lbl">Patrimônio em Estoque</span>
        <span class="kpi-val">R$ {{ fmtN(dash?.valor_estoque ?? 0) }}</span>
      </div>
    </div>

    <!-- Distribuição por Status -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Distribuição por Status</span>
        <span class="panel-total">{{ dash?.total_pneus ?? 0 }} pneus</span>
      </div>
      <div class="dist-grid">
        <div class="dist-item">
          <div class="dist-row">
            <span class="dist-dot" style="background:#3b82f6"></span>
            <span class="dist-label">Em Uso</span>
            <span class="dist-pct">{{ pct(dash?.em_uso, dash?.total_pneus) }}%</span>
            <span class="dist-count">{{ dash?.em_uso ?? 0 }}</span>
          </div>
          <div class="bar-track"><div class="bar-fill" style="background:#3b82f6" :style="{ width: pct(dash?.em_uso, dash?.total_pneus) + '%' }"></div></div>
        </div>
        <div class="dist-item">
          <div class="dist-row">
            <span class="dist-dot" style="background:var(--status-ok)"></span>
            <span class="dist-label">Em Estoque</span>
            <span class="dist-pct">{{ pct(dash?.em_estoque, dash?.total_pneus) }}%</span>
            <span class="dist-count">{{ dash?.em_estoque ?? 0 }}</span>
          </div>
          <div class="bar-track"><div class="bar-fill" style="background:var(--status-ok)" :style="{ width: pct(dash?.em_estoque, dash?.total_pneus) + '%' }"></div></div>
        </div>
        <div class="dist-item">
          <div class="dist-row">
            <span class="dist-dot" style="background:var(--status-warn)"></span>
            <span class="dist-label">Reciclagem</span>
            <span class="dist-pct">{{ pct(dash?.em_reciclagem, dash?.total_pneus) }}%</span>
            <span class="dist-count">{{ dash?.em_reciclagem ?? 0 }}</span>
          </div>
          <div class="bar-track"><div class="bar-fill" style="background:var(--status-warn)" :style="{ width: pct(dash?.em_reciclagem, dash?.total_pneus) + '%' }"></div></div>
        </div>
        <div class="dist-item">
          <div class="dist-row">
            <span class="dist-dot" style="background:var(--status-critical)"></span>
            <span class="dist-label">Descarte</span>
            <span class="dist-pct">{{ pct(dash?.descartados, dash?.total_pneus) }}%</span>
            <span class="dist-count">{{ dash?.descartados ?? 0 }}</span>
          </div>
          <div class="bar-track"><div class="bar-fill" style="background:var(--status-critical)" :style="{ width: pct(dash?.descartados, dash?.total_pneus) + '%' }"></div></div>
        </div>
      </div>
    </div>

    <!-- Vida útil + Medidas -->
    <div class="dash-row-two">
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">Distribuição por Vida Útil</span>
        </div>
        <div class="chart-bars">
          <div class="bar-row" v-for="v in [1,2,3,4]" :key="v">
            <span class="bar-label">{{ v }}ª Vida</span>
            <div class="bar-track">
              <div class="bar-fill"
                :style="{ width: pct(vidaCount(v), dash?.total_pneus) + '%', background: v <= 2 ? '#3b82f6' : v === 3 ? 'var(--status-warn)' : 'var(--status-critical)' }">
              </div>
            </div>
            <span class="bar-count">{{ vidaCount(v) }}</span>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">Medidas Mais Usadas</span>
        </div>
        <div v-if="dash?.top_medidas?.length" class="chart-bars">
          <div class="bar-row" v-for="m in dash.top_medidas" :key="m.medida">
            <span class="bar-label bar-label-mono">{{ m.medida }}</span>
            <div class="bar-track">
              <div class="bar-fill" style="background:var(--ink-300)" :style="{ width: pct(m.total, dash.total_pneus) + '%' }"></div>
            </div>
            <span class="bar-count">{{ m.total }}</span>
          </div>
        </div>
        <p v-else class="chart-empty">Nenhum registro para os filtros aplicados.</p>
      </div>
    </div>

  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as api from '../../api/gestaoPneus.js'

const dash = ref(null)
const loading = ref(true)
const alertasAbertos = ref(true)

const totalAlertas = computed(() => {
  if (!dash.value) return 0
  return (dash.value.alertas_sulco?.length ?? 0) + (dash.value.alertas_vida?.length ?? 0)
})

onMounted(async () => {
  try {
    dash.value = await api.fetchGPDashboard()
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
</script>

<style scoped>
.dash-root {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* ── Alertas ─────────────────────────────────────────────── */
.dash-alertas {
  background: var(--status-warn-bg);
  border: 1px solid var(--status-warn);
  border-radius: 4px;
  overflow: hidden;
}

.alerta-header {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 12px;
  color: #7c4d00;
  font-size: 12px;
}
.alerta-header svg { flex-shrink: 0; color: var(--status-warn); }
.alerta-titulo { flex: 1; font-weight: 600; }

.alerta-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: 1px solid var(--status-warn);
  border-radius: 3px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
  color: #7c4d00;
  cursor: pointer;
}
.alerta-toggle:hover { background: rgba(199,134,26,0.12); }

.alerta-detalhe {
  border-top: 1px solid var(--status-warn);
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alerta-grupo-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--ink-600);
  margin-bottom: 6px;
}

.alerta-lista { display: flex; flex-wrap: wrap; gap: 4px; }

.alerta-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.chip-critico { background: var(--status-critical-bg); color: var(--status-critical); border: 1px solid var(--status-critical); }
.chip-alerta  { background: var(--status-warn-bg); color: #7c4d00; border: 1px solid var(--status-warn); }
.chip-sub { font-weight: 400; opacity: 0.7; font-size: 10px; }

/* ── KPI strip ───────────────────────────────────────────── */
.kpi-strip {
  display: flex;
  background: var(--surface-0);
  border: 1px solid var(--ink-200);
  border-radius: 4px;
  overflow: hidden;
}

.kpi-cell {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px 14px;
  border-right: 1px solid var(--ink-200);
  gap: 3px;
}
.kpi-cell:last-child { border-right: none; }

.kpi-lbl {
  font-size: 10px;
  font-weight: 600;
  color: var(--ink-300);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  white-space: nowrap;
}
.kpi-val {
  font-size: 20px;
  font-weight: 600;
  color: var(--ink-900);
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
  letter-spacing: -0.01em;
}

/* Skeleton loading */
.kpi-skeleton { pointer-events: none; }
.kpi-skel-cell {
  background: linear-gradient(90deg, var(--surface-2) 25%, var(--ink-200) 50%, var(--surface-2) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
  height: 52px;
}
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

/* ── Panels (substituem chart-card) ─────────────────────── */
.panel {
  background: var(--surface-0);
  border: 1px solid var(--ink-200);
  border-radius: 4px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid var(--ink-200);
  background: var(--surface-1);
}
.panel-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--ink-600);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.panel-total { font-size: 11px; color: var(--ink-300); font-variant-numeric: tabular-nums; }

/* ── Distribuição por status ─────────────────────────────── */
.dist-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
}

.dist-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 10px 12px;
  border-right: 1px solid var(--ink-200);
}
.dist-item:last-child { border-right: none; }

.dist-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.dist-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.dist-label { font-size: 11px; color: var(--ink-600); flex: 1; }
.dist-pct { font-size: 11px; font-weight: 600; color: var(--ink-900); font-variant-numeric: tabular-nums; }
.dist-count { font-size: 10px; color: var(--ink-300); font-variant-numeric: tabular-nums; min-width: 28px; text-align: right; }

/* ── Barras ──────────────────────────────────────────────── */
.bar-track {
  height: 4px;
  background: var(--surface-2);
  border-radius: 2px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.15s ease;
}

/* ── Vida + Medidas ──────────────────────────────────────── */
.dash-row-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.chart-bars { display: flex; flex-direction: column; gap: 7px; padding: 10px 12px; }

.bar-row {
  display: grid;
  grid-template-columns: 90px 1fr 28px;
  align-items: center;
  gap: 8px;
}

.bar-label {
  font-size: 11px;
  color: var(--ink-600);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bar-label-mono { font-family: 'Courier New', monospace; font-size: 10px; }

.bar-count {
  font-size: 11px;
  font-weight: 600;
  color: var(--ink-900);
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.chart-empty { font-size: 12px; color: var(--ink-300); padding: 16px 12px; }
</style>
