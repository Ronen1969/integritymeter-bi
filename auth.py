"""
auth.py — Authentication: login, logout, session restore, user creation, welcome email.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import streamlit as st

from config import sb, sb_admin, logger


# ── Session state initialisation ────────────────────────────────────────────

def init_auth() -> None:
    """Initialise auth-related session state keys and try to restore session."""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if st.session_state.user is None:
        try_restore_session()


# ── Core auth functions ──────────────────────────────────────────────────────

def login(email: str, password: str):
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        if res.session:
            st.session_state['_access_token']  = res.session.access_token
            st.session_state['_refresh_token'] = res.session.refresh_token
        profile = sb.table('user_profiles').select('*').eq('id', res.user.id).execute()
        if profile.data:
            if not profile.data[0].get('is_active', True):
                st.session_state.user = None
                return False, "Conta desativada. Contate o administrador."
            st.session_state.user_profile = profile.data[0]
        return True, None
    except Exception as e:
        return False, str(e)


def try_restore_session() -> bool:
    """Try to restore a persisted Supabase session on page reload."""
    try:
        session = sb.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user
            profile = sb.table('user_profiles').select('*').eq('id', session.user.id).execute()
            if profile.data:
                if not profile.data[0].get('is_active', True):
                    st.session_state.user = None
                    return False
                st.session_state.user_profile = profile.data[0]
            return True
    except Exception as e:
        logger.warning(f"Session restore failed: {e}")
    return False


def logout() -> None:
    try:
        sb.auth.sign_out()
    except Exception as e:
        logger.warning(f"Sign out error: {e}")
    st.session_state.user = None
    st.session_state.user_profile = None
    for k in ['_access_token', '_refresh_token']:
        st.session_state.pop(k, None)


def is_admin() -> bool:
    return bool(
        st.session_state.user_profile
        and st.session_state.user_profile.get('role') == 'admin'
    )


# ── Welcome email ────────────────────────────────────────────────────────────

def send_welcome_email(to_email: str, user_name: str, temp_password: str, app_url: str = ""):
    """Send a welcome email with credentials to a newly created user."""
    try:
        smtp_host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(st.secrets.get("SMTP_PORT", 587))
        smtp_user = st.secrets.get("SMTP_USER", "")
        smtp_pass = st.secrets.get("SMTP_PASS", "")

        if not smtp_user or not smtp_pass:
            return False, "SMTP não configurado. Adicione SMTP_USER e SMTP_PASS nos secrets."

        msg = MIMEMultipart()
        msg['From']    = smtp_user
        msg['To']      = to_email
        msg['Subject'] = "Bem-vindo ao IntegrityMeter BI - Suas Credenciais"

        btn_html = (
            f'<p style="margin:15px 0 5px;text-align:center;">'
            f'<a href="{app_url}" style="background-color:#8DAE10;color:#ffffff;'
            f'padding:12px 30px;border-radius:8px;text-decoration:none;'
            f'font-weight:600;font-size:16px;display:inline-block;">Acessar Plataforma</a></p>'
            if app_url else ''
        )

        html_body = f"""
        <html><body style="font-family:'Inter',Arial,sans-serif;background:#f8fafc;padding:20px;">
        <div style="max-width:600px;margin:0 auto;background:white;border-radius:16px;
                    padding:40px;border:1px solid #e2e8f0;">
            <div style="text-align:center;margin-bottom:30px;">
                <h1 style="color:#8DAE10;margin:0;">IntegrityMeter BI</h1>
                <p style="color:#6B7280;font-size:14px;">Plataforma de Gestão de Margem</p>
            </div>
            <h2 style="color:#1F2937;">Olá, {user_name}!</h2>
            <p style="color:#374151;line-height:1.6;">
                Sua conta foi criada na plataforma IntegrityMeter BI.
                Abaixo estão suas credenciais de acesso:
            </p>
            <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;
                        padding:20px;margin:20px 0;">
                <p style="margin:5px 0;color:#1F2937;"><strong>Email:</strong> {to_email}</p>
                <p style="margin:5px 0;color:#1F2937;">
                    <strong>Senha temporária:</strong> {temp_password}
                </p>
                {btn_html}
            </div>
            <div style="background:#fff7ed;border:1px solid #fdba74;border-radius:10px;
                        padding:15px;margin:20px 0;">
                <p style="color:#9a3412;margin:0;font-weight:600;">
                    Importante: Altere sua senha no primeiro acesso!
                </p>
                <p style="color:#9a3412;margin:5px 0 0;font-size:13px;">
                    Após fazer login, vá em Dashboard e clique em "Alterar Senha" na barra lateral.
                </p>
            </div>
            <p style="color:#374151;line-height:1.6;">
                Em anexo você encontra o Manual do Usuário com instruções detalhadas.
            </p>
            <div style="text-align:center;margin-top:30px;padding-top:20px;
                        border-top:1px solid #e2e8f0;">
                <p style="color:#9CA3AF;font-size:12px;">
                    IntegrityMeter BI - Gestão de Margem e Pipeline
                </p>
            </div>
        </div>
        </body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        # Attach PDF manual if it exists
        for path in [
            os.path.expanduser("~/Desktop/IntegrityMeter_Manual.pdf"),
            "/mount/src/integritymeter-bi/IntegrityMeter_Manual.pdf",
        ]:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    pdf = MIMEApplication(f.read(), _subtype='pdf')
                    pdf.add_header('Content-Disposition', 'attachment',
                                   filename='IntegrityMeter_Manual.pdf')
                    msg.attach(pdf)
                break

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())

        return True, None
    except Exception as e:
        return False, str(e)


# ── Login screen ─────────────────────────────────────────────────────────────

def render_login() -> None:
    """Render the login screen. Call st.stop() after this if user is not logged in."""
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png')
        if not os.path.exists(logo_path):
            logo_path = os.path.expanduser("~/Desktop/integrity-meter-logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=250)
        else:
            st.markdown("## IntegrityMeter BI")

        st.markdown("### Entrar")
        email    = st.text_input("Email", placeholder="seu@email.com")
        password = st.text_input("Senha", type="password", placeholder="Sua senha")

        if st.button("Entrar", use_container_width=True):
            if email and password:
                success, error = login(email, password)
                if success:
                    st.rerun()
                else:
                    st.error(f"Falha no login: {error}")
            else:
                st.warning("Preencha email e senha.")

        with st.expander("Esqueci minha senha"):
            reset_email = st.text_input(
                "Digite seu email para recuperação",
                placeholder="seu@email.com",
                key="reset_email_input",
            )
            if st.button("Enviar link de recuperação", key="send_reset_btn", use_container_width=True):
                if reset_email.strip():
                    try:
                        sb.auth.reset_password_for_email(reset_email.strip())
                        st.success("Email de recuperação enviado! Verifique sua caixa de entrada.")
                    except Exception as e:
                        st.error(f"Erro ao enviar email: {e}")
                else:
                    st.warning("Preencha o email.")

        st.caption("Acesso restrito a funcionários da IntegrityMeter.")
