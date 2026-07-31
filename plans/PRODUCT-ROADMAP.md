# Roadmap de Produto — Gestão de Pneus
**Auditoria:** 2026-07-31 | **Base:** Comparação com Prolog/Gestran PneuFit

---

## 1. Mapa do que existe hoje

| Área | Entidades / Campos identificados | Status |
|------|----------------------------------|--------|
| **Autenticação** | JWT, roles: admin/gerente/operador, `/api/auth/*` | ✅ Completo |
| **Filiais** | CRUD `/api/gestao-pneus/filiais` | ✅ Completo |
| **Usuários** | CRUD `/api/usuarios` | ✅ Completo |
| **Veículos** | placa, modelo, tipo, frota, km_atual, config (eixos + posições nomeadas) | ✅ Completo |
| **Pneus (cadastro)** | numero_fogo, marca, medida, sulco_atual, km_total, vida, status, nf, filial_id, recebido | ⚠️ Parcial |
| **Configurações de eixo** | tipos pré-configurados com posições (1ESQ, 1DIR, etc.) | ✅ Completo |
| **Alocação** | drag-and-drop de pneu para posição no diagrama, `/api/gestao-pneus/alocar` | ✅ Completo |
| **Remoção** | remoção para sucata ou estoque, `/api/gestao-pneus/remover` | ✅ Completo |
| **Rodízio** | `/api/gestao-pneus/rodizio` | ✅ Completo |
| **Transferência** | entre filiais + confirmação de recebimento | ✅ Completo |
| **Estoque** | accordion Filial → Medida, mini-tabela com sulco e status | ✅ Completo |
| **Histórico** | movimentações auditáveis | ✅ Completo |
| **Solicitações** | fluxo operador → admin | ✅ Completo |
| **Reciclagem/Financeiro** | lotes de carcaça, crédito financeiro por filial | ✅ Completo |
| **Dashboard** | total, em uso, estoque, descartados, patrimônio | ⚠️ Parcial |
| **Importação CSV** | template + upload | ✅ Completo |
| **Sincronização SQL Server** | busca e sincronização de veículos | ✅ Completo |

**O que NÃO existe e os líderes têm:**

| Funcionalidade | Prolog | PneuFit | Este sistema |
|----------------|--------|---------|--------------|
| Aferição sulco 4 pontos | ✅ | ✅ | ❌ |
| Registro de pressão | ✅ | ✅ | ❌ |
| CPK (custo por km) | ✅ | ✅ | ❌ |
| KM acumulado automático por trecho | ✅ | ✅ | ❌ |
| Projeção de vida útil restante | ✅ | ✅ | ❌ |
| Detecção de padrão de desgaste | ✅ | ⚠️ | ❌ |
| Máquina de estados com validação | ✅ | ✅ | ❌ |
| Cronograma de inspeção + alertas atraso | ✅ | ✅ | ❌ |
| Ordem de Serviço automática | ✅ | ✅ | ❌ |
| Ciclo de recapagem (envio/retorno/nova vida) | ✅ | ✅ | ❌ |
| Causa raiz de descarte catalogada | ✅ | ✅ | ❌ |
| Linha do tempo completa por número de fogo | ✅ | ✅ | ❌ |
| DOT/número de série do fabricante | ✅ | ✅ | ❌ |
| Pressão recomendada + tolerância | ✅ | ✅ | ❌ |
| Alertas configuráveis por filial | ✅ | ✅ | ❌ |
| API REST para BI externo | ✅ | ⚠️ | ❌ |
| Inventário cíclico | ✅ | ⚠️ | ❌ |
| Modo offline / fila de sincronização | ⚠️ | ⚠️ | ❌ |

---

## 2. Top 5 Gaps de Maior Impacto Financeiro

### Gap #1 — KM por Trecho + CPK  
**Impacto:** Sem CPK não há resposta para "qual pneu devo comprar?" ou "vale recapar?".
O km_total hoje parece campo manual — subestimado ou zerado para muitos pneus.
Solução: tabela `pneu_aplicacoes` com hodômetro entrada/saída calcula km_parcial por trecho.
CPK = (valor_compra + custos_recapagem + consertos) ÷ km_acumulado.

### Gap #2 — Aferição Sistemática de Sulco e Pressão  
**Impacto:** Sem dados históricos de sulco não há projeção de vida útil, não há detecção
de desgaste irregular, e pneus podem atingir o limite legal sem aviso.
Cada pneu descartado 5mm antes do mínimo representa ~30% de vida jogada fora.

