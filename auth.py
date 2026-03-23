""" auth.py â Authentication: login, logout, session restore, user creation, welcome email. """
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import streamlit as st
from config import sb, sb_admin, logger


# ââ Session state initialisation ââââââââââââââââââââââââââââââââââââââââââââââ
def init_auth() -> None:
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if st.session_state.user is None:
        try_restore_session()


# ââ Core auth functions ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def login(email: str, password: str):
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        if res.session:
            st.session_state['_access_token'] = res.session.access_token
            st.session_state['_refresh_token'] = res.session.refresh_token
        profile = sb.table('user_profiles').select('*').eq('id', res.user.id).execute()
        if profile.data:
            if not profile.data[0].get('is_active', True):
                st.session_state.user = None
                return False, "Conta desativada. Entre em contato com o administrador."
            st.session_state.user_profile = profile.data[0]
        return True, None
    except Exception as e:
        return False, str(e)


def try_restore_session() -> bool:
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
        logger.warning(f"Falha ao restaurar sessÃ£o: {e}")
    return False


def logout() -> None:
    try:
        sb.auth.sign_out()
    except Exception as e:
        logger.warning(f"Erro ao sair: {e}")
    st.session_state.user = None
    st.session_state.user_profile = None
    for k in ['_access_token', '_refresh_token']:
        st.session_state.pop(k, None)


def is_admin() -> bool:
    return bool(
        st.session_state.user_profile
        and st.session_state.user_profile.get('role') == 'admin'
    )


# ââ Welcome email ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def send_welcome_email(to_email: str, user_name: str, temp_password: str, app_url: str = ""):
    try:
        smtp_host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(st.secrets.get("SMTP_PORT", 587))
        smtp_user = st.secrets.get("SMTP_USER", "")
        smtp_pass = st.secrets.get("SMTP_PASS", "")
        if not smtp_user or not smtp_pass:
            return False, "SMTP nÃ£o configurado. Adicione SMTP_USER e SMTP_PASS nos secrets."
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = "Bem-vindo ao IntegrityMeter BI â Suas Credenciais"
        btn_html = (
            f'<p style="margin:15px 0 5px;text-align:center;">'
            f'<a href="{app_url}" style="background-color:#8DAE10;color:#ffffff;'
            f'padding:12px 30px;border-radius:8px;text-decoration:none;'
            f'font-weight:600;font-size:16px;display:inline-block;">Acessar a Plataforma</a></p>'
            if app_url else ''
        )
        html_body = f"""
<html><body style="font-family:'Inter',Arial,sans-serif;background:#f8fafc;padding:20px;">
<div style="max-width:600px;margin:0 auto;background:white;border-radius:16px;
            padding:40px;border:1px solid #e2e8f0;">
  <div style="text-align:center;margin-bottom:30px;">
    <h1 style="color:#8DAE10;margin:0;">IntegrityMeter BI</h1>
    <p style="color:#6B7280;font-size:14px;">Plataforma de GestÃ£o de Margem</p>
  </div>
  <h2 style="color:#1F2937;">OlÃ¡, {user_name}!</h2>
  <p style="color:#374151;line-height:1.6;">
    Sua conta foi criada na plataforma IntegrityMeter BI.
    Abaixo estÃ£o suas credenciais de acesso:
  </p>
  <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;
              padding:20px;margin:20px 0;">
    <p style="margin:5px 0;color:#1F2937;"><strong>E-mail:</strong> {to_email}</p>
    <p style="margin:5px 0;color:#1F2937;">
      <strong>Senha temporÃ¡ria:</strong> {temp_password}
    </p>
    {btn_html}
  </div>
  <div style="background:#fff7ed;border:1px solid #fdba74;border-radius:10px;
              padding:15px;margin:20px 0;">
    <p style="color:#9a3412;margin:0;font-weight:600;">
      Importante: Altere sua senha no primeiro acesso!
    </p>
    <p style="color:#9a3412;margin:5px 0 0;font-size:13px;">
      ApÃ³s fazer login, vÃ¡ ao Painel e clique em "Alterar Senha" na barra lateral.
    </p>
  </div>
  <p style="color:#374151;line-height:1.6;">
    Em anexo vocÃª encontra o Manual do UsuÃ¡rio com instruÃ§Ãµes detalhadas.
  </p>
  <div style="text-align:center;margin-top:30px;padding-top:20px;
              border-top:1px solid #e2e8f0;">
    <p style="color:#9CA3AF;font-size:12px;">
      IntegrityMeter BI â GestÃ£o de Margem e Pipeline de Vendas
    </p>
  </div>
</div>
</body></html>
"""
        msg.attach(MIMEText(html_body, 'html'))
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


