---
status: Pendente
prioridade: ALTA
esforço: M
risco: baixo
categoria: Design — Sistema
dependências: nenhuma (executar antes de qualquer nova tela)
---

# 018 — Design System Tokens Gritsch (identidade corporativa)

## Por que isso importa

O sistema atual mistura três gerações de cores:
- `--brand: #C41230` (tokens antigos no style.css)
- `#1e293b`, `#0f172a`, `#64748b`, `#94a3b8` (Tailwind slate, hardcoded)
- `#3b82f6`, `#10b981`, `#f59e0b` (Tailwind azul/verde/âmbar, hardcoded)

Toda nova tela herda essa inconsistência. A paleta Gritsch define um sistema fechado
de 17 tokens — qualquer cor fora deles é automaticamente um erro. A refatoração é
uma vez; o benefício é permanente.

**Mudança visual principal:** o vermelho vivo `#C41230` (atual brand) vira
`--brand-900: #5A181C` (vinho escuro corporativo) para o botão primário e header de tabela.
O `--brand-signal: #E62C30` é reservado ao logo e a 1 número herói por tela.

---

## A — Arquivo de tokens: `frontend/src/style.css`

Substituir completamente a seção de variáveis atual pelas seguintes:

```css
/* ─────────────────────────────────────────────────────────
   GRITSCH DESIGN TOKENS  (nunca usar cor fora deste arquivo)
   ───────────────────────────────────────────────────────── */
:root {
  /* Marca — vinho/vermelho (usar com parcimônia, ≤10% da área) */
  --brand-900: #5A181C;   /* botão primário, header tabela, barra de seção */
  --brand-800: #83282E;   /* hover/active do primário, filete destaque */
  --brand-600: #C33D45;   /* 2ª série de gráfico, badge */
  --brand-400: #D9545F;   /* 3ª série de gráfico */
  --brand-100: #F5C8C9;   /* trilho de barra, fundo de linha destacada, chip */
  --brand-signal: #E62C30;/* EXCLUSIVO: logo e 1 número herói por tela */

  /* Neutros — devem ocupar ~90% da tela */
  --ink-900:   #2C2E35;   /* texto principal, títulos */
  --ink-600:   #4D4D4D;   /* texto secundário, labels */
  --ink-300:   #BFBFBF;   /* bordas, ícones inativos */
  --ink-200:   #E2E2E2;   /* divisores, borda de card */
  --surface-2: #F2F2F2;   /* fundo de card KPI, header de tabela claro */
  --surface-1: #F7F7F7;   /* fundo da aplicação */
  --surface-0: #FFFFFF;   /* fundo de conteúdo, linhas de tabela */

  /* Semântica — APENAS estas 4, somente para status */
  --status-ok:          #3F7A5E;
  --status-warn:        #C7861A;
  --status-critical:    #C33D45;
  --status-idle:        #BFBFBF;
  --status-ok-bg:       #EAF2ED;
  --status-warn-bg:     #FBF3E3;
  --status-critical-bg: #FBEAEB;

  /* Aliases de compatibilidade (remover após refatoração completa) */
  --brand:      var(--brand-900);
  --brand-dark: var(--brand-800);
  --brand-bg:   var(--brand-100);
  --brand-mid:  var(--brand-600);

  /* Layout */
  --radius-card:  6px;
  --radius-input: 4px;
  --radius-chip:  4px;
  --shadow-sm:    0 1px 2px rgba(44,46,53,0.06);
  --shadow-md:    0 4px 8px rgba(44,46,53,0.08);
  --shadow-float: 0 16px 32px rgba(44,46,53,0.14);
}
```

---

## B — Mapeamento completo: cor antiga → token

