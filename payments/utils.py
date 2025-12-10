from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


def send_card_verification_code(user_email, code):
    subject = "Your Suresave Card Verification Code"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color:#f5f7fa; padding: 30px;">
        <div style="max-width: 500px; margin: auto; background:white; padding:25px; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
            
            <h2 style="text-align:center; color:#0d6efd; margin-bottom:10px;">
                🔐 Suresave Card Verification
            </h2>
            
            <p style="font-size:15px; color:#333;">
                Hi {user_email},  
                <br><br>
                To verify your card, please enter the one-time verification code below:
            </p>

            <div style="text-align:center; margin:25px 0;">
                <p style="
                    font-size:32px; 
                    letter-spacing:8px; 
                    font-weight:bold; 
                    color:#0d6efd; 
                    padding:12px 0;
                ">
                    {code}
                </p>
            </div>

            <p style="font-size:14px; color:#555;">
                This code will expire in <strong>10 minutes</strong>.  
                If you did not request this, you can safely ignore this message.
            </p>

            <hr style="margin:30px 0; border:none; border-top:1px solid #eee;">

            <p style="font-size:12px; text-align:center; color:#999;">
                © {2025} Suresave. All rights reserved.
            </p>
        </div>
    </div>
    """

    # Fallback plain text for email clients that don’t show HTML
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject,
        text_content,
        "Suresave <noreply@suresave.com>",
        [user_email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()
