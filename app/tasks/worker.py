import random
import uuid
from pydantic import EmailStr

from app.core.redis_conf import broker, redis_service
from app.core.logger import get_logger
from app.core.security import create_verification_token
from app.database.db import new_session
from app.repo.subscription import SubscriptionRepository
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
        user_repo = UserRepository(session)
        sub_repo = SubscriptionRepository(session)

        if await user_repo.confirm_user_by_email(email):
            logger.info(f"V1: User {email} confirmed")

            user = await user_repo.get_by_email(email)
            if user:
                subscription = await sub_repo.create_free_subscription(user.id)

                if subscription:
                    logger.info(f"V1: Free subscription assigned to {email}")

                    delay_seconds = int(
                        (subscription.end_date - subscription.start_date).total_seconds()
                    )

                    await deactivate_subscription_task.kiq(
                        str(subscription.id)
                    ).send_with_delay(delay=delay_seconds)

                    logger.info(
                        f"V1: Deactivation scheduled in {delay_seconds}s for sub {subscription.id}"
                    )

                    await mail_service.send_subscription_activation(
                        recipient=email,
                        tariff_name="Бесплатный",
                        end_date=subscription.end_date
                    )
                else:
                    logger.error(f"V1: Failed to assign free subscription for {email}")
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
    user_uuid = uuid.UUID(user_id)

    async with new_session() as session:
        user_repo = UserRepository(session)
        sub_repo = SubscriptionRepository(session)

        if await user_repo.confirm_user_by_id(user_uuid):
            logger.info(f"V2: User ID {user_id} confirmed")

            subscription = await sub_repo.create_free_subscription(user_uuid)

            if subscription:
                logger.info(f"V2: Free subscription assigned to User {user_id}")

                # Планируем автоматическую деактивацию подписки
                delay_seconds = int((subscription.end_date - subscription.start_date).total_seconds())
                await deactivate_subscription_task.kiq(str(subscription.id)).send_with_delay(
                    delay=delay_seconds
                )
                logger.info(f"V2: Deactivation task scheduled in {delay_seconds}s for sub {subscription.id}")

                user = await user_repo.get_by_id(user_uuid)
                if user and user.email:
                    await mail_service.send_subscription_activation(
                        recipient=user.email,
                        tariff_name="Бесплатный",
                        end_date=subscription.end_date
                    )
            else:
                logger.error("V2: Tariff 'Бесплатный' not found in database")
        else:
            logger.error(f"V2: User ID {user_id} not found")


@broker.task(task_name="deactivate_subscription_task")
async def deactivate_subscription_task(subscription_id: str):
    async with new_session() as session:
        sub_repo = SubscriptionRepository(session)

        if await sub_repo.deactivate_subscription(subscription_id):
            logger.info(f"Subscription {subscription_id} has been deactivated by timeout")
        else:
            logger.warning(f"Subscription {subscription_id} not found or already inactive")
