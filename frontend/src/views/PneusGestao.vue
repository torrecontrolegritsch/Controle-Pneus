<template>
  <div class="app-layout">
    <!-- SIDEBAR NAV -->
    <aside class="sidebar">
      <div class="sidebar-top">
        <img src="/logo.jpg" alt="Logo" class="sidebar-logo" />
      </div>

      <nav class="sidebar-menu">
        <button
          v-for="t in visibleTabs"
          :key="t.id"
          class="menu-item"
          :class="{ active: tab === t.id }"
          @click="tab = t.id"
        >
          <span class="menu-icon" v-html="t.icon"></span>
          <span class="menu-label">{{ t.label }}</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <!-- Atalho Usuários (admin/gerente) -->
        <button
          v-if="user?.role === 'admin' || user?.role === 'gerente'"
          class="usuarios-shortcut"
          :class="{ active: tab === 'usuarios' }"
          @click="tab = 'usuarios'"
          title="Gerenciar Usuários e Permissões"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          Usuários &amp; Permissões
        </button>

        <div class="user-block" v-if="user">
          <div class="avatar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          </div>
          <div class="u-info">
            <span class="u-name">{{ user?.nome || user?.email?.split('@')[0] }}</span>
            <span class="u-tag">{{ user?.role === 'admin' ? 'Administrador' : (user?.role === 'gerente' ? 'Gerente' : 'Operador') }}</span>
          </div>
          <button class="mini-logout" @click="$emit('logout')" title="Sair">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- CONTENT AREA -->
    <main class="main-content">
      <header class="content-header">
        <div class="header-info">
          <h1>{{ currentTabLabel }}</h1>
          <p class="header-sub">{{ currentTabSubtitle }}</p>
        </div>

        <div class="header-kpis" v-if="dash">
          <div class="kpi-box">
             <span class="kpi-n">{{ dash.total_pneus }}</span>
             <span class="kpi-t">Total</span>
          </div>
          <div class="kpi-box kpi-blue">
             <span class="kpi-n">{{ dash.em_uso }}</span>
             <span class="kpi-t">Em Uso</span>
          </div>
          <div class="kpi-box kpi-green">
             <span class="kpi-n">{{ dash.em_estoque }}</span>
             <span class="kpi-t">Estoque</span>
          </div>
          <div class="kpi-box kpi-red">
             <span class="kpi-n">{{ dash.descartados }}</span>
             <span class="kpi-t">Descarte</span>
          </div>
          <div class="kpi-box kpi-gold">
             <span class="kpi-n">R$ {{ fmtN(dash.valor_estoque) }}</span>
             <span class="kpi-t">Patrimônio</span>
          </div>
        </div>
      </header>

    <!-- TAB: DASHBOARD -->
    <DashboardView v-if="tab === 'dashboard'" />

    <!-- TAB: ESTOQUE CENTRAL (NOVO) -->
    <EstoqueCentralView v-if="tab === 'estoque_central'" :filiais="filiais" />

    <!-- TAB: ALOCAÇÕES (NOVA) -->
    <section v-if="tab === 'alocacoes'" class="gp-section alocacao-layout">
      <!-- SIDEBAR BUSCA -->
      <div class="aloc-sidebar">
        <div class="search-box">
          <label>Buscar Veículo</label>
          <div class="input-with-icon">
            <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input v-model="searchVeiculo" placeholder="Placa ou Frota..." class="stock-input" />
          </div>
        </div>
        
        <div class="aloc-veiculo-list">
          <div v-for="v in filteredVeiculos" :key="v.id" 
               class="aloc-v-card" :class="{ active: veiculoDetail?.id === v.id }"
               @click="openVeiculoDetail(v)">
            <div class="v-card-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><path d="M10 9h4"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
            </div>
            <div class="v-card-info">
              <span class="v-placa">{{ v.placa }}</span>
              <span class="v-modelo">{{ v.modelo }}</span>
            </div>
            <div class="v-card-status">
               <span class="badge" :class="countPneusAlocados(v.id) === countPneus(v.tipo) ? 'badge-green' : 'badge-yellow'">
                 {{ countPneusAlocados(v.id) }}/{{ countPneus(v.tipo) }}
               </span>
            </div>
          </div>
          <div v-if="!filteredVeiculos.length" class="empty-mini">Nenhum veículo encontrado</div>
        </div>
      </div>

      <!-- ÁREA DE TRABALHO -->
      <div class="aloc-workbench">
        <div v-if="veiculoDetail" class="workbench-content">
          <!-- INFO STRIP (Vipal-style) -->
          <div class="wb-strip">
            <div class="wb-strip-placa">
              <div class="wsp-br">BRASIL</div>
              <div class="wsp-num">{{ veiculoDetail.placa }}</div>
            </div>
            <div class="wb-strip-sep"></div>
            <div class="wb-strip-metas">
              <div class="strip-meta" v-if="veiculoDetail.frota">
                <span class="sm-lbl">Frota</span>
                <span class="sm-val">{{ veiculoDetail.frota }}</span>
              </div>
              <div class="strip-meta">
                <span class="sm-lbl">Categoria</span>
                <span class="sm-val">{{ configLabel(veiculoDetail.tipo) }}</span>
              </div>
              <div class="strip-meta" v-if="veiculoDetail.modelo">
                <span class="sm-lbl">Modelo</span>
                <span class="sm-val">{{ veiculoDetail.modelo }}</span>
              </div>
              <div class="strip-meta">
                <span class="sm-lbl">Hodômetro</span>
                <span class="sm-val">{{ (veiculoDetail.km_atual || 0).toLocaleString('pt-BR') }} km</span>
              </div>
              <div class="strip-meta">
                <span class="sm-lbl">Pneus</span>
                <span class="sm-val" :class="countPneusAlocados(veiculoDetail.id) === countPneus(veiculoDetail.tipo) ? 'strip-ok' : 'strip-warn'">
                  {{ countPneusAlocados(veiculoDetail.id) }}/{{ countPneus(veiculoDetail.tipo) }}
                </span>
              </div>
            </div>
            <button class="strip-edit-btn" @click="openVeiculoForm(veiculoDetail)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>
              Editar
            </button>
          </div>

          <div class="wb-body">
             <!-- DIAGRAMA -->
             <div class="gp-vehicle-canvas">
                <div class="vehicle-diagram-area">
                  <div class="chassis-box">
                    <div class="placa-box">
                      <div class="placa-br">BRASIL</div>
                      <div class="placa-num">{{ veiculoDetail.placa }}</div>
                    </div>
                    <div class="chassis-vertical-line"></div>
                  </div>

                  <div class="axles-container">
                    <div v-for="eixo in veiculoDetail.config?.eixos" :key="eixo.num" class="axle-row">
                      <div class="axle-visual">
                        <div class="wheels-side side-esq">
                          <div v-for="pos in eixo.posicoes.filter(p => p.includes('ESQ'))" :key="pos" 
                               class="tire-drop-zone"
                               :class="{ occupied: veiculoDetail.pneus[pos], 'drag-over': dragOverPos === pos }"
                               @dragover.prevent="dragOverPos = pos"
                               @dragleave="dragOverPos = null"
                               @drop="handleDropOnSlot(pos)"
                               @click="handleTireClick(pos)">
                            <div v-if="veiculoDetail.pneus[pos]" class="tire-item in-vehicle"
                                 :class="tireStatusClass(veiculoDetail.pneus[pos])"
                                 draggable="true" @dragstart="handleDragStartFromVehicle($event, pos, veiculoDetail.pneus[pos])">
                              <div class="tire-id">{{ veiculoDetail.pneus[pos].numero_fogo }}</div>
                            </div>
                            <div v-else class="tire-placeholder"><span>+</span></div>
                          </div>
                        </div>
                        <div class="axle-bar"></div>
                        <div :class="['center-shape', eixo.num === 1 ? 'shape-diamond' : 'shape-circle']"></div>
                        <div class="wheels-side side-dir">
                          <div v-for="pos in eixo.posicoes.filter(p => p.includes('DIR'))" :key="pos" 
                               class="tire-drop-zone"
                               :class="{ occupied: veiculoDetail.pneus[pos], 'drag-over': dragOverPos === pos }"
                               @dragover.prevent="dragOverPos = pos"
                               @dragleave="dragOverPos = null"
                               @drop="handleDropOnSlot(pos)"
                               @click="handleTireClick(pos)">
                            <div v-if="veiculoDetail.pneus[pos]" class="tire-item in-vehicle"
                                 :class="tireStatusClass(veiculoDetail.pneus[pos])"
                                 draggable="true" @dragstart="handleDragStartFromVehicle($event, pos, veiculoDetail.pneus[pos])">
                              <div class="tire-id">{{ veiculoDetail.pneus[pos].numero_fogo }}</div>
                            </div>
                            <div v-else class="tire-placeholder"><span>+</span></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="spare-container" v-if="veiculoDetail.config?.estepes?.length">
                    <div class="spare-title">Estepes</div>
                    <div v-for="pos in veiculoDetail.config.estepes" :key="pos" 
                         class="tire-drop-zone spare-zone"
                         :class="{ occupied: veiculoDetail.pneus[pos], 'drag-over': dragOverPos === pos }"
                         @dragover.prevent="dragOverPos = pos"
                         @dragleave="dragOverPos = null"
                         @drop="handleDropOnSlot(pos)"
                         @click="handleTireClick(pos)">
                      <div v-if="veiculoDetail.pneus[pos]" class="tire-item in-vehicle"
                           :class="tireStatusClass(veiculoDetail.pneus[pos])"
                           draggable="true" @dragstart="handleDragStartFromVehicle($event, pos, veiculoDetail.pneus[pos])">
                        <div class="tire-id">{{ veiculoDetail.pneus[pos].numero_fogo }}</div>
                      </div>
                      <div v-else class="tire-placeholder"><span>+</span></div>
                    </div>
                  </div>
                </div>
             </div>

              <!-- COLUNA DE AÇÕES -->
              <div class="wb-action-col">
                <span class="action-col-label">Ações</span>
                <div
                  class="action-card action-sucata"
                  :class="{ 'drag-over': dragOverRemoval }"
                  @dragover.prevent="dragOverRemoval = true"
                  @dragleave="dragOverRemoval = false"
                  @drop="handleDropOnRemoval('sucata')"
                  title="Arraste pneu para descartar"
                >
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
                  <span>Sucata</span>
                </div>
                <div
                  class="action-card action-estoque"
                  :class="{ 'drag-over': dragOverEstoque }"
                  @dragover.prevent="dragOverEstoque = true"
                  @dragleave="dragOverEstoque = false"
                  @drop="handleDropOnRemoval('estoque')"
                  title="Arraste pneu para devolver ao estoque"
                >
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>
                  <span>Estoque</span>
                </div>
              </div>

              <!-- PAINEL DE ESTOQUE (GRID VIPAL) -->
              <div class="gp-stock-panel">
                <!-- Header com tabs -->
                <div class="stock-panel-head">
                  <div class="stock-tabs-row">
                    <button class="stock-tab stock-tab-active">
                      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/></svg>
                      Almoxarifado
                      <span class="stock-tab-count">{{ pneusEstoqueFilial.length }}</span>
                    </button>
                  </div>
                </div>

                <!-- Filtros -->
                <div class="stock-panel-filters">
                  <select
                    v-model="almoxarifadoFilialId"
                    :disabled="!!veiculoDetail"
                    class="stock-filial-sel"
                    @change="loadEstoqueAlmoxarifado"
                  >
                    <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
                  </select>
                  <div class="stock-search-wrap">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                    <input v-model="searchStock" placeholder="Pesquisar..." class="stock-search-inp" />
                  </div>
                </div>

                <!-- GRADE DE PNEUS -->
                <div class="stock-tire-grid" @dragover.prevent @drop="handleDropOnRemoval('estoque')">
                  <template v-for="grupo in filteredStockByMedida" :key="grupo.medida">
                    <div class="grid-medida-lbl">
                      <span>{{ grupo.medida }}</span>
                      <span class="grid-medida-cnt">{{ grupo.pneus.length }}</span>
                    </div>
                    <div class="grid-tires-row">
                      <div
                        v-for="p in grupo.pneus" :key="p.id"
                        class="grid-tire-item"
                        :class="{
                          'gt-pending': p.recebido === 0,
                          'gt-new':     p.recebido === 1 && (p.km_total||0) <= 0 && (Number(p.vida)==1||String(p.vida).startsWith('1')),
                          'gt-worn':    p.recebido === 1 && (p.km_total||0) > 0 && p.sulco_atual > 0 && p.sulco_atual < 4,
                          'gt-used':    p.recebido === 1 && (p.km_total||0) > 0 && !(p.sulco_atual > 0 && p.sulco_atual < 4)
                        }"
                        draggable="true"
                        @dragstart="handleDragStartFromStock($event, p)"
                        @click.stop="p.recebido === 0 && confirmarChegadaEstoque(p)"
                        :title="p.recebido === 0 ? 'Clique para confirmar chegada' : p.numero_fogo + ' · ' + p.marca + ' · sulco ' + (p.sulco_atual||0) + 'mm'"
                      >
                        <div class="gt-body">
                          <span class="gt-num">{{ p.numero_fogo }}</span>
                          <div v-if="p.recebido === 0" class="gt-pending-dot" title="Aguardando chegada">!</div>
                        </div>
                        <div class="gt-sulco">{{ p.sulco_atual || 0 }}mm</div>
                      </div>
                    </div>
                  </template>
                  <div v-if="!filteredStock.length" class="empty-stock">Sem pneus no estoque</div>
                </div>
              </div>
          </div>
        </div>
        <div v-else class="empty-state" style="border:none; background:transparent;">
          <div class="select-v-prompt">
            <span class="prompt-icon">
               <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><path d="M10 9h4"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
            </span>
            <h3>Selecione um veículo</h3>
            <p>Utilize a barra de pesquisa à esquerda para selecionar uma placa.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB: FILIAIS -->
    <FiliaisView v-if="tab === 'filiais'" :filiais="filiais" @refresh="loadFiliais" />

    <!-- TAB: VEÍCULOS -->
    <section v-if="tab === 'veiculos'" class="gp-section">
      <div class="sec-toolbar">
        <h2>Veículos</h2>
        <select v-model="filtroFilialV" @change="loadVeiculos" class="filter-select">
          <option value="">Todas as filiais</option>
          <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
        </select>

        <button class="btn-primary" @click="openVeiculoForm()">+ Novo Veículo</button>
      </div>
      <div class="table-responsive" v-if="veiculos.length">
        <table class="gp-table">
          <thead><tr><th>Placa</th><th>Frota</th><th>Modelo</th><th>Tipo</th><th>Filial</th><th>Pneus</th><th>Odômetro</th><th>Ações</th></tr></thead>
        <tbody>
           <tr v-for="v in veiculos" :key="v.id">
            <td>
              <div style="display: flex; align-items: center; gap: 8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><path d="M10 9h4"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
                <strong>{{ v.placa }}</strong>
              </div>
            </td>
            <td>{{ v.frota }}</td>
            <td>{{ v.modelo }}</td>
            <td>
              <select class="inline-select" v-model="v.tipo" @change="saveVeiculoInline(v)">
                <option v-for="(cfg, key) in vehicleConfigs" :key="key" :value="key">{{ cfg.nome }}</option>
              </select>
            </td>
            <td>
              <select class="inline-select" v-model="v.filial_id" @change="saveVeiculoInline(v)" :style="v.filial_id && !filiais.find(f => f.id === v.filial_id) ? 'border-color: var(--red); color: var(--red);' : ''">
                <option :value="null">— Sem Filial —</option>
                <option v-if="v.filial_id && !filiais.find(f => f.id === v.filial_id)" :value="v.filial_id">
                  ⚠️ ID: {{ v.filial_id }} (Inexistente)
                </option>
                <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
              </select>
            </td>
            <td><span class="badge" :class="countPneusAlocados(v.id) === countPneus(v.tipo) ? 'badge-green' : 'badge-yellow'">{{ countPneusAlocados(v.id) }}/{{ countPneus(v.tipo) }}</span></td>
            <td>
              <span v-if="v.km_atual" class="badge badge-purple" style="font-weight: 800">{{ (v.km_atual || 0).toLocaleString('pt-BR') }} <span style="font-size: 9px; opacity: 0.8">KM</span></span>
              <span v-else style="color: var(--text3); font-size: 11px;">Sem dados</span>
            </td>
            <td class="td-actions">
              <button class="btn-sm" @click="openVeiculoForm(v)">Editar</button>
              <button class="btn-sm btn-danger" @click="removeVeiculo(v)">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
      <div v-else class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px;"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><path d="M10 9h4"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
        <p>Nenhum veículo cadastrado na base de dados.</p>
        <p style="font-size: 11px; color: var(--text3); margin-top: 4px;">Utilize a Sincronização SQL Server ou cadastre manualmente.</p>
      </div>
    </section>

    <!-- TAB: ESTOQUE -->
    <section v-if="tab === 'estoque'" class="gp-section">
      <div class="sec-toolbar">
        <h2>Gerenciar Pneus</h2>
        <div style="display: flex; gap: 12px; margin-left: auto;">
          <select v-model="filtroFilialP" @change="loadPneus" class="filter-select">
            <option value="">Todas as filiais</option>
            <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
          </select>
          <select v-model="filtroStatus" @change="loadPneus" class="filter-select">
            <option value="">Todos os status</option>
            <option value="estoque">Em Estoque</option>
            <option value="em_uso">Em Uso</option>
            <option value="descarte">Descartados</option>
            <option value="recapagem">Em Recapagem</option>
          </select>
        </div>
      </div>
      <!-- Agrupamento Filial → Medida -->
      <div v-if="gruposFilialMedida.length" class="est-filial-list">
        <div v-for="gf in gruposFilialMedida" :key="gf.filial" class="est-filial-card">

          <!-- Header Filial -->
          <div class="est-filial-header" @click="toggleFilialEst(gf.filial)">
            <div class="est-filial-left">
              <span class="est-chevron" :class="{ open: expandedFilialEst.has(gf.filial) }">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
              </span>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:#64748b"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              <span class="est-filial-nome">{{ gf.filial }}</span>
              <span class="est-filial-badge">{{ gf.qtd }} pneu{{ gf.qtd !== 1 ? 's' : '' }}</span>
            </div>
            <div class="est-status-pills">
              <span v-if="gf.statusTotais.em_uso"    class="est-pill pill-uso">{{ gf.statusTotais.em_uso }} em uso</span>
              <span v-if="gf.statusTotais.estoque"   class="est-pill pill-est">{{ gf.statusTotais.estoque }} estoque</span>
              <span v-if="gf.statusTotais.reciclagem" class="est-pill pill-rec">{{ gf.statusTotais.reciclagem }} reciclagem</span>
              <span v-if="gf.statusTotais.descarte"  class="est-pill pill-des">{{ gf.statusTotais.descarte }} descarte</span>
            </div>
          </div>

          <!-- Medidas dentro da filial -->
          <div v-if="expandedFilialEst.has(gf.filial)" class="est-medidas">
            <div v-for="gm in gf.medidas" :key="gm.medida" class="est-medida-grupo">

              <!-- Header Medida -->
              <div class="est-medida-header" @click="toggleMedidaEst(gf.filial, gm.medida)">
                <span class="est-chevron est-chevron-sm" :class="{ open: expandedMedidaEst.has(gf.filial+'|'+gm.medida) }">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
                </span>
                <span class="est-medida-tag">{{ gm.medida }}</span>
                <span class="est-medida-qtd">{{ gm.qtd }} pneu{{ gm.qtd !== 1 ? 's' : '' }}</span>
                <div class="est-medida-meta">
                  <span v-if="gm.sulcoMedio > 0" :class="gm.sulcoMedio < 5 ? 'meta-critico' : 'meta-ok'">
                    sulco médio {{ gm.sulcoMedio.toFixed(1) }}mm
                  </span>
                  <span class="meta-vida">vida média {{ gm.vidaMedia.toFixed(1) }}ª</span>
                </div>
                <div class="est-medida-status">
                  <span v-if="gm.statusCount.em_uso"    class="est-pill pill-uso pill-xs">{{ gm.statusCount.em_uso }} uso</span>
                  <span v-if="gm.statusCount.estoque"   class="est-pill pill-est pill-xs">{{ gm.statusCount.estoque }} estoque</span>
                  <span v-if="gm.statusCount.reciclagem" class="est-pill pill-rec pill-xs">{{ gm.statusCount.reciclagem }} recicl.</span>
                </div>
              </div>

              <!-- Tabela dos pneus da medida -->
              <div v-if="expandedMedidaEst.has(gf.filial+'|'+gm.medida)" class="est-pneus-table">
                <table class="gm-table">
                  <thead>
                    <tr>
                      <th>N.Fogo</th>
                      <th>Marca / Modelo</th>
                      <th>Vida</th>
                      <th>Sulco</th>
                      <th>Status</th>
                      <th>Veículo</th>
                      <th>Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="p in gm.pneus" :key="p.id" :class="{'row-disabled': p.status === 'descarte'}">
                      <td><strong class="fogo-est">{{ p.numero_fogo }}</strong></td>
                      <td class="td-marca-est">{{ p.marca }} <span class="modelo-est">{{ p.modelo }}</span></td>
                      <td><span class="vida-badge">{{ p.vida }}ª</span></td>
                      <td>
                        <div class="sulco-wrap">
                          <div class="sulco-bar-mini">
                            <div class="sulco-fill-mini" :class="{ 'sulco-crit': (p.sulco_atual||0) < 5 }" :style="{ width: Math.min(100, (p.sulco_atual||0)/20*100)+'%' }"></div>
                          </div>
                          <span class="sulco-val-mini" :class="{ 'sulco-crit': (p.sulco_atual||0) < 5 }">{{ p.sulco_atual || 0 }}mm</span>
                        </div>
                      </td>
                      <td>
                        <span class="badge" :class="statusClass(p)">{{ statusLabel(p) }}</span>
                        <span v-if="p.recebido === 0" class="badge badge-yellow" style="margin-top:3px;display:block;font-size:9px;">TRÂNSITO</span>
                      </td>
                      <td class="td-placa-est">{{ p.veiculo_placa || '—' }}</td>
                      <td class="td-actions">
                        <button v-if="p.recebido === 0" class="btn-sm btn-accent" @click="doConfirmarRecebimento(p)">Confirmar</button>
                        <button class="btn-sm" @click="openPneuForm(p)">Editar</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px;"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="M5 5l1.5 1.5"/></svg>
        <p>Nenhum pneu atende aos filtros atuais.</p>
        <p style="font-size: 11px; color: var(--text3); margin-top: 4px;">Utilize a aba "Controle de Estoque" para realizar novos cadastros.</p>
      </div>
    </section>

    <!-- TAB: SUCATA -->
    <SucataView v-if="tab === 'sucata'" :pneus-geral="pneusGeral" :filiais="filiais" @refresh="() => { loadPneusGeral(); refreshDash() }" />

    <!-- TAB: HISTÓRICO -->
    <HistoricoView v-if="tab === 'historico'" />

    <!-- TAB: RECICLADORA -->
    <ReciclagemView v-if="tab === 'recicladora'" @refresh="() => { loadPneusGeral(); refreshDash() }" />

    <!-- TAB: FINANCEIRO -->
    <FinanceiroView v-if="tab === 'financeiro'" :filiais="filiais" />

    <!-- MODAL: VEÍCULO FORM -->
    <div v-if="showVeiculoModal" class="modal-overlay" @click.self="showVeiculoModal = false">
      <div class="modal-box">
        <header class="modal-header-gp">
          <h3>{{ editingVeiculo ? 'Editar Veículo' : 'Novo Veículo' }}</h3>
        </header>
        
        <div class="form-row">
          <div class="form-group">
            <label style="display: flex; justify-content: space-between; align-items: center;">
              Placa
              <span v-if="buscandoPlaca"
                    style="color: var(--brand); font-size: 11px; display:flex; align-items:center; gap:4px;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
                     style="animation: spin 1s linear infinite;">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                </svg>
                Buscando...
              </span>
              <span v-else-if="!editingVeiculo && veiculoForm.placa && veiculoForm.placa.replace('-','').length >= 7"
                    @click="buscarPlacaSQL()"
                    style="color: var(--brand); cursor: pointer; text-transform: none; font-size: 11px;">
                🔍 Autocompletar (SQL)
              </span>
            </label>
            <input v-model="veiculoForm.placa" placeholder="ABC1D23" @blur="buscarPlacaSQL" />
          </div>
          <div class="form-group"><label>Frota</label><input v-model="veiculoForm.frota" placeholder="000" /></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Marca</label><input v-model="veiculoForm.marca" placeholder="Ex: Scania, Volvo" /></div>
          <div class="form-group"><label>Modelo</label><input v-model="veiculoForm.modelo" placeholder="Ex: R450" /></div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Configuração de Eixos</label>
            <select v-model="veiculoForm.tipo" class="select-premium">
              <option v-for="(cfg, key) in vehicleConfigs" :key="key" :value="key">
                {{ cfg.nome }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label style="display:flex; justify-content:space-between; align-items:center;">
              Filial Responsável
              <span v-if="autoPreenchido.filial" style="font-size:10px; color:#16a34a; font-weight:600;">✓ preenchido via SQL</span>
            </label>
            <select v-model="veiculoForm.filial_id"
                    :style="autoPreenchido.filial ? 'border-color:#16a34a; background:#f0fdf4;' : ''">
              <option :value="null">— Selecione —</option>
              <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label style="display:flex;justify-content:space-between;align-items:center;">
              KM Odômetro Confirmado
              <span v-if="autoPreenchido.km" style="font-size:10px; color:#16a34a; font-weight:600;">✓ preenchido via SQL</span>
              <span v-else style="font-size:10px;color:var(--s5);font-weight:400;">preenchido automático via SQL</span>
            </label>
            <input type="number" v-model.number="veiculoForm.km_atual" placeholder="0" min="0"
                   :style="autoPreenchido.km ? 'border-color:#16a34a; background:#f0fdf4;' : ''" />
          </div>
        </div>

        <!-- Preview da Configuração -->
        <div class="config-preview-box" v-if="veiculoForm.tipo && vehicleConfigs[veiculoForm.tipo]">
          <div class="preview-info">
            <div class="p-item">
              <span class="p-icon">🚛</span>
              <span class="p-text"><strong>{{ vehicleConfigs[veiculoForm.tipo].eixos.length }}</strong> Eixos</span>
            </div>
            <div class="p-item">
              <span class="p-icon">🛞</span>
              <span class="p-text"><strong>{{ countPneus(veiculoForm.tipo) }}</strong> Pneus no total</span>
            </div>
          </div>
          <p class="preview-desc">Esta configuração inclui {{ vehicleConfigs[veiculoForm.tipo].estepes.length }} estepe(s).</p>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="showVeiculoModal = false">Cancelar</button>
          <button class="btn-primary" @click="saveVeiculo" :disabled="!veiculoForm.placa || !veiculoForm.tipo">
            Confirmar Cadastro
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL: PNEU FORM -->
    <div v-if="showPneuModal" class="modal-overlay" @click.self="showPneuModal = false">
      <div class="modal-box">
        <h3>{{ editingPneu ? 'Editar Pneu' : 'Novo Pneu' }}</h3>
        
        <div class="form-group" v-if="!editingPneu">
          <label>Modelo Pré-Cadastrado</label>
          <select class="select-premium" v-model="modeloSelecionado" @change="fillModelo">
            <option :value="null">— Selecione para preencher marca/medida —</option>
            <option v-for="(m, i) in modelosPreCadastrados" :key="i" :value="m">
              {{ m.marca }} {{ m.modelo ? '- ' + m.modelo : '' }} ({{ m.medida }})
            </option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group"><label>N. Fogo</label><input v-model="pneuForm.numero_fogo" placeholder="Número de fogo" /></div>
          <div class="form-group"><label>DOT</label><input v-model="pneuForm.dot" placeholder="Ex: 2024" /></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Marca</label><input v-model="pneuForm.marca" placeholder="Bridgestone, Pirelli..." /></div>
          <div class="form-group"><label>Modelo</label><input v-model="pneuForm.modelo" /></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Medida</label><input v-model="pneuForm.medida" placeholder="295/80R22.5" /></div>
          <div class="form-group"><label>Vida</label><input type="number" v-model.number="pneuForm.vida" min="1" max="5" /></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Valor (R$)</label><input type="number" v-model.number="pneuForm.valor" step="0.01" /></div>
          <div class="form-group"><label>Sulco (mm)</label><input type="number" v-model.number="pneuForm.sulco_atual" step="0.1" /></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>Fornecedor</label><input v-model="pneuForm.fornecedor" placeholder="Nome do Fornecedor" /></div>
          <div class="form-group"><label>NF Fiscal</label><input v-model="pneuForm.nf" placeholder="Número da Nota" /></div>
        </div>
        <div class="form-group">
          <label>Filial</label>
          <select v-model="pneuForm.filial_id">
            <option :value="null">— Selecione —</option>
            <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showPneuModal = false">Cancelar</button>
          <button class="btn-primary" @click="savePneu" :disabled="!pneuForm.numero_fogo || !pneuForm.marca || !pneuForm.medida || !pneuForm.filial_id">Salvar</button>
        </div>
      </div>
    </div>

    <!-- MODAL: DETALHE DO VEÍCULO (EIXOS) -->
    <div v-if="showEixosModal" class="modal-overlay" @click.self="showEixosModal = false">
      <div class="modal-box modal-expanded">
        <header class="modal-header-gp">
          <div>
            <h3>{{ veiculoDetail?.placa }} — {{ veiculoDetail?.modelo }}</h3>
            <span class="vd-config-badge">{{ configLabel(veiculoDetail?.tipo) }}</span>
          </div>
          <button class="btn-close" @click="showEixosModal = false">&times;</button>
        </header>

        <div class="gp-move-container">
          <!-- LADO ESQUERDO: DIAGRAMA DO VEÍCULO -->
          <div class="gp-vehicle-canvas">
            <div class="vehicle-diagram-area">
              <!-- CHASSIS -->
              <div class="chassis-box">
                <div class="placa-box">
                  <div class="placa-br">BRASIL</div>
                  <div class="placa-num">{{ veiculoDetail?.placa || 'AAA-1234' }}</div>
                </div>
                <div class="chassis-vertical-line"></div>
              </div>

              <div class="axles-container">
                <div v-for="eixo in veiculoDetail?.config?.eixos" :key="eixo.num" class="axle-row">
                  <div class="axle-visual">
                    <div class="wheels-side side-esq">
                      <div v-for="pos in eixo.posicoes.filter(p => p.includes('ESQ'))" :key="pos" 
                           class="tire-drop-zone"
                           :class="{ occupied: veiculoDetail.pneus[pos], 'drag-over': dragOverPos === pos }"
                           @dragover.prevent="dragOverPos = pos"
                           @dragleave="dragOverPos = null"
                           @drop="handleDropOnSlot(pos)"
                           @click="handleTireClick(pos)">
                        
                        <div v-if="veiculoDetail.pneus[pos]" class="tire-item in-vehicle"
                             :class="tireStatusClass(veiculoDetail.pneus[pos])"
                             draggable="true" @dragstart="handleDragStartFromVehicle($event, pos, veiculoDetail.pneus[pos])">
                          <div class="tire-id">{{ veiculoDetail.pneus[pos].numero_fogo }}</div>
                        </div>
                        <div v-else class="tire-placeholder">
                          <span>+</span>
                        </div>
                      </div>
                    </div>

                    <div class="axle-bar"></div>
                    <div :class="['center-shape', eixo.num === 1 ? 'shape-diamond' : 'shape-circle']"></div>

                    <div class="wheels-side side-dir">
                      <div v-for="pos in eixo.posicoes.filter(p => p.includes('DIR'))" :key="pos" 
                           class="tire-drop-zone"
                           :class="{ occupied: veiculoDetail.pneus[pos], 'drag-over': dragOverPos === pos }"
                           @dragover.prevent="dragOverPos = pos"
                           @dragleave="dragOverPos = null"
                           @drop="handleDropOnSlot(pos)"
                           @click="handleTireClick(pos)">
                        
                        <div v-if="veiculoDetail.pneus[pos]" class="tire-item in-vehicle"
                             :class="tireStatusClass(veiculoDetail.pneus[pos])"
                             draggable="true" @dragstart="handleDragStartFromVehicle($event, pos, veiculoDetail.pneus[pos])">
                          <div class="tire-id">{{ veiculoDetail.pneus[pos].numero_fogo }}</div>
                        </div>
                        <div v-else class="tire-placeholder">
                          <span>+</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Estepes -->
              <div class="spare-container" v-if="veiculoDetail?.config?.estepes?.length">
                <div class="spare-title">Estepes</div>
                <div v-for="pos in veiculoDetail.config.estepes" :key="pos" 
                     class="tire-drop-zone spare-zone"
                     :class="{ occupied: veiculoDetail.pneus[pos], 'drag-over': dragOverPos === pos }"
                     @dragover.prevent="dragOverPos = pos"
                     @dragleave="dragOverPos = null"
                     @drop="handleDropOnSlot(pos)"
                     @click="handleTireClick(pos)">
                  
                  <div v-if="veiculoDetail.pneus[pos]" class="tire-item in-vehicle"
                       :class="tireStatusClass(veiculoDetail.pneus[pos])"
                       draggable="true" @dragstart="handleDragStartFromVehicle($event, pos, veiculoDetail.pneus[pos])">
                    <div class="tire-id">{{ veiculoDetail.pneus[pos].numero_fogo }}</div>
                  </div>
                  <div v-else class="tire-placeholder"><span>+</span></div>
                </div>
              </div>
            </div>
          </div>

          <!-- LADO DIREITO: ESTOQUE (ALMOXARIFADO) -->
          <div class="gp-stock-panel">
            <div class="stock-header">
              <h4>Almoxarifado</h4>
              <span class="stock-count">{{ pneusEstoqueFilial.length }} pneus</span>
            </div>
            
            <div class="form-group" style="margin-bottom: 12px; margin-top: -6px;">
              <select v-model="almoxarifadoFilialId" class="select-premium" @change="loadEstoqueAlmoxarifado">
                <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
              </select>
            </div>
            
            <div class="search-stock">
              <input v-model="searchStock" placeholder="Buscar pneu no estoque..." class="stock-input" />
            </div>

            <div class="stock-list" @dragover.prevent @drop="handleDropOnRemoval('estoque')">
              <template v-for="grupo in filteredStockByMedida" :key="grupo.medida">
                <div class="medida-separator">
                  <span class="medida-sep-label">{{ grupo.medida }}</span>
                  <span class="medida-sep-count">{{ grupo.pneus.length }}</span>
                </div>
                <div v-for="p in grupo.pneus" :key="p.id"
                     class="tire-card-stock"
                     :class="{ 'tire-pending': p.recebido === 0, 'tire-new': Number(p.vida) === 1 && p.recebido === 1 }"
                     draggable="true"
                     @dragstart="handleDragStartFromStock($event, p)"
                     @click.stop="p.recebido === 0 && confirmarChegadaEstoque(p)"
                     :title="p.recebido === 0 ? '✅ Clique para confirmar chegada' : ''"
                     :style="p.recebido === 0 ? 'cursor:pointer;' : ''">
                  <div class="tire-mini-visual"></div>
                  <div class="tire-card-info">
                    <span class="t-fogo">{{ p.numero_fogo }}</span>
                    <span class="t-desc">{{ p.marca }}</span>
                    <div style="display:flex;gap:4px;align-items:center;margin-top:2px;">
                      <span class="t-status">Vida: {{ p.vida }}ª | {{ p.sulco_atual }}mm</span>
                    </div>
                  </div>
                  <div v-if="p.recebido === 0" class="pending-btn" title="Confirmar chegada">✓</div>
                </div>
              </template>
              <div v-if="!filteredStock.length" class="empty-stock">
                Nenhum pneu disponível nesta filial
              </div>
            </div>

            <!-- Área de Remoção (Lixeira) -->
            <div class="removal-zone sucata-drop" :class="{ 'drag-over': dragOverRemoval }"
                 @dragover.prevent="dragOverRemoval = true"
                 @dragleave="dragOverRemoval = false"
                 @drop="handleDropOnRemoval('sucata')">
              <span class="icon">🗑️</span>
              <span class="label">ARRASTE PARA SUCATA</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL: ALOCAR PNEU -->
    <div v-if="showAlocarModal" class="modal-overlay" @click.self="showAlocarModal = false">
      <div class="modal-box">
        <h3>Alocar Pneu</h3>
        <p v-if="alocarCtx.fromEixo">Posição: <strong>{{ posLabel(alocarCtx.posicao, veiculoDetail?.tipo) }}</strong> no veículo <strong>{{ veiculoDetail?.placa }}</strong></p>
        <div class="form-group" v-if="!alocarCtx.fromEixo">
          <label>Veículo</label>
          <select v-model="alocarForm.veiculo_id" @change="loadPosDisponiveis">
            <option :value="null">— Selecione —</option>
            <option v-for="v in veiculos" :key="v.id" :value="v.id">{{ v.placa }} — {{ v.modelo }}</option>
          </select>
        </div>
        <div class="form-group" v-if="!alocarCtx.fromEixo && alocarForm.veiculo_id">
          <label>Posição</label>
          <select v-model="alocarForm.posicao">
            <option value="">— Selecione —</option>
            <option v-for="p in posDisponiveis" :key="p" :value="p">{{ posLabel(p, currentSelectedVeiculoTipo) }}</option>
          </select>
        </div>
        <div class="form-group" v-if="alocarCtx.fromEixo">
          <label>Pneu (estoque da filial)</label>
          <select v-model="alocarForm.pneu_id">
            <option :value="null">— Selecione —</option>
            <option v-for="p in pneusEstoqueFilial" :key="p.id" :value="p.id">{{ p.numero_fogo }} — {{ p.marca }} {{ p.medida }}</option>
          </select>
        </div>
        <div class="form-group"><label>KM Instalação</label><input type="number" v-model.number="alocarForm.km_instalacao" /></div>
        <div class="form-group"><label>Observação</label><input v-model="alocarForm.observacao" /></div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showAlocarModal = false">Cancelar</button>
          <button class="btn-primary" @click="doAlocar">Confirmar</button>
        </div>
      </div>
    </div>

    <!-- MODAL: REMOVER PNEU -->
    <div v-if="showRemoverModal" class="modal-overlay" @click.self="showRemoverModal = false">
      <div class="modal-box">
        <h3>Remover Pneu</h3>
        <p>Pneu: <strong>{{ removerCtx?.numero_fogo }}</strong> ({{ removerCtx?.marca }} {{ removerCtx?.medida }})</p>
        <div class="form-group">
          <label>Destino</label>
          <select v-model="removerForm.destino">
            <option value="estoque">Voltar ao Estoque</option>
            <option value="descarte">Descarte</option>
            <option value="reciclagem">Reciclagem</option>
            <option value="recapagem">Recapagem</option>
          </select>
        </div>
        <div class="form-group">
          <label>Estoque Destino (Filial)</label>
          <select v-model="removerForm.filial_destino_id">
            <option v-for="f in filiais" :key="f.id" :value="f.id">{{ f.nome }}</option>
          </select>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
          <div class="form-group">
            <label>KM Inicial (Instalação)</label>
            <input type="number" :value="removerCtx?.km_instalacao || 0" disabled style="background: #f1f5f9; cursor: not-allowed;" />
          </div>
          <div class="form-group">
            <label>KM Atual (Remoção)</label>
            <input 
              type="number" 
              v-model.number="removerForm.km_momento" 
              :disabled="removerCtx?.ja_no_estoque || removerForm.destino === 'descarte'"
              :style="(removerCtx?.ja_no_estoque || removerForm.destino === 'descarte') ? 'background: #f1f5f9; cursor: not-allowed;' : ''"
            />
          </div>
        </div>
        
        <div class="percorrido-preview" v-if="removerForm.km_momento > (removerCtx?.km_instalacao || 0)" style="margin-bottom: 12px; padding: 10px; background: #f0fdf4; border-radius: 8px; border: 1px solid #bbf7d0; display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 13px; font-weight: 500; color: #166534;">KM Percorrido nesta vida:</span>
          <span style="font-size: 16px; font-weight: 700; color: #15803d;">+ {{ (removerForm.km_momento - (removerCtx?.km_instalacao || 0)).toLocaleString() }} KM</span>
        </div>

        <div class="form-group"><label>Observação</label><input v-model="removerForm.observacao" /></div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showRemoverModal = false">Cancelar</button>
          <button class="btn-primary btn-danger" @click="doRemover">Confirmar Remoção</button>
        </div>
      </div>
    </div>

    <!-- MODAL: TRANSFERIR -->
    <div v-if="showTransferirModal" class="modal-overlay" @click.self="showTransferirModal = false">
      <div class="modal-box">
        <h3>Transferir Pneu</h3>
        <p>Pneu: <strong>{{ transferirCtx?.numero_fogo }}</strong> — Filial atual: {{ transferirCtx?.filial_nome }}</p>
        <div class="form-group">
          <label>Filial Destino</label>
          <select v-model="transferirForm.filial_destino_id">
            <option :value="null">— Selecione —</option>
            <option v-for="f in filiais.filter(x => x.id !== transferirCtx?.filial_id)" :key="f.id" :value="f.id">{{ f.nome }}</option>
          </select>
        </div>
        <div class="form-group"><label>Observação</label><input v-model="transferirForm.observacao" /></div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showTransferirModal = false">Cancelar</button>
          <button class="btn-primary" @click="doTransferir" :disabled="!transferirForm.filial_destino_id">Confirmar</button>
        </div>
      </div>
    </div>

    <!-- TOAST -->
    <!-- MODAL: RODÍZIO -->
    <div v-if="showRodizioModal" class="modal-overlay" @click.self="showRodizioModal = false">
      <div class="modal-box">
        <h3>🔄 Rodízio de Pneus</h3>
        <p v-if="rodizioCtx" style="font-size: 13px; color: var(--text2); margin-bottom: 20px;">
          {{ rodizioCtx.isSwap ? 'Trocando pneus entre as posições:' : 'Movendo pneu para nova posição:' }}<br>
          <strong>{{ posLabel(rodizioCtx.oldPos) }} ➔ {{ posLabel(rodizioCtx.pos) }}</strong>
        </p>

        <div class="form-group">
          <label>KM Atual do Veículo</label>
          <input type="number" v-model="rodizioForm.km_momento" class="stock-input" />
        </div>

        <div class="form-group">
          <label>Observação</label>
          <textarea v-model="rodizioForm.observacao" class="stock-input" rows="2"></textarea>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="showRodizioModal = false">Cancelar</button>
          <button class="btn-primary" @click="doRodizio">Confirmar Rodízio</button>
        </div>
      </div>
    </div>

    <!-- TAB: ENTRADA NF -->
    <EntradaNFView
      v-if="tab === 'relatorio_nf'"
      :filiais="filiais"
    />

    <!-- TAB: SOLICITAÇÕES -->
    <section v-if="tab === 'solicitacoes'" class="gp-section">
      <SolicitacoesView :filiais="filiais" :user="user" />
    </section>

    <!-- TAB: USUÁRIOS -->
    <UsuariosView
      v-if="tab === 'usuarios'"
      :filiais="filiais"
      :showToast="showToast"
    />

      </main>
      <div v-if="toast" class="toast" :class="toast.type">{{ toast.msg }}</div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  fetchVehicleConfigs, fetchFiliais, createFilial, updateFilial, deleteFilial,
  fetchVeiculos, fetchVeiculo, createVeiculo, updateVeiculo, deleteVeiculo,
  fetchPneusList, createPneu, updatePneu as updatePneuApi,
  fetchPneusTemplate, importPneusCsv, fetchPneusPorNF,
  alocarPneu, removerPneu, transferirPneu,
  fetchMovimentacoes, fetchGPDashboard,
  fetchBuscaVeiculoSql, fetchSincronizarVeiculosSql,
  confirmarRecebimento, rodizioPneu,
  fetchLotesReciclagem, fetchPneusAguardandoLote, enviarParaReciclagem,
  atualizarValorLote, criarLoteReciclagem, fetchRelatorioFinanceiroReciclagem
} from '../api/gestaoPneus.js'
import EstoqueCentralView from '../components/views/EstoqueCentralView.vue'
import DashboardView from '../components/views/DashboardView.vue'
import SolicitacoesView from '../components/views/SolicitacoesView.vue'
import RelatorioNFView from './RelatorioNFView.vue'
import EntradaNFView from '../components/views/EntradaNFView.vue'
import UsuariosView from './UsuariosView.vue'
import HistoricoView from '../components/views/HistoricoView.vue'
import FinanceiroView from '../components/views/FinanceiroView.vue'
import SucataView from '../components/views/SucataView.vue'
import ReciclagemView from '../components/views/ReciclagemView.vue'
import FiliaisView from '../components/views/FiliaisView.vue'

