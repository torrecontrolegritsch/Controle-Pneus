# SKILL: Gestão de Pneus Gritsch — Assistente Mestre

## Descrição
Skill mestre para desenvolvimento do **Sistema de Gestão de Pneus da Gritsch**.
Sistema completo para controle de frota de pneus: cadastro, movimentações, alocações por posição de eixo, estoque por filial, reciclagem, KPIs e relatórios financeiros.

---

## Stack Tecnológico

| Camada        | Tecnologia                                                      |
|---------------|-----------------------------------------------------------------|
| Backend       | Python + FastAPI (main.py serve estático + API)                 |
| Banco Nuvem   | Supabase (PostgreSQL) — acesso via REST API (HTTPS bypass firewall) |
| Auth          | Supabase Auth (login) + JWT local (todas as rotas protegidas)   |
| Frontend      | Vue 3 + Vite (SPA única, compilada em `frontend/dist/`)         |
| UI            | CSS custom (dark theme) + ícones SVG inline                     |
| Porta Local   | `8015` — backend serve o frontend como estático                 |
| URL Dev       | `http://localhost:8015/frontend/`                               |
| Frontend Dev  | `http://localhost:5173` (Vite dev server separado)              |

---

## Arquitetura do Projeto

```
Pneus/
├── .env                          ← Variáveis de ambiente (SUPABASE_URL, KEY, JWT_SECRET_KEY)
├── backend/
│   ├── main.py                   ← FastAPI app (monta routers + serve static)
│   ├── config_app.py             ← Config centralizada (lê .env raiz)
│   ├── auth.py                   ← JWT: create_access_token, decode_token, get_current_user
│   ├── db_gestao_pneus.py        ← Camada de dados: todas as funções CRUD via Supabase REST
│   ├── db_sqlserver.py           ← Consulta veículos no SQL Server corporativo (bi.bluefleet.com.br)
│   ├── sync_veiculos.py          ← Sincroniza SQL Server → Supabase (executar local)
│   ├── cache.py                  ← Cache in-memory com TTL
│   ├── config.py                 ← VEICULO_GROUPS, CACHE_TTL_MINUTES
│   └── routers/
│       ├── auth.py               ← POST /api/auth/login, POST /api/auth/register
│       └── gestao_pneus.py       ← Todos os endpoints REST do sistema
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue         ← Tela de login
│   │   │   └── PneusGestao.vue   ← App principal (todas as abas, KPIs do header)
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── AppSidebar.vue
│   │   │   ├── ui/
│   │   │   │   ├── AppModal.vue, AppToast.vue, AppLoading.vue, AppTable.vue
│   │   │   └── views/
│   │   │       ├── DashboardView.vue     ← KPIs gerais
│   │   │       ├── PneusView.vue         ← Gestão de pneus individuais
│   │   │       ├── VeiculosView.vue      ← Cadastro de frota
│   │   │       ├── FiliaisView.vue       ← Cadastro de unidades/filiais
│   │   │       ├── MovimentacoesView.vue ← Histórico de movimentações
│   │   │       ├── EstoqueCentralView.vue← Estoque por filial
│   │   │       └── ReciclagemView.vue    ← Controle de lotes de reciclagem
│   │   ├── api/
│   │   │   └── gestaoPneus.js    ← Funções de fetch (get, post, put, del) com JWT
│   │   ├── composables/
│   │   │   └── usePneus.js       ← Composable principal de estado
│   │   └── App.vue               ← Roteamento Login ↔ PneusGestao
│   └── dist/                     ← Build do frontend (gerado com npm run build)
└── venv/                         ← Virtualenv Python
```

---

## Banco de Dados (Supabase — tabelas com prefixo `gp_`)

### `gp_filiais`
| Campo   | Tipo    | Descrição                        |
|---------|---------|----------------------------------|
| id      | PK int  |                                  |
| nome    | TEXT    | Nome da unidade/filial           |
| cidade  | TEXT    |                                  |
| estado  | TEXT    |                                  |
| ativo   | int     | 1 = ativo, 0 = inativo           |

