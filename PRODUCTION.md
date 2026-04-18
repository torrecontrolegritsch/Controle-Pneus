# Checklist de Produção - Gestão de Pneus

## ✅ Pronto para Produção

### Segurança
- [x] Autenticação JWT implementada
- [x] Endpoints protegidos
- [x] Roles (admin/gerente/operador)
- [x] Credenciais no .env (não commitadas)
- [x] .gitignore configured

### Backend
- [x] FastAPI com roteadores
- [x] Supabase como banco
- [x] SQL Server (consulta)

### Frontend
- [x] Vue.js 3 + Vite
- [x] Components separados
- [x]Composables criados

---

## 📋 Configuração Vercel (Produção)

### Environment Variables (Dashboard Vercel):

```
# Supabase
SUPABASE_URL=https://dpvdjldocvdsdgvmnsvu.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# JWT
JWT_SECRET_KEY=e7255e3dbb61676a2551579f49f4b5fd45fb89f606560b2d34dbdd467089fdcb

# SQL Server (opcional - apenas local)
SQLSERVER_HOST=bi.bluefleet.com.br
SQLSERVER_USER=referencia
SQLSERVER_PASSWORD=JSoo2iS*hdfbs5f2gdsf
SQLSERVER_DB=referencia
```

### Comandos:
```bash
# Build frontend
cd frontend && npm run build

# Deploy
vercel --prod
```

---

## 🚨 Antes de Deploy

1. **Testar localmente:**
```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

2. **Verificar .env NÃO está commitado:**
```bash
git status .env
# Should show: .env is NOT tracked
```

3. **Testar login:**
- Acesse http://localhost:8015
- Faça login
- Verifique se token é salvo
- Acesse dashboard

---

## 📝 Notas

- Frontend: `frontend/dist/` → Vercel serving
- Backend: `api/index.py` → Vercel Python
- Timeout: 30s (free tier)
- Functions: Serverless