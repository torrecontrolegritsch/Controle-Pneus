const BASE = import.meta.env.VITE_API_URL && import.meta.env.MODE === 'development' 
  ? import.meta.env.VITE_API_URL 
  : '';

const TOKEN_KEY = 'pneus_access_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY)
}

export function setToken(token, remember = false) {
  const storage = remember ? localStorage : sessionStorage
  storage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(TOKEN_KEY)
}

function getAuthHeaders() {
  const token = getToken()
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

async function handleRes(res) {
  if (res.status === 401) {
    clearToken()
    window.location.reload()
    throw new Error('Sessão expirada')
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || res.statusText)
  }
  return res.json()
}

async function get(path, params = {}) {
  const url = new URL(`${BASE}${path}`, location.origin)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') url.searchParams.set(k, v)
  })
  const res = await fetch(url, { headers: getAuthHeaders() })
  return handleRes(res)
}

async function post(path, body = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify(body),
  })
  return handleRes(res)
}

async function postForm(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body,
  })
  return handleRes(res)
}

async function put(path, body = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'PUT',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify(body),
  })
  return handleRes(res)
}

async function del(path) {
  const res = await fetch(`${BASE}${path}`, { 
    method: 'DELETE',
    headers: getAuthHeaders()
  })
  return handleRes(res)
}

// Auth
export const authLogin = (email, password) => post('/api/auth/login', { email, password })
export const authRegister = (data) => post('/api/auth/register', data)
export const authMe = () => get('/api/auth/me')

const P = '/api/gestao-pneus'

// Configs (público)
export const fetchVehicleConfigs = () => get(`${P}/configs/veiculos`)

// Filiais
export const fetchFiliais = () => get(`${P}/filiais`)
export const createFilial = (data) => post(`${P}/filiais`, data)
export const updateFilial = (id, data) => put(`${P}/filiais/${id}`, data)
export const deleteFilial = (id) => del(`${P}/filiais/${id}`)

// Veículos
export const fetchVeiculos = (params = {}) => get(`${P}/veiculos`, params)
export const fetchVeiculo = (id) => get(`${P}/veiculos/${id}`)
export const createVeiculo = (data) => post(`${P}/veiculos`, data)
export const updateVeiculo = (id, data) => put(`${P}/veiculos/${id}`, data)
export const deleteVeiculo = (id) => del(`${P}/veiculos/${id}`)

// Pneus
export const fetchPneusList = (params = {}) => get(`${P}/pneus`, params)
export const fetchPneuDetail = (id) => get(`${P}/pneus/${id}`)
export const createPneu = (data) => post(`${P}/pneus`, data)
export const updatePneu = (id, data) => put(`${P}/pneus/${id}`, data)

// Importação
export const fetchPneusTemplate = () => {
  const token = getToken()
  const baseUrl = `${BASE}${P}/pneus/template`
  return token ? `${baseUrl}?token=${token}` : baseUrl
}
export const importPneusCsv = (data) => postForm(`${P}/pneus/importar`, data)

// Operações
export const alocarPneu = (data) => post(`${P}/alocar`, data)
export const removerPneu = (data) => post(`${P}/remover`, data)
export const transferirPneu = (data) => post(`${P}/transferir`, data)
export const confirmarRecebimento = (pneuId) => post(`${P}/confirmar-recebimento`, { pneu_id: pneuId })
export const rodizioPneu = (data) => post(`${P}/rodizio`, data)

// Movimentações
export const fetchMovimentacoes = (params = {}) => get(`${P}/movimentacoes`, params)

// Dashboard
export const fetchGPDashboard = () => get(`${P}/dashboard`)

// Busca SQL Server
export const fetchBuscaVeiculoSql = (placa) => get(`${P}/busca-veiculo-sql/${placa}`)
export const fetchSincronizarVeiculosSql = (limite = 5000) =>
  fetch(`${BASE}${P}/sincronizar-veiculos-sql?limite=${limite}`, { 
    method: 'POST',
    headers: getAuthHeaders()
  }).then(handleRes)

// Reciclagem e Financeiro
export const fetchLotesReciclagem = (params = {}) => get(`${P}/reciclagem/lotes`, params)
export const fetchPneusAguardandoLote = (params = {}) => get(`${P}/reciclagem/aguardando`, params)
export const enviarParaReciclagem = (data) => post(`${P}/reciclagem/enviar`, data)
export const atualizarValorLote = (data) => post(`${P}/reciclagem/atualizar-valor`, data)
export const fetchRelatorioFinanceiroReciclagem = (params = {}) => get(`${P}/reciclagem/relatorio-financeiro`, params)
export const criarLoteReciclagem = (data) => post(`${P}/reciclagem/criar-lote`, data)