<template>
  <section class="gp-section">
    <div class="sec-toolbar">
      <div class="toolbar-left">
        <h2>Recapagem</h2>
        <p class="sec-subtitle">Pneus enviados para recauchutadora e retorno ao estoque</p>
      </div>
      <div class="toolbar-right">
        <button class="btn-primary" @click="abrirModalEnvio">+ Enviar para Recap</button>
      </div>
    </div>

    <!-- Pneus em recap -->
    <div class="recap-box" v-if="emRecap.length > 0">
      <div class="recap-box-header">
        <span class="recap-box-title">Em Recapagem ({{ emRecap.length }})</span>
        <span class="badge badge-amber">Aguardando Retorno</span>
      </div>
      <div class="table-responsive">
        <table class="gp-table">
          <thead>
            <tr>
              <th>N. Fogo</th>
              <th>Marca/Modelo</th>
              <th>Medida</th>
              <th>Recauchutadora</th>
              <th style="text-align:center">Data Envio</th>
              <th style="text-align:center">Dias Fora</th>
              <th style="text-align:center">Sulco Antes</th>
              <th style="text-align:right">Ação</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in emRecap" :key="r.id">
              <td><strong>{{ r.numero_fogo }}</strong></td>
              <td>{{ r.marca }} <span style="color:var(--ink-400);font-size:12px">{{ r.modelo }}</span></td>
              <td><span class="medida-badge">{{ r.medida || '—' }}</span></td>
              <td>{{ r.recauchutadora }}</td>
              <td style="text-align:center">{{ fmtDate(r.data_envio) }}</td>
              <td style="text-align:center">
                <span class="dias-badge" :class="diasClass(r.data_envio)">
                  {{ diasFora(r.data_envio) }}d
                </span>
              </td>
              <td style="text-align:center">{{ r.sulco_antes != null ? r.sulco_antes + ' mm' : '—' }}</td>
              <td style="text-align:right">
                <button class="btn-confirmar" @click="abrirModalRetorno(r)">
                  Confirmar Retorno
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="empty-state" style="margin-bottom:24px">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:12px"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
      <p>Nenhum pneu em recapagem no momento</p>
      <small>Clique em "+ Enviar para Recap" para registrar um envio</small>
    </div>

    <!-- Divisor histórico -->
    <div class="section-divider" v-if="historico.length > 0">
      <span>Histórico de Recapagens</span>
    </div>

    <!-- Histórico -->
    <div v-if="historico.length > 0" class="recap-box">
      <div class="table-responsive">
        <table class="gp-table mini">
          <thead>
            <tr>
              <th>N. Fogo</th>
              <th>Marca/Modelo</th>
              <th>Medida</th>
              <th>Recauchutadora</th>
              <th style="text-align:center">Envio</th>
              <th style="text-align:center">Retorno</th>
              <th style="text-align:center">Sulco Antes</th>
              <th style="text-align:center">Sulco Depois</th>
              <th style="text-align:center">Nova Vida</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in historico" :key="r.id">
              <td><strong>{{ r.numero_fogo }}</strong></td>
              <td>{{ r.marca }} <span style="color:var(--ink-400);font-size:12px">{{ r.modelo }}</span></td>
              <td><span class="medida-badge">{{ r.medida || '—' }}</span></td>
              <td>{{ r.recauchutadora }}</td>
              <td style="text-align:center">{{ fmtDate(r.data_envio) }}</td>
              <td style="text-align:center">{{ fmtDate(r.data_retorno) }}</td>
              <td style="text-align:center">{{ r.sulco_antes != null ? r.sulco_antes + ' mm' : '—' }}</td>
              <td style="text-align:center">
                <span v-if="r.sulco_depois != null" class="sulco-ok">{{ r.sulco_depois }} mm</span>
                <span v-else>—</span>
              </td>
              <td style="text-align:center">
                <span class="badge" style="background:var(--brand-100);color:var(--brand-900)">{{ (r.vida_atual || 1) }}ª</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal: Enviar para Recap -->
    <div v-if="showModalEnvio" class="modal-overlay" @click.self="showModalEnvio = false">
      <div class="modal-box">
        <header class="modal-header-gp">
          <h3>Enviar Pneu para Recapagem</h3>
          <button class="modal-close" @click="showModalEnvio = false">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </header>

        <div class="modal-body">
          <div class="form-group">
            <label>Selecionar Pneu (Estoque Central)</label>
            <select v-model="envioForm.pneu_id" @change="onPneuSelecionado">
              <option value="">— Selecione o pneu —</option>
              <option v-for="p in pneusEstoque" :key="p.id" :value="p.id">
                {{ p.numero_fogo }} — {{ p.marca }} {{ p.modelo }} ({{ p.medida }}) | Sulco: {{ p.sulco_atual }}mm | {{ p.vida }}ª vida
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Recauchutadora</label>
            <input type="text" v-model="envioForm.recauchutadora" placeholder="Nome da recauchutadora" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Data de Envio</label>
              <input type="date" v-model="envioForm.data_envio" />
            </div>
            <div class="form-group">
              <label>Sulco Atual (mm)</label>
              <input type="number" v-model="envioForm.sulco_antes" step="0.1" min="0" />
            </div>
          </div>

          <div v-if="pneuSelecionado" class="pneu-preview">
            <span class="medida-badge">{{ pneuSelecionado.medida }}</span>
            <span>{{ pneuSelecionado.numero_fogo }} · {{ pneuSelecionado.marca }} {{ pneuSelecionado.modelo }}</span>
            <span class="badge" style="background:var(--brand-100);color:var(--brand-900)">{{ pneuSelecionado.vida }}ª vida</span>
          </div>
        </div>

        <footer class="modal-footer">
          <button class="btn-secondary" @click="showModalEnvio = false">Cancelar</button>
          <button class="btn-primary" :disabled="!envioForm.pneu_id || !envioForm.recauchutadora || !envioForm.data_envio || salvando" @click="salvarEnvio">
            {{ salvando ? 'Enviando...' : 'Confirmar Envio' }}
          </button>
        </footer>
      </div>
    </div>

    <!-- Modal: Confirmar Retorno -->
    <div v-if="showModalRetorno" class="modal-overlay" @click.self="showModalRetorno = false">
      <div class="modal-box">
        <header class="modal-header-gp">
          <h3>Confirmar Retorno de Recapagem</h3>
          <button class="modal-close" @click="showModalRetorno = false">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </header>

        <div class="modal-body" v-if="retornoCtx">
          <div class="retorno-info">
            <div><span class="lbl">Pneu</span><strong>{{ retornoCtx.numero_fogo }}</strong></div>
            <div><span class="lbl">Medida</span><span class="medida-badge">{{ retornoCtx.medida }}</span></div>
            <div><span class="lbl">Recauchutadora</span>{{ retornoCtx.recauchutadora }}</div>
            <div><span class="lbl">Enviado em</span>{{ fmtDate(retornoCtx.data_envio) }}</div>
          </div>

          <div class="form-group" style="margin-top:16px">
            <label>Novo Sulco após Recapagem (mm)</label>
            <input type="number" v-model="retornoForm.sulco_novo" step="0.1" min="0" placeholder="Ex: 16.5" />
            <small style="color:var(--ink-400);font-size:11px">O pneu voltará ao estoque central com a nova medida de sulco e vida incrementada.</small>
          </div>

          <div class="form-group">
            <label>Filial Central (destino do pneu)</label>
            <select v-model="retornoForm.filial_central_id">
              <option value="">— Selecione —</option>
              <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
            </select>
          </div>
        </div>

        <footer class="modal-footer">
          <button class="btn-secondary" @click="showModalRetorno = false">Cancelar</button>
          <button class="btn-primary" :disabled="!retornoForm.sulco_novo || !retornoForm.filial_central_id || salvando" @click="salvarRetorno">
            {{ salvando ? 'Salvando...' : 'Confirmar Retorno ao Estoque' }}
          </button>
        </footer>
      </div>
    </div>

  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchRecapLotes, fetchPneusEstoqueRecap, enviarParaRecap, confirmarRetornoRecap } from '../../api/gestaoPneus.js'

