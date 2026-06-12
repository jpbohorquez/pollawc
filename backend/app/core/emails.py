import os
import smtplib
from email.message import EmailMessage

async def send_reset_password_email(email_to: str, token: str):
    """
    Envía un correo con el token de recuperación de contraseña usando smtplib.
    En este modo 'interno', el correo siempre se envía al ADMIN_EMAIL, 
    especificando qué usuario lo solicitó.
    """
    admin_email = os.getenv("ADMIN_EMAIL", "juanbohorquez11@gmail.com")
    from_email = os.getenv("EMAILS_FROM_EMAIL", "onboarding@resend.dev")
    smtp_host = os.getenv("SMTP_HOST", "smtp.resend.com")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    smtp_user = os.getenv("SMTP_USER", "resend")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

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

    msg = EmailMessage()
    msg.set_content("Tu cliente de correo no soporta HTML.")
    msg.add_alternative(html_content, subtype='html')
    
    msg['Subject'] = f"Token de Recuperación para: {email_to}"
    msg['From'] = from_email
    msg['To'] = admin_email

    try:
        if not smtp_password or smtp_password == "dummy":
            print(f"[EMAIL SIMULATION] Correo simulado a {admin_email}. Token: {token}")
            return

        # Si el puerto es 465, usar SMTP_SSL. Si es 587, usar starttls.
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"[EMAIL SUCCESS] Correo de recuperación de {email_to} redirigido al admin ({admin_email})")
    except Exception as e:
        print(f"[EMAIL ERROR] Fallo al enviar correo redirigido de {email_to}: {str(e)}")
