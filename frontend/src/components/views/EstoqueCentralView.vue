<template>
  <div class="estoque-central">

    <!-- SUB-NAV -->
    <div class="sub-nav">
      <button class="sub-nav-btn" :class="{ active: subTab === 'entrada' }" @click="subTab = 'entrada'">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
        Entrada de NF
      </button>
      <button class="sub-nav-btn" :class="{ active: subTab === 'controle' }" @click="subTab = 'controle'">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h1v6H9z"/><path d="M14 13h1v2h-1z"/><path d="M14 9h1v1h-1z"/></svg>
        Controle de Estoque
      </button>
    </div>

    <!-- ─────────────────────────────────────────────── -->
    <!--  SUB-TAB: ENTRADA DE NF                         -->
    <!-- ─────────────────────────────────────────────── -->
    <template v-if="subTab === 'entrada'">

      <div class="sec-toolbar">
        <div class="toolbar-left">
          <h2>Estoque Central</h2>
          <p class="sec-subtitle">Registro de Notas Fiscais e Distribuição Logística</p>
        </div>
        <div class="toolbar-right">
          <button class="btn-secondary" @click="downloadTemplate">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Baixar Modelo
          </button>
          <button class="btn-secondary" @click="triggerImport">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            Importar Estoque
          </button>
          <input type="file" ref="fileInput" style="display:none;" accept=".csv" @change="handleFileUpload" />
          <button class="btn-primary" @click="openPneuForm()">+ Registrar Novo Pneu (NF)</button>
        </div>
      </div>

      <!-- Barra de seleção em lote -->
      <div v-if="selectedIds.length > 0" class="batch-bar">
        <div class="batch-info">
          <strong>{{ selectedIds.length }}</strong> pneus selecionados
        </div>
        <div class="batch-actions">
          <select v-model="filialDestinoId" class="filter-select select-premium">
            <option :value="null">Selecionar Filial Destino...</option>
            <option v-for="f in filiaisDestino" :key="f.id" :value="f.id">{{ f.nome }}</option>
          </select>
          <button class="btn-primary" :disabled="!filialDestinoId" @click="distribuirEmLote">
            Confirmar Distribuição em Lote
          </button>
          <button class="btn-secondary" @click="selectedIds = []">Cancelar</button>
        </div>
      </div>

      <div class="table-responsive" v-if="pneus.length">
        <table class="gp-table">
          <thead>
            <tr>
              <th width="40"><input type="checkbox" :checked="allSelected" @change="toggleSelectAll" /></th>
              <th>N.Fogo</th>
              <th>Marca / Modelo</th>
              <th>Medida</th>
              <th>NF</th>
              <th>Fornecedor</th>
              <th>Valor Unit.</th>
              <th>Data Cadastro</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in pneus" :key="p.id">
              <td><input type="checkbox" v-model="selectedIds" :value="p.id" /></td>
              <td><strong>{{ p.numero_fogo }}</strong></td>
              <td>{{ p.marca }} {{ p.modelo }}</td>
              <td>{{ p.medida }}</td>
              <td>{{ p.nf || '—' }}</td>
              <td>{{ p.fornecedor || '—' }}</td>
              <td><strong>R$ {{ fmtN(p.valor) }}</strong></td>
              <td>{{ p.criado_em ? new Date(p.criado_em).toLocaleDateString('pt-BR') : '—' }}</td>
              <td class="td-actions">
                <button class="btn-sm" @click="openPneuForm(p)">Editar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v8"/><path d="M8 12h8"/></svg>
        <p>Nenhum pneu disponível no Estoque Central para distribuição.</p>
      </div>

    </template>

    <!-- ─────────────────────────────────────────────── -->
    <!--  SUB-TAB: CONTROLE DE ESTOQUE                   -->
    <!-- ─────────────────────────────────────────────── -->
    <template v-if="subTab === 'controle'">

      <div class="sec-toolbar">
        <div class="toolbar-left">
          <h2>Controle de Estoque — Matriz</h2>
          <p class="sec-subtitle">Visão consolidada por medida dos pneus disponíveis para distribuição</p>
        </div>
        <div class="toolbar-right">
          <button class="btn-secondary" @click="exportarCSV">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Exportar CSV
          </button>
        </div>
      </div>

      <!-- KPIs -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon kpi-icon-blue">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
          </div>
          <div class="kpi-body">
            <span class="kpi-num">{{ pneus.length }}</span>
            <span class="kpi-lbl">Pneus em Estoque</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon kpi-icon-purple">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          </div>
          <div class="kpi-body">
            <span class="kpi-num">{{ gruposMedida.length }}</span>
            <span class="kpi-lbl">Medidas Distintas</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon kpi-icon-green">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <div class="kpi-body">
            <span class="kpi-num">R$ {{ fmtN(valorTotal) }}</span>
            <span class="kpi-lbl">Valor Total em Estoque</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon kpi-icon-orange">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          <div class="kpi-body">
            <span class="kpi-num" :class="{ 'text-orange': medidasCriticas.length }">{{ medidasCriticas.length }}</span>
            <span class="kpi-lbl">Medidas com ≤ 2 unid.</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon kpi-icon-gray">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <div class="kpi-body">
            <span class="kpi-num">{{ marcasDistintas }}</span>
            <span class="kpi-lbl">Marcas no Estoque</span>
          </div>
        </div>
      </div>

      <!-- Alertas de estoque crítico -->
      <div v-if="medidasCriticas.length" class="alerta-critico">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <span>
          <strong>Atenção:</strong>
          {{ medidasCriticas.length }} medida(s) com estoque muito baixo (≤ 2 unidades):
          <strong>{{ medidasCriticas.map(g => g.medida).join(' · ') }}</strong>
        </span>
      </div>

      <!-- Tabela por medida -->
      <div class="table-card">
        <table class="gp-table">
          <thead>
            <tr>
              <th style="width:32px;"></th>
              <th>Medida</th>
              <th>Marcas</th>
              <th class="text-center">Qtd.</th>
              <th class="text-center">% do Total</th>
              <th class="text-right">Valor Médio</th>
              <th class="text-right">Valor Total</th>
              <th>NFs Vinculadas</th>
              <th>Última Entrada</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="g in gruposMedida" :key="g.medida">
              <!-- Linha de medida -->
              <tr
                class="medida-row"
                :class="{ 'row-critico': g.qtd <= 2 }"
                @click="toggleExpand(g.medida)"
                style="cursor:pointer;"
              >
                <td class="text-center">
                  <span class="expand-chevron" :class="{ expanded: expanded.has(g.medida) }">›</span>
                </td>
                <td>
                  <strong class="medida-tag">{{ g.medida }}</strong>
                  <span v-if="g.qtd <= 2" class="badge-critico">CRÍTICO</span>
                </td>
                <td>
                  <span v-for="m in g.marcas.slice(0,3)" :key="m" class="marca-chip">{{ m }}</span>
                  <span v-if="g.marcas.length > 3" class="marca-chip chip-more">+{{ g.marcas.length - 3 }}</span>
                </td>
                <td class="text-center">
                  <span class="qtd-badge" :class="{ 'qtd-low': g.qtd <= 2, 'qtd-med': g.qtd > 2 && g.qtd <= 5 }">
                    {{ g.qtd }}
                  </span>
                </td>
                <td class="text-center">
                  <div class="pct-bar-wrap">
                    <div class="pct-bar" :style="{ width: g.pct + '%' }"></div>
                    <span class="pct-label">{{ g.pct.toFixed(1) }}%</span>
                  </div>
                </td>
                <td class="text-right">R$ {{ fmtN(g.valorMedio) }}</td>
                <td class="text-right"><strong>R$ {{ fmtN(g.valorTotal) }}</strong></td>
                <td>
                  <span v-for="nf in g.nfs.slice(0,3)" :key="nf" class="nf-chip">{{ nf }}</span>
                  <span v-if="g.nfs.length > 3" class="nf-chip chip-more">+{{ g.nfs.length - 3 }}</span>
                  <span v-if="!g.nfs.length" class="text-muted">—</span>
                </td>
                <td class="text-muted" style="font-size:12px;">{{ g.ultimaEntrada }}</td>
              </tr>

              <!-- Detalhe dos pneus desta medida -->
              <tr v-if="expanded.has(g.medida)" class="detalhe-tr" v-for="p in g.pneus" :key="p.id">
                <td></td>
                <td colspan="2" style="padding-left:28px;">
                  <span class="fogo-label">{{ p.numero_fogo }}</span>
                  <span class="detalhe-marca">{{ p.marca }} {{ p.modelo }}</span>
                </td>
                <td class="text-center">
                  <span v-if="p.dot" class="dot-badge">DOT {{ p.dot }}</span>
                </td>
                <td class="text-center text-muted" style="font-size:11px;">Vida {{ p.vida }}ª</td>
                <td class="text-right">R$ {{ fmtN(p.valor) }}</td>
                <td class="text-right text-muted" style="font-size:11px;">NF: {{ p.nf || '—' }}</td>
                <td class="text-muted" style="font-size:11px;">{{ p.fornecedor || '—' }}</td>
                <td class="text-muted" style="font-size:11px;">{{ p.criado_em ? new Date(p.criado_em).toLocaleDateString('pt-BR') : '—' }}</td>
              </tr>

            </template>
          </tbody>
          <tfoot>
            <tr class="total-row">
              <td></td>
              <td><strong>TOTAL</strong></td>
              <td></td>
              <td class="text-center"><strong>{{ pneus.length }}</strong></td>
              <td class="text-center"><strong>100%</strong></td>
              <td></td>
              <td class="text-right"><strong>R$ {{ fmtN(valorTotal) }}</strong></td>
              <td colspan="2"></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Distribuição por marca -->
      <div class="marcas-section">
        <h3 class="section-label">Distribuição por Marca</h3>
        <div class="marcas-grid">
          <div class="marca-card" v-for="m in gruposMarca" :key="m.marca">
            <div class="marca-name">{{ m.marca }}</div>
            <div class="marca-qtd">{{ m.qtd }} <span>pneus</span></div>
            <div class="marca-valor">R$ {{ fmtN(m.valor) }}</div>
            <div class="marca-bar-wrap">
              <div class="marca-bar" :style="{ width: m.pct + '%' }"></div>
            </div>
            <div class="marca-pct">{{ m.pct.toFixed(1) }}% do estoque</div>
          </div>
        </div>
      </div>

    </template>

    <!-- Modal Cadastro/Edição -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <h3>{{ editingPneu ? 'Editar Pneu' : 'Entrada de Pneu (NF)' }}</h3>
        <div class="form-row">
          <div class="form-group">
            <label>Nº Fogo</label>
            <input v-model="pneuForm.numero_fogo" placeholder="EX: 0001" />
          </div>
          <div class="form-group">
            <label>Nota Fiscal (NF)</label>
            <input v-model="pneuForm.nf" placeholder="000.000.000" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Marca</label>
            <input v-model="pneuForm.marca" />
          </div>
          <div class="form-group">
            <label>Modelo</label>
            <input v-model="pneuForm.modelo" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Medida</label>
            <input v-model="pneuForm.medida" />
          </div>
          <div class="form-group">
            <label>Valor Unitário (R$)</label>
            <input type="number" step="0.01" v-model="pneuForm.valor" />
          </div>
        </div>
        <div class="form-group">
          <label>Fornecedor</label>
          <input v-model="pneuForm.fornecedor" />
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showModal = false">Cancelar</button>
          <button class="btn-primary" @click="savePneu">Salvar Entrada</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as api from '../../api/gestaoPneus.js'

