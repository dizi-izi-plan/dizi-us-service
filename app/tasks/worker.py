import random
import uuid
from pydantic import EmailStr

from app.core.redis_conf import broker, redis_service
from app.core.logger import get_logger
from app.core.security import create_verification_token
from app.database.db import new_session
from app.repo.user import UserRepository
from app.service.mail import mail_service

logger = get_logger(__name__)


@broker.task(task_name="send_verification_email")
async def send_verification_email(email: EmailStr):
    code = str(random.randint(100000, 999999))
    await redis_service.set_verification_code(email, code)
    await mail_service.send_verification_code(email, code)
    logger.info(f"V1: Verification code sent to {email}")


@broker.task(task_name="confirm_email_task")
async def confirm_email_task(email: EmailStr):
    await redis_service.delete(f"auth:code:{email}")

    async with new_session() as session:
        repo = UserRepository(session)
        if await repo.confirm_user_by_email(email):
            await redis_service.delete(f"auth:code:{email}")
            logger.info(f"V1: User {email} confirmed")
        else:
            logger.error(f"V1: User {email} not found")


@broker.task(task_name="send_verification_email_v2")
async def send_verification_email_v2(email: EmailStr, user_id: uuid.UUID):
    token = create_verification_token(str(user_id))
    verification_url = f"http://localhost/api/v2/auth/verify?token={token}"

    await mail_service.send_verification_link(email, verification_url)
    logger.info(f"V2: Verification link sent to {email}")


@broker.task(task_name="confirm_email_task_v2")
async def confirm_email_task_v2(user_id: str):
    async with new_session() as session:
        repo = UserRepository(session)
        if await repo.confirm_user_by_id(user_id):
            logger.info(f"V2: User ID {user_id} confirmed")
        else:
            logger.error(f"V2: User ID {user_id} not found")
