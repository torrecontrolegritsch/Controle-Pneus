---
status: Pendente
prioridade: BAIXA
esforço: S
risco: baixo
categoria: Design — Polish
dependências: nenhuma
---

# 012 — Modal borda excessiva + header subtitle estática

## Por que isso importa

Dois pequenos atritos visuais que somados criam percepção de "inacabado":

**A) Modal border-radius 20px vs cards 10-12px:** O `.modal-box` usa `border-radius: 20px` enquanto todos os cards, seções e accordions usam 10-12px. A modal parece pertencer a outro produto dentro da mesma tela.

**B) Header subtitle sempre o mesmo texto:** `.header-sub` sempre exibe "Gestão centralizada e inteligente de frota" independente da aba. No Financeiro, no Histórico, nas Solicitações — o subtitle não tem relação com o conteúdo. Perde a oportunidade de contextualizar o usuário.

**Why (A):** Resultado de evolução incremental — o modal foi criado com radius generoso no design original glassmorphism e não foi atualizado quando o restante foi refinado.

**Why (B):** Texto hardcoded no layout pai que não conhece a aba atual.

## Estado atual

```css
/* PneusGestao.vue linha ~2847 */
.modal-box { border-radius: 20px; ... }
```

```html
<!-- PneusGestao.vue linha ~57 -->
<p class="header-sub">Gestão centralizada e inteligente de frota</p>
```

## Mudanças necessárias

### A — Alinhar modal ao sistema de bordas

```css
.modal-box { border-radius: 12px; ... }
```

### B — Subtitle dinâmico por aba

No `<script setup>` de `PneusGestao.vue`, criar um mapa de subtítulos:

```js
const tabSubtitles = {
  dashboard:      'Visão geral da frota e alertas críticos',
  estoque_central:'Cadastro e distribuição de pneus por NF',
  alocacoes:      'Alocação e troca de pneus por veículo',
  veiculos:       'Cadastro e configuração da frota',
  estoque:        'Inventário agrupado por filial e medida',
  historico:      'Registro cronológico de todas as operações',
  sucata:         'Validação e controle de pneus descartados',
  recicladora:    'Lotes de coleta e retorno financeiro',
  financeiro:     'Créditos por filial referente às carcaças',
  solicitacoes:   'Solicitações de pneus por filial',
  filiais:        'Configuração das unidades operacionais',
  usuarios:       'Gerenciamento de usuários e permissões',
}

const currentTabSubtitle = computed(() =>
  tabSubtitles[tab.value] || 'Gestão centralizada de frota'
)
```

No template:
```html
<p class="header-sub">{{ currentTabSubtitle }}</p>
```

## Escopo

**Em escopo:**
- `.modal-box border-radius` em `PneusGestao.vue`
- `header-sub` template + computed em `PneusGestao.vue`

**Fora de escopo:**
- Outros modais em componentes filhos (EstoqueCentralView, SolicitacoesView) — esses têm seus próprios estilos e podem ser ajustados separadamente.

## Critérios de conclusão

- [ ] `.modal-box { border-radius: 12px }` confirmado no CSS
- [ ] `currentTabSubtitle` computed presente no script
- [ ] Template usa `{{ currentTabSubtitle }}` em vez do texto fixo
- [ ] Build sem erros

## STOP se

- O mapa de subtítulos não cobre todos os `t.id` da lista `allTabs` — adicionar antes de finalizar.