const props = defineProps(['user'])
const emit = defineEmits(['logout'])

const allTabs = [
  { id: 'dashboard',     label: 'Dashboard',          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>` },
  { id: 'relatorio_nf',  label: 'Entrada NF',         icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>` },
  { id: 'estoque_central', label: 'Controle de Estoque', icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8V21H3V8"></path><path d="M1 3H23V8H1V3Z"></path><path d="M10 12H14"></path></svg>` },
  { id: 'alocacoes',    label: 'Alocações',           icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>` },
  { id: 'veiculos',     label: 'Frota',               icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><path d="M10 9h4"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>` },
  { id: 'filiais',      label: 'Unidades',            icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>` },
  { id: 'estoque',      label: 'Estoque',             icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>` },
  { id: 'financeiro',   label: 'Financeiro',          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>` },
  { id: 'sucata',       label: 'Sucata',              icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>` },
  { id: 'recicladora',  label: 'Reciclagem',          icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 20V9c0-2 2-3 4-3s4 1 4 3v11"></path><path d="M14 20V5c0-2 2-3 4-3s4 1 4 3v15"></path><path d="M2 20h20"></path><path d="M22 7l-4-4-4 4"></path></svg>` },
  { id: 'historico',    label: 'Histórico',           icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>` },
  { id: 'solicitacoes', label: 'Solicitações',        icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>` }
]

const usuariosTab = { id: 'usuarios', label: 'Usuários', icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>` }

const solicitacoesTab = allTabs.find(t => t.id === 'solicitacoes')

const visibleTabs = computed(() => {
  const user = props.user
  if (!user || user.role === 'admin' || user.role === 'gerente') {
    return [...allTabs]
  }
  const telas = user.telas || []
  const filtered = allTabs.filter(t => telas.includes(t.id))
  // Solicitações sempre visível para todos os usuários
  if (solicitacoesTab && !filtered.find(t => t.id === 'solicitacoes')) {
    filtered.push(solicitacoesTab)
  }
  return filtered
})

const currentTabLabel = computed(() => visibleTabs.value.find(t => t.id === tab.value)?.label || '')
const tab = ref('estoque_central')

watch(visibleTabs, (tabs) => {
  if (tabs.length && !tabs.find(t => t.id === tab.value)) {
    tab.value = tabs[0].id
  }
})

const toast = ref(null)
const dash = ref(null)
const loteImpressao = ref(null)

const rodizioCtx = ref(null)
const showRodizioModal = ref(false)
const rodizioForm = ref({ km_momento: 0, observacao: '' })

// Data
const filiais = ref([])
const veiculos = ref([])
const pneusList = ref([])
const pneusGeral = ref([])
const loadingPneusGeral = ref(false)

// Accordion — Estoque: Filial → Medida
const expandedFilialEst = ref(new Set())
const expandedMedidaEst = ref(new Set())
const movs = ref([])
const vehicleConfigs = ref({})
const modeloSelecionado = ref(null)
const sincronizando = ref(false)
const pneusAguardandoLote = ref([])
const selectedPneusReciclagem = ref([])

// Filters
const filtroFilialV = ref('')
const filtroFilialP = ref('')
const filtroStatus = ref('')
const filtroTipoMov = ref('')
const filtroFilialSucata = ref('')
const searchSucata = ref('')
const filtroFilialFinanceiro = ref('')
const filtroMesFinanceiro = ref(new Date().toISOString().slice(0, 7))

// Modals
const showFilialModal = ref(false)
const showVeiculoModal = ref(false)
const showPneuModal = ref(false)
const showEixosModal = ref(false)
const showAlocarModal = ref(false)
const showRemoverModal = ref(false)
const showTransferirModal = ref(false)
const showReciclagemModal = ref(false)
const showValorLoteModal = ref(false)

// Edit states
const editingFilial = ref(null)
const editingVeiculo = ref(null)
const editingPneu = ref(null)
const veiculoDetail = ref(null)
const lotesReciclagem = ref([])
const relatorioFinanceiro = ref({ resumo_filiais: [], detalhes: [], total_geral: 0 })
const reciclagemCtx = ref(null)
const valorLoteCtx = ref(null)

// Forms
const fileInput = ref(null)
const filialForm = ref({ nome: '', estado: '' })
const veiculoForm = ref({ placa: '', frota: '', modelo: '', marca: '', tipo: 'truck', filial_id: null })
const buscandoPlaca = ref(false)
const autoPreenchido = ref({ km: false, filial: false })
const pneuForm = ref({ numero_fogo: '', marca: '', modelo: '', medida: '', dot: '', valor: 0, vida: 1, filial_id: null, sulco_atual: 0 })
const reciclagemForm = ref({ data_envio: new Date().toISOString().split('T')[0], observacao: '' })
const valorLoteForm = ref({ valor_total: 0 })
const alocarForm = ref({ pneu_id: null, veiculo_id: null, posicao: '', km_instalacao: 0, observacao: '' })
const alocarCtx = ref({ fromEixo: false, posicao: '' })
const removerForm = ref({ pneu_id: null, destino: 'estoque', filial_destino_id: null, km_momento: 0, observacao: '' })
const removerCtx = ref(null)
const transferirForm = ref({ filial_destino_id: null, observacao: '' })
const transferirCtx = ref(null)
const posDisponiveis = ref([])
const pneusEstoqueFilial = ref([])
const almoxarifadoFilialId = ref(null)

// Drag & Drop state
const draggedPneu = ref(null)
const dragSource = ref(null) // 'stock' or 'vehicle'
const dragOldPos = ref(null)
const dragOverPos = ref(null)
const dragOverRemoval = ref(false)
const dragOverEstoque = ref(false)
const searchStock = ref('')
const searchVeiculo = ref('')
const searchMov = ref('')

function tireStatusClass(tire) {
  if (!tire) return ''
  const km = tire.km_total || 0
  const sulco = tire.sulco_atual
  if (km <= 0) return 'tire-new'
  if (sulco > 0 && sulco < 4) return 'tire-worn'
  return 'tire-used'
}

const filteredVeiculos = computed(() => {
  if (!searchVeiculo.value) return veiculos.value
  const s = searchVeiculo.value.toLowerCase()
  return veiculos.value.filter(v => 
    v.placa.toLowerCase().includes(s) || 
    (v.frota && v.frota.toLowerCase().includes(s)) ||
    (v.modelo && v.modelo.toLowerCase().includes(s))
  )
})

const pneusSucataPendentes = computed(() => {
  let list = pneusGeral.value.filter(p => p.recebido === 0 && (p.status === 'descarte' || (p.filial_nome || '').toUpperCase().includes('SUCATA')))
  if (filtroFilialSucata.value) {
    list = list.filter(p => p.filial_origem_id === Number(filtroFilialSucata.value))
  }
  if (searchSucata.value) {
    const s = searchSucata.value.toLowerCase()
    list = list.filter(p => p.numero_fogo.toLowerCase().includes(s))
  }
  return list
})
const pneusSucataConfirmados = computed(() => {
  let list = pneusGeral.value.filter(p => p.recebido === 1 && !p.lote_id && (p.status === 'descarte' || (p.filial_nome || '').toUpperCase().includes('SUCATA')) && p.status !== 'reciclagem')
  if (filtroFilialSucata.value) {
    list = list.filter(p => p.filial_origem_id === Number(filtroFilialSucata.value))
  }
  if (searchSucata.value) {
    const s = searchSucata.value.toLowerCase()
    list = list.filter(p => p.numero_fogo.toLowerCase().includes(s))
  }
  return list
})

const gruposFilialMedida = computed(() => {
  const mapa = {}
  for (const p of pneusList.value) {
    const filial = p.filial_nome || 'Sem filial'
    const medida = (p.medida || 'Sem medida').trim()
    if (!mapa[filial]) mapa[filial] = {}
    if (!mapa[filial][medida]) mapa[filial][medida] = []
    mapa[filial][medida].push(p)
  }
  return Object.entries(mapa)
    .map(([filial, medidasMap]) => {
      const medidas = Object.entries(medidasMap)
        .map(([medida, pneus]) => {
          const sulcos = pneus.map(p => parseFloat(p.sulco_atual || 0)).filter(s => s > 0)
          const statusCount = pneus.reduce((acc, p) => {
            const s = p.status || 'desconhecido'; acc[s] = (acc[s] || 0) + 1; return acc
          }, {})
          return {
            medida,
            pneus,
            qtd: pneus.length,
            sulcoMedio: sulcos.length ? sulcos.reduce((a, b) => a + b, 0) / sulcos.length : 0,
            vidaMedia: pneus.reduce((s, p) => s + (parseInt(p.vida) || 1), 0) / pneus.length,
            statusCount
          }
        })
        .sort((a, b) => b.qtd - a.qtd)

      const statusTotais = medidas.reduce((acc, gm) => {
        for (const [s, n] of Object.entries(gm.statusCount)) { acc[s] = (acc[s] || 0) + n }
        return acc
      }, {})

      return {
        filial,
        medidas,
        qtd: medidas.reduce((s, gm) => s + gm.qtd, 0),
        statusTotais
      }
    })
    .sort((a, b) => b.qtd - a.qtd)
})

function toggleFilialEst(nome) {
  const s = new Set(expandedFilialEst.value)
  s.has(nome) ? s.delete(nome) : s.add(nome)
  expandedFilialEst.value = s
}
function toggleMedidaEst(filial, medida) {
  const key = `${filial}|${medida}`
  const s = new Set(expandedMedidaEst.value)
  s.has(key) ? s.delete(key) : s.add(key)
  expandedMedidaEst.value = s
}

const filteredStock = computed(() => {
  if (!searchStock.value) return pneusEstoqueFilial.value
  const s = searchStock.value.toLowerCase()
  return pneusEstoqueFilial.value.filter(p =>
    p.numero_fogo.toLowerCase().includes(s) ||
    p.marca.toLowerCase().includes(s) ||
    p.medida.toLowerCase().includes(s)
  )
})

const filteredStockByMedida = computed(() => {
  const mapa = {}
  for (const p of filteredStock.value) {
    const med = p.medida || 'Sem medida'
    if (!mapa[med]) mapa[med] = []
    mapa[med].push(p)
  }
  return Object.entries(mapa)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([medida, pneus]) => ({ medida, pneus }))
})

const modelosPreCadastrados = computed(() => {
  const defaults = [
    { marca: 'MICHELIN', modelo: 'X MULTI Z', medida: '295/80R22.5' },
    { marca: 'BRIDGESTONE', modelo: 'R268', medida: '295/80R22.5' },
    { marca: 'PIRELLI', modelo: 'FR88', medida: '295/80R22.5' },
    { marca: 'GOODYEAR', modelo: 'KMAX S', medida: '295/80R22.5' },
    { marca: 'FIRESTONE', modelo: 'FS440', medida: '295/80R22.5' }
  ];

  const uniques = new Map();
  
  // Adiciona os defaults primeiro
  defaults.forEach(d => {
    uniques.set(`${d.marca}|${d.modelo}|${d.medida}`, d);
  });

  // Lê os pneus carregados do banco e extrai as combinações já usadas
  pneusGeral.value.forEach(p => {
    if (p.marca && p.medida) {
      const marca = p.marca.toUpperCase().trim();
      const modelo = p.modelo ? p.modelo.toUpperCase().trim() : '';
      const medida = p.medida.toUpperCase().trim();
      
      const key = `${marca}|${modelo}|${medida}`;
      if (!uniques.has(key)) {
        uniques.set(key, { marca, modelo, medida });
      }
    }
  });

  // Retorna em ordem alfabética por Marca
  return Array.from(uniques.values()).sort((a, b) => a.marca.localeCompare(b.marca));
})

const filteredMovs = computed(() => {
  if (!searchMov.value) return movs.value
  const s = searchMov.value.toLowerCase()
  return movs.value.filter(m => 
    (m.numero_fogo && m.numero_fogo.toLowerCase().includes(s)) || 
    (m.veiculo_placa && m.veiculo_placa.toLowerCase().includes(s)) ||
    (m.observacao && m.observacao.toLowerCase().includes(s))
  )
})

const currentSelectedVeiculoTipo = computed(() => {
  if (!alocarForm.value.veiculo_id) return null
  const v = veiculos.value.find(x => x.id === alocarForm.value.veiculo_id)
  return v?.tipo
})

// Drag & Drop handlers
function handleDragStartFromStock(event, pneu) {
  event.dataTransfer.effectAllowed = 'move'
  draggedPneu.value = pneu
  dragSource.value = 'stock'
}

function handleDragStartFromVehicle(event, pos, pneu) {
  event.dataTransfer.effectAllowed = 'move'
  draggedPneu.value = pneu
  dragSource.value = 'vehicle'
  dragOldPos.value = pos
}

async function handleDropOnSlot(pos) {
  const p = draggedPneu.value
  const source = dragSource.value
  dragOverPos.value = null
  
  if (!p) return

  try {
    if (source === 'stock') {
      if (veiculoDetail.value.pneus[pos]) {
        showToast('Esta posição já está ocupada. Remova o pneu atual primeiro.', 'error')
        return
      }
      alocarCtx.value = { fromEixo: true, posicao: pos }
      alocarForm.value = { 
        pneu_id: p.id, 
        veiculo_id: veiculoDetail.value.id, 
        posicao: pos, 
        km_instalacao: veiculoDetail.value.km_atual || 0, 
        observacao: 'Montado via diagrama' 
      }
      showAlocarModal.value = true
    } 
    else if (source === 'vehicle') {
      const oldPos = dragOldPos.value
      if (oldPos === pos) return
      
      const isSwap = !!veiculoDetail.value.pneus[pos]
      rodizioCtx.value = { oldPos, pos, isSwap }
      rodizioForm.value = { 
        km_momento: veiculoDetail.value.km_atual || 0, 
        observacao: isSwap ? 'Troca de pneus' : 'Mudança de posição' 
      }
      showRodizioModal.value = true
    }
  } catch(e) { showToast(e.message, 'error') }
  
  draggedPneu.value = null
  dragSource.value = null
}

async function handleDropOnRemoval(target = 'estoque') {
  const p = draggedPneu.value
  const source = dragSource.value
  dragOverRemoval.value = false
  dragOverEstoque.value = false
  
  if (!p) return

  // CASO 1: Removendo do veículo
  if (source === 'vehicle') {
    removerCtx.value = p
    removerForm.value = { 
      pneu_id: p.id, 
      destino: target === 'sucata' ? 'descarte' : 'estoque', 
      filial_destino_id: veiculoDetail.value?.filial_id || p.filial_id, 
      km_momento: veiculoDetail.value?.km_atual || 0, 
      observacao: target === 'sucata' ? 'Remoção direta para sucata' : '' 
    }
    if (target === 'sucata') {
      const sucata = filiais.value.find(f => f.nome?.toUpperCase().includes('SUCATA'))
      if (sucata) {
        removerForm.value.filial_destino_id = sucata.id
      } else {
        showToast('Filial "SUCATA" não encontrada. Verifique o cadastro de filiais.', 'error')
        return
      }
    }
    showRemoverModal.value = true
  } 
  // CASO 2: Já está no estoque local e foi arrastado para a lixeira de Sucata
  else if (source === 'stock' && target === 'sucata') {
    const sucata = filiais.value.find(f => f.nome?.toUpperCase().includes('SUCATA'))
    if (!sucata) {
      showToast('Filial "SUCATA" não encontrada. Verifique o cadastro de filiais.', 'error')
      return
    }
    removerCtx.value = { ...p, ja_no_estoque: true }
    removerForm.value = { 
      pneu_id: p.id, 
      destino: 'descarte', 
      filial_destino_id: sucata.id, 
      km_momento: p.km_total || 0, 
      observacao: 'Descarte direto do almoxarifado' 
    }
    showRemoverModal.value = true
  }
  
  draggedPneu.value = null
  dragSource.value = null
}

// Helpers
const fmtN = (v) => v ? Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0,00'


const fmtDate = (d) => d ? new Date(d).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'
const configLabel = (t) => vehicleConfigs.value[t]?.nome || t
const countPneus = (tipo) => {
  const cfg = vehicleConfigs.value[tipo]
  if (!cfg) return 0
  const eixos = cfg.eixos.reduce((acc, e) => acc + e.posicoes.length, 0)
  return eixos + cfg.estepes.length
}
const countPneusAlocados = (veiculo_id) => {
  if (!pneusGeral.value) return 0
  return pneusGeral.value.filter(p => p.veiculo_id === veiculo_id && p.status === 'em_uso').length
}
const statusLabel = (p) => {
  const s = typeof p === 'string' ? p : p.status
  if (s === 'estoque' && typeof p === 'object' && (p.km_total > 0 || p.km_instalacao > 0) && !p.veiculo_id) return 'Estoque (Usado)'
  return { estoque: 'Estoque Novo', em_uso: 'Em Uso', descarte: 'Sucata', recapagem: 'Recapagem', reciclagem: 'Reciclagem' }[s] || s
}
const statusClass = (p) => {
  const s = typeof p === 'string' ? p : p.status
  if (s === 'estoque' && typeof p === 'object' && (p.km_total > 0 || p.km_instalacao > 0) && !p.veiculo_id) return 'badge-red'
  return { estoque: 'badge-green', em_uso: 'badge-blue', descarte: 'badge-red', recapagem: 'badge-yellow', reciclagem: 'badge-purple' }[s] || ''
}
const movLabel = (t) => ({ entrada_estoque: 'Entrada', alocacao: 'Alocação', remocao: 'Remoção', descarte: 'Descarte', transferencia: 'Transferência', recapagem: 'Recapagem', recebimento_sucata: 'Confirmação Sucata', rodizio: 'Rodízio / Troca' }[t] || t)
const movClass = (t) => ({ entrada_estoque: 'badge-green', alocacao: 'badge-blue', remocao: 'badge-yellow', descarte: 'badge-red', transferencia: 'badge-purple', recapagem: 'badge-yellow', recebimento_sucata: 'badge-green', rodizio: 'badge-purple' }[t] || '')
const movIcon = (t) => {
  const icons = {
    entrada_estoque: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m3 16 4 4 4-4"></path><path d="M7 20V4"></path><rect x="12" y="4" width="8" height="8" rx="1"></rect><path d="M12 18h8"></path></svg>`,
    alocacao: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-9h-4V5h-4v12h3"/><path d="M10 9h4"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>`,
    remocao: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>`,
    descarte: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path></svg>`,
    transferencia: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 11V7a5 5 0 0 1 10 0v4"></path><path d="M11 21a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V13a2 2 0 0 0-2-2h-6a2 2 0 0 0-2 2v8Z"></path></svg>`,
    recapagem: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v4"></path><path d="m16.2 4.2 2.8 2.8"></path><path d="M12 18v4"></path><path d="m4.9 19.1 2.8-2.8"></path><path d="M2 12h4"></path><path d="m4.2 16.2 2.8-2.8"></path><path d="M18 12h4"></path><path d="m19.1 4.9-2.8 2.8"></path></svg>`,
    recebimento_sucata: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
    rodizio: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m17 2 4 4-4 4"></path><path d="M3 11v-1a4 4 0 0 1 4-4h14"></path><path d="m7 22-4-4 4-4"></path><path d="M21 13v1a4 4 0 0 1-4 4H3"></path></svg>`
  }
  return icons[t] || `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`
}
const posLabel = (pos, type = null) => {
  if (!pos) return '—'
  
  // Nomes base
  const labels = {
    E1_ESQ: '1º Dianteiro LE',
    E1_DIR: '1º Dianteiro LD',
    E2_ESQ: '2º Dianteiro LE',
    E2_DIR: '2º Dianteiro LD',
    ESTEPE_1: 'Estepe 1',
    ESTEPE_2: 'Estepe 2'
  }

  if (labels[pos]) return labels[pos]

  // Lógica para Truck e Bitruck (E2, E3, E4)
  const isBitruck = type === 'bitruck'
  
  if (pos.startsWith('E2')) {
    // No Bitruck E2 é direcional simples, mas no Truck/Toco é Tração Dupla
    if (isBitruck) return pos.includes('ESQ') ? '2º Dianteiro LE' : '2º Dianteiro LD'
    return 'Tração ' + (pos.includes('ESQ') ? 'LE ' : 'LD ') + (pos.includes('INT') ? 'Int' : 'Fora')
  }

  if (pos.startsWith('E3')) {
    // No Bitruck E3 é Tração, no Truck E3 é o Eixo Truck
    const base = isBitruck ? 'Tração ' : 'Truck '
    return base + (pos.includes('ESQ') ? 'LE ' : 'LD ') + (pos.includes('INT') ? 'Int' : 'Fora')
  }

  if (pos.startsWith('E4')) {
    // No Bitruck E4 é o Eixo Truck
    return 'Truck ' + (pos.includes('ESQ') ? 'LE ' : 'LD ') + (pos.includes('INT') ? 'Int' : 'Fora')
  }

  return pos
}

function showToast(msg, type = 'success') {
  toast.value = { msg, type }
  setTimeout(() => toast.value = null, 3000)
}

// Load data
async function loadAll() {
  const tabs = visibleTabs.value
  if (tabs.length && !tabs.find(t => t.id === tab.value)) {
    tab.value = tabs[0].id
  }
  const [configs, filiaisData, dashData] = await Promise.all([
    fetchVehicleConfigs().catch(e => { console.error(e); return {} }),
    fetchFiliais().catch(e => { console.error(e); return [] }),
    fetchGPDashboard().catch(e => { console.error(e); return null })
  ])
  vehicleConfigs.value = configs
  filiais.value = filiaisData
  dash.value = dashData
  loadVeiculos()
  loadPneus()
  loadPneusGeral()
  loadMovs()
}
async function loadFiliais() {
  try { filiais.value = await fetchFiliais() } catch(e) { console.error(e) }
}
async function loadVeiculos() {
  try { 
    const v = await fetchVeiculos({ filial_id: filtroFilialV.value })
    // Filtra apenas veículos que possuem frota preenchida para manter a lista limpa
    veiculos.value = (v || []).filter(item => item.frota && item.frota.trim() !== '')
  } catch(e) { console.error(e) } 
}
async function loadPneus() { try { pneusList.value = await fetchPneusList({ filial_id: filtroFilialP.value, status: filtroStatus.value }) } catch(e) { console.error(e) } }
async function loadPneusGeral() {
  loadingPneusGeral.value = true
  try { pneusGeral.value = await fetchPneusList({}) } catch(e) { console.error(e) } finally { loadingPneusGeral.value = false }
}
async function loadMovs() { try { movs.value = await fetchMovimentacoes({ tipo: filtroTipoMov.value }) } catch(e) { console.error(e) } }
async function refreshDash() { try { dash.value = await fetchGPDashboard() } catch(e) {} }

// Relatório NF — wrapper para o componente filho
async function fetchPneusPorNFWrapper(nf) {
  const lista = await fetchPneusPorNF(nf)
  return Array.isArray(lista) ? lista : []
}

// Filiais CRUD
function openFilialForm(f = null) {
  editingFilial.value = f
  filialForm.value = f ? { nome: f.nome, estado: f.estado || '' } : { nome: '', estado: '' }
  showFilialModal.value = true
}
async function saveFilial() {
  try {
    if (editingFilial.value) await updateFilial(editingFilial.value.id, filialForm.value)
    else await createFilial(filialForm.value)
    showFilialModal.value = false
    showToast(editingFilial.value ? 'Filial atualizada!' : 'Filial criada!')
    filiais.value = await fetchFiliais()
    refreshDash()
  } catch(e) { showToast(e.message, 'error') }
}
async function removeFilial(f) {
  if (!confirm(`Desativar a filial "${f.nome}"?`)) return
  try { await deleteFilial(f.id); filiais.value = await fetchFiliais(); showToast('Filial desativada!'); refreshDash() }
  catch(e) { showToast(e.message, 'error') }
}

// Veículos CRUD
function openVeiculoForm(v = null) {
  editingVeiculo.value = v
  veiculoForm.value = v
    ? { placa: v.placa, frota: v.frota || '', modelo: v.modelo || '', marca: v.marca || '', tipo: v.tipo || 'truck', filial_id: v.filial_id, km_atual: v.km_atual || 0 }
    : { placa: '', frota: '', modelo: '', marca: '', tipo: 'truck', filial_id: null, km_atual: 0 }
  showVeiculoModal.value = true
}

async function buscarPlacaSQL() {
  if (editingVeiculo.value) return;
  let p = veiculoForm.value.placa;
  if (!p || p.replace('-', '').length < 7) return;

  // Normaliza a placa
  p = p.trim().toUpperCase().replace('-', '');

  buscandoPlaca.value = true;
  autoPreenchido.value = { km: false, filial: false };

  try {
    const res = await fetchBuscaVeiculoSql(p);
    if (res) {
      if (res.modelo) veiculoForm.value.modelo = res.modelo;
      if (res.marca)  veiculoForm.value.marca  = res.marca;
      if (res.frota)  veiculoForm.value.frota  = res.frota;
      if (res.tipo)   veiculoForm.value.tipo   = res.tipo;
      if (res.placa)  veiculoForm.value.placa  = res.placa;

      // ── KM Odômetro ──────────────────────────────────────────────────
      if (res.km_atual && Number(res.km_atual) > 0) {
        veiculoForm.value.km_atual = Number(res.km_atual);
        autoPreenchido.value.km = true;
      }

      // ── Filial Operacional (matching inteligente) ─────────────────────
      if (res.filial_nome) {
        const normalizar = (s) => s.toUpperCase()
          .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // remove acentos
          .replace(/[^A-Z0-9\s]/g, '')
          .trim();
        const nomeSql = normalizar(res.filial_nome);

        // 1. Tentativa: qualquer palavra da filial SQL está contida no cadastro
        let f = filiais.value.find(fi => {
          const nomeCad = normalizar(fi.nome);
          return nomeCad.includes(nomeSql) || nomeSql.includes(nomeCad);
        });

        // 2. Fallback: pelo menos 1 palavra significativa (>= 4 letras) em comum
        if (!f) {
          const palavrasSql = nomeSql.split(/\s+/).filter(w => w.length >= 4);
          f = filiais.value.find(fi => {
            const nomeCad = normalizar(fi.nome);
            return palavrasSql.some(w => nomeCad.includes(w));
          });
        }

        if (f) {
          veiculoForm.value.filial_id = f.id;
          autoPreenchido.value.filial = true;
        } else {
          // Exibe o nome retornado pelo SQL para o usuário selecionar manualmente
          showToast(`Filial "${res.filial_nome}" não encontrada no cadastro. Selecione manualmente.`, 'warning');
        }
      }

      const fonteMsgs = {
        supabase:   '✅ Dados preenchidos via Supabase',
        sqlserver:  '✅ Dados preenchidos via SQL Server corporativo',
        sistema:    '✅ Dados carregados do cadastro do sistema',
      };
      showToast(fonteMsgs[res.fonte] || '✅ Veículo encontrado!', 'success');
    }
  } catch (e) {
    const detail = e.message || '';
    if (detail.includes('nao encontrado') || detail.includes('não encontrado') || detail.includes('404')) {
      showToast('Placa não encontrada nas bases. Preencha os dados manualmente.', 'warning');
    } else {
      console.error(e);
      showToast('Erro ao consultar bases de veículo.', 'error');
    }
  } finally {
    buscandoPlaca.value = false;
  }
}

async function saveVeiculo() {
  try {
    if (editingVeiculo.value) await updateVeiculo(editingVeiculo.value.id, veiculoForm.value)
    else await createVeiculo(veiculoForm.value)
    showVeiculoModal.value = false
    showToast(editingVeiculo.value ? 'Veículo atualizado!' : 'Veículo criado!')
    loadVeiculos()
    refreshDash()
  } catch(e) { showToast(e.message, 'error') }
}
async function removeVeiculo(v) {
  if (!confirm(`Deseja realmente EXCLUIR o veículo ${v.placa}? Esta ação não pode ser desfeita.`)) return
  try {
    await deleteVeiculo(v.id)
    showToast('Veículo excluído com sucesso!')
    loadVeiculos()
    refreshDash()
  } catch(e) { showToast(e.message, 'error') }
}



async function saveVeiculoInline(v) {
  try {
    await updateVeiculo(v.id, { placa: v.placa, frota: v.frota, modelo: v.modelo, marca: v.marca, tipo: v.tipo, filial_id: v.filial_id })
    showToast('Veículo salvo com sucesso!')
    loadVeiculos() // Recarrega para obter contagens atualizadas
    refreshDash()
  } catch(e) {
    showToast(e.message, 'error')
    loadVeiculos() // Reverte
  }
}

async function loadEstoqueAlmoxarifado() {
  if (!almoxarifadoFilialId.value) {
    pneusEstoqueFilial.value = []
    return
  }
  try {
    pneusEstoqueFilial.value = await fetchPneusList({ filial_id: almoxarifadoFilialId.value, status: 'estoque' })
  } catch(e) { pneusEstoqueFilial.value = [] }
}

// Veículo Detail (Eixos)
async function openVeiculoDetail(v) {
  try {
    veiculoDetail.value = await fetchVeiculo(v.id)
    searchStock.value = ''
    almoxarifadoFilialId.value = veiculoDetail.value.filial_id
    await loadEstoqueAlmoxarifado()
    if (tab.value !== 'alocacoes') {
      showEixosModal.value = true
    }
  } catch(e) { showToast(e.message, 'error') }
}

// Handle Tire Click
async function handleTireClick(pos) {
  const pneu = veiculoDetail.value?.pneus?.[pos]
  if (pneu) {
    openRemoverModal(pneu)
  } else {
    // Alocar pneu
    alocarCtx.value = { fromEixo: true, posicao: pos }
    alocarForm.value = { pneu_id: null, veiculo_id: veiculoDetail.value.id, posicao: pos, km_instalacao: veiculoDetail.value?.km_atual || 0, observacao: '' }
    try { pneusEstoqueFilial.value = await fetchPneusList({ filial_id: veiculoDetail.value.filial_id, status: 'estoque' }) }
    catch(e) { pneusEstoqueFilial.value = [] }
    showAlocarModal.value = true
  }
}

// Pneus CRUD
function openPneuForm(p = null) {
  editingPneu.value = p
  modeloSelecionado.value = null
  pneuForm.value = p 
    ? { numero_fogo: p.numero_fogo, marca: p.marca, modelo: p.modelo || '', medida: p.medida, dot: p.dot || '', valor: p.valor || 0, vida: p.vida || 1, sulco_atual: p.sulco_atual || 0, filial_id: p.filial_id, nf: p.nf || '', fornecedor: p.fornecedor || '' } 
    : { numero_fogo: '', marca: '', modelo: '', medida: '', dot: '', valor: 0, vida: 1, sulco_atual: 0, filial_id: null, nf: '', fornecedor: '' }
  showPneuModal.value = true
}

function fillModelo() {
  if (modeloSelecionado.value) {
    pneuForm.value.marca = modeloSelecionado.value.marca || ''
    pneuForm.value.modelo = modeloSelecionado.value.modelo || ''
    pneuForm.value.medida = modeloSelecionado.value.medida || ''
  }
}

async function savePneu() {
  try {
    // pneuForm.value contains the data
    if (editingPneu.value) {
      await updatePneuApi(editingPneu.value.id, pneuForm.value)
    } else {
      await createPneu(pneuForm.value)
    }
    showPneuModal.value = false
    showToast(editingPneu.value ? 'Pneu atualizado!' : 'Pneu cadastrado!')
    loadPneus()
    refreshDash()
  } catch (e) {
    showToast(e.message || 'Erro ao salvar pneu', 'error')
  }
}

async function downloadTemplate() {
  const url = fetchPneusTemplate()
  // Usar window.open para download direto é mais robusto em domínios protegidos
  window.open(url, '_blank')
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
    showToast('Importando pneus... favor aguardar', 'info')
    const data = await importPneusCsv(formData)
    if (data.error) {
      showToast('Erro na Planilha: ' + data.error, 'error')
    } else {
       showToast(data.message || `Sucesso! ${data.count} pneus foram processados.`)
       loadPneus()
       refreshDash()
    }
  } catch (error) {
    console.error(error)
    showToast('Erro ao importar: ' + (error.response?.data?.detail || error.message), 'error')
  } finally {
    event.target.value = '' // Limpa o input
  }
}

