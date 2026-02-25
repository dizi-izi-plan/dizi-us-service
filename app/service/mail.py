import email.message
import aiosmtplib
from app.core.config import settings
from app.core.logger import logger

class MailService:

    @staticmethod
    async def send_verification_code(recipient: str, code: str):
        message = email.message.EmailMessage()
        message["From"] = settings.mail.username
        message["To"] = recipient
        message["Subject"] = "Код подтверждения регистрации"
        message.set_content(f"Ваш код подтверждения: {code}")

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.mail.server,
                port=settings.mail.port,
                username=settings.mail.username,
                password=settings.mail.password,
                use_tls=settings.mail.tls,
            )
            logger.info(f"Email sent successfully to {recipient}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            raise e

mail_service = MailService()
