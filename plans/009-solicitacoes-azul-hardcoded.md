---
status: Pendente
prioridade: ALTA
esforço: S
risco: baixo
categoria: Design — Consistência de Marca
dependências: nenhuma
---

# 009 — SolicitacoesView: botão e foco hardcoded azul

## Por que isso importa

`SolicitacoesView.vue` foi criado com estilos inline locais que redefinem `btn-primary` e o foco dos inputs com azul fixo (`#1d4ed8`). O botão "Nova Solicitação" e o foco dos campos do formulário aparecem azuis — enquanto o equivalente em todos os outros formulários do sistema é vermelho `var(--brand)`.

**Why:** O componente tem estilos scoped com redefinição local de `.btn-primary` para evitar conflito de escopo, mas usou azul fixo em vez do sistema de tokens.

**How to apply:** Substituir apenas os 3 valores hardcoded de cor de marca dentro do `<style scoped>` de `SolicitacoesView.vue`.

## Estado atual

Arquivo: `frontend/src/components/views/SolicitacoesView.vue` — linhas ~345 e ~420

```css
/* linha ~345 — foco do input */
.form-group input:focus,
.form-group select:focus { border-color: #3b82f6; }   /* ← azul */

/* linha ~420 — botão primário local */
.btn-primary {
  background: #1d4ed8;   /* ← azul */
  ...
}
.btn-primary:hover:not(:disabled) { background: #1e40af; }  /* ← azul escuro */
```

## Mudanças necessárias

```css
/* Foco */
.form-group input:focus,
.form-group select:focus { border-color: #C41230; box-shadow: 0 0 0 3px rgba(196,18,48,0.08); }

/* Botão */
.btn-primary {
  background: #C41230;
  ...
}
.btn-primary:hover:not(:disabled) { background: #a50f28; }
```

## Escopo

**Em escopo:** `frontend/src/components/views/SolicitacoesView.vue` — apenas as regras de cor listadas acima.

**Fora de escopo:** Demais cores semânticas do arquivo (chips de status pendente/aprovado/recusado — essas usam cores significativas corretas).

## Critérios de conclusão

- [ ] `grep -n "#1d4ed8\|#1e40af\|#3b82f6" frontend/src/components/views/SolicitacoesView.vue` → zero resultados
- [ ] Visual: botão "Nova Solicitação" aparece vermelho no browser

## STOP se

- Há dependência de `.btn-primary` azul em outro componente que importa SolicitacoesView — improvável dado que scoped, mas verificar.
