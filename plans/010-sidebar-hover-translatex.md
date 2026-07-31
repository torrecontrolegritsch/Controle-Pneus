---
status: Pendente
prioridade: MÉDIA
esforço: S
risco: baixo
categoria: Design — UX / Micro-interação
---

# 010 — Sidebar: menu item desloca 4px no hover

## Por que isso importa

`.menu-item:hover { transform: translateX(4px); }` faz os itens do menu se moverem lateralmente ao passar o mouse. Em sidebars, o usuário escaneia e clica rapidamente — um deslocamento lateral cria movimento inesperado que distrai sem agregar informação. É um dos antipatterns mais comuns de design gerado por IA ("parecer animado mas sem propósito").

**Why:** Hover em menus deve indicar "isso é clicável" e "isso está selecionado" — não mover o item.

**How to apply:** Remover o `transform: translateX(4px)` e compensar com um sinal visual mais claro (fundo mais escuro ou borda esquerda de acento).

## Estado atual

Arquivo: `frontend/src/views/PneusGestao.vue` — linha ~2605

```css
.menu-item:hover {
  background: #f1f5f9;
  color: #1e293b;
  transform: translateX(4px);   /* ← remove este */
}
```

## Mudança necessária

```css
.menu-item:hover {
  background: #f1f5f9;
  color: #1e293b;
  /* sem transform */
}
```

**Opcional (melhoria adicional):** adicionar borda esquerda de acento sutil no hover para reforçar o sinal sem movimento:

```css
.menu-item:hover {
  background: #f1f5f9;
  color: #1e293b;
  border-left: 2px solid #e2e8f0;
  padding-left: 18px;   /* compensar os 2px da borda */
}
```

> Nota: o opcional exige ajustar o `padding-left` padrão do `.menu-item` de `20px` para `20px` sem borda / `18px` com borda — implementar apenas se testar bem visualmente.

## Escopo

**Em escopo:** `.menu-item:hover` em `PneusGestao.vue`

**Fora de escopo:** `.menu-item.active` — esse não tem transform, sem mudança necessária.

## Critérios de conclusão

- [ ] `grep -n "translateX" frontend/src/views/PneusGestao.vue` → zero resultados no bloco `.menu-item:hover`
- [ ] Visual: hover no menu apenas muda cor, sem movimento