// Alocar
function openAlocarModal(p) {
  alocarCtx.value = { fromEixo: false, posicao: '' }
  alocarForm.value = { 
    pneu_id: p.id, 
    veiculo_id: veiculoDetail.value?.id || null, 
    posicao: '', 
    km_instalacao: veiculoDetail.value?.km_atual || 0, 
    observacao: '' 
  }
  showAlocarModal.value = true
}
async function loadPosDisponiveis() {
  if (!alocarForm.value.veiculo_id) { posDisponiveis.value = []; return }
  try {
    const v = await fetchVeiculo(alocarForm.value.veiculo_id)
    if (!alocarCtx.value.fromEixo) alocarForm.value.km_instalacao = v.km_atual || 0
    const cfg = v.config
    const all = []
    cfg.eixos.forEach(e => all.push(...e.posicoes))
    all.push(...cfg.estepes)
    posDisponiveis.value = all.filter(p => !v.pneus[p])
  } catch(e) { posDisponiveis.value = [] }
}
async function doAlocar() {
  // Validação de Pneu Usado vs Perfil
  const pneuParaAlocar = pneusGeral.value.find(p => p.id === alocarForm.value.pneu_id)
  const isUsado = pneuParaAlocar && (pneuParaAlocar.km_total > 0 || pneuParaAlocar.vida > 1)
  
  if (isUsado && props.user?.role !== 'admin') {
    showToast('Ação Bloqueada: Pneus USADOS só podem ser alocados por administradores.', 'error')
    return
  }

  const v = veiculos.value.find(x => x.id === alocarForm.value.veiculo_id)
  if (v && alocarForm.value.km_instalacao < (v.km_atual || 0)) {
    if (!confirm(`Atenção: O KM informado (${alocarForm.value.km_instalacao}) é menor que o KM atual do veículo (${v.km_atual}). Deseja continuar mesmo assim?`)) return
  }

  try {
    await alocarPneu(alocarForm.value)
    showAlocarModal.value = false
    showToast('Pneu alocado!')
    loadPneus(); loadVeiculos(); refreshDash(); await loadEstoqueAlmoxarifado();
    if (veiculoDetail.value) { 
      veiculoDetail.value = await fetchVeiculo(veiculoDetail.value.id) 
    }
  } catch(e) { showToast(e.message, 'error') }
}

