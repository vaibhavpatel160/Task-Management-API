import json
from typing import Optional, Callable, Any
import redis
from .config import settings

_redis = None

def get_client() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True)
    return _redis

def cache_get(key: str) -> Optional[str]:
    return get_client().get(key)

def cache_set(key: str, value: Any, ttl: int = 60) -> None:
    if not isinstance(value, str):
        value = json.dumps(value, default=str)
    get_client().setex(key, ttl, value)

def cache_delete_pattern(pattern: str) -> None:
    r = get_client()
    for k in r.scan_iter(pattern):
        r.delete(k)
