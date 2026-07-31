<template>
  <div class="login-page">
    <div class="login-card animate-in">

      <!-- PAINEL ESQUERDO: Formulário -->
      <div class="form-panel">
        <div class="brand-label">Grupo Gritsch</div>
        <h1 class="form-title">Entrar</h1>
        <p class="form-sub">Insira seus dados para acessar a plataforma.</p>

        <form @submit.prevent="handleLogin" class="form" novalidate>

          <!-- E-mail (floating label) -->
          <div class="field">
            <input
              v-model="email"
              type="email"
              id="lf-email"
              placeholder=" "
              required
              autocomplete="email"
            />
            <label for="lf-email">E-mail *</label>
          </div>

          <!-- Senha (floating label + toggle) -->
          <div class="field">
            <input
              v-model="password"
              :type="showPass ? 'text' : 'password'"
              id="lf-pass"
              placeholder=" "
              required
              autocomplete="current-password"
            />
            <label for="lf-pass">Senha *</label>
            <button type="button" class="eye-btn" @click="showPass = !showPass" tabindex="-1" :aria-label="showPass ? 'Ocultar senha' : 'Mostrar senha'">
              <svg v-if="!showPass" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>

          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

          <button type="submit" class="btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>Acessar Conta</span>
          </button>

          <button type="button" class="btn-secondary">Esqueci a Senha</button>

          <span class="link-suporte">Conversar com o Suporte</span>

        </form>
      </div>

      <!-- PAINEL DIREITO: Imagem insetada -->
      <div class="image-panel">
        <div class="image-wrap">
          <img :src="heroImg" alt="" class="hero-img" @error="(e) => e.target.style.display='none'" />
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['authenticated'])

const email    = ref('')
const password = ref('')
const loading  = ref(false)
const errorMsg = ref('')
const showPass = ref(false)
const heroImg  = '/login-hero.jpg'

const handleLogin = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const { authLogin, setToken } = await import('../api/gestaoPneus.js')
    const response = await authLogin(email.value, password.value)
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
/* ── Página ───────────────────────────────────────────────── */
.login-page {
  position: fixed; inset: 0;
  display: flex; align-items: center; justify-content: center;
  background: var(--surface-1);
  font-family: 'Inter', system-ui, sans-serif;
  padding: 20px;
}

/* ── Card split ───────────────────────────────────────────── */
.login-card {
  display: flex;
  width: 100%;
  max-width: 900px;
  height: 560px;
  background: var(--surface-0);
  border-radius: 22px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12), 0 4px 14px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.animate-in {
  animation: cardIn 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(16px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ── Painel esquerdo ──────────────────────────────────────── */
.form-panel {
  width: 360px;
  flex-shrink: 0;
  padding: 52px 44px 44px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.brand-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--ink-300);
  margin-bottom: 20px;
}

.form-title {
  font-size: 32px;
  font-weight: 800;
  color: var(--ink-900);
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}

.form-sub {
  font-size: 13px;
  color: var(--ink-600);
  margin: 0 0 32px;
  line-height: 1.55;
}

/* ── Formulário ───────────────────────────────────────────── */
.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* Floating label field */
.field {
  position: relative;
}

.field input {
  width: 100%;
  box-sizing: border-box;
  padding: 22px 14px 8px;
  background: var(--surface-0);
  border: 1px solid var(--ink-200);
  border-radius: 10px;
  font-size: 14px;
  color: var(--ink-900);
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.field input:focus {
  border-color: var(--brand-900);
  box-shadow: 0 0 0 3px rgba(90, 24, 28, 0.08);
}

.field label {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  color: var(--ink-300);
  font-weight: 400;
  pointer-events: none;
  transition: top 0.15s, font-size 0.15s, color 0.15s, transform 0.15s;
}

.field input:focus ~ label,
.field input:not(:placeholder-shown) ~ label {
  top: 9px;
  transform: none;
  font-size: 11px;
  font-weight: 600;
  color: var(--ink-600);
}
.field input:focus ~ label {
  color: var(--brand-900);
}

.field:has(.eye-btn) input {
  padding-right: 44px;
}

.eye-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--ink-300);
  display: flex;
  align-items: center;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.15s;
}
.eye-btn:hover { color: var(--ink-600); }

/* ── Botão principal ──────────────────────────────────────── */
.btn-primary {
  padding: 14px;
  background: var(--brand-900);
  border: none;
  border-radius: 10px;
  color: var(--surface-0);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, box-shadow 0.15s;
  letter-spacing: 0.01em;
  margin-top: 2px;
}
.btn-primary:hover:not(:disabled) {
  background: var(--brand-800);
  box-shadow: 0 4px 14px rgba(90, 24, 28, 0.28);
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

/* ── Botão secundário ─────────────────────────────────────── */
.btn-secondary {
  padding: 13px;
  background: transparent;
  border: 1px solid var(--ink-200);
  border-radius: 10px;
  color: var(--ink-600);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  width: 100%;
  transition: border-color 0.15s, background 0.15s;
}
.btn-secondary:hover {
  border-color: var(--ink-300);
  background: var(--surface-1);
}

/* ── Link suporte ─────────────────────────────────────────── */
.link-suporte {
  text-align: center;
  font-size: 13px;
  color: var(--ink-300);
  cursor: pointer;
  transition: color 0.15s;
}
.link-suporte:hover { color: var(--ink-600); }

/* ── Erro ─────────────────────────────────────────────────── */
.error-msg {
  background: var(--status-critical-bg);
  border: 1px solid var(--brand-100);
  color: var(--status-critical);
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 13px;
  margin: 0;
  line-height: 1.4;
}

/* ── Spinner ──────────────────────────────────────────────── */
.spinner {
  width: 18px; height: 18px;
  border: 2.5px solid rgba(255,255,255,0.35);
  border-radius: 50%;
  border-top-color: var(--surface-0);
  animation: spin 0.8s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Painel direito: imagem insetada ─────────────────────── */
.image-panel {
  flex: 1;
  padding: 14px 14px 14px 0;
  display: flex;
}

.image-wrap {
  flex: 1;
  border-radius: 14px;
  overflow: hidden;
  background: var(--ink-900);
}

.hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
}

/* ── Responsivo ───────────────────────────────────────────── */
@media (max-width: 680px) {
  .login-card    { height: auto; flex-direction: column; max-width: 420px; }
  .form-panel    { width: 100%; padding: 36px 28px 28px; }
  .image-panel   { padding: 0 14px 14px; height: 180px; }
}
</style>