### Gap #3 — Máquina de Estados Validada  
**Impacto:** Hoje o status pode ser alterado livremente no banco. Um pneu "em recapagem"
pode ser alocado acidentalmente, gerando dados inconsistentes no histórico e no CPK.
Sem validação de transições, a rastreabilidade é frágil.

### Gap #4 — Causa Raiz de Descarte  
**Impacto:** Frotas médias perdem 15–25% do orçamento de pneus em descartes antecipados.
Sem catalogar o motivo (subcalibragem, desalinhamento, corte), a empresa repete os mesmos
erros operacionais indefinidamente. Dois trimestres de dados já revelam o problema dominante.

### Gap #5 — Ciclo de Recapagem (nova vida após borracharia)  
**Impacto:** Recapagem custa 35–55% de um pneu novo. Uma 2ª vida bem controlada reduz CPK
em ~30%. O módulo de reciclagem atual controla carcaças descartadas → crédito financeiro,
mas não controla envio para recapagem → retorno com nova vida → reaplicação ao estoque.

---

## 3. Roadmap em 3 Ondas

### Onda 1 — Fundação (modelo de dados)
*Pré-requisito para tudo. Sem isso as ondas 2 e 3 não têm base.*

| Plano | Descrição | Esforço | Impacto |
|-------|-----------|---------|---------|
| [013](013-cpk-km-por-trecho.md) | Tabela `pneu_aplicacoes` + KM automático + CPK básico | M | 🔴 Crítico |
| [015](015-maquina-estados-pneu.md) | Máquina de estados validada no backend | M | 🔴 Crítico |
| [016](016-enriquecimento-cadastro-pneu.md) | DOT, modelo, banda, pressão recomendada, vida máxima | S | 🟡 Alto |

**Mudanças de schema necessárias antes de qualquer nova tela:**
- `pneus`: adicionar `dot`, `modelo`, `banda`, `pressao_recomendada`, `pressao_tolerancia`, `sulco_minimo`, `vidas_maximas`, `valor_aquisicao` (já existe?), `fornecedor`
- Nova tabela `pneu_aplicacoes`: `(id, pneu_id, veiculo_id, posicao, km_entrada, km_saida, usuario_id, data_entrada, data_saida, motivo_saida)`
- Nova tabela `pneu_status_log`: `(id, pneu_id, status_anterior, status_novo, usuario_id, data_hora, motivo, km_veiculo)`

### Onda 2 — Operação (dados de campo)
*Gera os dados que alimentam a inteligência da Onda 3.*

| Plano | Descrição | Esforço | Impacto |
|-------|-----------|---------|---------|
| [014](014-aferacao-sulco-pressao.md) | Tabela `aferacoes` + tela de aferição (sulco 4 pts + pressão) | M | 🔴 Crítico |
| [017](017-causa-raiz-descarte.md) | Enum causa raiz obrigatório ao sucatear | S | 🟡 Alto |
| [018](018-ciclo-recapagem.md) | Envio → recapadora → retorno com nova vida → estoque | L | 🟡 Alto |
| [019](019-cronograma-inspecao.md) | Periodicidade + painel "em atraso / hoje / próximos 7 dias" | M | 🟡 Alto |
| [020](020-ordem-servico-automatica.md) | OS gerada por condição crítica na aferição | M | 🟡 Alto |

### Onda 3 — Inteligência
*Valor percebido: onde a empresa toma decisões com dados.*

| Plano | Descrição | Esforço | Impacto |
|-------|-----------|---------|---------|
| [021](021-dashboard-cpk-rich.md) | Dashboard completo: CPK médio, ranking marcas, projeção compras | L | 🔴 Crítico |
| [022](022-alertas-configuráveis.md) | Motor de alertas in-app: sulco mínimo, aferição atrasada, estoque baixo | M | 🟡 Alto |
| [023](023-api-bi.md) | Endpoints de leitura autenticados por token para BI externo | M | 🟢 Médio |

---

## Decisão imediata recomendada

Comece pelo **Plano 013** (KM por trecho) + **Plano 015** (máquina de estados).
São as mudanças de schema mais invasivas e tudo na Onda 2 e 3 depende delas.
Fazer o Plano 014 (aferição) antes do 013 desperdiça trabalho porque sem km acumulado
as aferições não geram CPK.