const props = defineProps({
  filiais: { type: Array, default: () => [] }
})

const subTab = ref('entrada')
const loading = ref(false)
const pneus = ref([])
const selectedIds = ref([])
const filialDestinoId = ref(null)
const showModal = ref(false)
const editingPneu = ref(null)
const fileInput = ref(null)
const expanded = ref(new Set())

const pneuForm = ref({
  numero_fogo: '', marca: '', modelo: '', medida: '295/80R22.5',
  valor: 0, nf: '', fornecedor: '', filial_id: null
})

const centralFilial = computed(() =>
  props.filiais.find(f => f.nome.toUpperCase().includes('ESTOQUE CENTRAL'))
)

const filiaisDestino = computed(() =>
  props.filiais.filter(f => f.id !== centralFilial.value?.id && !f.nome.toUpperCase().includes('SUCATA'))
)

const allSelected = computed(() =>
  pneus.value.length > 0 && selectedIds.value.length === pneus.value.length
)

// ── Computeds controle de estoque ──────────────────────

const valorTotal = computed(() =>
  pneus.value.reduce((s, p) => s + parseFloat(p.valor || 0), 0)
)

const marcasDistintas = computed(() =>
  new Set(pneus.value.map(p => p.marca).filter(Boolean)).size
)

const gruposMedida = computed(() => {
  const mapa = {}
  for (const p of pneus.value) {
    const med = p.medida || 'Sem medida'
    if (!mapa[med]) mapa[med] = { medida: med, pneus: [], marcas: new Set(), nfs: new Set(), datas: [] }
    const g = mapa[med]
    g.pneus.push(p)
    if (p.marca) g.marcas.add(p.marca)
    if (p.nf) g.nfs.add(p.nf)
    if (p.criado_em) g.datas.push(new Date(p.criado_em))
  }
  const total = pneus.value.length || 1
  return Object.values(mapa)
    .sort((a, b) => b.pneus.length - a.pneus.length)
    .map(g => {
      const qtd = g.pneus.length
      const valorGrupo = g.pneus.reduce((s, p) => s + parseFloat(p.valor || 0), 0)
      const maxData = g.datas.length ? new Date(Math.max(...g.datas)) : null
      return {
        medida: g.medida,
        pneus: g.pneus,
        qtd,
        marcas: [...g.marcas],
        nfs: [...g.nfs],
        valorTotal: valorGrupo,
        valorMedio: qtd ? valorGrupo / qtd : 0,
        pct: (qtd / total) * 100,
        ultimaEntrada: maxData ? maxData.toLocaleDateString('pt-BR') : '—',
      }
    })
})

