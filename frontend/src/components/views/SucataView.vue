<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2>Gestão de Sucata</h2>
        <p class="sec-subtitle">Validação e controle de pneus descartados ou em fim de vida</p>
      </div>
      <div class="toolbar-right">
        <input v-model="searchSucata" placeholder="Buscar Nº Fogo..." class="filter-select select-premium" style="width:200px" />
        <select v-model="filtroFilial" class="filter-select" style="min-width:220px">
          <option value="">Todas as Origens</option>
          <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>
      </div>
    </div>

    <div class="sucata-grid">
      <!-- Pendentes -->
      <div class="sucata-column">
        <div class="col-header">
          <h3>Aguardando Chegada</h3>
          <span class="badge badge-yellow">{{ pendentes.length }}</span>
        </div>
        <div class="sucata-cards">
          <div v-for="p in pendentes" :key="p.id" class="sucata-card pending">
            <div class="s-card-id">{{ p.numero_fogo }}</div>
            <div class="s-card-info">
              <span class="s-tire-name">{{ p.marca }} {{ p.medida }}</span>
              <div class="s-origin-badge">
                <span class="lbl">Vem de:</span>
                <span class="val">{{ p.filial_origem_nome || (p.filial_nome?.toUpperCase().includes('SUCATA') ? '—' : p.filial_nome) }}</span>
              </div>
            </div>
            <button class="btn-confirm-arrival" @click="confirmarChegada(p)">Confirmar Chegada</button>
          </div>
          <div v-if="!pendentes.length" class="empty-sucata">Nenhum pneu em trânsito para sucata</div>
        </div>
      </div>

      <!-- Confirmados -->
      <div class="sucata-column">
        <div class="col-header">
          <h3>Sucata Processada</h3>
          <span class="badge badge-green">{{ confirmados.length }}</span>
        </div>
        <div class="sucata-cards">
          <div v-for="p in confirmados" :key="p.id" class="sucata-card done">
            <div class="s-card-id">{{ p.numero_fogo }}</div>
            <div class="s-card-info">
              <span class="s-tire-name">{{ p.marca }} {{ p.medida }}</span>
              <div class="s-origin-badge">
                <span class="lbl">Veio de:</span>
                <span class="val">{{ p.filial_origem_nome || (p.filial_nome?.toUpperCase().includes('SUCATA') ? '—' : p.filial_nome) }}</span>
              </div>
            </div>
            <div style="display:flex;gap:8px;align-items:center">
              <span class="badge badge-green">Validado</span>
              <button class="btn-recicladora" @click="openReciclagem(p)">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:4px;vertical-align:middle"><path d="M12 2v4"/><path d="m16.2 4.2 2.8 2.8"/><path d="M12 18v4"/><path d="m4.9 19.1 2.8-2.8"/><path d="M2 12h4"/><path d="m4.2 16.2 2.8-2.8"/><path d="M18 12h4"/><path d="m19.1 4.9-2.8 2.8"/></svg>
                Enviar
              </button>
            </div>
          </div>
          <div v-if="!confirmados.length" class="empty-sucata">Nenhuma sucata processada</div>
        </div>
      </div>
    </div>

    <!-- Modal reciclagem -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <h3>Enviar para Recicladora</h3>
        <p>Pneu: <strong>{{ reciclagemCtx?.numero_fogo }}</strong> ({{ reciclagemCtx?.marca }} {{ reciclagemCtx?.medida }})</p>
        <div class="form-group" style="margin-top:16px">
          <label>Data de Envio</label>
          <input type="date" v-model="reciclagemForm.data_envio" />
        </div>
        <div class="form-group">
          <label>Observação (Opcional)</label>
          <input v-model="reciclagemForm.observacao" placeholder="Ex: NF de venda, transportadora..." />
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showModal = false">Cancelar</button>
          <button class="btn-primary" @click="doEnviar">Confirmar Envio</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { confirmarRecebimento, enviarParaReciclagem } from '../../api/gestaoPneus.js'

const props = defineProps({
  pneusGeral: { type: Array, default: () => [] },
  filiais: { type: Array, default: () => [] }
})
const emit = defineEmits(['refresh'])

const searchSucata = ref('')
const filtroFilial = ref('')

