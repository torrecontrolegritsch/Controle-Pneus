<template>
  <section class="gp-section">
    <!-- Toolbar -->
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2 class="sec-title">Controle por Medida</h2>
        <p class="sec-subtitle">Quantidade de pneus agrupados por medida e marca</p>
      </div>
      <div class="toolbar-right" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <select v-model="filtroFilial" @change="aplicarFiltro" class="filter-select">
          <option value="">Todas as filiais</option>
          <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>
        <select v-model="filtroStatus" @change="aplicarFiltro" class="filter-select">
          <option value="">Todos os status</option>
          <option value="estoque">Em Estoque</option>
          <option value="em_uso">Em Uso</option>
          <option value="sucata">Sucata</option>
          <option value="reciclagem">Reciclagem</option>
        </select>
        <button class="btn-secondary" @click="expandAll = !expandAll" title="Expandir/Recolher detalhes">
          {{ expandAll ? '▲ Recolher' : '▼ Expandir' }}
        </button>
      </div>
    </div>

    <!-- Totalizadores -->
    <div class="medidas-totais">
      <div class="mt-card">
        <span class="mt-icon">📐</span>
        <div>
          <span class="mt-num">{{ gruposFiltrados.length }}</span>
          <span class="mt-label">Medidas distintas</span>
        </div>
      </div>
      <div class="mt-card mt-green">
        <span class="mt-icon">🟢</span>
        <div>
          <span class="mt-num">{{ totais.estoque }}</span>
          <span class="mt-label">Em Estoque</span>
        </div>
      </div>
      <div class="mt-card mt-blue">
        <span class="mt-icon">🔵</span>
        <div>
          <span class="mt-num">{{ totais.em_uso }}</span>
          <span class="mt-label">Em Uso</span>
        </div>
      </div>
      <div class="mt-card mt-red">
        <span class="mt-icon">🔴</span>
        <div>
          <span class="mt-num">{{ totais.sucata }}</span>
          <span class="mt-label">Sucata / Reciclagem</span>
        </div>
      </div>
      <div class="mt-card mt-purple">
        <span class="mt-icon">💰</span>
        <div>
          <span class="mt-num">R$ {{ fmtN(totais.valor_estoque) }}</span>
          <span class="mt-label">Valor em Estoque</span>
        </div>
      </div>
    </div>

    <!-- Spinner -->
    <div v-if="carregando" class="loading-spinner-wrap">
      <div class="loading-spinner"></div>
    </div>

    <!-- Tabela por medida -->
    <div v-else-if="gruposFiltrados.length" class="table-card" style="margin-top:16px;">
      <table class="gp-table">
        <thead>
          <tr>
            <th style="width:40px;"></th>
            <th>Medida</th>
            <th>Marcas</th>
            <th class="text-center">Estoque</th>
            <th class="text-center">Em Uso</th>
            <th class="text-center">Sucata</th>
            <th class="text-center">Recicl.</th>
            <th class="text-center">Total</th>
            <th class="text-right">Valor em Estoque</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="g in gruposFiltrados" :key="g.medida">
            <!-- Linha da medida -->
            <tr class="medida-row" @click="toggleMedida(g.medida)" style="cursor:pointer;">
              <td class="text-center">
                <span class="expand-icon">{{ (expandAll || expandedMedidas.has(g.medida)) ? '▾' : '▸' }}</span>
              </td>
              <td><strong class="medida-label">{{ g.medida }}</strong></td>
              <td>
                <span
                  v-for="m in g.marcas.slice(0, 4)"
                  :key="m"
                  class="badge badge-purple"
                  style="margin-right:4px;margin-bottom:2px;"
                >{{ m }}</span>
                <span v-if="g.marcas.length > 4" class="badge badge-gray">+{{ g.marcas.length - 4 }}</span>
              </td>
              <td class="text-center">
                <span v-if="g.estoque > 0" class="badge badge-green">{{ g.estoque }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="text-center">
                <span v-if="g.em_uso > 0" class="badge badge-blue">{{ g.em_uso }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="text-center">
                <span v-if="g.sucata > 0" class="badge badge-red">{{ g.sucata }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="text-center">
                <span v-if="g.reciclagem > 0" class="badge badge-yellow">{{ g.reciclagem }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="text-center"><strong>{{ g.total }}</strong></td>
              <td class="text-right">
                <span v-if="g.valor_estoque > 0">R$ {{ fmtN(g.valor_estoque) }}</span>
                <span v-else class="text-muted">—</span>
              </td>
            </tr>
            <!-- Linhas de detalhe por marca/modelo (expansível) -->
            <template v-if="expandAll || expandedMedidas.has(g.medida)">
              <tr
                v-for="d in g.detalhes"
                :key="d.marca + d.modelo"
                class="detalhe-row"
              >
                <td></td>
                <td class="text-muted" style="padding-left:24px;">↳ {{ d.marca }} <span style="font-size:11px;">{{ d.modelo }}</span></td>
                <td></td>
                <td class="text-center">
                  <span v-if="d.estoque > 0" class="badge badge-green badge-sm">{{ d.estoque }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="text-center">
                  <span v-if="d.em_uso > 0" class="badge badge-blue badge-sm">{{ d.em_uso }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="text-center">
                  <span v-if="d.sucata > 0" class="badge badge-red badge-sm">{{ d.sucata }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="text-center">
                  <span v-if="d.reciclagem > 0" class="badge badge-yellow badge-sm">{{ d.reciclagem }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="text-center">{{ d.total }}</td>
                <td class="text-right">
                  <span v-if="d.valor_estoque > 0" style="font-size:12px;">R$ {{ fmtN(d.valor_estoque) }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>

    <div v-else class="empty-state">
      <p>Nenhum pneu encontrado com os filtros selecionados.</p>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  pneus: { type: Array, default: () => [] },
  filiais: { type: Array, default: () => [] },
  carregando: { type: Boolean, default: false },
})

const filtroFilial = ref('')
const filtroStatus = ref('')
const expandAll = ref(false)
const expandedMedidas = ref(new Set())

function toggleMedida(medida) {
  const s = new Set(expandedMedidas.value)
  if (s.has(medida)) s.delete(medida)
  else s.add(medida)
  expandedMedidas.value = s
}

function aplicarFiltro() {
  // filtros reativos via computed
}

const pneusFiltrados = computed(() => {
  let lista = props.pneus
  if (filtroFilial.value) lista = lista.filter(p => String(p.filial_id) === String(filtroFilial.value))
  if (filtroStatus.value) lista = lista.filter(p => p.status === filtroStatus.value)
  return lista
})

const gruposFiltrados = computed(() => {
  const mapa = {}
  for (const p of pneusFiltrados.value) {
    const medida = p.medida || 'Sem medida'
    const marca = p.marca || 'Sem marca'
    const modelo = p.modelo || ''
    const key = medida
    const subKey = `${marca}||${modelo}`

    if (!mapa[key]) {
      mapa[key] = {
        medida,
        marcas: [],
        estoque: 0, em_uso: 0, sucata: 0, reciclagem: 0, total: 0,
        valor_estoque: 0,
        detalhes: {}
      }
    }
    const g = mapa[key]

    if (!g.marcas.includes(marca)) g.marcas.push(marca)

    if (!g.detalhes[subKey]) {
      g.detalhes[subKey] = { marca, modelo, estoque: 0, em_uso: 0, sucata: 0, reciclagem: 0, total: 0, valor_estoque: 0 }
    }
    const d = g.detalhes[subKey]

    const status = p.status || 'estoque'
    if (status === 'estoque') { g.estoque++; d.estoque++ }
    else if (status === 'em_uso') { g.em_uso++; d.em_uso++ }
    else if (status === 'sucata') { g.sucata++; d.sucata++ }
    else if (status === 'reciclagem') { g.reciclagem++; d.reciclagem++ }

    g.total++; d.total++

    if (status === 'estoque') {
      const v = parseFloat(p.valor || 0)
      g.valor_estoque += v
      d.valor_estoque += v
    }
  }

  return Object.values(mapa)
    .sort((a, b) => b.total - a.total)
    .map(g => ({ ...g, detalhes: Object.values(g.detalhes).sort((a, b) => b.total - a.total) }))
})

const totais = computed(() => {
  return gruposFiltrados.value.reduce(
    (acc, g) => {
      acc.estoque += g.estoque
      acc.em_uso += g.em_uso
      acc.sucata += g.sucata + g.reciclagem
      acc.valor_estoque += g.valor_estoque
      return acc
    },
    { estoque: 0, em_uso: 0, sucata: 0, valor_estoque: 0 }
  )
})

function fmtN(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.medidas-totais {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.mt-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  border: 1px solid var(--s2, #e2e8f0);
  border-radius: 10px;
  padding: 14px 20px;
  flex: 1;
  min-width: 160px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}

.mt-card.mt-green { border-left: 4px solid #22c55e; }
.mt-card.mt-blue  { border-left: 4px solid #3b82f6; }
.mt-card.mt-red   { border-left: 4px solid #ef4444; }
.mt-card.mt-purple{ border-left: 4px solid #8b5cf6; }

.mt-icon { font-size: 20px; }

.mt-num {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: var(--text1, #1e293b);
  line-height: 1.2;
}

.mt-label {
  display: block;
  font-size: 11px;
  color: var(--text3, #94a3b8);
  text-transform: uppercase;
  letter-spacing: .5px;
}

.medida-row { background: #f8fafc; }
.medida-row:hover { background: #f1f5f9; }
.medida-label { font-size: 14px; color: var(--text1, #1e293b); }

.detalhe-row td { font-size: 13px; background: white; }
.detalhe-row:hover td { background: #fafafa; }

.expand-icon { font-size: 12px; color: var(--text3, #94a3b8); }

.badge-sm { font-size: 10px !important; padding: 2px 6px !important; }
.badge-gray { background: #e2e8f0; color: #64748b; font-size: 10px; padding: 2px 6px; border-radius: 4px; }

.text-muted { color: var(--text3, #94a3b8); font-size: 12px; }

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

.text-center { text-align: center; }
.text-right  { text-align: right;  }
</style>
