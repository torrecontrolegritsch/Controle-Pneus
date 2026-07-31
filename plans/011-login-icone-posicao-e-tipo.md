---
status: Pendente
prioridade: ALTA
esforço: M
risco: baixo
categoria: Design — Bug Visual + Consistência
---

# 011 — Login: bug de posicionamento de ícone + emoji em sistema SVG

## Por que isso importa

Dois problemas combinados na tela de login:

**A) Bug de posicionamento:** `.input-wrapper .icon` usa `position: absolute` mas `.input-wrapper` não tem `position: relative` no CSS. O ícone é posicionado relativo ao `.glass-card` (que tem `position: relative`), não ao wrapper do input. Resultado: o emoji aparece em `left: 18px` a partir da borda esquerda do *card* (que tem `padding: 40px`), ou seja, dentro da área de padding do card, não sobre o input. Visualmente os ícones ficam desalinhados da caixa de texto.

**B) Emoji vs SVG:** O restante do sistema usa exclusivamente SVGs inline. Emojis (📧, 🔒) têm renderização inconsistente por SO — no Windows podem aparecer coloridos, diferentes de tamanho, ou levemente desalinhados verticalmente. Em uma ferramenta de gestão B2B isso soa amador.

**Why:** A) é um bug CSS real. B) é inconsistência de sistema de design.

**How to apply:** Adicionar `position: relative` ao `.input-wrapper`, substituir emojis por SVGs inline com as mesmas dimensões.

## Estado atual

Arquivo: `frontend/src/views/Login.vue`

```css
/* linha ~151 — falta position: relative */
.input-wrapper .icon {
  position: absolute;
  left: 18px;
  font-size: 18px;
  opacity: 0.4;
}
/* .input-wrapper NÃO tem position: relative definido */
```

```html
<!-- linha ~15 — emoji em sistema SVG -->
<span class="icon">📧</span>
<span class="icon">🔒</span>
```

## Mudanças necessárias

### CSS — adicionar position: relative ao wrapper

```css
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper .icon {
  position: absolute;
  left: 14px;
  display: flex;
  align-items: center;
  color: #94a3b8;
  pointer-events: none;
}
```

### HTML — substituir emojis por SVGs

```html
<!-- E-mail -->
<span class="icon">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <rect x="2" y="4" width="20" height="16" rx="2"/>
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
  </svg>
</span>

<!-- Senha -->
<span class="icon">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
</span>
```

### Ajuste no padding do input (já correto em 44px, confirmar alinhamento visual)

O input já tem `padding-left: 44px` — verificar se o ícone de 16px em `left: 14px` fica visualmente centrado sobre o input. Ajustar `left` se necessário.

## Escopo

**Em escopo:** `frontend/src/views/Login.vue` — apenas `<template>` e `.input-wrapper`/`.icon` no `<style scoped>`.

**Fora de escopo:** Demais estilos do login — card, botão, container.

## Critérios de conclusão

- [ ] `.input-wrapper` tem `position: relative` no CSS scoped
- [ ] Nenhum emoji nos ícones do form — apenas `<svg>`
- [ ] Visual: ícone aparece dentro e alinhado à esquerda de cada input
- [ ] Build sem erros: `npm run build` no diretório `frontend/`

## STOP se

- O ajuste de `left` do ícone fizer ele sobrepor o texto do input — ajustar padding-left do input para compensar.
