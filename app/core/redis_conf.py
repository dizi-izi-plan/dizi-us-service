from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

import json
from typing import Any, Optional, Type, TypeVar

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

broker = ListQueueBroker(settings.redis.broker_url)
result_backend = RedisAsyncResultBackend(settings.redis.result_backend_url)


T = TypeVar("T")


class RedisService:
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    async def init(self) -> None:
        if self.client is None:
            self.client = aioredis.from_url(
                settings.redis.broker_url,
                decode_responses=True
            )
            logger.info("Redis connection established")

    async def close(self) -> None:
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")

    def _ensure_client(self) -> None:
        if self.client is None:
            raise RuntimeError("Redis client is not initialized")

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ) -> None:
        self._ensure_client()

        try:
            data = json.dumps(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Value for key '{key}' is not JSON serializable") from e

        await self.client.set(name=key, value=data, ex=expire)

    async def get(self, key: str) -> Any:
        self._ensure_client()

        data = await self.client.get(key)
        if data is None:
            return None

        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupted JSON in Redis for key '{key}'") from e

    async def get_typed(self, key: str, expected_type: Type[T]) -> Optional[T]:
        value = await self.get(key)

        if value is None:
            return None

        if not isinstance(value, expected_type):
            raise TypeError(
                f"Invalid type for key '{key}': "
                f"expected {expected_type}, got {type(value)}"
            )

        return value

    async def delete(self, key: str) -> None:
        self._ensure_client()
        await self.client.delete(key)

    async def set_verification_code(
        self,
        email: str,
        code: str,
        ttl: int = 300
    ) -> None:
        key = f"auth:code:v1:{email}"
        await self.set(key, code, expire=ttl)

    async def get_verification_code(self, email: str) -> Optional[str]:
        key = f"auth:code:v1:{email}"
        return await self.get_typed(key, str)


redis_service = RedisService()
