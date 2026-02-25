import random
import uuid
from pydantic import EmailStr

from app.core.redis_conf import broker, redis_service
from app.core.logger import logger
from app.database.db import new_session
from app.repo.user import UserRepository
from app.service.mail import mail_service


@broker.task(task_name="send_verification_email")
async def send_verification_email(email: EmailStr, user_id: uuid.UUID):
    logger.info(f"Processing verification for user {user_id}")

    # 1. Генерация и сохранение кода в Redis
    code = str(random.randint(100000, 999999))
    await redis_service.set_verification_code(email, code)

    # 2. Отправка письма
    await mail_service.send_verification_code(email, code)

    logger.info(f"Verification process completed for {email}")


@broker.task(task_name="confirm_email_task")
async def confirm_email_task(email: EmailStr):
    # 1. Удаление кода из кеша
    await redis_service.delete(f"auth:code:{email}")

    # 2. Обновление статуса в БД
    async with new_session() as session:
        repo = UserRepository(session)
        user = await repo.get_by_email(email)

        if user:
            user.confirmed = True
            await session.commit()
            logger.info(f"User {email} confirmed")
        else:
            logger.error(f"User {email} not found for confirmation")
