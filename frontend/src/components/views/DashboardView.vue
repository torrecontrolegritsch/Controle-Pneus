<template>
  <section class="gp-section dashboard-section">
    <div class="dashboard-kpis">
      <div class="kpi-card">
        <div class="kpi-icon total">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle></svg>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ dash?.total_pneus || 0 }}</span>
          <span class="kpi-label">Total de Pneus</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon blue">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/></svg>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ dash?.em_uso || 0 }}</span>
          <span class="kpi-label">Em Uso</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon green">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H4"/><path d="M4 12v4a8 8 0 0 0 8 8h4a8 8 0 0 0 8-8v-4"/></svg>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ dash?.em_estoque || 0 }}</span>
          <span class="kpi-label">Em Estoque</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon red">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ dash?.descartados || 0 }}</span>
          <span class="kpi-label">Descartados</span>
        </div>
      </div>

      <div class="kpi-card kpi-wide">
        <div class="kpi-icon gold">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">R$ {{ fmtN(dash?.valor_estoque || 0) }}</span>
          <span class="kpi-label">Patrimônio em Pneus</span>
        </div>
      </div>
    </div>

    <div class="dashboard-charts">
      <div class="chart-card">
        <h3>Por Status</h3>
        <div class="chart-bars">
          <div class="bar-item">
            <span class="bar-label">Em Uso</span>
            <div class="bar-track"><div class="bar-fill blue" :style="{ width: pct(dash?.em_uso, dash?.total_pneus) + '%' }"></div></div>
            <span class="bar-value">{{ dash?.em_uso || 0 }}</span>
          </div>
          <div class="bar-item">
            <span class="bar-label">Estoque</span>
            <div class="bar-track"><div class="bar-fill green" :style="{ width: pct(dash?.em_estoque, dash?.total_pneus) + '%' }"></div></div>
            <span class="bar-value">{{ dash?.em_estoque || 0 }}</span>
          </div>
          <div class="bar-item">
            <span class="bar-label">Reciclagem</span>
            <div class="bar-track"><div class="bar-fill yellow" :style="{ width: pct(dash?.em_reciclagem, dash?.total_pneus) + '%' }"></div></div>
            <span class="bar-value">{{ dash?.em_reciclagem || 0 }}</span>
          </div>
          <div class="bar-item">
            <span class="bar-label">Descarte</span>
            <div class="bar-track"><div class="bar-fill red" :style="{ width: pct(dash?.descartados, dash?.total_pneus) + '%' }"></div></div>
            <span class="bar-value">{{ dash?.descartados || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <h3>Por Vida Útil</h3>
        <div class="chart-bars">
          <div class="bar-item" v-for="v in [1,2,3,4]" :key="v">
            <span class="bar-label">{{ v }}ª Vida</span>
            <div class="bar-track"><div class="bar-fill" :style="{ width: vidaPct(v) + '%' }"></div></div>
            <span class="bar-value">{{ vidaCount(v) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="dashboard-table">
      <h3>Últimas Movimentações</h3>
      <AppTable 
        :data="movimentacoes" 
        :columns="columns" 
        :loading="loading"
        empty-message="Nenhuma movimentação"
      >
        <template #tipo="{ value }">
          <span class="tipo-badge" :class="value">{{ value }}</span>
        </template>
        <template #created_at="{ value }">
          {{ formatDate(value) }}
        </template>
      </AppTable>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import AppTable from '../ui/AppTable.vue'
import * as api from '../../api/gestaoPneus.js'

const dash = ref(null)
const movimentacoes = ref([])
const loading = ref(true)

const columns = [
  { key: 'tipo', label: 'Tipo' },
  { key: 'numero_fogo', label: 'Pneu' },
  { key: 'created_at', label: 'Data' }
]

onMounted(async () => {
  try {
    dash.value = await api.fetchGPDashboard()
    movimentacoes.value = await api.fetchMovimentacoes({ limit: 10 })
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
  if (!total) return 0
  return Math.round((val / total) * 100)
}

function vidaCount(vida) {
  return dash.value?.por_vida?.[vida] || 0
}

function vidaPct(vida) {
  return pct(vidaCount(vida), dash.value?.total_pneus)
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('pt-BR')
}
</script>

<style scoped>
.dashboard-section {
  padding: 20px;
}

.dashboard-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  background: #1e1e3f;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-wide {
  grid-column: span 2;
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
}

.kpi-icon.blue { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.kpi-icon.green { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.kpi-icon.red { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.kpi-icon.gold { background: rgba(234, 179, 8, 0.2); color: #eab308; }

.kpi-content {
  display: flex;
  flex-direction: column;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.kpi-label {
  font-size: 13px;
  color: rgba(255,255,255,0.6);
}

.dashboard-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.chart-card {
  background: #1e1e3f;
  border-radius: 12px;
  padding: 20px;
}

.chart-card h3 {
  margin: 0 0 16px;
  color: #fff;
  font-size: 16px;
}

.chart-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-item {
  display: grid;
  grid-template-columns: 80px 1fr 50px;
  align-items: center;
  gap: 12px;
}

.bar-label {
  color: rgba(255,255,255,0.7);
  font-size: 13px;
}

.bar-track {
  height: 8px;
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  background: #6366f1;
  transition: width 0.3s;
}

.bar-fill.blue { background: #3b82f6; }
.bar-fill.green { background: #22c55e; }
.bar-fill.red { background: #ef4444; }
.bar-fill.yellow { background: #eab308; }

.bar-value {
  color: #fff;
  font-weight: 600;
  text-align: right;
}

.dashboard-table {
  background: #1e1e3f;
  border-radius: 12px;
  padding: 20px;
}

.dashboard-table h3 {
  margin: 0 0 16px;
  color: #fff;
  font-size: 16px;
}

.tipo-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.tipo-badge.alocacao { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
.tipo-badge.remocao { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.tipo-badge.transferencia { background: rgba(168, 85, 247, 0.2); color: #a855f7; }
</style>