// Remover
function openRemoverModal(p) {
  removerCtx.value = p
  removerForm.value = { pneu_id: p.id, destino: 'estoque', filial_destino_id: veiculoDetail.value?.filial_id || p.filial_id, km_momento: veiculoDetail.value?.km_atual || 0, observacao: '' }
  showRemoverModal.value = true
}
async function doRemover() {
  const v = veiculoDetail.value
  if (v && removerForm.value.km_momento < (v.km_atual || 0)) {
     if (!confirm(`Atenção: O KM informado (${removerForm.value.km_momento}) é menor que o KM atual do veículo (${v.km_atual}). Deseja continuar mesmo assim?`)) return
  }

  try {
    await removerPneu({ pneu_id: removerCtx.value.id, ...removerForm.value })
    showRemoverModal.value = false
    showToast('Pneu removido!')
    loadPneus(); loadVeiculos(); refreshDash()
    if (veiculoDetail.value) { 
      veiculoDetail.value = await fetchVeiculo(veiculoDetail.value.id) 
      await loadEstoqueAlmoxarifado()
    }
  } catch(e) { showToast(e.message, 'error') }
}

async function doRodizio() {
  try {
    const v = veiculoDetail.value
    if (v && rodizioForm.value.km_momento < (v.km_atual || 0)) {
       showToast(`KM do rodízio (${rodizioForm.value.km_momento}) não pode ser menor que o atual do veículo (${v.km_atual}).`, 'error')
       return
    }
    if (rodizioForm.value.km_momento <= 0) {
      showToast('Por favor, informe um KM válido.', 'error')
      return
    }
    await rodizioPneu({
      veiculo_id: veiculoDetail.value.id,
      pos_origem: rodizioCtx.value.oldPos,
      pos_destino: rodizioCtx.value.pos,
      km_momento: rodizioForm.value.km_momento,
      observacao: rodizioForm.value.observacao
    })
    showRodizioModal.value = false
    showToast('Rodízio realizado com sucesso!')
    veiculoDetail.value = await fetchVeiculo(veiculoDetail.value.id)
    loadPneus(); loadVeiculos(); refreshDash(); await loadEstoqueAlmoxarifado()
  } catch(e) { showToast(e.message, 'error') }
}

