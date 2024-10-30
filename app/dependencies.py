from app.cache import redis_client

async def get_redis_client():
    return redis_client
