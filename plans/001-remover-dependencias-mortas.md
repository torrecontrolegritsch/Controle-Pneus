# 001 — Remover Dependências Mortas

**Categoria:** Leveza / Dependencies  
**Prioridade:** ALTA | **Esforço:** S | **Risco:** Baixo | **Confiança:** Alta

## Por que importa

`pandas` (≈30 MB), `openpyxl` (≈5 MB) e `slowapi` estão em `requirements.txt` mas **não são importados em nenhum arquivo `.py` do projeto**. Cada dependência morta:
- Aumenta o cold start da função Vercel (Python serverless carrega tudo em memória)
- Aumenta a superfície de ataque (vulnerabilidades em libs que nem são usadas)
- Infla o bundle de deploy sem nenhum benefício

## Evidência

```bash
grep -rn "import pandas\|from pandas\|openpyxl\|slowapi" backend/ api/ --include="*.py"
# Retorna: (vazio)
```

`requirements.txt` linhas 6, 7, 11:
```
pandas        # ← MORTO
openpyxl      # ← MORTO
slowapi       # ← MORTO (instalado, nunca importado)
```

## Passos

1. Editar `requirements.txt` — remover as 3 linhas:
   ```
   pandas
   openpyxl
   slowapi
   ```

2. Verificar que nenhum arquivo usa essas libs (já confirmado):
   ```bash
   grep -rn "pandas\|openpyxl\|slowapi" backend/ api/ --include="*.py"
   ```
   Deve retornar vazio.

3. Fazer commit:
   ```
   chore: remove dependencias mortas (pandas, openpyxl, slowapi)
   ```

## Critérios de Conclusão

- [ ] `requirements.txt` não contém `pandas`, `openpyxl`, `slowapi`
- [ ] Grep por essas libs retorna vazio
- [ ] Deploy na Vercel funciona (cold start mais rápido)

## Fora do Escopo

- Implementar rate limiting (ver plano 005 se quiser usar slowapi de verdade)
- Substituir por libs menores
