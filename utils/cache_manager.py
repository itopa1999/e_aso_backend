from django.core.cache import cache
from django.conf import settings

CACHE_TTL = getattr(settings, "CACHE_TTL", 60 * 60 * 24)  # 15 min fallback


class GlobalCache:
    @staticmethod
    def get(key):
        """Fetch cached data by key"""
        return cache.get(key)

    @staticmethod
    def set(key, value, timeout=CACHE_TTL):
        """Store data globally"""
        cache.set(key, value, timeout)

    @staticmethod
    def delete(key):
        """Delete a single cache key"""
        cache.delete(key)

    @staticmethod
    def clear():
        """Clear all cache data (GLOBAL CLEAR)"""
        cache.clear()
        return True

    @staticmethod
    def delete_prefix(prefix: str):
        """
        Delete all cache keys starting with a given prefix.
        Works with Redis and LocMemCache (if keys() supported).
        """
        pattern = f"{prefix}*"
        try:
            # For RedisCache (supports delete_pattern)
            if hasattr(cache, "delete_pattern"):
                cache.delete_pattern(pattern)
            # For caches that expose .keys() (like LocMemCache)
            elif hasattr(cache, "keys"):
                for key in cache.keys(pattern):
                    cache.delete(key)
            else:
                # fallback: do a full clear if prefix filtering isn't supported
                cache.clear()
                print(f"⚠️ Cache backend doesn't support prefix delete — cleared all cache.")
            return True
        except Exception as e:
            print(f"⚠️ Failed to delete prefix '{prefix}' from cache: {e}")
            return False