"""
Cache in-memory para o Gestão de Pneus.
Usa um dicionário simples com TTL para evitar chamadas repetidas ao Supabase.
"""
import time
from typing import Any, Optional
from functools import wraps

# Cache store: { "key": (expiry_timestamp, value) }
_cache = {}
_cache_enabled = True
_default_ttl = 60  # 60 segundos padrão


def get_cache(key: str) -> Optional[Any]:
    """Retorna valor do cache se existir e não expirado."""
    if not _cache_enabled:
        return None
    entry = _cache.get(key)
    if entry is None:
        return None
    expiry, value = entry
    if time.time() > expiry:
        # Expirou - remove
        del _cache[key]
        return None
    return value


def set_cache(key: str, value: Any, ttl: int = _default_ttl):
    """Define valor no cache com TTL em segundos."""
    if not _cache_enabled:
        return
    expiry = time.time() + ttl
    _cache[key] = (expiry, value)


def delete_cache(key: str):
    """Remove chave específica."""
    _cache.pop(key, None)


def clear_cache():
    """Limpa todo o cache."""
    _cache.clear()


def cache_key(*args) -> str:
    """Gera chave de cache a partir de argumentos."""
    return ":".join(str(a) for a in args)


def cached(ttl: int = _default_ttl, key_prefix: str = ""):
    """
    Decorator para cachear resultados de funções.
    Uso: @cached(ttl=120, key_prefix="filiais")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not _cache_enabled:
                return func(*args, **kwargs)
            
            # Gera chave
            cache_key_str = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
            
            # Tenta cache
            result = get_cache(cache_key_str)
            if result is not None:
                return result
            
            # Executa e cachea
            result = func(*args, **kwargs)
            set_cache(cache_key_str, result, ttl)
            return result
        return wrapper
    return decorator


# Funções utilitárias para invalidar cache
def invalidate_prefix(prefix: str):
    """Invalid todas as chaves que começam com prefix."""
    keys_to_delete = [k for k in _cache.keys() if k.startswith(prefix)]
    for k in keys_to_delete:
        del _cache[k]


# Status
def get_cache_stats():
    """Retorna estatísticas do cache."""
    now = time.time()
    active = sum(1 for exp, _ in _cache.values() if exp > now)
    return {
        "enabled": _cache_enabled,
        "total_keys": len(_cache),
        "active_keys": active,
        "expired_keys": len(_cache) - active
    }


def disable_cache():
    """Desabilita cache (útil para debug)."""
    global _cache_enabled
    _cache_enabled = False


def enable_cache():
    """Habilita cache."""
    global _cache_enabled
    _cache_enabled = True