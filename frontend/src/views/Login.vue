<template>
  <div class="login-container">
    <div class="glass-card animate-fade-in">
      <header class="gp-header">
        <div class="header-branding">
          <img src="/logo.jpg" alt="Logo" class="header-logo" />
          <h1>Gestão de Pneus</h1>
        </div>
      </header>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label for="email">E-mail</label>
          <div class="input-wrapper">
            <span class="icon">📧</span>
            <input 
              v-model="email" 
              type="email" 
              id="email" 
              placeholder="seu@email.com" 
              required
            />
          </div>
        </div>

        <div class="input-group">
          <label for="password">Senha</label>
          <div class="input-wrapper">
            <span class="icon">🔒</span>
            <input 
              v-model="password" 
              type="password" 
              id="password" 
              placeholder="••••••••" 
              required
            />
          </div>
        </div>

        <button :disabled="loading" type="submit" class="login-btn">
          <span v-if="loading" class="loader"></span>
          <span v-else>Entrar no Sistema</span>
        </button>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      </form>

      <div class="footer-links">
        <span>© 2026 BlueFleet • v2.1.0</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['authenticated'])

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
  loading.value = true
  errorMsg.value = ''
  
  // Detecta a BASE API de forma resiliente
  const BASE = import.meta.env.VITE_API_URL && import.meta.env.MODE === 'development' 
    ? import.meta.env.VITE_API_URL 
    : '';

  try {
    const response = await fetch(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Falha na autenticação')
    }

    const userData = await response.json()
    
    // Sucesso! Salva no localStorage e emite o evento
    localStorage.setItem('gp_user', JSON.stringify(userData))
    emit('authenticated', userData)
    
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: url('/bg.jpg');
  background-size: cover;
  background-position: center;
  font-family: 'Inter', sans-serif;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0.4) 100%);
  pointer-events: none;
}

.glass-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 32px;
  box-shadow: 0 40px 80px -15px rgba(0, 0, 0, 0.1), 0 10px 30px -10px rgba(0, 0, 0, 0.05);
}

.header-branding { display: flex; flex-direction: column; align-items: flex-start; gap: 8px; margin-bottom: 32px; }
.header-logo { height: 40px; width: auto; border-radius: 8px; }
.gp-header h1 { font-size: 24px; font-weight: 800; color: #1e293b; margin: 0; letter-spacing: -0.5px; }

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group label {
  display: block;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
  margin-left: 4px;
}

.input-wrapper input {
  width: 100%;
  padding: 16px 16px 16px 48px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  color: #1e293b;
  font-size: 15px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-wrapper input:focus {
  outline: none;
  background: #fff;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.input-wrapper .icon {
  position: absolute;
  left: 18px;
  font-size: 18px;
  opacity: 0.4;
}

.login-btn {
  margin-top: 8px;
  padding: 18px;
  background: #1e293b;
  border: none;
  border-radius: 16px;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-btn:hover {
  background: #0f172a;
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

.login-btn:active {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-msg {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  text-align: center;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.footer-links {
  margin-top: 32px;
  text-align: center;
  font-size: 12px;
  color: rgba(255,255,255,0.3);
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.loader {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
