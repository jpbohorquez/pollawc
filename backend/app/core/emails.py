import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

def get_mail_config():
    return ConnectionConfig(
        MAIL_USERNAME=os.getenv("SMTP_USER", "dummy"),
        MAIL_PASSWORD=os.getenv("SMTP_PASSWORD", "dummy"),
        MAIL_FROM=os.getenv("EMAILS_FROM_EMAIL", "onboarding@resend.dev"),
        MAIL_PORT=int(os.getenv("SMTP_PORT", 465)),
        MAIL_SERVER=os.getenv("SMTP_HOST", "smtp.dummy.com"),
        MAIL_FROM_NAME=os.getenv("EMAILS_FROM_NAME", "Polla WC26"),
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

async def send_reset_password_email(email_to: str, token: str):
    """
    Envía un correo con el token de recuperación de contraseña.
    En este modo 'interno', el correo siempre se envía al ADMIN_EMAIL, 
    especificando qué usuario lo solicitó.
    """
    # Se obtienen las variables de entorno en el momento de la ejecución
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-w-md: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
        <h2 style="color: #15803d; text-align: center;">Polla WC26 - Recuperación (Modo Interno)</h2>
        <p><strong>⚠️ ATENCIÓN ADMIN:</strong></p>
        <p>El usuario con correo <strong>{email_to}</strong> ha solicitado restablecer su contraseña.</p>
        <p>Por favor, envíale el siguiente código de seguridad:</p>
        <div style="background-color: #f3f4f6; padding: 15px; text-align: center; border-radius: 5px; font-size: 24px; font-family: monospace; letter-spacing: 2px; font-weight: bold; margin: 20px 0;">
            {token}
        </div>
        <p>Este código expirará en 1 hora.</p>
    </div>
    """

    message = MessageSchema(
        subject=f"Token de Recuperación para: {email_to}",
        recipients=[admin_email],
        body=html_content,
        subtype=MessageType.html
    )

    try:
        fm = FastMail(get_mail_config())
        await fm.send_message(message)
        print(f"[EMAIL SUCCESS] Correo de recuperación de {email_to} redirigido al admin ({admin_email})")
    except Exception as e:
        print(f"[EMAIL ERROR] Fallo al enviar correo redirigido de {email_to}: {str(e)}")