const medidasCriticas = computed(() => gruposMedida.value.filter(g => g.qtd <= 2))

const gruposMarca = computed(() => {
  const mapa = {}
  for (const p of pneus.value) {
    const m = p.marca || 'Sem marca'
    if (!mapa[m]) mapa[m] = { marca: m, qtd: 0, valor: 0 }
    mapa[m].qtd++
    mapa[m].valor += parseFloat(p.valor || 0)
  }
  const total = pneus.value.length || 1
  return Object.values(mapa)
    .sort((a, b) => b.qtd - a.qtd)
    .map(m => ({ ...m, pct: (m.qtd / total) * 100 }))
})

// ── Funções ────────────────────────────────────────────

onMounted(loadData)

async function loadData() {
  if (!centralFilial.value) return
  loading.value = true
  try {
    pneus.value = await api.fetchPneusList({
      status: 'estoque',
      filial_id: centralFilial.value.id
    })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function toggleSelectAll() {
  selectedIds.value = allSelected.value ? [] : pneus.value.map(p => p.id)
}

function toggleExpand(medida) {
  const s = new Set(expanded.value)
  if (s.has(medida)) s.delete(medida)
  else s.add(medida)
  expanded.value = s
}

function openPneuForm(p = null) {
  editingPneu.value = p
  pneuForm.value = p
    ? { ...p }
    : { numero_fogo: '', marca: '', modelo: '', medida: '295/80R22.5', valor: 0, nf: '', fornecedor: '', filial_id: centralFilial.value?.id }
  showModal.value = true
}

async function savePneu() {
  try {
    if (editingPneu.value) {
      await api.updatePneu(editingPneu.value.id, pneuForm.value)
    } else {
      await api.createPneu(pneuForm.value)
    }
    showModal.value = false
    loadData()
  } catch (e) {
    alert(e.message)
  }
}

async function distribuirEmLote() {
  if (!filialDestinoId.value || !selectedIds.value.length) return
  const filialNome = props.filiais.find(f => f.id === filialDestinoId.value)?.nome
  if (!confirm(`Deseja enviar ${selectedIds.value.length} pneus para ${filialNome}?`)) return
  loading.value = true
  try {
    for (const id of selectedIds.value) {
      await api.transferirPneu({ pneu_id: id, filial_destino_id: filialDestinoId.value, observacao: 'Distribuição em lote do Estoque Central' })
    }
    selectedIds.value = []
    filialDestinoId.value = null
    loadData()
    alert('Pneus distribuídos com sucesso!')
  } catch (e) {
    alert('Erro na distribuição: ' + e.message)
  } finally {
    loading.value = false
  }
}

function downloadTemplate() {
  window.open(api.fetchPneusTemplate(), '_blank')
}

function triggerImport() {
  fileInput.value.click()
}

async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await api.importPneusCsv(formData, centralFilial.value?.id)
    alert(res.message || 'Importação concluída!')
    loadData()
  } catch (e) {
    alert('Erro: ' + e.message)
  } finally {
    event.target.value = ''
  }
}

