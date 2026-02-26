import json
from typing import Any, Optional

import redis.asyncio as aioredis
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

broker = ListQueueBroker(settings.redis.broker_url)
result_backend = RedisAsyncResultBackend(settings.redis.result_backend_url)


class RedisService:
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    async def init(self):
        if self.client is None:
            self.client = aioredis.from_url(
                settings.redis.broker_url,
                decode_responses=True
            )
            logger.info("Redis cache connection established")

    async def close(self):
        if self.client:
            await self.client.close()
            logger.info("Redis cache connection closed")

    async def set(self, key: str, value: Any, expire: int = 300) -> None:
        if not self.client:
            await self.init()

        data = json.dumps(value) if not isinstance(value, str) else value
        await self.client.set(key, data, ex=expire)

    async def get(self, key: str) -> Any:
        if not self.client:
            await self.init()
        data = await self.client.get(key)
        if data is None:
            return None
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data

    async def delete(self, key: str) -> None:
        if not self.client:
            await self.init()
        await self.client.delete(key)

    async def set_verification_code(self, email: str, code: str, ttl: int = 300):
        await self.set(f"auth:code:{email}", code, expire=ttl)

    async def get_verification_code(self, email: str) -> Optional[str]:
        return await self.get(f"auth:code:{email}")


redis_service = RedisService()
