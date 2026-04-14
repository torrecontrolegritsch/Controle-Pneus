<template>
  <div class="main-app">
    <Login v-if="!user" @authenticated="onAuth" />
    <PneusGestao v-else :user="user" @logout="onLogout" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Login from './views/Login.vue'
import PneusGestao from './views/PneusGestao.vue'

const user = ref(null)

onMounted(() => {
  const saved = localStorage.getItem('gp_user')
  if (saved) {
    try {
      user.value = JSON.parse(saved)
    } catch {
      localStorage.removeItem('gp_user')
    }
  }
})

const onAuth = (u) => {
  user.value = u
}

const onLogout = () => {
  localStorage.removeItem('gp_user')
  user.value = null
}
</script>

<style>
/* Reset global simples */
body { margin: 0; padding: 0; overflow-x: hidden; }
.main-app { width: 100vw; height: 100vh; }
</style>
