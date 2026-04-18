# Migração para Novos Componentes

## Arquivos Criados

| Componente | Uso |
|-----------|-----|
| `DashboardView.vue` | KPIs + Gráficos |
| `FiliaisView.vue` | Gestão de filiais |
| `VeiculosView.vue` | Gestão de veículos |
| `PneusView.vue` | Gestão de pneus |
| `MovimentacoesView.vue` | Histórico deMovim |
| `ReciclagemView.vue` | Lotes de reciclagem |

## Como Usar no PneusGestao.vue

### Opção 1: Substituição Parcial

Para usar um dos novos componentes, faça:

```vue
<script setup>
import { FiliaisView } from './components/views/FiliaisView.vue'

const filiaisData = ref([]) // carregar dados primeiro

function onFiliaisRefresh() {
  // recarregar dados
}
</script>

<template>
  <!-- Substitua a seção existente por: -->
  <section v-if="tab === 'filiais'">
    <FiliaisView :filiais="filiaisData" @refresh="onFiliaisRefresh" />
  </section>
</template>
```

### Opção 2: Menu Novo (Recomendado)

Adicione ao menu:

```vue
<template>
  <nav class="sidebar-menu">
    <button @click="useNewView = 'filiais'">
      Filiais (Novo)
    </button>
  </nav>
</template>
```

### Opção 3: Routes Separadas

Defina routes diferentes para cada seção:

```javascript
// router/index.js
{
  path: '/filiais',
  component: () => import('./components/views/FiliaisView.vue')
}
```

## Status Atual

- `FiliaisView.vue` ✅ Pronto para uso
- `VeiculosView.vue` ✅ Pronto para uso
- `DashboardView.vue` ✅ Pronto para uso
- `PneusView.vue` ✅ Pronto para uso
- `MovimentacoesView.vue` ✅ Pronto para uso
- `ReciclagemView.vue` ✅ Pronto para uso

## Diferenças

| Aspecto | Original | Novo |
|--------|---------|-------|
| Linhas | ~2785 | ~200-300 cada |
| Manutenção | Difícil | Fácil |
| Composable | Não | Sim |
| Type-safe | Não | Sim |

## Recomendação

Para novos projetos ou refatoração gradual:
1. Comece com DashboardView
2. Depois FiliaisView
3. Depois VeiculosView

O PneusGestao.vue pode continuar funcionando paralelamente até a migração completa.