### `gp_veiculos`
| Campo      | Tipo    | Descrição                                              |
|------------|---------|--------------------------------------------------------|
| id         | PK int  |                                                        |
| placa      | TEXT UK | Placa sem hífen, uppercase                             |
| frota      | TEXT    | Número de frota interno                                |
| modelo     | TEXT    |                                                        |
| marca      | TEXT    |                                                        |
| tipo       | TEXT    | `simples` / `toco` / `truck` / `bitruck`               |
| filial_id  | FK      | gp_filiais.id                                          |
| km_atual   | float   |                                                        |
| ativo      | int     | 1 = ativo                                              |

### `gp_pneus`
| Campo             | Tipo    | Descrição                                             |
|-------------------|---------|-------------------------------------------------------|
| id                | PK int  |                                                       |
| numero_fogo       | TEXT UK | Identificador único do pneu (uppercase)               |
| marca             | TEXT    |                                                       |
| modelo            | TEXT    |                                                       |
| medida            | TEXT    | Ex: `295/80R22.5`                                     |
| dot               | TEXT    | Código DOT / data de fabricação                       |
| valor             | float   | Valor de compra                                       |
| vida              | int     | Número de reformas (1 = novo, 2 = 1ª recapagem, etc.) |
| status            | TEXT    | `estoque` / `em_uso` / `descarte` / `reciclagem`      |
| filial_id         | FK      | Filial atual do pneu                                  |
| filial_origem_id  | FK      | Filial de onde saiu (descarte/reciclagem)             |
| veiculo_id        | FK/null | Veículo onde está instalado                           |
| posicao           | TEXT    | Posição no veículo (ex: `E1_ESQ`, `E2_DIR_EXT`)       |
| km_instalacao     | float   | KM no momento da instalação                           |
| km_total          | float   | KM acumulado ao longo de todas as vidas               |
| sulco_atual       | float   | Profundidade do sulco em mm                           |
| nf                | TEXT    | Nota fiscal de compra                                 |
| fornecedor        | TEXT    | Nome do fornecedor                                    |
| recebido          | int     | 1 = recebido na filial, 0 = em trânsito               |
| lote_id           | TEXT    | ID do lote de reciclagem                              |
| valor_arrecadado  | float   | Valor recebido na reciclagem                          |

### `gp_movimentacoes`
| Campo             | Tipo    | Descrição                                              |
|-------------------|---------|--------------------------------------------------------|
| id                | PK int  |                                                        |
| pneu_id           | FK      |                                                        |
| tipo              | TEXT    | `alocacao` / `remocao` / `transferencia` / `envio_recicladora` |
| veiculo_id        | FK/null |                                                        |
| posicao           | TEXT    |                                                        |
| km_momento        | float   |                                                        |
| filial_id         | FK      | Filial onde ocorreu                                    |
| filial_destino_id | FK      | Filial destino (transferências)                        |
| observacao        | TEXT    |                                                        |
| criado_em         | datetime| Auto                                                   |

### `usuarios` (Supabase Auth profile)
| Campo     | Tipo    | Descrição                              |
|-----------|---------|----------------------------------------|
| id        | UUID    | Vinculado ao Supabase Auth user.id     |
| email     | TEXT    |                                        |
| role      | TEXT    | `admin` / `gerente` / `operador`       |
| filial_id | FK/null | Restrição de filial (operadores)       |

---

## Ciclo de Vida do Pneu

```
COMPRA
  ↓
[estoque] → [em_uso] → [estoque]  ← pode ir e voltar
                ↓
            [descarte]
                ↓
           [reciclagem] → criar_lote → arrecadar valor
```

**Status e transições:**
- `estoque` → `em_uso`: função `alocar_pneu()` 
- `em_uso` → `estoque`: função `remover_pneu(destino="estoque")`
- `em_uso` → `descarte`: função `remover_pneu(destino="descarte")`
- `descarte`/`em_uso` → `reciclagem`: função `enviar_para_recicladora()`
- Pneus em `reciclagem` sem `lote_id`: aguardando agrupamento
- Pneus em `reciclagem` com `lote_id`: em lote registrado

---

## Tipos de Veículo e Configuração de Eixos

