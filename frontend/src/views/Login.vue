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

  try {
    const { authLogin, setToken } = await import('../api/gestaoPneus.js')
    const response = await authLogin(email.value, password.value)
    
    // Sucesso! Salva o token e emite o evento
    if (response.access_token) {
      setToken(response.access_token, true)
      emit('authenticated', response)
    } else {
      throw new Error('Resposta inválida do servidor')
    }
    
  } catch (err) {
    errorMsg.value = err.message || 'Falha na autenticação'
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
  background: #f1f5f9;
  font-family: 'Inter', sans-serif;
}

.glass-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  padding: 40px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
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
  padding: 13px 16px 13px 44px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #1e293b;
  font-size: 14px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input-wrapper input:focus {
  outline: none;
  background: #fff;
  border-color: #C41230;
  box-shadow: 0 0 0 3px rgba(196, 18, 48, 0.08);
}

.input-wrapper .icon {
  position: absolute;
  left: 18px;
  font-size: 18px;
  opacity: 0.4;
}

.login-btn {
  margin-top: 8px;
  padding: 14px;
  background: #C41230;
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-btn:hover {
  background: #a50f28;
  box-shadow: 0 4px 12px rgba(196, 18, 48, 0.25);
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
  color: #94a3b8;
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