| Cor hardcoded | Onde aparece | Token correto |
|--------------|-------------|---------------|
| `#C41230`, `#C33D45` | brand atual (botão, sidebar ativo) | `var(--brand-900)` |
| `#a50f28`, `#9E0E26` | hover do brand | `var(--brand-800)` |
| `#FDF2F4`, `fdf2f4` | brand-bg | `var(--brand-100)` |
| `#FCCDD4` | brand-mid | `var(--brand-600)` |
| `#1e293b`, `#0f172a` | títulos, sidebar dark | `var(--ink-900)` |
| `#475569`, `#334155` | texto secundário | `var(--ink-600)` |
| `#64748b` | labels, muted | `var(--ink-600)` |
| `#94a3b8` | ícones inativos | `var(--ink-300)` |
| `#cbd5e1` | bordas claras | `var(--ink-300)` |
| `#e2e8f0` | divisores, bordas card | `var(--ink-200)` |
| `#f1f5f9` | fundo hover, superfície | `var(--surface-2)` |
| `#f8fafc`, `#fafafa` | fundo app | `var(--surface-1)` |
| `#ffffff`, `#fff` | fundo conteúdo | `var(--surface-0)` |
| `#3b82f6`, `#1d4ed8`, `#2563eb` | azul (herança Tailwind) | `var(--brand-900)` (ativo) ou `var(--status-ok)` (conforme) |
| `#10b981`, `#16a34a` | verde (status ok) | `var(--status-ok)` |
| `#ef4444`, `#dc2626` | vermelho (status crítico) | `var(--status-critical)` |
| `#f59e0b`, `#f97316` | âmbar (status atenção) | `var(--status-warn)` |
| `#14532d`, `#15803d`, `#22c55e` | verde escuro (novo pneu) | `var(--status-ok)` |
| `rgba(196,18,48,...)` | sombra brand | `rgba(90,24,28,...)` usando `--brand-900` |

**Arquivos afetados:**
- `frontend/src/style.css` — tokens globais (substituição total)
- `frontend/src/views/PneusGestao.vue` — ~80 ocorrências de cores hardcoded (CSS scoped ≈3600 linhas)
- `frontend/src/views/Login.vue` — `#C41230`, `#a50f28`, `#e8ecf0`, `#0f172a`, etc.
- `frontend/src/components/views/SolicitacoesView.vue` — `#C41230`, focus/button
- Outros componentes (`EstoqueCentralView.vue`, `DashboardView.vue`) — verificar

---

## C — Regras visuais obrigatórias para o executor

### Botão primário (1 por tela)
```css
.btn-primary {
  background: var(--brand-900);
  color: var(--surface-0);
  border: none;
  border-radius: var(--radius-input);
}
.btn-primary:hover { background: var(--brand-800); }
```

### Botão secundário
```css
.btn-secondary {
  background: var(--surface-0);
  color: var(--ink-900);
  border: 1px solid var(--ink-300);
  border-radius: var(--radius-input);
}
```

### Header de tabela / barra de seção
```css
.gp-table th, .section-header-bar {
  background: var(--brand-900);
  color: var(--surface-0);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
```

### Card KPI
```css
.kpi-box {
  background: var(--surface-0);
  border: 1px solid var(--ink-200);
  border-radius: var(--radius-card);
}
.kpi-t { color: var(--ink-600); }
.kpi-n { color: var(--ink-900); }
/* Apenas o KPI mais crítico pode ter valor colorido: */
.kpi-hero .kpi-n { color: var(--brand-signal); }
```

### Chips de status (nunca sólido saturado)
```css
.badge-ok       { background: var(--status-ok-bg);       color: var(--status-ok); }
.badge-warn     { background: var(--status-warn-bg);     color: var(--status-warn); }
.badge-critical { background: var(--status-critical-bg); color: var(--status-critical); }
.badge-idle     { background: var(--surface-2);          color: var(--status-idle); }
```

### Barra de progresso (sulco)
```css
.sulco-bar-mini { background: var(--brand-100); }
.sulco-fill-mini { background: var(--status-ok); }
.sulco-fill-mini.sulco-crit { background: var(--status-critical); }
```

### Sidebar ativa
```css
.menu-item.active {
  background: var(--brand-900);
  color: var(--surface-0);
  box-shadow: none; /* sem sombra colorida */
}
.menu-item:hover:not(.active) {
  background: var(--surface-2);
  color: var(--ink-900);
}
```

### Inputs e foco
```css
.form-group input:focus, .form-group select:focus {
  border-color: var(--brand-900);
  box-shadow: 0 0 0 3px var(--brand-100);
}
```

---

## D — Tela-piloto de referência

**Usar `Login.vue` como piloto** — menor arquivo, já refatorado recentemente.

