# authapp/utils.py
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .config import get_verification_url, get_password_reset_url

def send_verification_email(user, token):
    """Send HTML email to verify user account."""
    subject = "✅ Verify Your Email - Admin Dashboard"
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = get_verification_url(uid, token)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .email-card {{ background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 40px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
            .header p {{ margin: 8px 0 0 0; opacity: 0.9; font-size: 14px; }}
            .body {{ padding: 40px 30px; }}
            .body h2 {{ color: #1f2937; font-size: 20px; margin: 0 0 15px 0; }}
            .body p {{ color: #4b5563; line-height: 1.6; margin: 0 0 20px 0; font-size: 14px; }}
            .cta-button {{ display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; transition: transform 0.2s; }}
            .cta-button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4); }}
            .info-box {{ background: #f0fdf4; border-left: 4px solid #10b981; padding: 15px; border-radius: 6px; margin: 20px 0; font-size: 13px; color: #166534; }}
            .footer {{ background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px; }}
            .footer p {{ margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="email-card">
                <div class="header">
                    <h1>✅ Verify Your Email</h1>
                    <p>Admin Dashboard</p>
                </div>
                
                <div class="body">
                    <h2>Welcome {user.username}! 🎉</h2>
                    <p>Thank you for signing up! To complete your registration, please verify your email address by clicking the button below:</p>
                    
                    <center>
                        <a href="{verification_link}" class="cta-button">Verify Email Address</a>
                    </center>
                    
                    <p>Or copy this link if the button doesn't work:</p>
                    <p style="word-break: break-all; background: #f3f4f6; padding: 10px; border-radius: 6px; font-size: 12px; color: #374151;">
                        {verification_link}
                    </p>
                    
                    <div class="info-box">
                        <strong>⏰ Expiration:</strong> This verification link will expire in 24 hours.
                    </div>
                    
                    <div class="info-box">
                        <strong>🔒 Security Tip:</strong> Never share this link with anyone. This is a personal verification link for {user.email}.
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>Didn't sign up?</strong> Ignore this email and your account will not be created.</p>
                    <p>If you have questions, contact our support team.</p>
                    <p>© 2025 Admin Dashboard. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    email = EmailMessage(subject, html_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.content_subtype = "html"
    email.send(fail_silently=False)


def send_password_reset_email(user, token, uid):
    """Send HTML email to reset user password."""
    subject = "🔐 Reset Your Password"
    reset_link = get_password_reset_url(uid, token)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .email-card {{ background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
            .header p {{ margin: 8px 0 0 0; opacity: 0.9; font-size: 14px; }}
            .body {{ padding: 40px 30px; }}
            .body h2 {{ color: #1f2937; font-size: 20px; margin: 0 0 15px 0; }}
            .body p {{ color: #4b5563; line-height: 1.6; margin: 0 0 20px 0; font-size: 14px; }}
            .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; transition: transform 0.2s; }}
            .cta-button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }}
            .info-box {{ background: #f0f9ff; border-left: 4px solid #667eea; padding: 15px; border-radius: 6px; margin: 20px 0; font-size: 13px; color: #1e40af; }}
            .footer {{ background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px; }}
            .footer p {{ margin: 5px 0; }}
            .expires {{ color: #dc2626; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="email-card">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                    <p>Admin Dashboard</p>
                </div>
                
                <div class="body">
                    <h2>Hello {user.username}! 👋</h2>
                    <p>We received a request to reset your password. Click the button below to proceed:</p>
                    
                    <center>
                        <a href="{reset_link}" class="cta-button">Reset Your Password</a>
                    </center>
                    
                    <p>Or copy this link if the button doesn't work:</p>
                    <p style="word-break: break-all; background: #f3f4f6; padding: 10px; border-radius: 6px; font-size: 12px; color: #374151;">
                        {reset_link}
                    </p>
                    
                    <div class="info-box">
                        <strong>⏰ Expiration:</strong> This link will expire in 24 hours for security reasons.
                    </div>
                    
                    <div class="info-box" style="border-left-color: #f59e0b; background: #fffbeb; color: #92400e;">
                        <strong>🔒 Security Tip:</strong> Never share this link with anyone. We will never ask for your password via email.
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>Didn't request this?</strong> Ignore this email and your password will remain unchanged.</p>
                    <p>If you have questions, contact our support team.</p>
                    <p>© 2025 Admin Dashboard. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    email = EmailMessage(subject, html_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.content_subtype = "html"
    email.send(fail_silently=False)


def send_welcome_email(user, raw_password):
    """Send HTML welcome email with credentials."""
    subject = "🎓 Welcome to the Learning Management System!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .email-card {{ background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #198754 0%, #146c43 100%); color: white; padding: 40px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
            .body {{ padding: 40px 30px; }}
            .body h2 {{ color: #1f2937; font-size: 20px; margin: 0 0 15px 0; }}
            .body p {{ color: #4b5563; line-height: 1.6; margin: 0 0 20px 0; font-size: 14px; }}
            .credentials-box {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; border-radius: 10px; margin: 25px 0; }}
            .credential-item {{ display: flex; margin-bottom: 10px; }}
            .label {{ font-weight: 600; width: 100px; color: #6c757d; }}
            .value {{ font-family: monospace; font-size: 16px; color: #198754; font-weight: 700; }}
            .footer {{ background: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="email-card">
                <div class="header">
                    <h1>🎓 Welcome Aboard!</h1>
                </div>
                
                <div class="body">
                    <h2>Hello {user.first_name}! 👋</h2>
                    <p>Your account has been successfully created. You can now log into the LMS using the following credentials:</p>
                    
                    <div class="credentials-box">
                        <div style="margin-bottom: 10px;">
                            <span style="font-weight: 600; color: #6c757d;">Username:</span> 
                            <span style="font-family: monospace; font-weight: 700;">{user.username}</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <span style="font-weight: 600; color: #6c757d;">Email:</span> 
                            <span style="font-family: monospace; font-weight: 700;">{user.email}</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <span style="font-weight: 600; color: #6c757d;">Password:</span> 
                            <span style="color: #198754; font-family: monospace; font-weight: 700;">{raw_password}</span>
                        </div>
                    </div>
                    
                    <p>For security reasons, we recommend that you change your password after your first login.</p>
                </div>
                
                <div class="footer">
                    <p>If you didn't expect this, please contact the administrator.</p>
                    <p>© 2025 Learning Management System. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    email = EmailMessage(subject, html_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.content_subtype = "html"
    email.send(fail_silently=False)
