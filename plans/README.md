# Planos de Melhoria — Gestão de Pneus

Auditoria executada em: 2026-07-27 (segurança) · 2026-07-31 (design) · 2026-07-31 (produto/roadmap)

Ver análise estratégica completa: [PRODUCT-ROADMAP.md](PRODUCT-ROADMAP.md)

---

## Onda 0 — Segurança e Design (já escritos)

| # | Plano | Categoria | Prioridade | Esforço | Status |
|---|-------|-----------|-----------|---------|--------|
| 1 | [001-remover-dependencias-mortas](001-remover-dependencias-mortas.md) | Leveza | ALTA | S | Pendente |
| 2 | [002-cors-wildcard-producao](002-cors-wildcard-producao.md) | Segurança | ALTA | S | Pendente |
| 3 | [003-debug-endpoint-sem-auth](003-debug-endpoint-sem-auth.md) | Segurança | ALTA | S | Pendente |
| 4 | [008-sidebar-cor-ativa-inconsistente](008-sidebar-cor-ativa-inconsistente.md) | Design — Marca | ALTA | S | ✅ Executado |
| 5 | [009-solicitacoes-azul-hardcoded](009-solicitacoes-azul-hardcoded.md) | Design — Marca | ALTA | S | ✅ Executado |
| 6 | [011-login-icone-posicao-e-tipo](011-login-icone-posicao-e-tipo.md) | Design — Bug | ALTA | M | ✅ Executado |
| 7 | [004-jwt-query-param](004-jwt-query-param.md) | Segurança | MÉDIA | M | Pendente |
| 8 | [005-rate-limiting-login](005-rate-limiting-login.md) | Segurança | MÉDIA | M | Pendente |
| 9 | [006-gitignore-env-files](006-gitignore-env-files.md) | Segurança | MÉDIA | S | Pendente |
| 10 | [010-sidebar-hover-translatex](010-sidebar-hover-translatex.md) | Design — UX | MÉDIA | S | ✅ Executado |
| 11 | [007-endpoint-configs-sem-auth](007-endpoint-configs-sem-auth.md) | Segurança | BAIXA | S | Pendente |
| 12 | [012-modal-e-header-polish](012-modal-e-header-polish.md) | Design — Polish | BAIXA | S | ✅ Executado |

---

## Onda 1 — Fundação do Produto (executar primeiro — sem isso as ondas 2/3 não têm base)

| # | Plano | Descrição | Prioridade | Esforço | Status |
|---|-------|-----------|-----------|---------|--------|
| 13 | [013-cpk-km-por-trecho](013-cpk-km-por-trecho.md) | Tabela `pneu_aplicacoes` + hodômetro obrigatório + CPK básico | CRÍTICA | M | Pendente |
| 14 | [015-maquina-estados-pneu](015-maquina-estados-pneu.md) | Enum de status + validação de transições + log auditável | CRÍTICA | M | Pendente |
| 15 | [016-enriquecimento-cadastro-pneu](016-enriquecimento-cadastro-pneu.md) | DOT, modelo, banda, pressão rec., sulco original/mínimo, valor | ALTA | S | Pendente |

---

## Design System (transversal — executar antes de qualquer nova tela)

| # | Plano | Descrição | Prioridade | Esforço | Status |
|---|-------|-----------|-----------|---------|--------|
| DS | [018-design-system-tokens-gritsch](018-design-system-tokens-gritsch.md) | 17 tokens Gritsch, refatoração de hardcodes, piloto Login.vue, aba DesignSystem | ALTA | M | Pendente |

## Onda 2 — Operação de Campo

| # | Plano | Descrição | Prioridade | Esforço | Status |
|---|-------|-----------|-----------|---------|--------|
| 16 | [014-aferacao-sulco-pressao](014-aferacao-sulco-pressao.md) | Tabela `aferacoes` (4 pontos + pressão) + modal no diagrama | CRÍTICA | M | Pendente |
| 17 | [017-causa-raiz-descarte](017-causa-raiz-descarte.md) | Enum de causa obrigatório ao sucatar + relatório | ALTA | S | Pendente |
| 19 | 019-ciclo-recapagem *(a escrever)* | Envio → recapadora → retorno com nova vida | ALTA | L | — |
| 20 | 020-cronograma-inspecao *(a escrever)* | Periodicidade + painel "em atraso / hoje / próximos 7 dias" | ALTA | M | — |
| 21 | 021-ordem-servico-automatica *(a escrever)* | OS gerada por condição crítica na aferição | ALTA | M | — |

---

## Onda 3 — Inteligência e CPK

| # | Plano | Descrição | Prioridade | Esforço | Status |
|---|-------|-----------|-----------|---------|--------|
| 21 | 021-dashboard-cpk-rich *(a escrever)* | CPK por pneu/marca/modelo, ranking, projeção de compra | CRÍTICA | L | — |
| 22 | 022-alertas-configuráveis *(a escrever)* | Motor de alertas in-app por filial | ALTA | M | — |
| 23 | 023-api-bi *(a escrever)* | Endpoints autenticados por token para BI externo | MÉDIA | M | — |

---

## Ordem de execução recomendada

```
013 + 015 + 016 (em paralelo, são independentes)
    ↓
014 (depende de 016 para sulco_minimo_mm)
    ↓
017 (depende de 015 para DESCARTADO como estado formal)
    ↓
018 → 019 → 020 (Onda 2, sequencial)
    ↓
021 → 022 → 023 (Onda 3, sequencial)
```