// Transferir
function openTransferirModal(p) {
  transferirCtx.value = p
  transferirForm.value = { filial_destino_id: null, observacao: '' }
  showTransferirModal.value = true
}
async function doTransferir() {
  try {
    await transferirPneu({ pneu_id: transferirCtx.value.id, ...transferirForm.value })
    showTransferirModal.value = false
    showToast('Pneu transferido!')
    loadPneus(); refreshDash()
  } catch(e) { showToast(e.message, 'error') }
}

// Reciclagem
async function loadLotes() { 
  try { 
    lotesReciclagem.value = await fetchLotesReciclagem() 
    pneusAguardandoLote.value = await fetchPneusAguardandoLote()
  } catch(e) { console.error(e) } 
}
async function loadFinanceiro() {
  try {
    relatorioFinanceiro.value = await fetchRelatorioFinanceiroReciclagem({
      mes: filtroMesFinanceiro.value,
      filial_id: filtroFilialFinanceiro.value
    })
  } catch(e) { console.error(e) }
}

function exportarFinanceiroCSV() {
  const rf = relatorioFinanceiro.value
  const mes = filtroMesFinanceiro.value || 'todos'
  const sep = ';'
  const header = ['Mes','N. Fogo','Marca','Modelo','Medida','Vida','Lote','Filial Origem','Valor Recebido']
  const rows = rf.detalhes.map(p => [
    mes, p.numero_fogo||'', p.marca||'', p.modelo||'',
    p.medida||'', p.vida||'',
    p.lote_id ? 'LOTE-'+p.lote_id : '',
    p.filial_origem_nome || '',
    String(p.valor_arrecadado||0).replace('.',',')
  ])
  const csv = [header,...rows].map(r=>r.map(c=>`"${String(c).replace(/"/g,'""')}"`).join(sep)).join('\r\n')
  const blob = new Blob(['﻿'+csv],{type:'text/csv;charset=utf-8;'})
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href=url
  a.download = `retorno_financeiro_${mes}.csv`
  a.click(); URL.revokeObjectURL(url)
}

function openReciclagemModal(p) {
  reciclagemCtx.value = p
  reciclagemForm.value = { data_envio: new Date().toISOString().split('T')[0], observacao: '' }
  showReciclagemModal.value = true
}

async function doEnviarParaRecicladora() {
  try {
    const pId = reciclagemCtx.value.id
    await enviarParaReciclagem({
      pneu_id: pId,
      data_envio: reciclagemForm.value.data_envio,
      observacao: reciclagemForm.value.observacao
    })
    
    showReciclagemModal.value = false
    showToast('Pneu enviado para reciclagem!')
    await loadPneusGeral(); 
    await loadPneus(); 
    await loadLotes();
    refreshDash()
  } catch(e) { showToast(e.message, 'error') }
}

function togglePneuSelection(pId) {
  const idx = selectedPneusReciclagem.value.indexOf(pId)
  if (idx > -1) selectedPneusReciclagem.value.splice(idx, 1)
  else selectedPneusReciclagem.value.push(pId)
}

async function doGerarLoteManual() {
  if (selectedPneusReciclagem.value.length === 0) return
  try {
    const res = await criarLoteReciclagem({
      pneu_ids: selectedPneusReciclagem.value,
      filial_id: filtroFilialSucata.value || (pneusAguardandoLote.value[0]?.filial_id) || 1
    })
    showToast(`Lote ${res.lote_id} gerado com sucesso!`)
    selectedPneusReciclagem.value = []
    await loadLotes()
    await loadPneusGeral()
  } catch(e) { showToast(e.message, 'error') }
}

function openValorLoteModal(lote) {
  valorLoteCtx.value = lote
  valorLoteForm.value = { valor_total: lote.valor_total || 0 }
  showValorLoteModal.value = true
}

function imprimirLote(lote) {
  loteImpressao.value = lote
  setTimeout(() => {
    window.print()
    loteImpressao.value = null
  }, 300)
}

async function doAtualizarValorLote() {
  try {
    await atualizarValorLote({
      lote_id: valorLoteCtx.value.id,
      valor_total: valorLoteForm.value.valor_total
    })
    showValorLoteModal.value = false
    showToast('Lote atualizado com sucesso!')
    loadLotes()
  } catch(e) { showToast(e.message, 'error') }
}

async function confirmarChegadaEstoque(p) {
  if (!confirm(`Confirmar chegada do pneu ${p.numero_fogo} (${p.medida}) na filial?`)) return
  try {
    await confirmarRecebimento(p.id)
    // Atualiza só o flag recebido sem alterar status
    const idx = pneusEstoqueFilial.value.findIndex(x => x.id === p.id)
    if (idx !== -1) pneusEstoqueFilial.value[idx].recebido = 1
    showToast(`Pneu ${p.numero_fogo} confirmado!`)
    loadPneus(); refreshDash()
  } catch(e) { showToast(e.message, 'error') }
}