const props = defineProps({ filiais: { type: Array, default: () => [] } })
const emit = defineEmits(['refresh'])

const recaps = ref([])
const pneusEstoque = ref([])
const salvando = ref(false)

const showModalEnvio = ref(false)
const showModalRetorno = ref(false)
const retornoCtx = ref(null)

const envioForm = ref({ pneu_id: '', recauchutadora: '', data_envio: new Date().toISOString().slice(0, 10), sulco_antes: '' })
const retornoForm = ref({ sulco_novo: '', filial_central_id: '' })
const pneuSelecionado = ref(null)

const emRecap = computed(() => recaps.value.filter(r => r.status === 'enviado'))
const historico = computed(() => recaps.value.filter(r => r.status === 'retornado'))

async function loadData() {
  try {
    recaps.value = await fetchRecapLotes()
  } catch(e) { console.error(e) }
}

async function abrirModalEnvio() {
  try {
    pneusEstoque.value = await fetchPneusEstoqueRecap()
  } catch(e) { console.error(e) }
  envioForm.value = { pneu_id: '', recauchutadora: '', data_envio: new Date().toISOString().slice(0, 10), sulco_antes: '' }
  pneuSelecionado.value = null
  showModalEnvio.value = true
}

function onPneuSelecionado() {
  const p = pneusEstoque.value.find(p => p.id === envioForm.value.pneu_id)
  pneuSelecionado.value = p || null
  if (p) envioForm.value.sulco_antes = p.sulco_atual || ''
}

