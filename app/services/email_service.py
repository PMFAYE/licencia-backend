import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.core.config import settings


def send_devis_confirmation(
    to_email: str,
    nom_contact: str,
    reference: str,
    offres: List[str],
) -> None:
    """Envoie un email de confirmation après création d'un devis."""

    # Si SMTP non configuré, on log et on skip
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        print(f"[EMAIL] SMTP non configuré — email de confirmation non envoyé pour {reference}")
        return

    offres_html = "".join([f"<li>{o}</li>" for o in offres]) if offres else "<li>Demande générale</li>"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .header {{ background: linear-gradient(135deg, #0f172a, #1e293b); padding: 32px; text-align: center; }}
            .header h1 {{ color: #22c55e; margin: 0; font-size: 28px; }}
            .header p {{ color: #94a3b8; margin: 8px 0 0; font-size: 14px; }}
            .body {{ padding: 32px; }}
            .body h2 {{ color: #1e293b; font-size: 20px; margin-top: 0; }}
            .ref {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px; text-align: center; margin: 24px 0; }}
            .ref span {{ font-size: 24px; font-weight: 700; color: #16a34a; }}
            ul {{ padding-left: 20px; }}
            li {{ color: #475569; margin: 6px 0; }}
            .footer {{ background: #f8fafc; padding: 20px 32px; text-align: center; border-top: 1px solid #e2e8f0; }}
            .footer p {{ color: #94a3b8; font-size: 12px; margin: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Licencia</h1>
                <p>Votre partenaire de gestion sportive</p>
            </div>
            <div class="body">
                <h2>Bonjour {nom_contact},</h2>
                <p>Nous avons bien reçu votre demande de devis. Notre équipe la traitera dans les plus brefs délais.</p>

                <div class="ref">
                    <p style="color: #64748b; margin: 0 0 4px;">Référence de votre devis</p>
                    <span>{reference}</span>
                </div>

                <p><strong>Offre(s) sélectionnée(s) :</strong></p>
                <ul>{offres_html}</ul>

                <p>Un membre de notre équipe vous contactera sous 24h pour discuter de votre projet.</p>
                <p>En attendant, n'hésitez pas à répondre à cet email pour toute question.</p>
            </div>
            <div class="footer">
                <p>© 2026 Licencia — Gestion fédérale sportive intelligente</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"SportivAI — Confirmation de votre demande {reference}"
    msg["From"] = getattr(settings, 'SMTP_FROM', 'noreply@sportivai.com')
    msg["To"] = to_email

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, int(getattr(settings, 'SMTP_PORT', 587))) as server:
            server.starttls()
            smtp_user = getattr(settings, 'SMTP_USER', None)
            smtp_pass = getattr(settings, 'SMTP_PASSWORD', None)
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(msg["From"], to_email, msg.as_string())
        print(f"[EMAIL] Confirmation envoyée à {to_email} pour {reference}")
    except Exception as e:
        print(f"[EMAIL] Erreur lors de l'envoi: {e}")
        raise


def send_invitation_email(
    to_email: str,
    invitation_link: str,
    role: str,
) -> None:
    """Envoie un email d'invitation pour rejoindre la plateforme."""

    if not settings.SMTP_HOST or not settings.SMTP_USER:
        print(f"[EMAIL] SMTP non configuré — invitation non envoyée à {to_email}")
        return

    role_display = role.replace("_", " ").capitalize()

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .header {{ background: linear-gradient(135deg, #0f172a, #1e293b); padding: 32px; text-align: center; }}
            .header h1 {{ color: #22c55e; margin: 0; font-size: 28px; }}
            .header p {{ color: #94a3b8; margin: 8px 0 0; font-size: 14px; }}
            .body {{ padding: 32px; }}
            .body h2 {{ color: #1e293b; font-size: 20px; margin-top: 0; }}
            .cta-container {{ text-align: center; margin: 32px 0; }}
            .cta {{ background: #22c55e; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; display: inline-block; }}
            .footer {{ background: #f8fafc; padding: 20px 32px; text-align: center; border-top: 1px solid #e2e8f0; }}
            .footer p {{ color: #94a3b8; font-size: 12px; margin: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Licencia</h1>
                <p>Invitation à rejoindre la plateforme</p>
            </div>
            <div class="body">
                <h2>Bonjour,</h2>
                <p>Vous avez été invité à rejoindre <strong>Licencia</strong> en tant que <strong>{role_display}</strong>.</p>
                <p>Pour finaliser votre inscription et accéder à votre espace, veuillez cliquer sur le bouton ci-dessous :</p>

                <div class="cta-container">
                    <a href="{invitation_link}" class="cta">Créer mon compte</a>
                </div>

                <p>Ce lien est valable pendant 1 heure.</p>
                <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :</p>
                <p style="font-size: 12px; color: #64748b;">{invitation_link}</p>
            </div>
            <div class="footer">
                <p>© 2026 Licencia — Gestion fédérale sportive intelligente</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Licencia — Invitation à rejoindre la plateforme"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(msg["From"], to_email, msg.as_string())
        print(f"[EMAIL] Invitation envoyée à {to_email}")
    except Exception as e:
        print(f"[EMAIL] Erreur lors de l'envoi de l'invitation: {e}")
        raise