async function doConfirmarRecebimento(p) {
  if (!confirm(`Confirmar que o pneu ${p.numero_fogo} CHEGOU na filial ${p.filial_nome || ''}?`)) return
  try {
    await confirmarRecebimento(p.id)
    
    // Atualização otimista local
    const pIndex = pneusGeral.value.findIndex(px => px.id === p.id)
    if (pIndex !== -1) {
      pneusGeral.value[pIndex].recebido = 1
      pneusGeral.value[pIndex].status = 'descarte'
    }

    showToast('Recebimento confirmado!')
    await loadPneusGeral()
    loadPneus(); refreshDash(); await loadEstoqueAlmoxarifado();
    if (veiculoDetail.value) { 
       veiculoDetail.value = await fetchVeiculo(veiculoDetail.value.id) 
    }
  } catch(e) { showToast(e.message, 'error') }
}

async function mandarPneuParaSucata(p) {
  const sucataFilial = filiais.value.find(f => f.nome.toUpperCase().includes('SUCATA'))
  if (!sucataFilial) {
    showToast('Não encontrei uma filial com o nome "SUCATA". Crie uma primeiro.', 'error')
    return
  }
  if (!confirm(`Deseja enviar o pneu ${p.numero_fogo} para a filial SUCATA?`)) return
  try {
    await transferirPneu({ pneu_id: p.id, filial_destino_id: sucataFilial.id, observacao: 'Enviado para sucata via atalho' })
    showToast('Pneu enviado para a fila de recebimento da Sucata!')
    loadPneus(); loadPneusGeral(); refreshDash()
  } catch(e) { showToast(e.message, 'error') }
}

watch(tab, (t) => {
  if (t === 'sucata') loadPneusGeral()
})

watch(() => removerForm.value.destino, (val) => {
  if (val === 'descarte') {
    const sucata = filiais.value.find(f => f.nome.toUpperCase().includes('SUCATA'))
    if (sucata) removerForm.value.filial_destino_id = sucata.id
  }
})

onMounted(loadAll)

const tabSubtitles = {
  dashboard:       'Visão geral da frota e alertas críticos',
  estoque_central: 'Cadastro e distribuição de pneus por NF',
  alocacoes:       'Alocação e troca de pneus por veículo',
  veiculos:        'Cadastro e configuração da frota',
  estoque:         'Inventário agrupado por filial e medida',
  historico:       'Registro cronológico de todas as operações',
  sucata:          'Validação e controle de pneus descartados',
  recicladora:     'Lotes de coleta e retorno financeiro',
  financeiro:      'Créditos por filial referente às carcaças',
  solicitacoes:    'Solicitações de pneus por filial',
  filiais:         'Configuração das unidades operacionais',
  usuarios:        'Gerenciamento de usuários e permissões',
}
const currentTabSubtitle = computed(() => tabSubtitles[tab.value] || 'Gestão centralizada de frota')
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: var(--surface-2);
  overflow: hidden;
  font-family: 'Inter', system-ui, sans-serif;
}

/* SIDEBAR */
.sidebar {
  width: 200px;
  height: 100vh;
  background: var(--surface-0);
  display: flex;
  flex-direction: column;
  color: var(--ink-900);
  border-right: 1px solid var(--ink-200);
  z-index: 100;
  overflow: hidden;
  position: sticky;
  top: 0;
}

.sidebar-top {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  border-bottom: 1px solid var(--ink-200);
}

.sidebar-logo {
  height: 36px;
  width: auto;
  border-radius: 3px;
}

.sidebar-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow-y: auto;
  scrollbar-width: none;
  padding: 6px 0;
}
.sidebar-menu::-webkit-scrollbar { display: none; }

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  border: none;
  background: none;
  border-radius: 0;
  color: var(--ink-600);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.12s;
  text-align: left;
  border-left: 2px solid transparent;
  width: 100%;
}

.menu-item:hover {
  background: var(--surface-2);
  color: var(--ink-900);
}

.menu-item.active {
  background: var(--surface-2);
  color: var(--brand-900);
  font-weight: 600;
  border-left-color: var(--brand-900);
}

.menu-icon {
  display: flex;
  flex-shrink: 0;
  opacity: 0.7;
}
.menu-item.active .menu-icon { opacity: 1; }

.sidebar-footer {
  padding: 10px 14px;
  border-top: 1px solid var(--ink-200);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.usuarios-shortcut {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 6px 10px;
  background: var(--surface-1);
  border: 1px solid var(--ink-200);
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  color: var(--ink-600);
  cursor: pointer;
  transition: background 0.12s;
  text-align: left;
}
.usuarios-shortcut:hover { background: var(--surface-2); color: var(--ink-900); }
.usuarios-shortcut.active { background: var(--brand-bg); border-color: var(--brand-mid); color: var(--brand-dark); }

.user-block {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: var(--surface-1);
  border-radius: 3px;
  border: 1px solid var(--ink-200);
}

.avatar {
  width: 28px;
  height: 28px;
  background: var(--ink-200);
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--ink-600);
}

.u-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.u-name {
  font-size: 11px;
  font-weight: 600;
  color: var(--ink-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.u-tag {
  font-size: 10px;
  color: var(--ink-300);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.mini-logout {
  background: none;
  border: 1px solid var(--ink-200);
  cursor: pointer;
  padding: 5px;
  border-radius: 3px;
  transition: background 0.12s, border-color 0.12s;
  color: var(--ink-600);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mini-logout:hover {
  background: var(--status-critical-bg);
  border-color: var(--status-critical);
  color: var(--status-critical);
}

/* MAIN CONTENT */
.main-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
  position: relative;
}

/* Abas com scroll (filhos diretos de main-content que não são alocacao) */
.main-content > .gp-section:not(.alocacao-layout) {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

/* wb-body substitui gp-move-container */
.wb-body { flex: 1; display: flex; overflow: hidden; }
.gp-vehicle-canvas { flex: 1; padding: 24px; background: #fafafa; overflow-y: auto; border-right: 1px solid #e2e8f0; display: flex; justify-content: center; align-items: flex-start; }

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid var(--ink-200);
  background: var(--surface-0);
  flex-shrink: 0;
}

.header-info h1 {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-900);
  margin: 0;
}

.header-sub {
  color: var(--ink-600);
  font-size: 11px;
  margin: 2px 0 0 0;
}

.header-kpis {
  display: flex;
  gap: 0;
  border: 1px solid var(--ink-200);
  border-radius: 3px;
  overflow: hidden;
}

.kpi-box {
  background: var(--surface-0);
  padding: 6px 14px;
  border-right: 1px solid var(--ink-200);
  display: flex;
  flex-direction: column;
  min-width: 90px;
}
.kpi-box:last-child { border-right: none; }

.kpi-n {
  font-size: 16px;
  font-weight: 600;
  color: var(--ink-900);
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.kpi-t {
  font-size: 9px;
  text-transform: uppercase;
  color: var(--ink-300);
  font-weight: 600;
  letter-spacing: 0.05em;
}

.kpi-blue .kpi-n { color: var(--blue); }
.kpi-green .kpi-n { color: var(--status-ok); }
.kpi-red .kpi-n { color: var(--status-critical); }
.kpi-gold .kpi-n { color: var(--status-warn); }

.gp-section {
  background: var(--surface-0);
  border-radius: var(--radius-card);
  border: 1px solid var(--ink-200);
  padding: 14px 16px;
}
.sec-toolbar { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.sec-toolbar h2 { font-size: 13px; font-weight: 600; margin-right: auto; }

/* Tables */
.table-responsive { width: 100%; overflow-x: auto; }
.table-responsive::-webkit-scrollbar { height: 6px; }
.table-responsive::-webkit-scrollbar-track { background: var(--surface-2); }
.table-responsive::-webkit-scrollbar-thumb { background: var(--ink-300); }
.table-responsive::-webkit-scrollbar-thumb:hover { background: var(--ink-600); }

.gp-table { width: 100%; border-collapse: collapse; font-size: 12px; white-space: nowrap; }
.gp-table th { background: var(--brand-900); font-weight: 600; color: var(--surface-0); text-transform: uppercase; letter-spacing: 0.05em; font-size: 10px; padding: 6px 10px; border-bottom: 1px solid var(--brand-800); text-align: left; }
.gp-table td { padding: 6px 10px; border-bottom: 1px solid var(--ink-200); color: var(--ink-900); vertical-align: middle; }
.gp-table tr:hover td { background: var(--surface-2); }
.row-disabled td { opacity: 0.45; text-decoration: line-through; }
.td-actions { display: flex; gap: 6px; }

.vida-badge { background: var(--s2); font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px; color: var(--text2); }

/* Inline Select */
.inline-select { padding: 5px 10px; border: 1px solid var(--ink-300); border-radius: var(--radius-input); background: var(--surface-0); font-size: 12px; font-weight: 500; color: var(--ink-900); outline: none; transition: border-color 0.12s; width: 100%; max-width: 180px; cursor: pointer; height: 30px; }
.inline-select:focus { border-color: var(--brand-900); }

/* Badges */
.badge { display: inline-block; padding: 2px 6px; border-radius: var(--radius-chip); font-size: 10px; font-weight: 600; }
.badge-green { background: var(--status-ok-bg); color: var(--status-ok); }
.badge-blue { background: var(--blue2); color: var(--blue); }
.badge-red { background: var(--status-critical-bg); color: var(--status-critical); }
.badge-yellow { background: var(--status-warn-bg); color: var(--status-warn); }
.badge-purple { background: #e0e7ff; color: #3730a3; }

/* Buttons */
.btn-primary { padding: 6px 14px; background: var(--brand-900); color: var(--surface-0); border: 1px solid var(--brand-800); border-radius: var(--radius-input); font-size: 12px; font-weight: 600; cursor: pointer; transition: background 0.12s; white-space: nowrap; }
.btn-primary:hover:not(:disabled) { background: var(--brand-800); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { padding: 6px 14px; background: var(--surface-0); color: var(--ink-900); border: 1px solid var(--ink-300); border-radius: var(--radius-input); font-size: 12px; font-weight: 600; cursor: pointer; transition: background 0.12s, border-color 0.12s; }
.btn-secondary:hover { background: var(--surface-2); border-color: var(--ink-600); }
.btn-sm { padding: 4px 10px; border: 1px solid var(--ink-300); background: var(--surface-0); border-radius: var(--radius-input); font-size: 11px; font-weight: 600; cursor: pointer; color: var(--ink-900); transition: background 0.12s, border-color 0.12s; white-space: nowrap; display: inline-flex; align-items: center; gap: 4px; }
.btn-sm:hover { background: var(--surface-2); border-color: var(--ink-600); }
.btn-accent { background: var(--brand-100); color: var(--brand-900); border-color: var(--brand-600); }
.btn-accent:hover { background: var(--brand-600); color: var(--surface-0); }
.btn-danger { color: var(--status-critical); border-color: var(--ink-200); }
.btn-danger:hover { background: var(--status-critical-bg); border-color: var(--status-critical); }

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.filter-select { padding: 5px 10px; border: 1px solid var(--ink-300); border-radius: var(--radius-input); font-size: 12px; font-weight: 500; background: var(--surface-0); color: var(--ink-900); min-width: 140px; outline: none; transition: border-color 0.12s; height: 30px; }
.filter-select:focus { border-color: var(--brand-900); }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.55); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background: var(--surface-0); border-radius: var(--radius-card); border: 1px solid var(--ink-200); padding: 20px 24px; width: 480px; max-width: 95vw; max-height: 90vh; overflow-y: auto; box-shadow: var(--shadow-float); animation: modalIn 0.12s ease; }
@keyframes modalIn { from { opacity: 0; } to { opacity: 1; } }
.modal-wide { width: 800px; }
.modal-box h3 { font-size: 14px; font-weight: 600; margin-bottom: 16px; color: var(--ink-900); }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--ink-200); }

/* Forms */
.form-group { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; flex: 1; }
.form-group label { font-size: 10px; font-weight: 600; color: var(--ink-600); text-transform: uppercase; letter-spacing: 0.06em; }
.form-group input, .form-group select { padding: 7px 10px; border: 1px solid var(--ink-300); border-radius: var(--radius-input); font-size: 13px; color: var(--ink-900); background: var(--surface-0); transition: border-color 0.12s; outline: none; }
.form-group input:focus, .form-group select:focus { border-color: var(--brand-900); box-shadow: 0 0 0 2px rgba(90,24,28,0.1); }
.form-row { display: flex; gap: 12px; }

/* Empty */
.empty-state { text-align: center; padding: 24px 16px; color: var(--ink-300); font-size: 12px; display: flex; flex-direction: column; align-items: center; border: 1px solid var(--ink-200); border-radius: var(--radius-card); margin: 8px 0; background: var(--surface-1); }
.empty-state p { margin: 0; }

/* ── Accordion Estoque: Filial → Medida ─────────────────────────── */
.est-filial-list { display: flex; flex-direction: column; gap: 10px; margin-top: 12px; }
.est-filial-card { background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: 4px; overflow: hidden; }
.est-filial-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; cursor: pointer; user-select: none;
  background: var(--surface-1); border-bottom: 1px solid transparent; gap: 12px;
  transition: background 120ms;
}
.est-filial-header:hover { background: var(--surface-2); }
.est-filial-left { display: flex; align-items: center; gap: 8px; }
.est-filial-nome { font-size: 13px; font-weight: 700; color: var(--ink-900); }
.est-filial-badge { font-size: 10px; font-weight: 600; background: var(--ink-200); color: var(--ink-600); padding: 1px 6px; border-radius: 3px; }
.est-chevron { display: flex; align-items: center; color: var(--ink-300); transition: transform 180ms; }
.est-chevron.open { transform: rotate(90deg); }
.est-chevron-sm { display: flex; align-items: center; color: var(--ink-300); transition: transform 180ms; }
.est-chevron-sm.open { transform: rotate(90deg); }
.est-status-pills { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.est-pill { font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 3px; white-space: nowrap; }
.pill-uso  { background: var(--blue2); color: var(--blue); }
.pill-est  { background: var(--status-ok-bg); color: var(--status-ok); }
.pill-rec  { background: var(--status-warn-bg); color: var(--status-warn); }
.pill-des  { background: var(--status-critical-bg); color: var(--status-critical); }
.pill-xs   { font-size: 9px; padding: 1px 6px; }
.est-medidas { padding: 8px; display: flex; flex-direction: column; gap: 6px; }
.est-medida-grupo { border: 1px solid var(--ink-200); border-radius: 7px; overflow: hidden; }
.est-medida-header {
  display: flex; align-items: center; gap: 8px;
  padding: 9px 12px; cursor: pointer; user-select: none;
  background: var(--surface-0); transition: background 120ms; flex-wrap: wrap;
}
.est-medida-header:hover { background: var(--surface-1); }
.est-medida-tag { font-size: 11px; font-weight: 600; background: var(--blue2); color: var(--blue); padding: 1px 6px; border-radius: 3px; }
.est-medida-qtd { font-size: 11px; color: var(--ink-600); }
.est-medida-meta { display: flex; gap: 10px; margin-left: 4px; }
.est-medida-meta span { font-size: 10px; }
.meta-ok { color: var(--status-ok); }
.meta-critico { color: var(--status-critical); font-weight: 600; }
.meta-vida { color: var(--ink-600); }
.est-medida-status { display: flex; gap: 5px; margin-left: auto; flex-wrap: wrap; justify-content: flex-end; }
.est-pneus-table { padding: 0 10px 10px; }
.gm-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.gm-table th { text-align: left; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; color: var(--ink-300); padding: 6px 8px; border-bottom: 1px solid var(--ink-200); white-space: nowrap; }
.gm-table td { padding: 7px 8px; border-bottom: 1px solid var(--surface-2); color: var(--ink-600); vertical-align: middle; }
.gm-table tbody tr:last-child td { border-bottom: none; }
.gm-table tbody tr:hover td { background: var(--surface-1); }
.fogo-est { color: var(--ink-900); font-size: 12px; }
.td-marca-est { color: var(--ink-600); }
.modelo-est { color: var(--ink-300); font-size: 11px; margin-left: 4px; }
.td-placa-est { font-family: monospace; font-size: 11px; color: var(--ink-600); }
.sulco-wrap { display: flex; align-items: center; gap: 5px; }
.sulco-bar-mini { width: 36px; height: 5px; background: var(--brand-100); border-radius: 99px; overflow: hidden; flex-shrink: 0; }
.sulco-fill-mini { height: 100%; background: var(--status-ok); border-radius: 99px; }
.sulco-fill-mini.sulco-crit { background: var(--status-critical); }
.sulco-val-mini { font-size: 11px; color: var(--ink-600); white-space: nowrap; }
.sulco-val-mini.sulco-crit { color: var(--status-critical); font-weight: 700; }

/* Eixos Diagram PREMIUM */
.modal-expanded { width: 1100px; max-width: 98vw; padding: 0; overflow: hidden; display: flex; flex-direction: column; }
.modal-header-gp { padding: 10px 16px; border-bottom: 1px solid var(--ink-200); display: flex; justify-content: space-between; align-items: center; background: var(--surface-1); }
.vd-config-badge { font-size: 10px; font-weight: 600; background: var(--surface-2); color: var(--ink-600); padding: 1px 6px; border-radius: 3px; text-transform: uppercase; letter-spacing: 0.04em; }
.btn-close { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--ink-300); line-height: 1; }

.gp-move-container { display: flex; height: 600px; }

/* Diagram Área */
.gp-vehicle-canvas { flex: 1; padding: 24px 20px; background: var(--surface-1); overflow-y: auto; border-right: 1px solid var(--ink-200); display: flex; justify-content: center; align-items: flex-start; }

.vehicle-diagram-area { position: relative; padding: 60px 40px; margin-top: 20px; }

.chassis-box { position: absolute; left: 50%; transform: translateX(-50%); width: 220px; top: 0; bottom: 0; border: 6px solid var(--ink-200); border-radius: 20px; z-index: 1; background: var(--surface-1); }
.placa-box { position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: var(--surface-0); border: 1px solid var(--ink-300); border-radius: 4px; border-top: 5px solid #0284c7; width: 90px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index: 5; }
.placa-br { font-size: 8px; font-weight: 700; color: var(--surface-0); background: #0284c7; margin-top: -5px; padding-bottom: 1px; }
.placa-num { font-size: 14px; font-weight: 700; color: var(--ink-900); padding: 2px 0; font-family: monospace; }
.chassis-vertical-line { position: absolute; left: 50%; transform: translateX(-50%); width: 10px; background: var(--ink-300); top: 10%; bottom: 10%; z-index: 1; border-radius: 4px; }

.axles-container { display: flex; flex-direction: column; gap: 30px; z-index: 2; position: relative; }

.axle-row { display: flex; align-items: center; justify-content: center; position: relative; width: 100%; z-index: 2; }
.axle-visual { display: flex; align-items: center; justify-content: center; position: relative; width: 350px; height: 100px; }

.axle-bar { position: absolute; left: 16px; right: 16px; height: 10px; background: var(--ink-300); z-index: 1; border-radius: 4px; }

.center-shape { position: absolute; z-index: 3; background: var(--surface-1); border: 6px solid var(--ink-300); }
.shape-diamond { width: 40px; height: 40px; transform: rotate(45deg); }
.shape-circle { width: 40px; height: 40px; border-radius: 50%; }

.wheels-side { display: flex; gap: 4px; z-index: 5; position: absolute; }
.side-esq { left: 0; }
.side-dir { right: 0; }

.tire-drop-zone {
  width: 32px; height: 90px; border: 2px dashed var(--ink-300); border-radius: 8px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  transition: all 0.2s; background: var(--surface-0); cursor: pointer;
}
.tire-drop-zone.drag-over { border-color: var(--brand); background: var(--brand-bg); }
.tire-drop-zone.occupied { border: none; background: transparent; }

.tire-placeholder { display: flex; flex-direction: column; align-items: center; color: var(--ink-300); }
.tire-placeholder span { font-size: 24px; font-weight: 300; }

.tire-item {
  width: 32px; height: 90px; background: var(--ink-900);
  border-radius: 6px; display: flex; align-items: center; justify-content: center;
  color: var(--surface-0); cursor: grab;
  position: relative; box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  border: 3px solid transparent; box-sizing: border-box; transition: border-color 0.15s;
}
.tire-item.tire-new  { border-color: transparent; }
.tire-item.tire-used { border-color: transparent; }
.tire-item.tire-worn { border-color: transparent; }

.tire-id { writing-mode: vertical-rl; transform: rotate(180deg); font-size: 12px; font-weight: 700; letter-spacing: 1px; color: var(--surface-0); z-index: 2; }

/* Estepes */
.spare-container { position: absolute; right: -80px; top: 50%; transform: translateY(-50%); display: flex; flex-direction: column; align-items: center; gap: 10px; z-index: 5; }
.spare-title { font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 5px; }


/* Stock Panel */
.gp-stock-panel { width: 280px; background: var(--surface-1); border-left: 1px solid var(--ink-200); display: flex; flex-direction: column; }
.stock-header { padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--ink-200); background: var(--surface-0); }
.stock-header h4 { font-size: 12px; font-weight: 600; }
.stock-count { font-size: 10px; font-weight: 600; color: var(--brand-900); background: var(--brand-100); padding: 1px 6px; border-radius: 3px; }
.search-stock { padding: 8px 10px; border-bottom: 1px solid var(--ink-200); }

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 8px;
  color: var(--ink-300);
  pointer-events: none;
}

.stock-input {
  width: 100%;
  padding: 6px 10px 6px 30px;
  border: 1px solid var(--ink-300);
  border-radius: var(--radius-input);
  font-size: 12px;
  background: var(--surface-0);
  transition: border-color 0.12s;
  outline: none;
}

.stock-input:focus {
  border-color: var(--brand-900);
}

.stock-list { flex: 1; overflow-y: auto; padding: 8px 10px; display: flex; flex-direction: column; gap: 6px; }
.tire-card-stock {
  background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: 3px; padding: 8px 10px;
  display: flex; gap: 8px; cursor: grab; transition: border-color 0.12s;
}
.tire-card-stock:hover { border-color: var(--ink-300); }
/* Separador de medida */
.medida-separator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  margin: 6px 0 2px;
  background: var(--surface-2);
  border-left: 2px solid var(--brand-900);
}
.medida-sep-label { font-size: 10px; font-weight: 600; color: var(--ink-600); text-transform: uppercase; letter-spacing: 0.04em; }
.medida-sep-count { font-size: 10px; font-weight: 600; color: var(--surface-0); background: var(--brand-900); border-radius: 3px; padding: 1px 5px; }

/* Botão de confirmação PENDENTE */
.pending-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px; height: 22px;
  border-radius: 3px;
  background: var(--status-warn);
  color: white;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
  margin-left: auto;
  border: none;
  cursor: pointer;
  transition: background 0.12s;
}
.tire-card-stock:hover .pending-btn { background: #b87518; }

.tire-card-stock.tire-pending { border-left: 3px solid var(--status-warn); }
.tire-card-stock.tire-new  { border-left: 3px solid var(--status-ok); }
.tire-card-stock.tire-used { border-left: 3px solid var(--status-critical); }
.tire-mini-visual { 
  width: 24px; height: 56px; 
  background: linear-gradient(to right, #1a1a1a 0%, #4a4a4a 50%, #1a1a1a 100%);
  border-radius: 4px; position: relative; border: 1px solid #000;
  box-shadow: inset 0 0 3px rgba(0,0,0,0.8), var(--shadow-sm);
  flex-shrink: 0;
}
.tire-mini-visual::before {
  content: ''; position: absolute; top: 0; left: 4px; right: 4px; bottom: 0;
  border-left: 1px solid rgba(255,255,255,0.08); border-right: 1px solid rgba(255,255,255,0.08);
}
.tire-card-info { display: flex; flex-direction: column; }
.t-fogo { font-size: 13px; font-weight: 700; color: var(--text); }
.t-desc { font-size: 11px; color: var(--text2); }
.t-status { font-size: 10px; font-weight: 600; color: var(--text3); margin-top: 2px; }

.removal-zone {
  margin: 10px; padding: 14px; border: 1px dashed var(--ink-300); border-radius: 3px;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  color: var(--ink-300); transition: border-color 0.12s, background 0.12s;
}
.removal-zone.drag-over { border-color: var(--status-critical); background: var(--status-critical-bg); color: var(--status-critical); }
.removal-zone .icon { font-size: 18px; }
.removal-zone .label { font-size: 10px; font-weight: 600; text-align: center; text-transform: uppercase; letter-spacing: 0.04em; }

.empty-stock { text-align: center; padding: 24px 16px; font-size: 12px; color: var(--ink-300); }

@media (max-width: 768px) {
  .gp-move-container { flex-direction: column; height: auto; }
  .gp-stock-panel { width: 100%; height: 400px; border-left: none; border-top: 1px solid var(--border); }
}

/* Config Preview Box */
.config-preview-box { background: var(--brand-100); border: 1px solid var(--brand-600); border-radius: 3px; padding: 12px; margin-top: 8px; }

/* Sucata Tab Styles */
.sucata-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 14px; }
.sucata-column { background: var(--surface-1); border: 1px solid var(--ink-200); border-radius: 4px; padding: 14px; display: flex; flex-direction: column; gap: 10px; }
.col-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--ink-200); padding-bottom: 10px; }
.col-header h3 { font-size: 13px; font-weight: 600; color: var(--ink-900); }
.sucata-cards { display: flex; flex-direction: column; gap: 6px; overflow-y: auto; max-height: 600px; }
.sucata-card {
  background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: 4px; padding: 10px 12px;
  display: flex; align-items: center; gap: 10px;
}
.sucata-card.pending { border-left: 3px solid var(--status-warn); }
.sucata-card.done { border-left: 3px solid var(--status-ok); }
.s-card-id { font-size: 12px; font-weight: 700; color: var(--ink-900); background: var(--surface-2); padding: 2px 6px; border-radius: 3px; font-variant-numeric: tabular-nums; }
.s-card-info { flex: 1; display: flex; flex-direction: column; }
.s-card-info span { font-size: 12px; font-weight: 600; }
.s-card-info small { font-size: 10px; color: var(--ink-300); }
.btn-confirm-arrival {
  background: var(--brand-900); color: var(--surface-0); border: 1px solid var(--brand-800); padding: 5px 12px; border-radius: var(--radius-input);
  font-size: 11px; font-weight: 600; cursor: pointer; transition: background 0.12s;
}
.btn-confirm-arrival:hover { background: var(--brand-800); }
.empty-sucata { text-align: center; padding: 24px 16px; color: var(--ink-300); font-size: 12px; }
.s-card-actions { display: flex; align-items: center; gap: 6px; }
.btn-icon { background: none; border: none; cursor: pointer; font-size: 14px; opacity: 0.6; transition: opacity 0.15s; color: var(--ink-600); }
.btn-icon:hover { opacity: 1; }