function fmtN(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function exportarCSV() {
  const sep = ';'
  const header = ['Medida', 'Marca', 'Modelo', 'N. Fogo', 'NF', 'Fornecedor', 'Valor', 'DOT', 'Vida', 'Data Entrada']
  const rows = pneus.value.map(p => [
    p.medida || '',
    p.marca || '',
    p.modelo || '',
    p.numero_fogo || '',
    p.nf || '',
    p.fornecedor || '',
    String(p.valor || 0).replace('.', ','),
    p.dot || '',
    p.vida || '',
    p.criado_em ? new Date(p.criado_em).toLocaleDateString('pt-BR') : '',
  ])
  const csv = [header, ...rows]
    .map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(sep))
    .join('\r\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `estoque_central_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.estoque-central { display: flex; flex-direction: column; gap: 20px; }

/* ── Sub-nav ── */
.sub-nav {
  display: flex;
  gap: 4px;
  background: var(--s1, #f8fafc);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 10px;
  padding: 4px;
  width: fit-content;
}
.sub-nav-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 18px;
  border: none;
  border-radius: 7px;
  background: transparent;
  color: var(--text3, #94a3b8);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all .18s;
}
.sub-nav-btn:hover { background: white; color: var(--text, #1e293b); }
.sub-nav-btn.active {
  background: white;
  color: var(--brand, #c41230);
  box-shadow: 0 1px 4px rgba(0,0,0,.1);
}

/* ── Toolbar ── */
.sec-toolbar { display: flex; justify-content: space-between; align-items: center; }
.toolbar-right { display: flex; gap: 12px; flex-wrap: wrap; }
.sec-subtitle { font-size: 13px; color: var(--text3); margin-top: 4px; }

/* ── KPI Grid ── */
.kpi-grid {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}
.kpi-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: white;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 12px;
  padding: 16px 20px;
  flex: 1;
  min-width: 160px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.kpi-icon {
  width: 44px; height: 44px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.kpi-icon-blue   { background: #eff6ff; color: #3b82f6; }
.kpi-icon-purple { background: #f5f3ff; color: #8b5cf6; }
.kpi-icon-green  { background: #f0fdf4; color: #16a34a; }
.kpi-icon-orange { background: #fff7ed; color: #f97316; }
.kpi-icon-gray   { background: #f8fafc; color: #64748b; }
.kpi-body { display: flex; flex-direction: column; }
.kpi-num { font-size: 22px; font-weight: 800; color: var(--text, #1e293b); line-height: 1.2; }
.kpi-lbl { font-size: 11px; color: var(--text3, #94a3b8); text-transform: uppercase; letter-spacing: .5px; margin-top: 2px; }
.text-orange { color: #f97316 !important; }

/* ── Alerta crítico ── */
.alerta-critico {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-left: 4px solid #f97316;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  color: #92400e;
}

/* ── Table card ── */
.table-card {
  background: white;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}

.gp-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px; }
.gp-table th { background: #f9fafb; font-weight: 700; color: var(--text3, #64748b); text-transform: uppercase; letter-spacing: .05em; font-size: 11px; padding: 14px 16px; border-bottom: 2px solid var(--border); text-align: left; }
.gp-table td { padding: 14px 16px; border-bottom: 1px solid var(--border); color: var(--text); vertical-align: middle; }
.gp-table tr:last-child td { border-bottom: none; }

.medida-row { background: #f8fafc; transition: background .15s; }
.medida-row:hover { background: #f1f5f9; }
.row-critico { background: #fff7ed; }
.row-critico:hover { background: #ffedd5; }

.detalhe-tr td { background: white; font-size: 12px; padding: 8px 16px; }
.detalhe-tr:hover td { background: #fafafa; }

.total-row td { background: #f9fafb; font-size: 13px; padding: 12px 16px; border-top: 2px solid var(--border); }

/* ── Elementos da tabela ── */
.medida-tag { font-size: 14px; color: var(--text, #1e293b); margin-right: 8px; }
.badge-critico {
  display: inline-block;
  background: #fef2f2;
  border: 1px solid #fca5a5;
  color: #dc2626;
  font-size: 9px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: .5px;
  vertical-align: middle;
}
.expand-chevron {
  display: inline-block;
  font-size: 18px;
  color: var(--text3, #94a3b8);
  transition: transform .2s;
  font-style: normal;
  line-height: 1;
}
.expand-chevron.expanded { transform: rotate(90deg); color: var(--brand, #c41230); }

.marca-chip {
  display: inline-block;
  background: #ede9fe;
  color: #6d28d9;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  margin-right: 3px;
  margin-bottom: 2px;
}
.chip-more { background: #f1f5f9; color: #64748b; }

.nf-chip {
  display: inline-block;
  background: #f0fdf4;
  color: #15803d;
  border: 1px solid #bbf7d0;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  margin-right: 3px;
  margin-bottom: 2px;
}

.qtd-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 800;
  background: #e0f2fe;
  color: #0369a1;
}
.qtd-badge.qtd-low { background: #fef2f2; color: #dc2626; }
.qtd-badge.qtd-med { background: #fff7ed; color: #c2410c; }

.pct-bar-wrap { display: flex; align-items: center; gap: 8px; }
.pct-bar {
  height: 6px;
  background: linear-gradient(90deg, var(--brand, #c41230), #f97316);
  border-radius: 3px;
  min-width: 3px;
  max-width: 80px;
  transition: width .3s;
}
.pct-label { font-size: 11px; color: var(--text3, #94a3b8); white-space: nowrap; }

.fogo-label { font-weight: 700; color: var(--text, #1e293b); margin-right: 8px; font-size: 13px; }
.detalhe-marca { color: var(--text3, #94a3b8); font-size: 12px; }
.dot-badge { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 10px; padding: 1px 6px; color: #64748b; }

/* ── Distribuição por marca ── */
.marcas-section { margin-top: 4px; }
.section-label { font-size: 13px; font-weight: 700; color: var(--text3, #64748b); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 12px; }
.marcas-grid { display: flex; gap: 12px; flex-wrap: wrap; }
.marca-card {
  background: white;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 12px;
  padding: 16px 20px;
  flex: 1;
  min-width: 150px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.marca-name { font-size: 13px; font-weight: 700; color: var(--text, #1e293b); margin-bottom: 4px; }
.marca-qtd { font-size: 26px; font-weight: 800; color: var(--brand, #c41230); line-height: 1.2; }
.marca-qtd span { font-size: 13px; font-weight: 400; color: var(--text3); }
.marca-valor { font-size: 12px; color: var(--text3, #94a3b8); margin: 2px 0 10px; }
.marca-bar-wrap { background: #f1f5f9; border-radius: 4px; height: 6px; overflow: hidden; margin-bottom: 4px; }
.marca-bar { height: 100%; background: linear-gradient(90deg, var(--brand, #c41230), #f97316); border-radius: 4px; transition: width .3s; }
.marca-pct { font-size: 11px; color: var(--text3, #94a3b8); }

/* ── Batch bar ── */
.batch-bar { background: #eff6ff; border: 1px solid #bfdbfe; padding: 16px 24px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; }
.batch-info { font-size: 14px; color: #1e40af; }
.batch-info strong { font-size: 16px; }
.batch-actions { display: flex; gap: 12px; align-items: center; }

/* ── Botões ── */
.btn-primary { padding: 10px 20px; background: linear-gradient(180deg, var(--brand) 0%, var(--brand-dark) 100%); color: #fff; border: 1px solid var(--brand-dark); border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.btn-primary:hover { transform: translateY(-1px); }
.btn-primary:disabled { opacity: .5; cursor: not-allowed; transform: none; }
.btn-secondary { padding: 10px 20px; background: #fff; color: var(--text); border: 1px solid var(--s4); border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.btn-secondary:hover { background: var(--s3); }
.btn-sm { padding: 6px 12px; border: 1px solid var(--s4); background: #fff; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; color: var(--text); }

.filter-select { padding: 10px 14px; border: 1px solid var(--s4); border-radius: 8px; font-size: 13px; background: #fff; color: var(--text); min-width: 200px; outline: none; }
.select-premium { border-color: var(--brand-mid); color: var(--brand); font-weight: 600; }

.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,.6); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px); }
.modal-box { background: #fff; border-radius: 20px; padding: 32px; width: 500px; max-width: 95vw; box-shadow: 0 25px 50px rgba(0,0,0,.25); }
.modal-box h3 { font-size: 20px; font-weight: 800; margin-bottom: 24px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; }

.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; flex: 1; }
.form-group label { font-size: 12px; font-weight: 700; color: var(--text2); text-transform: uppercase; }
.form-group input { padding: 10px 14px; border: 1px solid var(--s4); border-radius: 8px; font-size: 14px; outline: none; }
.form-group input:focus { border-color: var(--brand); }
.form-row { display: flex; gap: 16px; }

.table-responsive { overflow-x: auto; border-radius: 12px; border: 1px solid var(--border); }
.empty-state { text-align: center; padding: 48px; color: var(--text3); border: 2px dashed var(--s2); border-radius: 12px; }

.text-center { text-align: center; }
.text-right  { text-align: right;  }
.text-muted  { color: var(--text3, #94a3b8); }
</style>
