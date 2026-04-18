<template>
  <div class="main-app">
    <div v-if="loading" class="loading-screen">Carregando...</div>
    <Login v-else-if="!isAuthenticated" @authenticated="onAuth" />
    <PneusGestao v-else :user="user" @logout="onLogout" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Login from './views/Login.vue'
import PneusGestao from './views/PneusGestao.vue'
import { authMe, getToken, clearToken } from './api/gestaoPneus.js'

const user = ref(null)
const loading = ref(true)
const isAuthenticated = ref(false)

async function checkAuth() {
  const token = getToken()
  if (!token) {
    loading.value = false
    return
  }
  try {
    const userData = await authMe()
    user.value = userData
    isAuthenticated.value = true
  } catch (e) {
    clearToken()
  } finally {
    loading.value = false
  }
}

onMounted(checkAuth)

const onAuth = async (u) => {
  if (u && u.access_token) {
    localStorage.setItem('pneus_access_token', u.access_token)
    user.value = u.user || { email: u.email }
    isAuthenticated.value = true
  } else {
    await checkAuth()
  }
}

const onLogout = () => {
  clearToken()
  user.value = null
  isAuthenticated.value = false
}
</script>

<style>
body { margin: 0; padding: 0; overflow-x: hidden; }
.main-app { width: 100vw; height: 100vh; }
.loading-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: #1a1a2e;
  color: #fff;
  font-family: 'Inter', sans-serif;
}
</style>
