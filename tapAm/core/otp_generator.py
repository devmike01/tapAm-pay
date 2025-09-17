import uuid
from threading import Thread

from django.template.loader import render_to_string
from django.utils import timezone
from core.strings import signup_otp_msg
from django.core.mail import send_mail
from django.utils.html import strip_tags
from onboarding.models import EmailOtpValidation

from tapAm import settings


def get_otp():
    return uuid.uuid4().hex[0:4]


def get_session_meeting_id():
    return uuid.uuid4().hex[0:10]


def send_new_email(to_email: str, title: str, msg: str):
    html_message = render_to_string('email/booking_request.html', {'context': 'values'})
    plain_message = strip_tags(html_message)
    from_email = 'From <from@example.com>'
    to = 'to@example.com'

    send_mail(
        title,
        plain_message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False,
        html_message=html_message,
    )


def _do_send_otp(user):
    email_otp = get_otp()
    EmailOtpValidation.objects.create(otp=email_otp,
                                      expired_at=timezone.now() + timezone.timedelta(
                                          minutes=5),
                                      cust_profile=user)
    print('email_otp', email_otp)
    send_new_email(user.email, "Timney Signup OTP", signup_otp_msg.format(email_otp))


def send_otp_email(user):
    thread = Thread(target=_do_send_otp, args=user)
    thread.run()
