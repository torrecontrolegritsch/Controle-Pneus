<template>
  <aside class="sidebar">
    <div class="sidebar-top">
      <img src="/logo.jpg" alt="Logo" class="sidebar-logo" />
      <h2 class="sidebar-title">Controle Pneu</h2>
    </div>

    <nav class="sidebar-menu">
      <button 
        v-for="t in tabs" 
        :key="t.id" 
        class="menu-item" 
        :class="{ active: modelValue === t.id }" 
        @click="$emit('update:modelValue', t.id)"
      >
        <span class="menu-icon" v-html="t.icon"></span>
        <span class="menu-label">{{ t.label }}</span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <div class="user-block" v-if="user">
        <div class="avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="7" r="4"></circle><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path></svg>
        </div>
        <div class="u-info">
          <span class="u-name">{{ userEmail }}</span>
          <span class="u-tag">{{ userRole }}</span>
        </div>
        <button class="mini-logout" @click="$emit('logout')" title="Sair">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: 'alocacoes' },
  user: { type: Object, default: null }
})

defineEmits(['update:modelValue', 'logout'])

const tabs = [
  { id: 'alocacoes', label: 'Alocações', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a10 10 0 0 1 0 20"></path></svg>' },
  { id: 'filiais', label: 'Filiais', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>' },
  { id: 'veiculos', label: 'Veículos', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="15" rx="2" ry="2"></rect><path d="M16 3h4l3 3v11h-7V3z"></path><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>' },
  { id: 'pneus', label: 'Pneus', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle></svg>' },
  { id: 'movimentacoes', label: 'Movimentos', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>' },
  { id: 'dashboard', label: 'Dashboard', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>' },
  { id: 'reciclagem', label: 'Reciclagem', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>' },
]

const userEmail = computed(() => props.user?.email?.split('@')[0] || 'Usuário')
const userRole = computed(() => {
  const role = props.user?.role || props.user?.user_metadata?.role || 'operador'
  return role.charAt(0).toUpperCase() + role.slice(1)
})
</script>

<style scoped>
.sidebar {
  width: 200px;
  height: 100vh;
  background: var(--surface-0);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
  border-right: 1px solid var(--ink-200);
}

.sidebar-top {
  padding: 12px 14px;
  border-bottom: 1px solid var(--ink-200);
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar-logo {
  width: 28px;
  height: 28px;
  border-radius: 3px;
  object-fit: cover;
}

.sidebar-title {
  font-size: 12px;
  color: var(--ink-600);
  font-weight: 600;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.sidebar-menu {
  flex: 1;
  padding: 6px 0;
  overflow-y: auto;
}

.menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  border: none;
  background: transparent;
  color: var(--ink-600);
  border-radius: 0;
  border-left: 2px solid transparent;
  cursor: pointer;
  transition: background 0.12s;
  margin-bottom: 0;
  font-size: 12px;
  font-weight: 500;
}

.menu-item:hover {
  background: var(--surface-2);
  color: var(--ink-900);
}

.menu-item.active {
  background: var(--surface-2);
  color: var(--brand-900);
  border-left-color: var(--brand-900);
  font-weight: 600;
}

.menu-icon {
  display: flex;
  opacity: 0.7;
  flex-shrink: 0;
}
.menu-item.active .menu-icon { opacity: 1; }

.menu-label {
  font-size: 12px;
}

.sidebar-footer {
  padding: 10px 14px;
  border-top: 1px solid var(--ink-200);
}

.user-block {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar {
  width: 28px;
  height: 28px;
  background: var(--surface-2);
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ink-600);
  flex-shrink: 0;
}

.u-info {
  flex: 1;
  min-width: 0;
}

.u-name {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--ink-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.u-tag {
  font-size: 10px;
  color: var(--ink-300);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.mini-logout {
  width: 24px;
  height: 24px;
  border: 1px solid var(--ink-200);
  background: none;
  border-radius: 3px;
  color: var(--ink-600);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.12s, border-color 0.12s, color 0.12s;
  flex-shrink: 0;
}

.mini-logout:hover {
  background: var(--status-critical-bg);
  border-color: var(--status-critical);
  color: var(--status-critical);
}
</style>