| Tipo      | Eixos | Posições                                                                 | Estepes    |
|-----------|-------|--------------------------------------------------------------------------|------------|
| simples   | 2     | E1_ESQ/DIR, E2_ESQ/DIR                                                   | ESTEPE_1   |
| toco      | 2     | E1_ESQ/DIR, E2_ESQ_EXT/INT/DIR_INT/EXT                                   | ESTEPE_1   |
| truck     | 3     | E1_ESQ/DIR, E2 duplo (4), E3 duplo (4)                                   | ESTEPE_1   |
| bitruck   | 4     | E1_ESQ/DIR, E2_ESQ/DIR, E3 duplo (4), E4 duplo (4)                       | ESTEPE_1/2 |

**Padrão de posição:** `E{eixo}_{lado}` para simples, `E{eixo}_{lado}_{EXT|INT}` para duplo.

---

## API REST — Mapa Completo

### Auth `/api/auth`
- `POST /api/auth/login` — login Supabase Auth + retorna JWT local
- `POST /api/auth/register` — cria usuário no Supabase Auth

### Gestão Pneus `/api/gestao-pneus`

**Filiais**
- `GET /filiais` — lista filiais ativas
- `POST /filiais` — criar filial *(admin)*
- `PUT /filiais/{id}` — editar filial *(admin)*
- `DELETE /filiais/{id}` — desativar filial *(admin)*

**Veículos**
- `GET /veiculos?filial_id=` — lista frota
- `POST /veiculos` — cadastrar veículo
- `GET /veiculos/{id}` — detalhe com pneus instalados por posição
- `PUT /veiculos/{id}` — editar
- `DELETE /veiculos/{id}` — desativar *(impede se tiver pneus alocados)*
- `GET /busca-veiculo-sql/{placa}` — busca no SQL Server corporativo (fallback local)
- `POST /sincronizar-veiculos-sql` — sincroniza SQL Server → Supabase (rodar local)

**Pneus**
- `GET /pneus?filial_id=&status=&veiculo_id=` — lista pneus
- `POST /pneus` — cadastrar pneu (status inicia como `estoque`)
- `GET /pneus/{id}` — detalhe do pneu
- `PUT /pneus/{id}` — editar dados do pneu
- `DELETE /pneus/{id}` — remover registro
- `GET /pneus/template` — baixa CSV modelo para importação (com BOM UTF-8)
- `POST /pneus/importar` — importação em lote via CSV (upsert por `numero_fogo`)
- `POST /pneus/{id}/alocar` — instalar pneu em posição de veículo
- `POST /pneus/{id}/remover` — remover do veículo (destino: estoque/descarte/reciclagem)
- `POST /pneus/{id}/transferir` — transferir entre filiais (`recebido=0`)
- `POST /pneus/{id}/confirmar-recebimento` — marcar como recebido (`recebido=1`)

**Movimentações**
- `GET /movimentacoes?pneu_id=&veiculo_id=&filial_id=&tipo=` — histórico

**Dashboard**
- `GET /dashboard?filial_id=` — KPIs: total_pneus, em_uso, em_estoque, descartados, valor_estoque, etc.

**Reciclagem**
- `POST /reciclagem/enviar` — marcar pneu como em reciclagem
- `GET /reciclagem/aguardando?filial_id=` — pneus sem lote
- `GET /reciclagem/lotes?filial_id=` — lotes agrupados
- `POST /reciclagem/criar-lote` — agrupa pneus em lote (`{pneu_ids: [...], filial_id}`)
- `POST /reciclagem/atualizar-valor` — registra valor arrecadado no lote
- `GET /reciclagem/relatorio-financeiro?mes=&filial_id=` — relatório financeiro

---

## Camada de Dados (db_gestao_pneus.py)

**Padrão de acesso ao Supabase:**
```python
# Todos os acessos usam _api_request() — NUNCA conexão direta
_api_request("GET", "gp_pneus", params={"status": "eq.estoque"})
_api_request("POST", "gp_pneus", payload={...})
_api_request("PATCH", "gp_pneus", params={"id": f"eq.{id}"}, payload={...})
```

**Filtros PostgREST (params):**
- Igual: `"campo": "eq.valor"`
- IS NULL: `"campo": "is.null"`
- NOT NULL: `"campo": "not.is.null"`
- Select: `"select": "*,gp_filiais(nome)"` — join automático
- Order: `"order": "campo.desc"` ou `"order": "campo"`

**Cache in-memory:**
- `get_cached(key)` / `set_cached(key, value, ttl)` / `invalidate_pattern(pattern)`
- Decorator `@cached(ttl=30)` disponível
- Filiais: TTL 60s; Veículos: TTL 60s

