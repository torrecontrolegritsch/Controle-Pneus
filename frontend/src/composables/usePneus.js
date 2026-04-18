// Composables para gestão de pneus
import { ref, computed } from 'vue'
import * as api from '../api/gestaoPneus.js'

// Estado global reativo
const filiais = ref([])
const veiculos = ref([])
const pneus = ref([])
const movimentacoes = ref([])
const vehicleConfigs = ref({})
const loading = ref(false)
const error = ref(null)

// Carregar configurações de veículos
export function useVehicleConfigs() {
  const loadConfigs = async () => {
    try {
      vehicleConfigs.value = await api.fetchVehicleConfigs()
    } catch (e) {
      console.error('Erro ao carregar configs:', e)
    }
  }
  return { vehicleConfigs, loadConfigs }
}

// Filiais
export function useFiliais() {
  const loadFiliais = async () => {
    loading.value = true
    error.value = null
    try {
      filiais.value = await api.fetchFiliais()
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  const createFilial = async (data) => {
    const result = await api.createFilial(data)
    filiais.value.push(result)
    return result
  }

  const updateFilial = async (id, data) => {
    const result = await api.updateFilial(id, data)
    const idx = filiais.value.findIndex(f => f.id === id)
    if (idx >= 0) filiais.value[idx] = { ...filiais.value[idx], ...result }
    return result
  }

  const deleteFilial = async (id) => {
    await api.deleteFilial(id)
    filiais.value = filiais.value.filter(f => f.id !== id)
  }

  return { filiais, loading, error, loadFiliais, createFilial, updateFilial, deleteFilial }
}

// Veículos
export function useVeiculos() {
  const loadVeiculos = async (filialId = null) => {
    loading.value = true
    error.value = null
    try {
      veiculos.value = await api.fetchVeiculos({ filial_id: filialId })
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  const createVeiculo = async (data) => {
    const result = await api.createVeiculo(data)
    veiculos.value.push(result)
    return result
  }

  const updateVeiculo = async (id, data) => {
    const result = await api.updateVeiculo(id, data)
    const idx = veiculos.value.findIndex(v => v.id === id)
    if (idx >= 0) veiculos.value[idx] = { ...veiculos.value[idx], ...result }
    return result
  }

  const deleteVeiculo = async (id) => {
    await api.deleteVeiculo(id)
    veiculos.value = veiculos.value.filter(v => v.id !== id)
  }

  const getVeiculoDetalhe = async (id) => {
    return await api.fetchVeiculo(id)
  }

  return { veiculos, loading, error, loadVeiculos, createVeiculo, updateVeiculo, deleteVeiculo, getVeiculoDetalhe }
}

// Pneus
export function usePneus() {
  const loadPneus = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      pneus.value = await api.fetchPneusList(params)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  const createPneu = async (data) => {
    const result = await api.createPneu(data)
    pneus.value.push(result)
    return result
  }

  const updatePneu = async (id, data) => {
    const result = await api.updatePneu(id, data)
    const idx = pneus.value.findIndex(p => p.id === id)
    if (idx >= 0) pneus.value[idx] = { ...pneus.value[idx], ...result }
    return result
  }

  const getPneuDetalhe = async (id) => {
    return await api.fetchPneuDetail(id)
  }

  // Alocar pneu em veículo
  const alocarPneu = async (pneuId, veiculoId, posicao, kmInstalacao = 0) => {
    const result = await api.alocarPneu({
      pneumatic_id: pneId,
      veiculo_id: veiculoId,
      posicao,
      km_instalacao: kmInstalacao
    })
    // Atualiza o estado
    const idx = pneus.value.findIndex(p => p.id === pneId)
    if (idx >= 0) {
      pneus.value[idx].status = 'alocado'
      pneus.value[idx].veiculo_id = veiculoId
    }
    return result
  }

  // Remover/Alocar do veículo
  const removerPneu = async (pneuId, destino, kmMomento = 0, filialDestinoId = null) => {
    const result = await api.removerPneu({
      pneumatic_id: pneId,
      destino,
      km_momento: kmMomento,
      filial_destino_id: filialDestinoId
    })
    // Atualiza o estado
    const idx = pneus.value.findIndex(p => p.id === pneId)
    if (idx >= 0) {
      pneus.value[idx].status = destino
      pneus.value[idx].veiculo_id = null
    }
    return result
  }

  return { 
    pneus, 
    loading, 
    error, 
    loadPneus, 
    createPneu, 
    updatePneu, 
    getPneuDetalhe,
    alocarPneu,
    removerPneu
  }
}

// Movimentações
export function useMovimentacoes() {
  const loadMovimentacoes = async (params = {}) => {
    loading.value = true
    try {
      movimentacoes.value = await api.fetchMovimentacoes(params)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  return { movimentacoes, loading, error, loadMovimentacoes }
}

// Dashboard
export function useDashboard() {
  const dash = ref(null)
  
  const loadDashboard = async () => {
    loading.value = true
    error.value = null
    try {
      dash.value = await api.fetchGPDashboard()
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  return { dash, loading, error, loadDashboard }
}