# 003 — Endpoint de Debug Público

**Categoria:** Segurança  
**Prioridade:** ALTA | **Esforço:** S | **Risco:** Médio | **Confiança:** Alta

## Por que importa

`api/index.py:38-50`:
```python
@app.get("/api/debug-server")
def debug_server():
    return {
        "caminho_atual": os.getcwd(),
        "dist_existe": os.path.exists(dist_path),
        "arquivos_dist": os.listdir(dist_path),  # lista arquivos internos
        "sys_path": sys.path                       # expõe estrutura de diretórios
    }
```

Qualquer pessoa (sem autenticação) pode chamar `https://controle-pneus-six.vercel.app/api/debug-server` e ver:
- Estrutura de diretórios interna da função Vercel
- `sys.path` completo (facilita ataques de path traversal)
- Nomes dos arquivos do bundle JS/CSS (facilita fingerprinting)

Este endpoint foi criado para diagnóstico durante desenvolvimento. Deve ser protegido ou removido.

## Evidência

- `api/index.py:38` — sem `Depends(get_current_user)`
- Acessível publicamente em produção

## Passos

**Opção A (recomendada): Remover o endpoint**

Em `api/index.py`, deletar as linhas 38-50:
```python
# REMOVER este bloco inteiro:
@app.get("/api/debug-server")
def debug_server():
    ...
```

**Opção B: Proteger com auth de admin**

```python
from backend.auth import get_current_user, TokenData, require_admin
from fastapi import Depends

@app.get("/api/debug-server")
def debug_server(current_user: TokenData = Depends(require_admin)):
    # só admins conseguem acessar
    return { ... }
```

### Commit

```
fix: remove endpoint debug-server publico (exposicao de paths internos)
```

## Critérios de Conclusão

- [ ] `GET /api/debug-server` retorna 404 (removido) ou 401 (protegido) para usuário não autenticado
- [ ] API continua funcionando normalmente

## Fora do Escopo

- Adicionar logging estruturado como substituto