---

## Frontend (Vue 3 / SPA)

### Abas disponíveis em PneusGestao.vue
| ID               | Label          | Componente                  |
|------------------|----------------|-----------------------------|
| `estoque_central`| Estoque Central| `EstoqueCentralView`        |
| `alocacoes`      | Alocações      | inline em PneusGestao.vue   |
| `veiculos`       | Frota          | `VeiculosView`              |
| `filiais`        | Unidades       | `FiliaisView`               |
| `estoque`        | Estoque        | `PneusView`                 |
| `financeiro`     | Financeiro     | inline em PneusGestao.vue   |
| `sucata`         | Sucata         | inline em PneusGestao.vue   |
| `recicladora`    | Reciclagem     | `ReciclagemView`            |
| `historico`      | Histórico      | `MovimentacoesView`         |

### API Client (gestaoPneus.js)
```javascript
import { get, post, put, del } from '@/api/gestaoPneus'

// Exemplos
await get('/api/gestao-pneus/pneus', { filial_id: 1, status: 'estoque' })
await post('/api/gestao-pneus/pneus', { numero_fogo: 'EX001', marca: 'BRIDGESTONE', ... })
await put('/api/gestao-pneus/pneus/5', { sulco_atual: 14.2 })
```

Token JWT armazenado em `localStorage` (lembrar=true) ou `sessionStorage`, chave `pneus_access_token`.

### Roles de Usuário
| Role      | Acesso                                                         |
|-----------|----------------------------------------------------------------|
| `admin`   | Tudo — criar filiais, excluir veículos, registrar usuários     |
| `gerente` | Tudo exceto criar filiais                                      |
| `operador`| Operações do dia a dia; pode ter filial_id fixo                |

---

## Padrões de Desenvolvimento

### Backend (FastAPI / Python)
- Todo novo endpoint vai em `backend/routers/gestao_pneus.py`
- Toda nova função CRUD vai em `backend/db_gestao_pneus.py` usando `_api_request()`
- Usar Pydantic models para input (`class XxxIn(BaseModel)`)
- Auth via `Depends(get_current_user)` — retorna `TokenData(user_id, email, role, filial_id)`
- Admin: `Depends(require_admin)` = roles admin + gerente
- Operador: `Depends(require_operador)` = todos os roles
- Sempre `invalidate_pattern("nome_entidade")` após POST/PATCH para limpar cache

### Frontend (Vue 3)
- Usar Composition API (`<script setup>`)
- Novos componentes de view em `frontend/src/components/views/`
- Importar e registrar em `PneusGestao.vue` ou `components/index.js`
- Sempre chamar `get/post/put/del` de `@/api/gestaoPneus.js` — nunca fetch direto
- Tratamento de erro: `try { ... } catch(e) { toast.error(e.message) }`
- Reatividade: `ref()` e `reactive()` do Vue 3

### Importação em Lote (CSV)
- Separador: `;`
- Encoding: UTF-8 com BOM (`﻿`)
- Colunas obrigatórias: `numero_fogo`, `marca`, `medida`
- Colunas opcionais com sinônimos mapeados (ver `importar_pneus_lote()`)
- Coluna `filial`: aceita nome exato da filial cadastrada
- Upsert por `numero_fogo` — atualiza se já existir

---

## O Que Já Existe (Pronto)

- [x] Login com Supabase Auth + JWT local
- [x] Dashboard com KPIs no header (total, em uso, estoque, descarte, patrimônio)
- [x] CRUD completo de Filiais / Unidades
- [x] CRUD completo de Veículos com busca no SQL Server corporativo
- [x] Cadastro e importação em lote de Pneus (via CSV)
- [x] Alocação de pneu por posição de eixo (visual do veículo)
- [x] Remoção de pneu com destinos (estoque, descarte, reciclagem)
- [x] Transferência de pneu entre filiais (controle de recebimento)
- [x] Estoque Central por filial
- [x] Histórico de movimentações com filtros
- [x] Fluxo de Reciclagem: envio → aguardando lote → criar lote → registrar valor
- [x] Relatório financeiro de reciclagem
- [x] Cache in-memory para filiais e veículos
- [x] Roles: admin / gerente / operador

---

## Roadmap de Features (A Construir)

