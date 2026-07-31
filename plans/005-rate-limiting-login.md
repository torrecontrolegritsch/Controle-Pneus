# 005 — Rate Limiting no Login (slowapi)

**Categoria:** Segurança  
**Prioridade:** MÉDIA | **Esforço:** M | **Risco:** Médio | **Confiança:** Alta

## Por que importa

O endpoint `POST /api/auth/login` não tem nenhuma proteção contra força bruta. Um atacante pode fazer milhares de tentativas de senha por segundo. `slowapi` já está em `requirements.txt` mas nunca foi implementado.

**Nota:** Se optar por remover `slowapi` (plano 001), implemente com um contador simples em memória em vez disso.

## Evidência

- `requirements.txt:11` — `slowapi` instalado
- `backend/routers/auth.py:36-142` — sem nenhum decorator de rate limit
- Nenhum import de slowapi em arquivo algum

## Passos

### 1. Implementar slowapi no app principal (`api/index.py`)

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### 2. Aplicar limite no endpoint de login (`backend/routers/auth.py`)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")   # 5 tentativas por minuto por IP
def login(request: Request, req: LoginRequest):
    ...
```

### 3. Verificar que o limiter do app está disponível

O `limiter` do `api/index.py` precisa ser o mesmo estado compartilhado pelo router. Use `request.app.state.limiter` ou exporte o limiter de um módulo compartilhado.

### 4. Commit

```
feat: aplica rate limiting de 5/min no endpoint de login via slowapi
```

## Critérios de Conclusão

- [ ] `POST /api/auth/login` com mais de 5 tentativas/min por IP retorna 429
- [ ] Login normal (1 tentativa) continua funcionando
- [ ] Sem impacto no resto dos endpoints

## Fora do Escopo

- Bloqueio permanente de IP (requer Redis/estado persistente)
- CAPTCHA após N falhas