async function salvarEnvio() {
  if (salvando.value) return
  salvando.value = true
  try {
    await enviarParaRecap({
      pneu_id: envioForm.value.pneu_id,
      recauchutadora: envioForm.value.recauchutadora,
      data_envio: envioForm.value.data_envio,
      sulco_antes: envioForm.value.sulco_antes || null,
    })
    showModalEnvio.value = false
    await loadData()
    emit('refresh')
  } catch(e) { alert(e.message) }
  finally { salvando.value = false }
}

function abrirModalRetorno(recap) {
  retornoCtx.value = recap
  retornoForm.value = { sulco_novo: '', filial_central_id: props.filiais[0]?.id || '' }
  showModalRetorno.value = true
}

async function salvarRetorno() {
  if (salvando.value) return
  salvando.value = true
  try {
    await confirmarRetornoRecap({
      recap_id: retornoCtx.value.id,
      sulco_novo: parseFloat(retornoForm.value.sulco_novo),
      filial_central_id: retornoForm.value.filial_central_id,
    })
    showModalRetorno.value = false
    await loadData()
    emit('refresh')
  } catch(e) { alert(e.message) }
  finally { salvando.value = false }
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR')
}

function diasFora(dataEnvio) {
  if (!dataEnvio) return 0
  const diff = Date.now() - new Date(dataEnvio + 'T12:00:00').getTime()
  return Math.floor(diff / 86400000)
}

function diasClass(dataEnvio) {
  const d = diasFora(dataEnvio)
  if (d > 14) return 'dias-alert'
  if (d > 7) return 'dias-warn'
  return 'dias-ok'
}

onMounted(loadData)
</script>

<style scoped>
.recap-box { background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: 12px; overflow: hidden; box-shadow: var(--shadow-sm); margin-bottom: 20px; }
.recap-box-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--ink-200); background: var(--surface-1); }
.recap-box-title { font-weight: 700; font-size: 14px; color: var(--ink-900); }

.badge-amber { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }

.medida-badge { font-size: 12px; font-weight: 700; color: var(--brand-900); background: var(--brand-100); padding: 2px 8px; border-radius: 5px; }

.dias-badge { padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.dias-ok { background: #f0fdf4; color: #15803d; }
.dias-warn { background: #fef3c7; color: #92400e; }
.dias-alert { background: #fef2f2; color: var(--status-critical); }

.btn-confirmar { padding: 5px 12px; font-size: 12px; font-weight: 600; background: var(--status-ok-bg, #f0fdf4); color: var(--status-ok); border: 1px solid var(--status-ok); border-radius: 7px; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.btn-confirmar:hover { background: var(--status-ok); color: #fff; }

.sulco-ok { color: var(--status-ok); font-weight: 700; }

.section-divider { display: flex; align-items: center; gap: 16px; margin: 4px 0 20px; }
.section-divider::before, .section-divider::after { content: ''; flex: 1; height: 1px; background: var(--ink-200); }
.section-divider span { font-size: 12px; font-weight: 700; color: var(--ink-300); text-transform: uppercase; letter-spacing: 0.06em; white-space: nowrap; }

/* Modal */
.modal-header-gp { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px 16px; border-bottom: 1px solid var(--ink-200); }
.modal-header-gp h3 { font-size: 16px; font-weight: 700; color: var(--ink-900); margin: 0; }
.modal-close { background: none; border: none; cursor: pointer; color: var(--ink-400); padding: 4px; display: flex; align-items: center; }
.modal-body { padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--ink-200); display: flex; justify-content: flex-end; gap: 10px; background: var(--surface-1); }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 12px; font-weight: 600; color: var(--ink-600); text-transform: uppercase; letter-spacing: 0.04em; }
.form-group input, .form-group select { padding: 9px 12px; border: 1px solid var(--ink-200); border-radius: 8px; font-size: 14px; color: var(--ink-900); background: var(--surface-0); }
.form-group input:focus, .form-group select:focus { outline: none; border-color: var(--brand-900); }

.pneu-preview { display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: var(--brand-100); border: 1px solid var(--brand-200, var(--ink-200)); border-radius: 8px; flex-wrap: wrap; }

.retorno-info { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 14px; background: var(--surface-1); border-radius: 8px; border: 1px solid var(--ink-200); }
.retorno-info .lbl { display: block; font-size: 10px; font-weight: 700; color: var(--ink-300); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
</style>