Após executar a refatoração de tokens:
- `#e8ecf0` → `var(--surface-1)` (fundo da página)
- `#0f172a` → `var(--ink-900)` (título "Entrar")
- `#64748b` → `var(--ink-600)` (subtítulo, label flutuante)
- `#94a3b8` → `var(--ink-300)` (placeholder, ícone olho)
- `#e2e8f0` → `var(--ink-200)` (borda input)
- `#C41230` → `var(--brand-900)` (botão "Acessar Conta", foco)
- `rgba(196,18,48,0.08)` → `rgba(90,24,28,0.08)` (sombra do foco)
- `#a50f28` → `var(--brand-800)` (hover do botão)
- `#1e293b` → `var(--ink-900)` (painel direito da imagem)
- `#475569` → `var(--ink-600)` (label "Grupo Gritsch" e "brand-name")

---

## E — Componente `DesignSystemView.vue` (nova aba admin)

Criar `frontend/src/components/views/DesignSystemView.vue` e adicionar à lista de tabs
visíveis apenas para `role === 'admin'`:

```js
// PneusGestao.vue — allTabs
{ id: 'design_system', label: 'Design System', icon: '...', roles: ['admin'] }
```

O componente deve exibir:

1. **Paleta** — swatches de cada token com hex, nome e descrição de uso
2. **Tipografia** — escala de tamanhos com exemplos em peso 400/600/700
3. **Botões** — primário, secundário, terciário, desabilitado, danger
4. **Chips de status** — ok, warn, critical, idle (com ponto + rótulo)
5. **Inputs** — default, foco, erro, desabilitado
6. **Cards KPI** — com e sem valor herói
7. **Tabela de exemplo** — com header brand-900 e zebra
8. **Regras** — as 8 regras de uso impressas como referência

Estrutura mínima do componente:
```html
<template>
  <div class="ds-page">
    <section class="ds-section">
      <h2 class="ds-section-title">Paleta de Cores</h2>
      <div class="ds-palette-grid">
        <div v-for="t in tokens" :key="t.name" class="ds-swatch"
             :style="{ background: t.value }">
          <span class="ds-swatch-name">{{ t.name }}</span>
          <span class="ds-swatch-hex">{{ t.value }}</span>
        </div>
      </div>
    </section>
    <!-- Demais seções... -->
  </div>
</template>
```

---

## Escopo

**Em escopo:**
- `style.css` — substituição total dos tokens
- `Login.vue` — piloto de referência (100% sem hardcode)
- `PneusGestao.vue` — varredura e substituição de cores (CSS scoped)
- `SolicitacoesView.vue` — cores de foco e botão
- `DesignSystemView.vue` — componente novo, aba admin
- `README.md` dos planos — atualizar status

**Fora de escopo:**
- Componentes em `EstoqueCentralView.vue`, `DashboardView.vue` — documentar pendências
  mas não bloquear execução
- Modo escuro — tratar como plano futuro separado
- Tipografia / importação de fonte — manter Inter/System-UI atual

---

## Critérios de conclusão

- [ ] `style.css` tem os 17 tokens Gritsch e aliases de compatibilidade
- [ ] `grep -r "#[0-9a-fA-F]\{6\}" frontend/src` retorna zero resultado (nenhum hex direto)
- [ ] `Login.vue` usa apenas `var(--...)` — zero cores hardcoded
- [ ] `PneusGestao.vue` sidebar ativa usa `var(--brand-900)` (não `#C41230`)
- [ ] Headers de tabela `.gp-table th` com `background: var(--brand-900)` (vinho escuro)
- [ ] Status badges usam `--status-ok-bg / --status-warn-bg / --status-critical-bg`
- [ ] `DesignSystemView.vue` acessível via aba admin sem erro de console
- [ ] Contraste WCAG AA verificado: brand-900 sobre surface-0 ≥ 4.5:1 ✓ (razão: ~9:1)
- [ ] Build sem erros

## STOP se

- O `grep` de hardcodes revela mais de 200 ocorrências — dividir em sub-tarefas por arquivo
- Algum componente filho usa tokens de cor via props ou JavaScript (não CSS) — mapear antes
  de substituir para não quebrar lógica de coloração condicional
- `brand-900 #5A181C` sobre `surface-1 #F7F7F7` — verificar contraste antes de usar em
  texto pequeno (< 14px); se insuficiente, usar `--ink-900` para o texto e `--brand-900`
  apenas em fundo com texto branco
