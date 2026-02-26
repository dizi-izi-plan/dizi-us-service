import datetime
import email.message
import aiosmtplib
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class MailService:

    @staticmethod
    async def _send_mail(message: email.message.EmailMessage, recipient: str):
        try:
            await aiosmtplib.send(
                message,
                hostname=settings.mail.server,
                port=settings.mail.port,
                username=settings.mail.username,
                password=settings.mail.password,
                use_tls=settings.mail.tls,
            )
            logger.info(f"Email sent to {recipient}")
        except Exception as e:
            logger.error(f"Mail error for {recipient}: {e}")
            raise e

    async def send_verification_code(self, recipient: str, code: str):
        message = email.message.EmailMessage()
        message["From"] = settings.mail.username
        message["To"] = recipient
        message["Subject"] = "Подтверждение регистрации"
        message.set_content(f"Ваш код подтверждения: {code}")

        await self._send_mail(message, recipient)

    async def send_verification_link(self, recipient: str, url: str):
        message = email.message.EmailMessage()
        message["From"] = settings.mail.username
        message["To"] = recipient
        message["Subject"] = "Подтверждение регистрации"
        message.set_content(
            f"Для подтверждения регистрации перейдите по ссылке:\n\n{url}"
        )

        await self._send_mail(message, recipient)

    async def send_subscription_activation(
            self,
            recipient: str,
            tariff_name: str,
            end_date: datetime.datetime
    ):
        formatted_date = end_date.strftime("%d.%m.%Y")
        message = email.message.EmailMessage()
        message["From"] = settings.mail.username
        message["To"] = recipient
        message["Subject"] = "Подписка активирована"

        content = (
            f"Здравствуйте!\n\n"
            f"Ваша подписка по тарифу «{tariff_name}» "
            f"активирована и действует с текущего момента.\n"
            f"Дата окончания действия: {formatted_date}.\n\n"
            f"Спасибо, что выбрали наш сервис!"
        )
        message.set_content(content)

        await self._send_mail(message, recipient)


mail_service = MailService()
