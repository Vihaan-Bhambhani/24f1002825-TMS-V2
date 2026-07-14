import json
import redis

# Redis connection for caching
cache = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

DEFAULT_TTL = 300  # 5 minutes


def cache_get(key):
    """Get a cached value by key. Returns parsed JSON or None."""
    data = cache.get(key)
    if data:
        return json.loads(data)
    return None


def cache_set(key, value, ttl=DEFAULT_TTL):
    """Cache a value as JSON with a TTL (seconds)."""
    cache.setex(key, ttl, json.dumps(value))


def cache_delete(pattern):
    """Delete all keys matching a pattern. Use 'treks*' to clear trek cache."""
    keys = cache.keys(pattern)
    if keys:
        cache.delete(*keys)


def cache_clear_all():
    """Clear all app cache."""
    cache.flushdb()
