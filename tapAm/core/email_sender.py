import asyncio
import smtplib
import threading

from django.core.mail import send_mail, EmailMultiAlternatives
from django.core import mail
from django.http import BadHeaderError
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from tapAm import settings

from onboarding.models import EmailOtpValidation

from .otp_generator import get_otp
from concurrent.futures import ThreadPoolExecutor

retry_count = 0
executor = ThreadPoolExecutor(max_workers=10)


def send_new_email(to_email: str, title: str, msg: str):
    html_message = render_to_string('email/booking_request.html', {'context': 'values'})
    plain_message = strip_tags(html_message)

    send_mail(
        title,
        plain_message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False,
        html_message=html_message,
    )


def send_booking_email(to_email: str, title: str, context: dict):
    html_message = render_to_string(template_name='email/booking_request.html',
                                    context=context)
    plain_message = strip_tags(html_message)

    send_mail(
        title,
        plain_message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False,
        html_message=html_message,
    )


def send_otp_email(to_email: str, first_name: str, user):
    email_otp = get_otp()
    context = {
        'otp_code': email_otp,
        'user_firstname': first_name
    }
    EmailOtpValidation.objects.create(otp=email_otp,
                                      expired_at=timezone.now() + timezone.timedelta(
                                          minutes=5),
                                      cust_profile=user)

    html_message = render_to_string(template_name='email/otp.html',
                                    context=context)
    plain_message = strip_tags(html_message)

    send_mail(
        "Otp verification",
        plain_message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False,
        html_message=html_message,
    )


def send_session_accepted_email(to_email: str, title: str, context: dict,
                                retry_count=0,
                                template_name='booking_confirmed.html'):
    executor.submit(send_session_accepted_email_async, to_email, title, context, retry_count, template_name)


def send_session_accepted_email_async(to_email: str, title: str, context: dict,
                                      retry_count=0,
                                      template_name='booking_confirmed.html'):
    if retry_count > 6:
        print('Done retrying')
        return
    print('message_to: %s' % to_email)
    html_message = render_to_string(template_name=f'email/{template_name}',
                                    context=context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            title,
            plain_message,
            settings.EMAIL_HOST_USER,
            [to_email],
            fail_silently=False,
            html_message=html_message,
        )
    except smtplib.SMTPServerDisconnected as smtperr:
        print('RETRYING...', 'smtperr', smtperr)
        send_session_accepted_email(to_email, title, context, retry_count + 1, template_name)


def send_session_declined_email(to_email: str, title: str, context: dict):
    html_message = render_to_string(template_name='email/booking_declined.html',
                                    context=context)
    plain_message = strip_tags(html_message)

    send_mail(
        title,
        plain_message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False,
        html_message=html_message,
    )
