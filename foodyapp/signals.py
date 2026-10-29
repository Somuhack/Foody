# yourapp/signals.py

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

@receiver(user_logged_in)
def send_login_notification(sender, request, user, **kwargs):
    # Ensure the user has an email address registered
    if not user.email:
        return

    subject = "Security Alert: Successful Login to Your Account"
    
    # Get user IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    
    # Get user browser/agent
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown device')
    time_now = timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    message = f"""Hi {user.username},

We detected a successful login to your account.

Details:
- Date & Time: {time_now}
- IP Address: {ip}
- Device/Browser: {user_agent}

If this was you, you can safely ignore this email.
If you did NOT log in, please reset your password immediately.

Best regards,
Your Security Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,  # Prevents login crashes if the mail server fails
    )