const showModal = ref(false)
const reciclagemCtx = ref(null)
const reciclagemForm = ref({ data_envio: new Date().toISOString().split('T')[0], observacao: '' })

const pendentes = computed(() => {
  let list = props.pneusGeral.filter(p =>
    p.recebido === 0 && (p.status === 'descarte' || (p.filial_nome || '').toUpperCase().includes('SUCATA'))
  )
  if (filtroFilial.value) list = list.filter(p => p.filial_origem_id === Number(filtroFilial.value))
  if (searchSucata.value) {
    const s = searchSucata.value.toLowerCase()
    list = list.filter(p => p.numero_fogo.toLowerCase().includes(s))
  }
  return list
})

const confirmados = computed(() => {
  let list = props.pneusGeral.filter(p =>
    p.recebido === 1 && !p.lote_id &&
    (p.status === 'descarte' || (p.filial_nome || '').toUpperCase().includes('SUCATA')) &&
    p.status !== 'reciclagem'
  )
  if (filtroFilial.value) list = list.filter(p => p.filial_origem_id === Number(filtroFilial.value))
  if (searchSucata.value) {
    const s = searchSucata.value.toLowerCase()
    list = list.filter(p => p.numero_fogo.toLowerCase().includes(s))
  }
  return list
})

async function confirmarChegada(p) {
  if (!confirm(`Confirmar que o pneu ${p.numero_fogo} CHEGOU na filial ${p.filial_nome || ''}?`)) return
  try {
    await confirmarRecebimento(p.id)
    emit('refresh')
  } catch(e) { alert(e.message) }
}

function openReciclagem(p) {
  reciclagemCtx.value = p
  reciclagemForm.value = { data_envio: new Date().toISOString().split('T')[0], observacao: '' }
  showModal.value = true
}

async function doEnviar() {
  try {
    await enviarParaReciclagem({
      pneu_id: reciclagemCtx.value.id,
      data_envio: reciclagemForm.value.data_envio,
      observacao: reciclagemForm.value.observacao
    })
    showModal.value = false
    emit('refresh')
  } catch(e) { alert(e.message) }
}
</script>

<style scoped>
.sucata-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }

.sucata-column { display: flex; flex-direction: column; gap: 0; }
.col-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; background: var(--surface-1); border: 1px solid var(--ink-200); border-bottom: none; border-radius: 12px 12px 0 0; }
.col-header h3 { font-size: 14px; font-weight: 700; color: var(--ink-900); margin: 0; }

.sucata-cards { display: flex; flex-direction: column; gap: 0; border: 1px solid var(--ink-200); border-radius: 0 0 12px 12px; overflow: hidden; }

.sucata-card { background: var(--surface-0); padding: 16px; display: flex; flex-direction: column; gap: 10px; border-bottom: 1px solid var(--ink-200); transition: background 0.15s; }
.sucata-card:last-child { border-bottom: none; }
.sucata-card:hover { background: var(--surface-1); }
.sucata-card.pending { border-left: 3px solid var(--status-warn); }
.sucata-card.done    { border-left: 3px solid var(--status-ok); }

.s-card-id { font-size: 16px; font-weight: 800; color: var(--ink-900); }
.s-card-info { display: flex; flex-direction: column; gap: 4px; }
.s-tire-name { font-size: 13px; color: var(--ink-600); }
.s-origin-badge { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.s-origin-badge .lbl { color: var(--ink-300); font-weight: 600; }
.s-origin-badge .val { color: var(--ink-900); font-weight: 600; }

.btn-confirm-arrival { padding: 8px 14px; background: var(--brand-900); color: var(--surface-0); border: none; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.btn-confirm-arrival:hover { background: var(--brand-800); }

.btn-recicladora { padding: 6px 12px; background: var(--surface-0); border: 1px solid var(--ink-300); border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; color: var(--ink-900); display: inline-flex; align-items: center; transition: all 0.2s; }
.btn-recicladora:hover { background: var(--status-ok-bg); border-color: var(--status-ok); color: var(--status-ok); }

.empty-sucata { padding: 32px; text-align: center; color: var(--ink-300); font-size: 13px; background: var(--surface-1); }

@media (max-width: 768px) { .sucata-grid { grid-template-columns: 1fr; } }
</style>