# ââ Login screen âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def render_login() -> None:
    """Render a full two-panel login screen."""

    st.markdown("""
<style>
/* Remove Streamlit default padding on login page */
[data-testid="stAppViewContainer"] > .main > div:first-child {
    padding-top: 2rem !important;
}
[data-testid="stSidebar"] { display: none !important; }

/* Brand panel */
.login-brand {
    background: linear-gradient(155deg, #8DAE10 0%, #5a7a00 100%);
    border-radius: 20px;
    padding: 52px 44px;
    min-height: 520px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    color: white;
}
.login-brand h1 {
    color: white;
    font-size: 30px;
    font-weight: 700;
    margin: 0 0 6px 0;
    line-height: 1.2;
}
.login-brand .tagline {
    color: rgba(255,255,255,0.88);
    font-size: 15px;
    margin: 0 0 36px 0;
    line-height: 1.5;
}
.login-feature {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin: 14px 0;
}
.login-feature-icon {
    font-size: 18px;
    flex-shrink: 0;
    margin-top: 1px;
}
.login-feature-text {
    color: rgba(255,255,255,0.9);
    font-size: 14px;
    line-height: 1.4;
}
.login-footer {
    margin-top: 44px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.25);
    color: rgba(255,255,255,0.6);
    font-size: 12px;
}

/* Form panel spacing */
.login-form-wrap {
    padding: 12px 8px;
}
.login-form-wrap h2 {
    font-size: 26px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 4px;
}
.login-form-wrap .subtitle {
    color: #6B7280;
    font-size: 14px;
    margin-bottom: 28px;
}
</style>
""", unsafe_allow_html=True)

    left, right = st.columns([1, 1], gap="large")

    # ââ Left: branding panel ââââââââââââââââââââââââââââââââââââââââââââââââââ
    with left:
        st.markdown("""
<div class='login-brand'>
  <div style='font-size:48px;margin-bottom:20px;'>ð</div>
  <h1>IntegrityMeter BI</h1>
  <p class='tagline'>Plataforma de GestÃ£o de Margem<br>e Pipeline de Vendas</p>

  <div class='login-feature'>
    <span class='login-feature-icon'>â</span>
    <span class='login-feature-text'>Calcule margens em tempo real com cÃ¢mbio atualizado</span>
  </div>
  <div class='login-feature'>
    <span class='login-feature-icon'>ð</span>
    <span class='login-feature-text'>Acompanhe seu pipeline de vendas por status</span>
  </div>
  <div class='login-feature'>
    <span class='login-feature-icon'>ðµ</span>
    <span class='login-feature-text'>Taxa de cÃ¢mbio USD/BRL em tempo real</span>
  </div>
  <div class='login-feature'>
    <span class='login-feature-icon'>ð¯</span>
    <span class='login-feature-text'>Alertas inteligentes e metas mensais</span>
  </div>
  <div class='login-feature'>
    <span class='login-feature-icon'>ð</span>
    <span class='login-feature-text'>RelatÃ³rios e histÃ³rico de negÃ³cios</span>
  </div>

  <div class='login-footer'>
    Acesso restrito a funcionÃ¡rios da IntegrityMeter
  </div>
</div>
""", unsafe_allow_html=True)

    # ââ Right: form âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    with right:
        st.markdown("<div class='login-form-wrap'>", unsafe_allow_html=True)
        st.markdown("<h2>Entrar na sua conta</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p class='subtitle'>Bem-vindo de volta! Insira suas credenciais abaixo.</p>",
            unsafe_allow_html=True,
        )

        email = st.text_input("E-mail", placeholder="seu@email.com")
        password = st.text_input("Senha", type="password", placeholder="Sua senha")

        if st.button("Entrar", use_container_width=True):
            if email and password:
                success, error = login(email, password)
                if success:
                    st.rerun()
                else:
                    st.error(f"Erro ao entrar: {error}")
            else:
                st.warning("Preencha o e-mail e a senha.")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("Esqueci minha senha"):
            reset_email = st.text_input(
                "Digite seu e-mail para recuperaÃ§Ã£o",
                placeholder="seu@email.com",
                key="reset_email_input",
            )
            if st.button(
                "Enviar link de recuperaÃ§Ã£o",
                key="send_reset_btn",
                use_container_width=True,
            ):
                if reset_email.strip():
                    try:
                        sb.auth.reset_password_for_email(reset_email.strip())
                        st.success(
                            "E-mail de recuperaÃ§Ã£o enviado! Verifique sua caixa de entrada."
                        )
                    except Exception as e:
                        st.error(f"Erro ao enviar e-mail: {e}")
                else:
                    st.warning("Preencha o e-mail.")

        st.markdown("</div>", unsafe_allow_html=True)