### Alta Prioridade
1. **KPIs Detalhados** — custo por KM por pneu, vida média por marca, taxa de descarte
2. **Alertas de Sulco** — notificar pneus com sulco_atual abaixo do mínimo legal (1.6mm)
3. **Módulo de Fornecedores** — CRUD com tabela `gp_fornecedores`, vincular compras/NFs
4. **Relatório de Estoque** — exportação Excel/PDF com todos os pneus por filial
5. **Custo Total de Pneus** — relatório de gastos por período, filial, marca
6. **Histórico de KM por Pneu** — gráfico de evolução e aproveitamento por vida

### Média Prioridade
7. **Inspeção Periódica** — tabela `gp_inspecoes`: registrar medida do sulco com data e veículo
8. **Prevenc Preventiva** — agenda de revisão baseada em km_total acumulado
9. **Recapagem** — rastrear pneus enviados para recapagem como status próprio
10. **Painel por Filial** — visão isolada de KPIs para operadores por unidade
11. **Notificações** — alertas por e-mail/WhatsApp para sulco baixo, pneus em trânsito
12. **Sincronização Automática** — sync periódico SQL Server → Supabase via cron

### Baixa Prioridade
13. **App Mobile** — PWA ou React Native para inspeção em campo
14. **QR Code** — etiqueta por pneu para scan e atualização rápida
15. **Multi-empresa** — isolamento de dados por empresa além de por filial
16. **Integração NF-e** — importar nota fiscal de compra automaticamente

---

## Regras Críticas do Projeto

1. **NUNCA** conectar ao banco diretamente — usar sempre `_api_request()` em `db_gestao_pneus.py`
2. **Supabase URL** é `https://dpvdjldocvdsdgvmnsvu.supabase.co` — se o projeto estiver pausado, é preciso reativá-lo no dashboard Supabase
3. **JWT_SECRET_KEY** obrigatório no `.env` raiz — sem ela o backend não sobe
4. **CORS** configurado em `backend/.env` via `CORS_ORIGINS` — ao adicionar nova origem, incluir lá
5. **Placa de veículo** sempre sem hífen e uppercase: `placa.strip().upper().replace("-","")`
6. **numero_fogo** sempre uppercase: `numero_fogo.strip().upper()`
7. **NÃO** excluir veículo com pneus alocados — `desativar_veiculo()` verifica e lança ValueError
8. **Não** usar `filial_id=None` em `remover_pneu()` sem fallback — o sistema busca da filial do veículo se não informado
9. **Build do frontend** é obrigatório antes de deploy: `cd frontend && npm run build`
10. **Cache**: sempre chamar `invalidate_pattern()` após operações de escrita

---

## Como Rodar Localmente

```bash
# 1. Backend
cd "c:\Users\fabio.pepplow\Desktop\Projetos Antigravity\Pneus"
venv\Scripts\activate
pip install -r requirements.txt
python backend/main.py
# → http://localhost:8015/frontend/

# 2. Frontend (desenvolvimento)
cd frontend
npm install
npm run dev
# → http://localhost:5173

# 3. Build do frontend (produção)
cd frontend
npm run build
# Gera frontend/dist/ — servido automaticamente pelo backend
```

---

## Conexões Externas

| Sistema         | Uso                                   | Credenciais (.env)                       |
|-----------------|---------------------------------------|------------------------------------------|
| Supabase        | Banco de dados + Auth                 | SUPABASE_URL, SUPABASE_KEY               |
| SQL Server      | Consulta referência de veículos       | SQLSERVER_HOST=bi.bluefleet.com.br:1433  |

---

## Skills Auxiliares Recomendadas

| Tarefa                           | Skill                       |
|----------------------------------|-----------------------------|
| Novas funções Python/FastAPI      | `python-patterns`           |
| Design de tabelas Supabase        | `database-design`           |
| Novos componentes Vue 3           | `vue-best-practices`        |
| Debug de componente Vue           | `vue-debug-guides`          |
| Estilo e UI                       | `frontend-design`           |
| Análise de dados / relatórios     | `data-analysis`             |
| Revisão de código                 | `code-review-checklist`     |
| Arquitetura de features           | `architecture`              |
| Testes Python                     | `python-testing-patterns`   |
| Deploy / servidor                 | `server-management`         |
