<template>
  <div class="main-app">
    <div v-if="fatalError" class="fatal-error">
      <h2>Erro ao carregar o sistema</h2>
      <pre>{{ fatalError }}</pre>
      <button @click="fatalError=null; checkAuth()">Tentar novamente</button>
    </div>
    <div v-else-if="loading" class="loading-screen">Carregando sistema...</div>
    <Login v-else-if="!isAuthenticated" @authenticated="onAuth" />
    <PneusGestao v-else :user="user" @logout="onLogout" />
  </div>
</template>

<script setup>
import { ref, onMounted, onErrorCaptured } from 'vue'
import Login from './views/Login.vue'
import PneusGestao from './views/PneusGestao.vue'
import { authMe, getToken, clearToken } from './api/gestaoPneus.js'

const user = ref(null)
const loading = ref(true)
const isAuthenticated = ref(false)
const fatalError = ref(null)

onErrorCaptured((err, instance, info) => {
  fatalError.value = `${err?.message || err}\n[${info}]`
  loading.value = false
  return false
})

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
  background: #f8fafc;
  color: #64748b;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.02em;
}
.fatal-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: #f8fafc;
  color: #1e293b;
  font-family: 'Inter', sans-serif;
  padding: 40px;
  text-align: center;
}
.fatal-error pre {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 16px;
  border-radius: 8px;
  font-size: 12px;
  max-width: 600px;
  overflow: auto;
  color: #C41230;
  margin: 16px 0;
}
.fatal-error button {
  padding: 12px 24px;
  background: #C41230;
  border: none;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  font-size: 15px;
}
</style>
