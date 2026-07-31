---
status: Pendente
prioridade: ALTA
esforço: S
risco: baixo
categoria: Design — Consistência de Marca
---

# 008 — Sidebar: cor ativa azul em app de marca vermelha

## Por que isso importa

O item de menu ativo usa `background: #3b82f6` (azul) com `box-shadow` azul, enquanto **todo o restante do sistema** usa `--brand: #C41230` (vermelho). O sidebar é o elemento mais visto do sistema — aparece em 100% das telas. É o conflito de identidade visual mais visível da aplicação.

**Why:** O token `--brand` existe exatamente para garantir consistência. O azul entrou provavelmente de um template/cópia anterior.

**How to apply:** Substituir apenas as regras `.menu-item.active` e `.usuarios-shortcut.active` — sem tocar em outros estilos.

## Estado atual

Arquivo: `frontend/src/views/PneusGestao.vue` — linha ~2611

```css
/* ATUAL — azul */
.menu-item.active {
  background: #3b82f6;              /* ← azul fixo */
  color: #fff;
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);  /* ← sombra azul */
}

.usuarios-shortcut.active {
  background: #eff6ff;              /* ← azul claro */
  border-color: #bfdbfe;
  color: #1d4ed8;
}
```

## Mudanças necessárias

```css
/* NOVO — vermelho de marca */
.menu-item.active {
  background: var(--brand);
  color: #fff;
  box-shadow: 0 4px 12px rgba(196, 18, 48, 0.25);
}

/* .menu-item.active .menu-icon — sem mudança necessária */

.usuarios-shortcut.active {
  background: var(--brand-bg);
  border-color: var(--brand-mid);
  color: var(--brand-dark);
}
```

## Escopo

**Em escopo:**
- `.menu-item.active` em `PneusGestao.vue`
- `.usuarios-shortcut.active` em `PneusGestao.vue`

**Fora de escopo:**
- Outros badges azuis no sistema (são semânticos, não de marca)
- DashboardView e outros componentes

## Critérios de conclusão

- [ ] `grep -n "#3b82f6" frontend/src/views/PneusGestao.vue` → zero resultados no bloco `.menu-item.active`
- [ ] `grep -n "#eff6ff" frontend/src/views/PneusGestao.vue` → zero resultados no bloco `.usuarios-shortcut.active`
- [ ] Visual: item ativo aparece vermelho `#C41230` no browser

## STOP se

- Outro componente importar `.menu-item.active` — verificar antes de alterar
