# apps/common/email_utils.py

import textwrap
from django.core.mail import send_mail
from django.conf import settings


def send_custom_email(
    subject: str,
    recipient_email: str,
    message: str = "",
    greeting_name: str = "Valued Customer",
    support_footer: bool = True,
    fail_silently: bool = False
):
    """
    General-purpose helper for sending transactional emails.

    Args:
        subject (str): The email subject.
        recipient_email (str): The recipient's email address.
        message (str): The main message body (without greeting/footer).
        greeting_name (str): Name to personalize greeting.
        support_footer (bool): Whether to append standard support details.
        fail_silently (bool): Whether to suppress exceptions on failure.
    """

    body = textwrap.dedent(f"""
        Dear {greeting_name},

        {message.strip()}
    """)

    if support_footer:
        body += textwrap.dedent("""

            Need help? Contact us:  
            📞 +234 1 700 0000  
            ✉️ support@aso-okemarketplace.ng  

            Preserving Nigeria’s textile heritage,  
            The Aso Oke & Aso Ofi Marketplace Team
        """)

    send_mail(
        subject=subject,
        message=body,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient_email],
        fail_silently=fail_silently,
    )

    return True
