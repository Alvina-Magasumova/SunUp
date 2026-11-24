from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


def send_verification_email(request, user):
    # Генерируем токен
    token = user.generate_verification_token()

    # Строим ссылку. request.build_absolute_uri нужен, чтобы получить полный адрес (http://...)
    verify_url = request.build_absolute_uri(
        reverse('verify-email') + f'?token={token}'
    )

    subject = 'Подтвердите ваш email в SunUp'
    message = f'''
    Здравствуйте, {user.username}!

    Спасибо за регистрацию в SunUp.
    Пожалуйста, подтвердите ваш email, перейдя по ссылке:

    {verify_url}

    Ссылка действительна в течение 24 часов.
    '''

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )