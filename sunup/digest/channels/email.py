from django.core.mail import send_mail
from django.conf import settings

from .base import NotificationChannel


class EmailChannel(NotificationChannel):
    """Доставка через email (SMTP)"""

    def send(self, user, message: str) -> bool:
        if not user.email:
            return False
        try:
            send_mail(
                subject='☀️ Ваш утренний дайджест SunUp',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"ОШИБКА ОТПРАВКИ EMAIL: {type(e).__name__}: {e}")
            return False