from flask_caching import Cache as FlaskCache
import flask
from tenjin.tasks.rq_task import create_task


class Cache:
    cache: FlaskCache = None

    @classmethod
    def get_cache(cls) -> FlaskCache:
        if not cls.cache:
            cls.init_cache(flask.current_app)
        return cls.cache

    @classmethod
    def init_cache(cls, app):
        use_redis = app.config.get("REDIS_QUEUE_ENABLED")
        if use_redis:
            redis_config = {
                "CACHE_TYPE": "RedisCache",
                "CACHE_REDIS_URL": app.config.get("REDIS_URL")

            }
        else:
            redis_config = {
                "CACHE_TYPE": "SimpleCache",
            }
        cache_key_prefix = app.config.get("REDIS_DB", "fm_cache_")
        redis_config.update({
            "CACHE_DEFAULT_TIMEOUT": 60,
            "CACHE_KEY_PREFIX": cache_key_prefix
        })
        cache = FlaskCache(app, config=redis_config)
        if app.config.get("DEV_SESSION"):
            try:
                cache.clear()
            except:
                pass
        cls.cache = cache
        
    @staticmethod
    def set_many(key_value_pairs, timeout=60):

        cache = Cache.get_cache()
        cache.set_many(key_value_pairs, timeout)

        
