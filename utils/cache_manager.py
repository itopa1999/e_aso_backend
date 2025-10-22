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
