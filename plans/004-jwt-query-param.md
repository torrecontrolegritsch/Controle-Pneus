# 004 — JWT via Query Parameter

**Categoria:** Segurança  
**Prioridade:** MÉDIA | **Esforço:** M | **Risco:** Médio | **Confiança:** Alta

## Por que importa

`backend/auth.py:92-100`:
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token: Optional[str] = Query(None)   # ← aceita ?token=JWT_AQUI
) -> TokenData:
    token_str = None
    if credentials:
        token_str = credentials.credentials
    elif token:
        token_str = token   # ← JWT na URL
```

Quando um JWT vai na URL (`?token=eyJ...`), ele fica gravado em:
- Logs de acesso do servidor Vercel (consultáveis no dashboard)
- Histórico do browser do usuário
- Headers `Referer` enviados a servidores terceiros
- Analytics e monitoramento

Isso foi adicionado para suportar download de template CSV (`GET /pneus/template`). 

## Evidência

- `backend/auth.py:94` — `token: Optional[str] = Query(None)`
- Commit `70e4b97` — "fix: permitir autenticação via token query param para download de planilha"

## Passos

### 1. Remover o query param do `get_current_user`

Em `backend/auth.py`, alterar a assinatura:
```python
# ANTES:
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token: Optional[str] = Query(None)
) -> TokenData:
    token_str = None
    if credentials:
        token_str = credentials.credentials
    elif token:
        token_str = token

# DEPOIS:
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    token_str = credentials.credentials if credentials else None
```

### 2. Corrigir o download de template no frontend

O template CSV não precisa de autenticação especial — basta o frontend fazer o download com o header Authorization via fetch e criar um Blob URL:

Em `frontend/src/api/gestaoPneus.js`, substituir o link direto por:
```js
export async function downloadPneusTemplate() {
  const token = getToken()
  const res = await fetch(`${API}/pneus/template`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'modelo_pneus.csv'
  a.click()
  URL.revokeObjectURL(url)
}
```

Em `EstoqueCentralView.vue`, trocar `window.open(url)` ou `<a href>` pelo `downloadPneusTemplate()` da API.

### 3. Commit

```
fix: remove JWT via query param, download de template usa fetch + Blob
```

## Critérios de Conclusão

- [ ] `get_current_user` não aceita mais `token` como query param
- [ ] Download do template CSV ainda funciona no Estoque Central
- [ ] Nenhum JWT aparece em URLs da aplicação

## Fora do Escopo

- Implementar tokens de download de curta duração (overkill para este sistema)
