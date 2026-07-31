# 006 — .gitignore Incompleto para Arquivos .env

**Categoria:** Segurança  
**Prioridade:** MÉDIA | **Esforço:** S | **Risco:** Alto (se acidentalmente commitado) | **Confiança:** Alta

## Por que importa

O `.gitignore` atual contém apenas:
```
.env
```

Isso protege apenas o `.env` na raiz do projeto. Os arquivos `backend/.env` e `frontend/.env` **não estão listados**. Eles não estão no git atualmente, mas um `git add -A` ou `git add backend/` os incluiria silenciosamente.

`backend/.env` contém:
- `SUPABASE_KEY` (service_role — acesso total ao banco)
- `SQLSERVER_PASSWORD` (senha do SQL Server de produção)
- `SUPABASE_DB_URL` (URL com senha do Postgres)

Se qualquer um desses arquivos for commitado e o repositório se tornar público (ou cair em mãos erradas), as credenciais ficam expostas **permanentemente no histórico git**, mesmo após remoção.

## Evidência

- `.gitignore:6` — contém apenas `.env`
- `backend/.env` existe com credenciais sensíveis
- `frontend/.env` existe com `VITE_API_URL`

## Passos

### 1. Atualizar `.gitignore`

Substituir a linha `.env` por:
```gitignore
# Variáveis de ambiente — NUNCA commitar
.env
.env.*
**/.env
**/.env.*
!.env.example
```

### 2. Criar `.env.example` como documentação segura (opcional mas recomendado)

Na raiz do projeto, criar `.env.example`:
```
# Copie este arquivo para .env e preencha os valores reais
SUPABASE_URL=https://SEU_PROJETO.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_DB_URL=postgresql://...
JWT_SECRET_KEY=gere_com_python_secrets_token_hex_32
SQLSERVER_HOST=
SQLSERVER_PORT=1433
SQLSERVER_USER=
SQLSERVER_PASSWORD=
SQLSERVER_DB=
PORT=8015
CORS_ORIGINS=http://localhost:5173,https://SEU_DOMINIO.vercel.app
```

### 3. Verificar que nenhum .env está rastreado

```bash
git ls-files | grep "\.env"
# Deve retornar vazio
```

### 4. Commit

```
chore: gitignore cobre todos os .env em qualquer subdiretorio
```

## Critérios de Conclusão

- [ ] `.gitignore` cobre `**/.env` e `**/.env.*`
- [ ] `git ls-files | grep ".env"` retorna vazio
- [ ] `.env.example` criado como referência (sem valores reais)

## Fora do Escopo

- Migrar segredos para Vercel Secrets/environment variables (já estão, mas vale revisar)
- Rotacionar as chaves atuais (só necessário se houver suspeita de exposição)
