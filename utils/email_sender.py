
import textwrap
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

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

    html_message = render_to_string('email_template.html', {
        'greeting_name': greeting_name,
        'message': message,
        'support_footer': support_footer
    })
    html_message = html_message.replace("var(--primary-color)", "#8a4b38") \
                           .replace("var(--secondary-color)", "#e8d0b3") \
                           .replace("var(--accent-color)", "#d4a373") \
                           .replace("var(--dark-color)", "#4a2c2a") \
                           .replace("var(--light-color)", "#f9f5f0")

    # Send email with both plain text and HTML versions
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=fail_silently)

    return True
