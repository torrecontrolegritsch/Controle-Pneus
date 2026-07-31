# 002 — CORS Wildcard em Produção

**Categoria:** Segurança  
**Prioridade:** ALTA | **Esforço:** S | **Risco:** Médio | **Confiança:** Alta

## Por que importa

`api/index.py:53`:
```python
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
```

O default `"*"` significa que **se a variável `CORS_ORIGINS` não estiver configurada na Vercel**, qualquer site na internet pode fazer requests autenticados para a API. Isso combinado com `allow_credentials=True` é uma configuração proibida pelos browsers modernos — mas o risco real é que o fallback `*` remove toda proteção de origem.

## Evidência

- `api/index.py:53-58`: CORS com default wildcard e `allow_credentials=True`
- `backend/.env:3`: só tem origens localhost (não inclui o domínio Vercel)
- `vercel.json`: não define variáveis de ambiente

## Passos

### 1. Verificar se CORS_ORIGINS está configurada na Vercel

Acesse: https://vercel.com/dashboard → projeto → Settings → Environment Variables  
Confirme se `CORS_ORIGINS` está definida com o domínio de produção:
```
CORS_ORIGINS=https://controle-pneus-six.vercel.app
```

### 2. Remover o default wildcard em `api/index.py`

```python
# ANTES (inseguro):
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# DEPOIS (falha explicitamente se não configurado):
_cors_raw = os.getenv("CORS_ORIGINS")
if not _cors_raw:
    logger.warning("CORS_ORIGINS não configurado — restringindo a domínio Vercel padrão")
    _cors_raw = "https://controle-pneus-six.vercel.app"
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",")]
```

### 3. Adicionar ao `.env` local para dev

```
CORS_ORIGINS=http://localhost:5173,http://localhost:8015,https://controle-pneus-six.vercel.app
```

### 4. Commit

```
fix: remove CORS wildcard default, restringe origens conhecidas
```

## Critérios de Conclusão

- [ ] `CORS_ORIGINS` configurada na Vercel dashboard com domínio de produção
- [ ] Código não usa `"*"` como fallback
- [ ] Login ainda funciona em produção após deploy

## Fora do Escopo

- Implementar CSP headers (melhoria futura)
