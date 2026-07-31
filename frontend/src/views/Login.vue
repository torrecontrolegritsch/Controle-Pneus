<template>
  <div class="login-page">
    <div class="login-card animate-in">

      <!-- PAINEL ESQUERDO: Formulário -->
      <div class="form-panel">
        <div class="brand">
          <img src="/logo.jpg" alt="Logo" class="brand-logo" />
          <span class="brand-name">Gestão de Pneus</span>
        </div>

        <h1 class="form-title">Entrar</h1>
        <p class="form-sub">Insira suas credenciais para acessar a plataforma.</p>

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

          <button type="submit" class="btn-login" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>Acessar Conta</span>
          </button>

        </form>

        <p class="form-footer">© 2026 Gestão de Pneus · v2.1.0</p>
      </div>

      <!-- PAINEL DIREITO: Imagem -->
      <div class="image-panel">
        <img src="/bg.jpg" alt="" class="hero-img" />
        <div class="image-overlay">
          <div class="image-caption">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.85)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
            <span>Controle inteligente da frota de pneus</span>
          </div>
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
  background: #e8ecf0;
  font-family: 'Inter', system-ui, sans-serif;
  padding: 20px;
}

/* ── Card split ───────────────────────────────────────────── */
.login-card {
  display: flex;
  width: 100%;
  max-width: 920px;
  height: 580px;
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.12), 0 4px 16px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.animate-in {
  animation: cardIn 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(18px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0)    scale(1); }
}

/* ── Painel esquerdo ──────────────────────────────────────── */
.form-panel {
  width: 380px;
  flex-shrink: 0;
  padding: 48px 44px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #f1f5f9;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 36px;
}
.brand-logo {
  height: 36px;
  width: auto;
  border-radius: 8px;
}
.brand-name {
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  letter-spacing: 0.01em;
}

.form-title {
  font-size: 30px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 6px;
  letter-spacing: -0.5px;
}

.form-sub {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 28px;
  line-height: 1.5;
}

/* ── Formulário ───────────────────────────────────────────── */
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
}

/* Floating label field */
.field {
  position: relative;
}

.field input {
  width: 100%;
  box-sizing: border-box;
  padding: 22px 14px 8px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  color: #0f172a;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.field input:focus {
  border-color: #C41230;
  box-shadow: 0 0 0 3px rgba(196, 18, 48, 0.08);
}

.field label {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  color: #94a3b8;
  font-weight: 400;
  pointer-events: none;
  transition: top 0.15s, font-size 0.15s, color 0.15s, transform 0.15s;
  background: transparent;
}

/* Label sobe quando input tem foco ou valor */
.field input:focus ~ label,
.field input:not(:placeholder-shown) ~ label {
  top: 9px;
  transform: none;
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
}
.field input:focus ~ label {
  color: #C41230;
}

/* Campo de senha: padding direito para o botão */
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
  color: #94a3b8;
  display: flex;
  align-items: center;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.15s;
}
.eye-btn:hover { color: #475569; }

/* ── Botão ────────────────────────────────────────────────── */
.btn-login {
  margin-top: 4px;
  padding: 14px;
  background: #C41230;
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, box-shadow 0.15s;
  letter-spacing: 0.01em;
}
.btn-login:hover:not(:disabled) {
  background: #a50f28;
  box-shadow: 0 4px 14px rgba(196, 18, 48, 0.28);
}
.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ── Erro ─────────────────────────────────────────────────── */
.error-msg {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
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
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Rodapé do form ───────────────────────────────────────── */
.form-footer {
  margin-top: 20px;
  font-size: 11px;
  color: #cbd5e1;
  text-align: center;
}

/* ── Painel direito: imagem ───────────────────────────────── */
.image-panel {
  flex: 1;
  position: relative;
  overflow: hidden;
  /* Fallback: gradiente escuro de pneu/frota */
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 60%, #1a1a2e 100%);
}

.hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(10, 15, 30, 0.75) 0%,
    rgba(10, 15, 30, 0.15) 50%,
    transparent 100%
  );
  display: flex;
  align-items: flex-end;
  padding: 28px 32px;
}

.image-caption {
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.01em;
  text-shadow: 0 1px 4px rgba(0,0,0,0.5);
}

/* ── Responsivo ───────────────────────────────────────────── */
@media (max-width: 700px) {
  .login-card { height: auto; flex-direction: column; max-width: 420px; }
  .form-panel  { width: 100%; border-right: none; border-bottom: 1px solid #f1f5f9; padding: 36px 28px; }
  .image-panel { height: 180px; }
}
</style>
