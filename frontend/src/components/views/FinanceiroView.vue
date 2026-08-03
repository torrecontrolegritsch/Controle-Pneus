<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2>Retorno Financeiro</h2>
        <p class="sec-subtitle">Créditos por filial referente às carcaças recicladas no período</p>
      </div>
      <div class="toolbar-right">
        <input type="month" v-model="filtroMes" @change="loadFinanceiro" class="filter-select" />
        <select v-model="filtroFilial" @change="loadFinanceiro" class="filter-select">
          <option value="">Todas as Filiais</option>
          <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>
        <button v-if="relatorio.detalhes.length" class="btn-secondary" style="display:inline-flex;align-items:center;gap:6px;white-space:nowrap" @click="exportarCSV">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Exportar CSV
        </button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="fin-kpis">
      <div class="fin-kpi fin-kpi-green">
        <div class="fin-kpi-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <div>
          <span class="fin-kpi-num">{{ relatorio.total_geral.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}</span>
          <span class="fin-kpi-lbl">Total Arrecadado</span>
        </div>
      </div>
      <div class="fin-kpi">
        <div class="fin-kpi-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
        </div>
        <div>
          <span class="fin-kpi-num">{{ relatorio.detalhes.length }}</span>
          <span class="fin-kpi-lbl">Pneus Reciclados</span>
        </div>
      </div>
      <div class="fin-kpi fin-kpi-blue">
        <div class="fin-kpi-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <div>
          <span class="fin-kpi-num">{{ relatorio.detalhes.length ? (relatorio.total_geral / relatorio.detalhes.length).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : 'R$ 0,00' }}</span>
          <span class="fin-kpi-lbl">Média por Pneu</span>
        </div>
      </div>
      <div class="fin-kpi fin-kpi-purple">
        <div class="fin-kpi-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div>
          <span class="fin-kpi-num">{{ relatorio.resumo_filiais.length }}</span>
          <span class="fin-kpi-lbl">Filiais Participantes</span>
        </div>
      </div>
    </div>

    <div v-if="!relatorio.detalhes.length" class="empty-state">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:12px"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
      <p>Nenhum retorno encontrado para o período selecionado.</p>
      <small>Verifique se há lotes de reciclagem com valor informado neste mês.</small>
    </div>

    <div v-else class="fin-body">

      <!-- Retorno por Filial -->
      <div class="fin-box">
        <div class="fin-box-header">
          <span class="fin-box-title">Retorno por Filial</span>
          <span class="badge badge-green">{{ relatorio.resumo_filiais.length }} filial(is)</span>
        </div>
        <div class="table-responsive">
          <table class="gp-table fin-table">
            <colgroup><col style="width:45%"/><col style="width:18%"/><col style="width:20%"/><col style="width:17%"/></colgroup>
            <thead>
              <tr>
                <th style="text-align:left">Filial</th>
                <th style="text-align:center">Qtd Pneus</th>
                <th style="text-align:right">Valor p/ Receber</th>
                <th style="text-align:right">% do Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in relatorio.resumo_filiais" :key="r.nome">
                <td style="text-align:left">
                  <strong>{{ r.nome }}</strong>
                  <div class="fin-bar-wrap">
                    <div class="fin-bar" :style="{ width: relatorio.total_geral ? (r.total / relatorio.total_geral * 100) + '%' : '0%' }"></div>
                  </div>
                </td>
                <td style="text-align:center">{{ r.pneus }}</td>
                <td style="text-align:right"><strong class="text-green">{{ r.total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}</strong></td>
                <td style="text-align:right;color:var(--ink-600);font-size:12px">{{ relatorio.total_geral ? (r.total / relatorio.total_geral * 100).toFixed(1) + '%' : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Detalhe dos pneus -->
      <div class="fin-box">
        <div class="fin-box-header">
          <span class="fin-box-title">Pneus Reciclados no Período</span>
          <span class="badge badge-blue">{{ relatorio.detalhes.length }} pneu(s)</span>
        </div>
        <div class="table-responsive">
          <table class="gp-table fin-table">
            <thead>
              <tr>
                <th>N. Fogo</th>
                <th>Marca / Modelo</th>
                <th>Medida</th>
                <th style="text-align:center">Vida</th>
                <th>Lote</th>
                <th style="text-align:right">Valor Recebido</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in relatorio.detalhes" :key="p.id">
                <td><strong>{{ p.numero_fogo }}</strong></td>
                <td>{{ p.marca }}<span style="color:var(--ink-300);margin-left:4px;font-size:12px">{{ p.modelo }}</span></td>
                <td>{{ p.medida }}</td>
                <td style="text-align:center"><span class="badge" style="background:var(--surface-2);color:var(--ink-600);border:1px solid var(--ink-200)">{{ p.vida }}ª</span></td>
                <td style="font-size:12px;color:var(--ink-600)">{{ p.lote_id ? 'LOTE-' + p.lote_id : '—' }}</td>
                <td style="text-align:right">
                  <strong :class="p.valor_arrecadado > 0 ? 'text-green' : 'text-muted'">
                    {{ (p.valor_arrecadado || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}
                  </strong>
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
import { ref, onMounted } from 'vue'
import { fetchRelatorioFinanceiroReciclagem } from '../../api/gestaoPneus.js'

const props = defineProps({ filiais: { type: Array, default: () => [] } })

const filtroMes = ref(new Date().toISOString().slice(0, 7))
const filtroFilial = ref('')
const relatorio = ref({ resumo_filiais: [], detalhes: [], total_geral: 0 })

async function loadFinanceiro() {
  try {
    relatorio.value = await fetchRelatorioFinanceiroReciclagem({
      mes: filtroMes.value,
      filial_id: filtroFilial.value
    })
  } catch(e) { console.error(e) }
}

function exportarCSV() {
  const rf = relatorio.value
  const mes = filtroMes.value || 'todos'
  const sep = ';'
  const header = ['Mes', 'N. Fogo', 'Marca', 'Modelo', 'Medida', 'Vida', 'Lote', 'Filial Origem', 'Valor Recebido']
  const rows = rf.detalhes.map(p => [
    mes, p.numero_fogo || '', p.marca || '', p.modelo || '',
    p.medida || '', p.vida || '',
    p.lote_id ? 'LOTE-' + p.lote_id : '',
    p.filial_origem_nome || '',
    String(p.valor_arrecadado || 0).replace('.', ',')
  ])
  const csv = [header, ...rows].map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(sep)).join('\r\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `retorno_financeiro_${mes}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(loadFinanceiro)
</script>

<style scoped>
.fin-kpis { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; margin-bottom: 14px; }
.fin-kpi { background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: 6px; padding: 12px 14px; display: flex; align-items: center; gap: 12px; }
.fin-kpi-green  { border-top: 3px solid var(--status-ok); }
.fin-kpi-blue   { border-top: 3px solid #3b82f6; }
.fin-kpi-purple { border-top: 3px solid #6366f1; }
.fin-kpi-icon { width: 38px; height: 38px; border-radius: 6px; background: var(--surface-2); display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: var(--ink-600); }
.fin-kpi-green  .fin-kpi-icon { background: var(--status-ok-bg); color: var(--status-ok); }
.fin-kpi-blue   .fin-kpi-icon { background: #dbeafe; color: #1d4ed8; }
.fin-kpi-purple .fin-kpi-icon { background: #e0e7ff; color: #4338ca; }
.fin-kpi-num { display: block; font-size: 20px; font-weight: 600; color: var(--ink-900); font-variant-numeric: tabular-nums; line-height: 1.2; }
.fin-kpi-lbl { display: block; font-size: 10px; font-weight: 600; color: var(--ink-300); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 1px; }

.fin-body { display: flex; flex-direction: column; gap: 24px; }
.fin-box { background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: 12px; overflow: hidden; box-shadow: var(--shadow-sm); }
.fin-box-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--ink-200); background: var(--surface-1); }
.fin-box-title { font-weight: 700; font-size: 14px; color: var(--ink-900); }

.fin-table { margin: 0; }
.fin-bar-wrap { height: 4px; background: var(--ink-200); border-radius: 2px; margin-top: 6px; }
.fin-bar { height: 4px; background: var(--status-ok); border-radius: 2px; transition: width 0.4s ease; }

.text-green { color: var(--status-ok); }
.text-muted { color: var(--ink-300); }
</style>