.preview-info { display: flex; gap: 16px; margin-bottom: 4px; }
.p-item { display: flex; align-items: center; gap: 8px; }
.p-icon { font-size: 18px; }
.p-text { font-size: 13px; color: var(--ink-900); }
.p-text strong { font-size: 16px; color: var(--brand-900); }
.preview-desc { font-size: 10px; color: var(--ink-300); font-weight: 500; margin: 0; }

.select-premium { border-color: var(--brand-mid) !important; font-weight: 600; color: var(--brand-900); }

/* Toast */
.toast { position: fixed; bottom: 16px; right: 16px; padding: 8px 16px; border-radius: var(--radius-chip); font-size: 12px; font-weight: 500; color: #fff; z-index: 2000; animation: slideIn 0.12s ease; box-shadow: var(--shadow-float); }
.toast.success { background: var(--status-ok); }
.toast.error { background: var(--status-critical); }
.toast.warning { background: var(--status-warn); }
.toast.info { background: #2563eb; }
@keyframes slideIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .gp-page { padding: 16px; }
  .form-row { flex-direction: column; }
  .modal-wide { width: 95vw; }
}

/* ── ALOCAÇÃO — VIPAL-STYLE ──────────────────────────────── */
.alocacao-layout { display: flex; gap: 0; padding: 0 !important; flex: 1; min-height: 0; overflow: hidden; margin: 0; }

/* Sidebar esquerda */
.aloc-sidebar { width: 280px; border-right: 1px solid var(--ink-200); background: var(--surface-0); display: flex; flex-direction: column; flex-shrink: 0; }
.aloc-sidebar .search-box { padding: 16px; border-bottom: 1px solid var(--ink-200); }
.aloc-veiculo-list { flex: 1; overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 4px; }
.aloc-v-card { display: flex; align-items: center; gap: 8px; padding: 7px 10px; border-radius: 3px; cursor: pointer; transition: background 0.12s, border-color 0.12s; border: 1px solid var(--ink-200); }
.aloc-v-card:hover { background: var(--surface-1); border-color: var(--ink-300); }
.aloc-v-card.active { background: var(--surface-2); border-color: var(--brand-900); border-left-width: 3px; }
.v-card-icon { color: var(--ink-600); flex-shrink: 0; }
.v-card-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.v-placa { font-weight: 800; color: var(--ink-900); font-size: 14px; }
.v-modelo { font-size: 11px; color: var(--ink-300); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Workbench */
.aloc-workbench { flex: 1; background: #f8fafc; display: flex; flex-direction: column; overflow: hidden; }
.workbench-content { height: 100%; display: flex; flex-direction: column; overflow: hidden; }

/* INFO STRIP */
.wb-strip {
  display: flex; align-items: center; gap: 0;
  background: var(--surface-0);
  border-top: 3px solid var(--brand-900);
  border-bottom: 1px solid var(--ink-200);
  flex-shrink: 0; padding: 0 20px; height: 56px;
}
.wb-strip-placa {
  background: var(--surface-0); border-radius: 4px;
  border: 1px solid var(--ink-200); border-top: 5px solid #2563eb;
  box-shadow: var(--shadow-sm);
  text-align: center; min-width: 76px; padding: 2px 8px; margin-right: 20px; flex-shrink: 0;
}
.wsp-br { font-size: 7px; font-weight: 700; color: var(--surface-0); background: #2563eb; margin: -2px -8px 1px; padding: 1px 4px; letter-spacing: 1px; }
.wsp-num { font-size: 14px; font-weight: 800; color: var(--ink-900); font-family: monospace; letter-spacing: 1.5px; }
.wb-strip-sep { width: 1px; height: 28px; background: var(--ink-200); margin-right: 20px; flex-shrink: 0; }
.wb-strip-metas { display: flex; gap: 24px; flex: 1; align-items: center; }
.strip-meta { display: flex; flex-direction: column; }
.sm-lbl { font-size: 9px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--ink-300); font-weight: 600; }
.sm-val { font-size: 13px; font-weight: 600; color: var(--ink-900); white-space: nowrap; }
.strip-ok   { color: var(--status-ok); }
.strip-warn { color: var(--status-warn); }
.strip-edit-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 5px 10px; background: transparent; border: 1px solid var(--ink-200);
  border-radius: var(--radius-input); color: var(--ink-600); font-size: 11px; font-weight: 600; cursor: pointer;
  transition: background 0.12s, border-color 0.12s, color 0.12s; flex-shrink: 0;
}
.strip-edit-btn:hover { background: var(--brand-100); border-color: var(--brand-900); color: var(--brand-900); }

/* CORPO PRINCIPAL */
.wb-body { flex: 1; display: flex; overflow: hidden; }

/* COLUNA DE AÇÕES */
.wb-action-col {
  width: 76px; flex-shrink: 0;
  background: var(--surface-2); border-left: 1px solid var(--ink-200); border-right: 1px solid var(--ink-200);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; padding: 12px 8px;
}
.action-col-label { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--ink-300); }
.action-card {
  width: 58px; padding: 8px 4px; border: 1px dashed var(--ink-300); border-radius: 3px;
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  color: var(--ink-600); font-size: 9px; font-weight: 600; text-transform: uppercase; text-align: center;
  cursor: pointer; transition: border-color 0.12s, background 0.12s, color 0.12s; user-select: none;
}
.action-card:hover { border-color: var(--ink-600); background: var(--ink-200); color: var(--ink-900); }
.action-sucata.drag-over { border-color: var(--status-critical); background: var(--status-critical-bg); color: var(--status-critical); border-style: solid; }
.action-estoque:hover { border-color: var(--brand); background: var(--brand-bg); color: var(--brand); }
.action-estoque.drag-over { border-color: var(--brand-900); background: var(--brand-100); color: var(--brand-900); border-style: solid; }

/* PAINEL DE ESTOQUE */
.gp-stock-panel { width: 290px; flex-shrink: 0; background: var(--surface-0); border-left: 1px solid var(--ink-200); display: flex; flex-direction: column; overflow: hidden; }

.stock-panel-head { background: var(--surface-1); border-bottom: 1px solid var(--ink-200); padding: 0 12px; flex-shrink: 0; }
.stock-tabs-row { display: flex; }
.stock-tab { display: flex; align-items: center; gap: 5px; padding: 10px 12px; font-size: 12px; font-weight: 600; color: var(--ink-600); background: none; border: none; border-bottom: 2px solid transparent; cursor: pointer; transition: all 0.15s; }
.stock-tab-active { color: var(--ink-900); border-bottom-color: var(--brand-900); }
.stock-tab-count { font-size: 10px; font-weight: 700; background: var(--brand-900); color: var(--surface-0); padding: 1px 5px; border-radius: 3px; }

.stock-panel-filters { padding: 8px 10px; display: flex; flex-direction: column; gap: 6px; border-bottom: 1px solid var(--ink-200); flex-shrink: 0; background: var(--surface-0); }
.stock-filial-sel { width: 100%; padding: 5px 8px; border: 1px solid var(--ink-200); border-radius: 6px; font-size: 12px; background: var(--surface-1); outline: none; }
.stock-filial-sel:focus { border-color: var(--brand-900); }
.stock-search-wrap { display: flex; align-items: center; gap: 6px; background: var(--surface-1); border: 1px solid var(--ink-200); border-radius: 6px; padding: 5px 8px; }
.stock-search-wrap svg { color: var(--ink-300); flex-shrink: 0; }
.stock-search-inp { border: none; background: transparent; font-size: 12px; outline: none; width: 100%; color: var(--ink-900); }

/* GRADE DE PNEUS */
.stock-tire-grid { flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 12px; }
.grid-medida-lbl { display: flex; align-items: center; justify-content: space-between; font-size: 10px; font-weight: 700; color: var(--ink-600); text-transform: uppercase; letter-spacing: .04em; padding: 2px 0; border-bottom: 1px solid var(--surface-2); }
.grid-medida-cnt { background: var(--brand-900); color: var(--surface-0); font-size: 9px; padding: 1px 5px; border-radius: 3px; }
.grid-tires-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(48px, 1fr)); gap: 6px; padding-top: 6px; }

