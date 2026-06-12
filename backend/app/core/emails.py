import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

# Configuración SMTP desde variables de entorno
# Si no existen, se usan valores dummy para evitar crashes en desarrollo local
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_USER", "dummy"),
    MAIL_PASSWORD=os.getenv("SMTP_PASSWORD", "dummy"),
    MAIL_FROM=os.getenv("EMAILS_FROM_EMAIL", "soporte@pollawc26.com"),
    MAIL_PORT=int(os.getenv("SMTP_PORT", 465)),
    MAIL_SERVER=os.getenv("SMTP_HOST", "smtp.dummy.com"),
    MAIL_FROM_NAME=os.getenv("EMAILS_FROM_NAME", "Polla WC26"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_reset_password_email(email_to: EmailStr, token: str):
    """
    Envía un correo con el token de recuperación de contraseña.
    """
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-w-md: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
        <h2 style="color: #15803d; text-align: center;">Polla WC26 - Recuperación de Contraseña</h2>
        <p>Hola,</p>
        <p>Hemos recibido una solicitud para restablecer tu contraseña. Si no fuiste tú, puedes ignorar este correo.</p>
        <p>Para crear una nueva contraseña, utiliza el siguiente código de seguridad:</p>
        <div style="background-color: #f3f4f6; padding: 15px; text-align: center; border-radius: 5px; font-size: 24px; font-family: monospace; letter-spacing: 2px; font-weight: bold; margin: 20px 0;">
            {token}
        </div>
        <p>Este código expirará en 1 hora.</p>
        <hr style="border: 0; border-top: 1px solid #e0e0e0; margin: 20px 0;" />
        <p style="font-size: 12px; color: #6b7280; text-align: center;">Este es un mensaje automático, por favor no respondas a este correo.</p>
    </div>
    """

    message = MessageSchema(
        subject="Recuperación de Contraseña - Polla WC26",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html
    )

    try:
        fm = FastMail(conf)
        await fm.send_message(message)
        print(f"[EMAIL SUCCESS] Correo de recuperación enviado a {email_to}")
    except Exception as e:
        print(f"[EMAIL ERROR] Fallo al enviar correo a {email_to}: {str(e)}")
        # En producción podrías querer lanzar una excepción o loggearlo en Sentry
