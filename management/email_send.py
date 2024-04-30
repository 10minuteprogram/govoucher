from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html
from django.conf import settings

def send_email_from_db(subject, to_email, template_name, file_paths=[]):
    try:
        # Retrieve HTML template string from the database based on template_name
        # Assuming you have a Template model with a field 'html_content'
        html_template = template_name

        from_email = settings.EMAIL_HOST_USER
        formatted_from = format_html('10 Minute Program <{}>', from_email)

        # Create the email message
        email = EmailMultiAlternatives(
            subject=subject,
            body="",  # No need for body as we're sending HTML content
            from_email=formatted_from,
            to=to_email
        )

        # Attach the HTML content
        email.attach_alternative(html_template, "text/html")

        # Attach files if any
        for file_path in file_paths:
            email.attach_file(file_path)

        # Send the email
        email.send()

        return {
            "status": "sent",
            "message": "Email sent successfully"
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }
