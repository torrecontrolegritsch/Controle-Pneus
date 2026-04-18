<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div 
          v-for="t in toasts" 
          :key="t.id" 
          class="toast" 
          :class="t.type"
        >
          <span class="toast-icon">
            <svg v-if="t.type === 'success'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
            <svg v-else-if="t.type === 'error'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
            <svg v-else-if="t.type === 'warning'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
          </span>
          <span class="toast-message">{{ t.message }}</span>
          <button class="toast-close" @click="remove(t.id)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let id = 0

function show(message, type = 'info', duration = 4000) {
  const toastId = ++id
  toasts.value.push({ id: toastId, message, type })
  
  if (duration > 0) {
    setTimeout(() => remove(toastId), duration)
  }
}

function remove(toastId) {
  const idx = toasts.value.findIndex(t => t.id === toastId)
  if (idx >= 0) toasts.value.splice(idx, 1)
}

defineExpose({ show, remove })
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #1e1e3f;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  min-width: 280px;
  border-left: 3px solid #6366f1;
}

.toast.success { border-left-color: #22c55e; }
.toast.success .toast-icon { color: #22c55e; }
.toast.error { border-left-color: #ef4444; }
.toast.error .toast-icon { color: #ef4444; }
.toast.warning { border-left-color: #f59e0b; }
.toast.warning .toast-icon { color: #f59e0b; }

.toast-icon {
  display: flex;
  color: #6366f1;
}

.toast-message {
  flex: 1;
  color: #fff;
  font-size: 14px;
}

.toast-close {
  background: none;
  border: none;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  padding: 4px;
}

.toast-close:hover {
  color: #fff;
}

.toast-enter-active, .toast-leave-active {
  transition: all 0.3s;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>