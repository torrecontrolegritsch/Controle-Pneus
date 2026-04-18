<template>
  <div v-if="show" class="loading-overlay" :class="{ fixed: fixed }">
    <div class="loading-content">
      <div class="spinner"></div>
      <span v-if="message" class="loading-message">{{ message }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  message: { type: String, default: '' },
  fixed: { type: Boolean, default: false }
})
</script>

<style scoped>
.loading-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.loading-overlay.fixed {
  position: fixed;
  inset: 0;
  background: rgba(26, 26, 46, 0.9);
  z-index: 1000;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(99, 102, 241, 0.2);
  border-top-color: #818cf8;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-message {
  color: rgba(255,255,255,0.7);
  font-size: 14px;
}
</style>