/* Item de pneu na grade */
.grid-tire-item { display: flex; flex-direction: column; align-items: center; gap: 3px; cursor: grab; }
.grid-tire-item:active { cursor: grabbing; }
.grid-tire-item:hover .gt-body { box-shadow: 0 0 0 2px var(--brand-600); }

.gt-body {
  width: 38px; height: 86px;
  background: linear-gradient(to right, #111 0%, #333 40%, #444 50%, #333 60%, #111 100%);
  border-radius: 5px; border: 3px solid transparent;
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  box-shadow: 2px 2px 6px rgba(0,0,0,.35);
  transition: transform 0.12s, box-shadow 0.12s;
}
.gt-body::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(90deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.06) 50%, rgba(255,255,255,0) 70%);
}

/* Novo pneu — borda verde */
.gt-new .gt-body {
  border-color: #22c55e;
  box-shadow: 2px 2px 6px rgba(0,0,0,.3), 0 0 0 2px rgba(34,197,94,.25);
}
/* Pendente chegada — borda dashed âmbar */
.gt-pending .gt-body {
  border-color: var(--status-warn);
  border-style: dashed;
}
/* Usado — borda âmbar (tem km, sulco ok) */
.gt-used .gt-body { border-color: var(--status-warn); box-shadow: 2px 2px 6px rgba(0,0,0,.3), 0 0 0 2px rgba(199,134,26,.2); }
/* Desgastado — borda vermelha (sulco crítico < 4mm) */
.gt-worn .gt-body { border-color: var(--status-critical); box-shadow: 2px 2px 6px rgba(0,0,0,.3), 0 0 0 2px rgba(195,61,69,.25); }

.gt-num {
  writing-mode: vertical-rl; transform: rotate(180deg);
  font-size: 10px; font-weight: 700; color: rgba(255,255,255,.92);
  letter-spacing: .5px; z-index: 2;
  text-shadow: 0 1px 3px rgba(0,0,0,.9);
}
.gt-pending-dot {
  position: absolute; top: 3px; right: 3px;
  width: 12px; height: 12px; background: #f97316; border-radius: 50%;
  font-size: 9px; font-weight: 900; color: #fff;
  display: flex; align-items: center; justify-content: center;
}
.gt-sulco { font-size: 9px; color: #94a3b8; text-align: center; }

/* Utilitários */
.empty-mini { text-align: center; padding: 20px; font-size: 12px; color: var(--text3); }
.select-v-prompt { text-align: center; margin-top: 100px; }
.prompt-icon { display: block; margin-bottom: 20px; opacity: 0.4; }

@media (max-width: 1200px) {
  .aloc-sidebar { width: 230px; }
  .gp-stock-panel { width: 260px; }
}
@media (max-width: 1024px) {
  .wb-action-col { width: 58px; }
  .action-card span { display: none; }
}

/* Histórico Timeline */
.sec-subtitle { font-size: 13px; color: var(--text3); margin: -4px 0 0; }
.search-box-pill { display: flex; align-items: center; gap: 6px; background: var(--surface-1); padding: 5px 10px; border-radius: var(--radius-input); border: 1px solid var(--ink-300); width: 240px; }
.search-box-pill input { background: transparent; border: none; outline: none; font-size: 12px; width: 100%; color: var(--ink-900); }
.search-box-pill svg { color: var(--ink-300); }

.timeline-container { display: flex; flex-direction: column; gap: 2px; padding: 16px 0; max-width: 900px; margin: 0 auto; }
.timeline-item { display: flex; gap: 20px; padding: 10px 12px; border-radius: var(--radius-card); transition: background 0.12s; position: relative; }
.timeline-item:hover { background: var(--surface-1); }
.timeline-item::before { content: ''; position: absolute; left: 95px; top: 0; bottom: 0; width: 2px; background: var(--ink-200); z-index: 1; }
.timeline-item:first-child::before { top: 20px; }
.timeline-item:last-child::before { bottom: 20px; }

.tl-date { width: 60px; display: flex; flex-direction: column; align-items: flex-end; }
.tl-day { font-size: 14px; font-weight: 800; color: var(--text); }
.tl-time { font-size: 11px; color: var(--text3); font-weight: 600; }

.tl-icon-box {
  width: 32px; height: 32px; border-radius: 3px; background: var(--surface-2); border: 1px solid var(--ink-200);
  display: flex; align-items: center; justify-content: center; font-size: 16px;
  z-index: 2; position: relative; flex-shrink: 0;
}

.tl-content { flex: 1; background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: var(--radius-card); padding: 10px 14px; }
.tl-header { display: flex; justify-content: space-between; margin-bottom: 8px; align-items: center; }
.tl-type { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--ink-900); }
.tl-pneu { font-size: 13px; color: var(--text2); }

.tl-details { display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 12px; }
.tl-detail-item { display: flex; flex-direction: column; gap: 2px; }
.tl-label { font-size: 10px; font-weight: 700; color: var(--text3); text-transform: uppercase; }
.tl-val { font-size: 13px; font-weight: 600; color: var(--text); }

.tl-obs { background: var(--surface-1); padding: 7px 10px; border-radius: 3px; font-size: 11px; color: var(--ink-600); display: flex; align-items: center; gap: 6px; font-style: italic; }
.obs-icon { font-style: normal; }

/* Sucata Origin Badges */
.s-origin-badge { display: flex; align-items: center; gap: 6px; margin-top: 4px; }
.s-origin-badge .lbl { font-size: 10px; font-weight: 700; text-transform: uppercase; color: var(--text3); }
.s-origin-badge .val { font-size: 11px; font-weight: 700; color: #0284c7; background: #f0f9ff; padding: 2px 8px; border-radius: 4px; border: 1px solid #bae6fd; }
.s-tire-name { font-weight: 800; color: #1e293b; font-size: 14px; }

.badge-new-tiny { background: #dcfce7; color: #166534; font-size: 9px; font-weight: 800; padding: 1px 4px; border-radius: 4px; border: 1px solid #bbf7d0; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

.row-new td { background-color: #f0fdf4 !important; border-top: 1px solid #bbf7d0; border-bottom: 1px solid #bbf7d0; }
.row-new:hover td { background-color: #dcfce7 !important; }

/* Reciclagem e Financeiro Styles */
.btn-recicladora { background: #e0f2f1; color: #00897b; border: none; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-recicladora:hover { background: #00897b; color: white; }

.lotes-container { display: flex; flex-direction: column; gap: 24px; }
.lote-card { background: var(--surface-0); border-radius: var(--radius-card); border: 1px solid var(--ink-200); overflow: hidden; }
.lote-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: var(--surface-1); border-bottom: 1px solid var(--ink-200); }
.lote-title { display: flex; gap: 10px; align-items: center; }
.lote-icon { font-size: 16px; }
.lote-names h3 { margin: 0; font-size: 13px; font-weight: 600; color: var(--ink-900); }
.lote-date { font-size: 11px; color: var(--ink-300); }
.lote-finance { display: flex; gap: 16px; align-items: center; }
.finance-item { display: flex; flex-direction: column; text-align: right; }
.finance-item .lbl { font-size: 10px; color: var(--ink-300); text-transform: uppercase; }
.finance-item .val { font-size: 14px; font-weight: 600; color: var(--status-ok); font-variant-numeric: tabular-nums; }
.btn-lote-valor { background: var(--surface-0); border: 1px solid var(--ink-200); padding: 5px 12px; border-radius: var(--radius-input); font-size: 12px; font-weight: 600; color: var(--ink-600); cursor: pointer; transition: border-color 0.12s, color 0.12s; }
.btn-lote-valor:hover { border-color: var(--brand-900); color: var(--brand-900); }
.lote-pneus { padding: 0; }
.gp-table.mini { margin: 0; font-size: 12px; border: none; }
.gp-table.mini th { background: transparent; color: var(--ink-600); padding: 6px 14px; }
.gp-table.mini td { padding: 6px 14px; }

/* ── Financeiro KPIs ── */
.fin-kpis { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
.fin-kpi { display: flex; align-items: center; gap: 10px; background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: var(--radius-card); padding: 10px 14px; flex: 1; min-width: 140px; }
.fin-kpi-icon { width: 30px; height: 30px; background: var(--surface-2); border-radius: 3px; display: flex; align-items: center; justify-content: center; color: var(--ink-600); flex-shrink: 0; }
.fin-kpi-green { border-top: 3px solid var(--status-ok); }
.fin-kpi-green .fin-kpi-icon { background: var(--status-ok-bg); color: var(--status-ok); }
.fin-kpi-blue { border-top: 3px solid var(--blue); }
.fin-kpi-blue .fin-kpi-icon { background: var(--blue2); color: var(--blue); }
.fin-kpi-purple { border-top: 3px solid #8b5cf6; }
.fin-kpi-purple .fin-kpi-icon { background: #f5f3ff; color: #7c3aed; }
.fin-kpi-num { display: block; font-size: 16px; font-weight: 600; color: var(--ink-900); line-height: 1.2; font-variant-numeric: tabular-nums; }
.fin-kpi-lbl { display: block; font-size: 10px; color: var(--ink-300); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 1px; }

/* ── Financeiro body ── */
.fin-body { display: flex; flex-direction: column; gap: 16px; }
.fin-box { background: var(--surface-0); border: 1px solid var(--ink-200); border-radius: var(--radius-card); overflow: hidden; }
.fin-box-header { display: flex; align-items: center; justify-content: space-between; padding: 8px 14px; background: var(--surface-1); border-bottom: 1px solid var(--ink-200); }
.fin-box-title { font-weight: 600; font-size: 14px; color: var(--text, #1e293b); }

/* Barra de proporção */
.fin-bar-wrap { height: 3px; background: var(--surface-2); border-radius: 2px; margin-top: 5px; overflow: hidden; }
.fin-bar { height: 100%; background: var(--status-ok); border-radius: 2px; transition: width .4s ease; }

/* Legados (mantidos para compatibilidade) */
.financeiro-dashboard { display: flex; flex-direction: column; gap: 24px; }
.fin-card-main { display: flex; gap: 24px; background: var(--surface-0); padding: 16px 20px; border-radius: var(--radius-card); border: 1px solid var(--ink-200); }
.fin-stat { display: flex; flex-direction: column; gap: 4px; }
.fin-stat .lbl { font-size: 11px; font-weight: 600; color: var(--ink-600); }
.fin-stat .val { font-size: 20px; font-weight: 600; color: var(--ink-900); font-variant-numeric: tabular-nums; }
.fin-stat .val.big { color: var(--status-ok); }
.fin-grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
.fin-table-box { background: var(--surface-0); padding: 14px 16px; border-radius: var(--radius-card); border: 1px solid var(--ink-200); }
.fin-table-box h3 { margin-bottom: 12px; font-size: 13px; font-weight: 600; }
.text-right { text-align: right; }
.text-center { text-align: center; }
.text-green { color: var(--status-ok); }
.opacity-50 { opacity: 0.5; }

/* PRINT STYLES */
.print-only { display: none; }

@media print {
  /* Oculta sidebar e cabeçalho do app */
  .sidebar,
  .content-header,
  .header-kpis,
  .toast,
  .modal-overlay {
    display: none !important;
  }

  /* Oculta tudo dentro do main EXCETO o manifesto */
  .main-content > *:not(#printable-lote) {
    display: none !important;
  }

  /* Remove flex do layout para o manifesto fluir normalmente */
  .app-layout {
    display: block !important;
    height: auto !important;
    overflow: visible !important;
  }

  .main-content {
    display: block !important;
    margin: 0 !important;
    padding: 0 !important;
    height: auto !important;
    overflow: visible !important;
    width: 100% !important;
  }

  /* Manifesto ocupa a página toda */
  #printable-lote {
    display: block !important;
    width: 100% !important;
    position: static !important;
    background: #fff !important;
  }

  @page {
    size: A4 portrait;
    margin: 15mm;
  }
}

/* ── MANIFESTO DE IMPRESSÃO ─────────────────────────────── */
#printable-lote {
  font-family: 'Inter', Arial, sans-serif;
  color: #111;
  background: #fff;
  padding: 32px;
  box-sizing: border-box;
}

/* CABEÇALHO */
.pm-header {
  display: flex;
  border: 2px solid #1a1a1a;
  margin-bottom: 0;
}

.pm-logo-cell {
  width: 160px;
  min-width: 160px;
  padding: 16px 12px;
  border-right: 2px solid #1a1a1a;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #fff;
}

.pm-logo {
  width: 110px;
  height: auto;
  display: block;
}

.pm-system-label {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: #555;
  text-align: center;
}

.pm-company-cell {
  flex: 1;
  padding: 14px 16px;
  border-right: 2px solid #1a1a1a;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 3px;
}

.pm-company-name {
  font-size: 13px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.pm-company-info {
  font-size: 10px;
  color: #333;
  line-height: 1.5;
}

.pm-title-cell {
  width: 160px;
  min-width: 160px;
  padding: 14px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: #1a1a1a;
  color: #fff;
  gap: 2px;
}

.pm-title-main {
  font-size: 16px;
  font-weight: 900;
  letter-spacing: 1px;
  line-height: 1.1;
}

.pm-title-sub {
  font-size: 9px;
  font-weight: 500;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-top: 6px;
  opacity: 0.85;
  border-top: 1px solid rgba(255,255,255,0.3);
  padding-top: 6px;
  width: 100%;
}

/* METADADOS DO LOTE */
.pm-meta {
  display: flex;
  border: 2px solid #1a1a1a;
  border-top: none;
  margin-bottom: 24px;
}

.pm-meta-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px 16px;
  border-right: 1px solid #ccc;
  gap: 2px;
}

.pm-meta-item:last-child { border-right: none; }

.pm-meta-label {
  font-size: 8px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #666;
}

.pm-meta-value {
  font-size: 14px;
  font-weight: 700;
  color: #111;
}

/* TABELA */
.pm-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 48px;
  font-size: 12px;
}

.pm-table th {
  background: #1a1a1a;
  color: #fff;
  padding: 10px 12px;
  text-align: left;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  border: 1px solid #1a1a1a;
}

.pm-table td {
  border: 1px solid #ccc;
  padding: 9px 12px;
  color: #222;
  vertical-align: middle;
}

.pm-tr-even td { background: #f8f8f8; }

/* ASSINATURAS */
.pm-signatures {
  display: flex;
  justify-content: space-between;
  gap: 40px;
  margin-top: 16px;
}

.pm-sig-block {
  flex: 1;
  text-align: center;
}

.pm-sig-line {
  border-top: 1.5px solid #1a1a1a;
  margin-bottom: 8px;
  margin-top: 48px;
}

.pm-sig-label {
  font-size: 11px;
  font-weight: 600;
  margin: 0;
  color: #111;
}

.pm-sig-sub {
  font-size: 9px;
  color: #777;
  margin: 3px 0 0;
}

/* RODAPÉ */
.pm-footer {
  margin-top: 32px;
  font-size: 9px;
  text-align: center;
  color: #aaa;
  border-top: 1px dotted #ccc;
  padding-top: 10px;
}


.aguardando-lote-box {
  background: var(--surface-0);
  border: 1px dashed var(--ink-300);
  border-radius: var(--radius-card);
  padding: 14px 16px;
  margin-bottom: 14px;
}
.aguardando-lote-box .box-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.aguardando-lote-box .title-group h3 { margin: 0 0 2px 0; font-size: 13px; font-weight: 600; color: var(--ink-900); }
.aguardando-lote-box .title-group p { margin: 0; font-size: 11px; color: var(--ink-300); }

.aguardando-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 8px;
}
.pneu-selection-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--surface-1);
  border: 1px solid var(--ink-200);
  border-radius: var(--radius-card);
  cursor: pointer;
  transition: border-color 0.12s, background 0.12s;
}
.pneu-selection-card:hover { border-color: var(--ink-300); background: var(--surface-0); }
.pneu-selection-card.selected {
  background: var(--brand-100);
  border-color: var(--brand-900);
}

.selection-indicator .check-circle { 
  width: 24px; 
  height: 24px; 
  border-radius: 50%; 
  border: 2px solid #cbd5e1; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  color: white; 
  transition: all 0.2s; 
}
.pneu-selection-card.selected .check-circle { 
  background: #3b82f6; 
  border-color: #3b82f6; 
}

.pneu-brief { display: flex; flex-direction: column; gap: 2px; }
.pneu-brief .pneu-fogo { font-weight: 800; font-size: 15px; color: var(--text); }
.pneu-brief .pneu-model { font-size: 13px; color: #64748b; }
.pneu-brief .pneu-origin { font-size: 11px; color: #94a3b8; margin-top: 4px; text-transform: uppercase; font-weight: 600; }

.section-divider { 
  display: flex; 
  align-items: center; 
  gap: 16px; 
  margin: 40px 0 24px 0; 
}
.section-divider::before, .section-divider::after { content: ""; flex: 1; height: 1px; background: var(--border); }
.section-divider span { font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }

.tire-pending { background: #fffbeb !important; border-color: #fcd34d !important; }
.tire-pending::after { content: 'TRÂNSITO'; position: absolute; top: 0; right: 0; font-size: 8px; font-weight: 900; color: #92400e; background: #fcd34d; padding: 2px 6px; border-bottom-left-radius: 8px; }

</style>
