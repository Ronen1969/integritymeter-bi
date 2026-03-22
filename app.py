import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta
from supabase import create_client
import os
import io
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import streamlit.components.v1 as components

# ============================================================
# 1. CONFIG & SUPABASE
# ============================================================
st.set_page_config(page_title="IntegrityMeter BI", layout="wide")

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://nblpirdnqpjvuarjxigm.supabase.co")
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ibHBpcmRucXBqdnVhcmp4aWdtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwMzk2NjUsImV4cCI6MjA4OTYxNTY2NX0.MkQYjG7MoAn3oYCmS65dS4atfLfl0YJ50uJAtL-ggpA")
SUPABASE_SERVICE_KEY = st.secrets.get("SUPABASE_SERVICE_KEY", "")

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@st.cache_resource
def get_supabase_admin():
    if SUPABASE_SERVICE_KEY:
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return None

sb = get_supabase()
sb_admin = get_supabase_admin()

# ============================================================
# 2. DESIGN SYSTEM
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }
[data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #F3F4F6; width: 400px !important; transition: margin-left 0.3s ease, opacity 0.3s ease; }
.stButton>button {
    background-color: #8DAE10 !important; color: white !important;
    border-radius: 10px !important; min-height: 45px; height: auto;
    padding: 10px 20px !important; font-weight: 600 !important;
    border: none !important; white-space: normal !important;
    line-height: 1.4 !important;
}
.main-card { padding: 30px; border-radius: 16px; background-color: #FFFFFF; border: 1px solid #F3F4F6; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.02); }
.sidebar-deal-btn button { font-size: 13px !important; min-height: 36px !important; padding: 6px 12px !important; text-align: left !important; }
.sidebar-del-btn button { background-color: #EF4444 !important; min-height: 36px !important; max-height: 36px !important; padding: 4px 10px !important; font-size: 14px !important; }
.loaded-banner { padding: 10px 16px; border-radius: 8px; background-color: #F0FDF4; border: 1px solid #BBF7D0; color: #166534; font-weight: 500; margin-bottom: 8px; }
.kpi-card { padding: 16px; border-radius: 12px; background: linear-gradient(135deg, #f8fafc, #f1f5f9); border: 1px solid #e2e8f0; text-align: center; }
.kpi-value { font-size: 28px; font-weight: 700; color: #8DAE10; margin: 4px 0; }
.kpi-label { font-size: 11px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; }
.funnel-row { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
.funnel-bar { height: 24px; border-radius: 4px; background: #8DAE10; display: flex; align-items: center; padding: 0 8px; color: white; font-size: 11px; font-weight: 600; }
.user-badge { padding: 6px 12px; border-radius: 20px; background: #F0FDF4; color: #166534; font-size: 12px; font-weight: 600; display: inline-block; margin-bottom: 8px; }
.alert-card { padding: 12px 16px; border-radius: 10px; margin: 6px 0; font-size: 13px; }
.alert-warning { background: #FFF7ED; border: 1px solid #FDBA74; color: #9A3412; }
.alert-danger { background: #FEF2F2; border: 1px solid #FCA5A5; color: #991B1B; }
.alert-info { background: #EFF6FF; border: 1px solid #93C5FD; color: #1E40AF; }
.target-progress { background: #f1f5f9; border-radius: 10px; height: 20px; overflow: hidden; }
.target-bar { height: 100%; border-radius: 10px; display: flex; align-items: center; padding: 0 8px; font-size: 11px; font-weight: 600; color: white; }
.client-rank { display: flex; align-items: center; gap: 12px; padding: 10px; border-radius: 8px; background: #f8fafc; border: 1px solid #e2e8f0; margin: 4px 0; }
.rank-num { font-size: 20px; font-weight: 700; color: #8DAE10; min-width: 30px; }
/* Fix 1: Sidebar toggle button */
.sidebar-toggle-btn button {
    background-color: #f1f5f9 !important; color: #6B7280 !important;
    border: 1px solid #e2e8f0 !important; min-height: 32px !important;
    padding: 4px 12px !important; font-size: 18px !important;
    border-radius: 8px !important;
}
.sidebar-toggle-btn button:hover { background-color: #e2e8f0 !important; }
/* Fix 2: Pipeline delete button */
.pipe-del-btn button {
    background-color: #FEF2F2 !important; color: #EF4444 !important;
    border: 1px solid #FCA5A5 !important; min-height: 32px !important;
    padding: 4px 8px !important; font-size: 12px !important;
}
.pipe-del-btn button:hover { background-color: #EF4444 !important; color: white !important; }
/* Fix 6: Confirmation dialog styling */
.confirm-delete { padding: 12px 16px; border-radius: 10px; background: #FEF2F2; border: 1px solid #FCA5A5; margin: 6px 0; }
.confirm-delete-btns button { min-height: 32px !important; padding: 4px 16px !important; }
</style>
""", unsafe_allow_html=True)

# Fix 5: JavaScript to auto-select number input content on focus
# This prevents the "0.005 instead of 5" problem
st.markdown("""
<script>
document.addEventListener('focusin', function(e) {
    if (e.target && e.target.tagName === 'INPUT' && e.target.type === 'number') {
        setTimeout(function() { e.target.select(); }, 50);
    }
});
</script>
""", unsafe_allow_html=True)

# Alternative JS injection via components for broader browser support
components.html("""
<script>
// Fix 5: Auto-select number inputs on focus so typing replaces the value
const doc = window.parent.document;
doc.addEventListener('focusin', function(e) {
    if (e.target && e.target.tagName === 'INPUT' && e.target.type === 'number') {
        setTimeout(function() { e.target.select(); }, 50);
    }
});

// Fix 4: Session persistence - save/restore auth tokens in localStorage
function saveSession(accessToken, refreshToken, userId) {
    if (accessToken) {
        localStorage.setItem('im_access_token', accessToken);
        localStorage.setItem('im_refresh_token', refreshToken || '');
        localStorage.setItem('im_user_id', userId || '');
    }
}
function clearSession() {
    localStorage.removeItem('im_access_token');
    localStorage.removeItem('im_refresh_token');
    localStorage.removeItem('im_user_id');
}
function getSession() {
    return {
        access_token: localStorage.getItem('im_access_token'),
        refresh_token: localStorage.getItem('im_refresh_token'),
        user_id: localStorage.getItem('im_user_id')
    };
}
// Expose functions globally
window.imSaveSession = saveSession;
window.imClearSession = clearSession;
window.imGetSession = getSession;
</script>
""", height=0)

# ============================================================
# 3. AUTHENTICATION
# ============================================================
if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None

def login(email, password):
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        # Fix 4: Store session tokens for persistence across refreshes
        if res.session:
            st.session_state['_access_token'] = res.session.access_token
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

def try_restore_session():
    """Fix 4: Try to restore session from Supabase's internal session."""
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
    except:
        pass
    return False

def logout():
    try:
        sb.auth.sign_out()
    except:
        pass
    st.session_state.user = None
    st.session_state.user_profile = None
    # Fix 4: Clear stored session tokens
    for k in ['_access_token', '_refresh_token']:
        st.session_state.pop(k, None)

# Fix 4: Try to restore session on page reload
if st.session_state.user is None:
    try_restore_session()

def is_admin():
    return st.session_state.user_profile and st.session_state.user_profile.get('role') == 'admin'

def send_welcome_email(to_email, user_name, temp_password, app_url=""):
    """Send welcome email with credentials to new user."""
    try:
        smtp_host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(st.secrets.get("SMTP_PORT", 587))
        smtp_user = st.secrets.get("SMTP_USER", "")
        smtp_pass = st.secrets.get("SMTP_PASS", "")

        if not smtp_user or not smtp_pass:
            return False, "SMTP não configurado. Adicione SMTP_USER e SMTP_PASS nos secrets."

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = "Bem-vindo ao IntegrityMeter BI - Suas Credenciais"

        html_body = f"""
        <html>
        <body style="font-family: 'Inter', Arial, sans-serif; background-color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; padding: 40px; border: 1px solid #e2e8f0;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #8DAE10; margin: 0;">IntegrityMeter BI</h1>
                    <p style="color: #6B7280; font-size: 14px;">Plataforma de Gestão de Margem</p>
                </div>

                <h2 style="color: #1F2937;">Olá, {user_name}!</h2>

                <p style="color: #374151; line-height: 1.6;">
                    Sua conta foi criada na plataforma IntegrityMeter BI.
                    Abaixo estão suas credenciais de acesso:
                </p>

                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 20px; margin: 20px 0;">
                    <p style="margin: 5px 0; color: #1F2937;"><strong>Email:</strong> {to_email}</p>
                    <p style="margin: 5px 0; color: #1F2937;"><strong>Senha temporária:</strong> {temp_password}</p>
                    {f'<p style="margin: 15px 0 5px; text-align: center;"><a href="{app_url}" style="background-color: #8DAE10; color: #ffffff; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block;">Acessar Plataforma</a></p>' if app_url else ''}
                </div>

                <div style="background: #fff7ed; border: 1px solid #fdba74; border-radius: 10px; padding: 15px; margin: 20px 0;">
                    <p style="color: #9a3412; margin: 0; font-weight: 600;">
                        Importante: Altere sua senha no primeiro acesso!
                    </p>
                    <p style="color: #9a3412; margin: 5px 0 0; font-size: 13px;">
                        Após fazer login, vá em Dashboard e clique em "Alterar Senha" na barra lateral.
                    </p>
                </div>

                <p style="color: #374151; line-height: 1.6;">
                    Em anexo você encontra o Manual do Usuário com instruções
                    detalhadas sobre como usar a plataforma.
                </p>

                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #9CA3AF; font-size: 12px;">IntegrityMeter BI - Gestão de Margem e Pipeline</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        # Attach PDF manual if it exists
        manual_path = os.path.expanduser("~/Desktop/IntegrityMeter_Manual.pdf")
        if not os.path.exists(manual_path):
            manual_path = "/mount/src/integritymeter-bi/IntegrityMeter_Manual.pdf"
        if os.path.exists(manual_path):
            with open(manual_path, 'rb') as f:
                pdf_attach = MIMEApplication(f.read(), _subtype='pdf')
                pdf_attach.add_header('Content-Disposition', 'attachment', filename='IntegrityMeter_Manual.pdf')
                msg.attach(pdf_attach)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())

        return True, None
    except Exception as e:
        return False, str(e)

# --- LOGIN SCREEN ---
if not st.session_state.user:
    col_spacer1, col_login, col_spacer2 = st.columns([1, 1.5, 1])
    with col_login:
        logo_path = os.path.expanduser("~/Desktop/integrity-meter-logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=250)
        else:
            st.markdown("## IntegrityMeter BI")
        st.markdown("### Entrar")
        email = st.text_input("Email", placeholder="seu@email.com")
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
        st.caption("Acesso restrito a funcionários da IntegrityMeter.")
    st.stop()

# ============================================================
# 4. STATUS DEFINITIONS
# ============================================================
STATUS_CONFIG = {
    'proposta_enviada':   {'label': 'Proposta Enviada',   'color': '#6B7280', 'order': 1},
    'em_negociacao':      {'label': 'Em Negociação',      'color': '#3B82F6', 'order': 2},
    'aprovado':           {'label': 'Aprovado',           'color': '#10B981', 'order': 3},
    'contrato_assinado':  {'label': 'Contrato Assinado',  'color': '#8B5CF6', 'order': 4},
    'em_execucao':        {'label': 'Em Execução',        'color': '#F59E0B', 'order': 5},
    'concluido':          {'label': 'Concluído',          'color': '#059669', 'order': 6},
    'perdido':            {'label': 'Perdido',            'color': '#EF4444', 'order': 7},
}
STATUS_LABELS = [v['label'] for v in sorted(STATUS_CONFIG.values(), key=lambda x: x['order'])]
STATUS_KEYS = [k for k in sorted(STATUS_CONFIG, key=lambda x: STATUS_CONFIG[x]['order'])]

def status_key_to_label(key): return STATUS_CONFIG.get(key, {}).get('label', key)
def status_label_to_key(label):
    for k, v in STATUS_CONFIG.items():
        if v['label'] == label: return k
    return 'proposta_enviada'
def status_dot(key):
    """Return a small colored circle HTML span for the status."""
    color = STATUS_CONFIG.get(key, {}).get('color', '#6B7280')
    return f"<span style='display:inline-block;width:10px;height:10px;border-radius:50%;background:{color};margin-right:6px;'></span>"

def status_dot_text(key):
    """Return colored dot + label as plain text (for buttons)."""
    return f"● {STATUS_CONFIG.get(key, {}).get('label', key)}"

# ============================================================
# 5. FX RATE
# ============================================================
def get_live_fx():
    try:
        ticker = yf.Ticker("USDBRL=X")
        rate = float(ticker.fast_info['last_price'])
        try:
            sb.table('fx_snapshots').insert({'rate': rate, 'source': 'yfinance'}).execute()
        except:
            pass
        return rate
    except:
        try:
            res = sb.table('fx_snapshots').select('rate').order('created_at', desc=True).limit(1).execute()
            if res.data: return float(res.data[0]['rate'])
        except:
            pass
        return 5.30

def get_cached_fx():
    try:
        res = sb.table('fx_snapshots').select('rate,created_at').order('created_at', desc=True).limit(1).execute()
        if res.data:
            cached_time = datetime.fromisoformat(res.data[0]['created_at'].replace('Z', '+00:00'))
            if (datetime.now(cached_time.tzinfo) - cached_time).total_seconds() < 900:
                return float(res.data[0]['rate'])
    except:
        pass
    return get_live_fx()

def get_fx_history(days=30):
    """Get FX rate history from snapshots table."""
    try:
        since = (datetime.now() - timedelta(days=days)).isoformat()
        res = sb.table('fx_snapshots').select('rate,created_at').gte('created_at', since).order('created_at').execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['rate'] = df['rate'].astype(float)
            return df
    except:
        pass
    return pd.DataFrame()

# ============================================================
# 6. SESSION STATE
# ============================================================
if 'dolar_live' not in st.session_state:
    st.session_state.dolar_live = get_cached_fx()

FORM_DEFAULTS = {
    'selected_deal_id': None,
    'form_client': '',
    'form_qty': 0,
    'form_cost': 0.0,
    'form_vreal': 0.0,
    'form_status_idx': 0,
    'form_notes': '',
    'just_loaded': False,
}
for key, default in FORM_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default

def clear_form():
    """Schedule form clear for next rerun (avoids widget conflict)."""
    st.session_state['_pending_clear'] = True

def load_deal_to_form(deal):
    """Schedule deal load for next rerun (avoids widget conflict)."""
    st.session_state['_pending_load'] = deal

# --- Process pending form operations BEFORE widgets render ---
if st.session_state.get('_pending_clear', False):
    for key, default in FORM_DEFAULTS.items():
        st.session_state[key] = default
    del st.session_state['_pending_clear']

if '_pending_load' in st.session_state and st.session_state['_pending_load'] is not None:
    _deal = st.session_state['_pending_load']
    _cn = (_deal.get('clients', {}) or {}).get('name', '?')
    st.session_state.form_client = _cn
    st.session_state.form_qty = int(_deal['qty'])
    st.session_state.form_cost = float(_deal['cost_usd'])
    st.session_state.form_vreal = float(_deal['v_real'])
    st.session_state.form_status_idx = STATUS_KEYS.index(_deal['status']) if _deal['status'] in STATUS_KEYS else 0
    st.session_state.form_notes = (_deal.get('clients', {}) or {}).get('notes', '') or ''
    st.session_state.selected_deal_id = _deal['id']
    st.session_state.just_loaded = True
    del st.session_state['_pending_load']

# ============================================================
# 7. LOAD ALL DEALS (used across tabs)
# ============================================================
try:
    deals_res = sb.table('deals').select('*, clients(name, notes)').order('updated_at', desc=True).execute()
    all_deals = deals_res.data or []
except:
    all_deals = []

# ============================================================
# 8. SIDEBAR (Fix 1: collapsible via Streamlit native button)
# ============================================================
# Fix 1: Sidebar collapse/expand hint at top of main area
# Streamlit has a built-in sidebar collapse (arrow button).
# We add an explicit toggle button in the main content area for better discoverability.
if 'sidebar_collapsed' not in st.session_state:
    st.session_state.sidebar_collapsed = False

col_toggle, col_spacer = st.columns([0.08, 0.92])
with col_toggle:
    st.markdown("<div class='sidebar-toggle-btn'>", unsafe_allow_html=True)
    toggle_label = ">" if st.session_state.sidebar_collapsed else "<"
    if st.button(toggle_label, key="sidebar_toggle", help="Ocultar/mostrar barra lateral para maximizar conteúdo"):
        st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Fix 1: Apply CSS to hide sidebar when collapsed
if st.session_state.sidebar_collapsed:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    .main .block-container { max-width: 100% !important; padding-left: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    logo_path = os.path.expanduser("~/Desktop/integrity-meter-logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path)

    user_name = st.session_state.user_profile.get('full_name', '') or st.session_state.user.email
    user_role = st.session_state.user_profile.get('role', 'user')
    role_label = "Admin" if user_role == 'admin' else "Usuário"
    st.markdown(f"<div class='user-badge'>{user_name} ({role_label})</div>", unsafe_allow_html=True)

    col_sair, col_pw = st.columns(2)
    # Fix 6: Logout with confirmation
    if col_sair.button("Sair", key="logout_btn", use_container_width=True):
        st.session_state['_confirm_logout'] = True
    if st.session_state.get('_confirm_logout', False):
        st.warning("Deseja realmente sair?")
        cl1, cl2 = st.columns(2)
        if cl1.button("Sim, sair", key="confirm_logout_yes"):
            st.session_state['_confirm_logout'] = False
            logout()
            st.rerun()
        if cl2.button("Cancelar", key="confirm_logout_no"):
            st.session_state['_confirm_logout'] = False
            st.rerun()
    if col_pw.button("Alterar Senha", key="change_pw_btn", use_container_width=True):
        st.session_state.show_pw_change = not st.session_state.get('show_pw_change', False)

    if st.session_state.get('show_pw_change', False):
        with st.form("change_password_form"):
            new_pw = st.text_input("Nova senha", type="password")
            confirm_pw = st.text_input("Confirmar nova senha", type="password")
            pw_submitted = st.form_submit_button("Salvar Nova Senha")
            if pw_submitted:
                if not new_pw or len(new_pw) < 6:
                    st.error("Senha deve ter pelo menos 6 caracteres.")
                elif new_pw != confirm_pw:
                    st.error("Senhas não conferem.")
                else:
                    try:
                        sb.auth.update_user({"password": new_pw})
                        st.success("Senha alterada com sucesso!")
                        st.session_state.show_pw_change = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

    st.markdown("---")
    st.caption("CÂMBIO EM TEMPO REAL")
    col_v, col_r = st.columns([2, 1])
    col_v.markdown(f"### R$ {st.session_state.dolar_live:.3f}")
    if col_r.button("Att.", help="Atualizar câmbio"):
        old = st.session_state.dolar_live
        st.session_state.dolar_live = get_live_fx()
        st.toast(f"Câmbio: R$ {st.session_state.dolar_live:.3f}" if st.session_state.dolar_live != old else "Câmbio já atualizado.")
        st.rerun()

    st.markdown("---")
    st.subheader("Configurações Fiscais")
    tax_p = st.number_input("Lucro Presumido (%)", value=16.33, min_value=0.0, step=0.5, format="%.2f", key="tax_presumido", help="Alíquota do regime Lucro Presumido — imposto federal sobre o faturamento bruto")
    adm_p = st.number_input("Taxa Administração (%)", value=2.50, min_value=0.0, step=0.5, format="%.2f", key="tax_admin", help="Taxa administrativa cobrada sobre o faturamento para custos operacionais")
    total_tax_pct = tax_p + adm_p
    st.caption(f"Total impostos: **{total_tax_pct:.2f}%**")

    st.markdown("---")
    st.caption("MEUS NEGÓCIOS")
    if st.button("+ Novo Negócio", key="new_deal_btn", use_container_width=True, help="Limpa o formulário e abre a aba Novo Negócio"):
        clear_form()
        st.rerun()  # Form will be cleared on next cycle

    # Search filter for deals
    search_sidebar = st.text_input("Buscar cliente...", key="sidebar_search", placeholder="Nome do cliente")

    filtered_deals = all_deals
    if search_sidebar:
        filtered_deals = [d for d in all_deals if search_sidebar.lower() in ((d.get('clients',{}) or {}).get('name','') or '').lower()]

    if not filtered_deals:
        st.info("Nenhum negócio encontrado." if search_sidebar else "Nenhum negócio salvo.")
    else:
        for deal in filtered_deals:
            cn = deal.get('clients', {}).get('name', '?') if deal.get('clients') else '?'
            sk = deal['status']
            dd = deal['created_at'][:10] if deal.get('created_at') else ''

            col_load, col_del = st.columns([4, 1])
            with col_load:
                st.markdown("<div class='sidebar-deal-btn'>", unsafe_allow_html=True)
                if st.button(f"{status_dot_text(sk)} {cn} | {dd}", key=f"btn_{deal['id']}"):
                    load_deal_to_form(deal)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            with col_del:
                st.markdown("<div class='sidebar-del-btn'>", unsafe_allow_html=True)
                if st.button("X", key=f"del_{deal['id']}", help=f"Excluir {cn}"):
                    try:
                        sb.table('deal_events').delete().eq('deal_id', deal['id']).execute()
                        sb.table('deals').delete().eq('id', deal['id']).execute()
                        if st.session_state.selected_deal_id == deal['id']:
                            clear_form()
                        st.toast(f"Negócio '{cn}' excluído!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")
                st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 9. MAIN TABS
# ============================================================
tab_names = ["Dashboard", "Novo Negócio", "Pipeline", "Relatórios", "Câmbio"]
if is_admin():
    tab_names.append("Admin")
tab_list = st.tabs(tab_names)

# ============================================================
# TAB 0: DASHBOARD
# ============================================================
with tab_list[0]:
    st.header("Painel Principal")

    if not all_deals:
        st.info("Bem-vindo! Comece adicionando seu primeiro negócio na aba 'Novo Negócio' ou clique '+ Novo Negócio' na barra lateral.")
    else:
        df_all = pd.DataFrame(all_deals)
        df_all['client_name'] = df_all['clients'].apply(lambda c: c.get('name', '?') if c else '?')
        for col in ['v_real','profit','margin','cost_usd']: df_all[col] = df_all[col].astype(float)
        df_all['qty'] = df_all['qty'].astype(int)
        df_all['created_at_dt'] = pd.to_datetime(df_all['created_at'], utc=True)

        # Current month filter
        now = pd.Timestamp.now(tz='UTC')
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        df_month = df_all[df_all['created_at_dt'] >= month_start]
        df_active = df_all[~df_all['status'].isin(['concluido','perdido'])]
        df_won = df_all[df_all['status'] == 'concluido']
        df_lost = df_all[df_all['status'] == 'perdido']

        # --- KPIs ---
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        total_pipeline = df_active['v_real'].sum()
        total_won = df_won['v_real'].sum()
        total_profit = df_won['profit'].sum()
        month_deals = len(df_month)
        win_rate = (len(df_won)/(len(df_won)+len(df_lost))*100) if (len(df_won)+len(df_lost))>0 else 0
        avg_margin = df_won['margin'].mean() if not df_won.empty else 0

        for col, lbl, val in [
            (k1, "Pipeline Ativo", f"R$ {total_pipeline:,.0f}"),
            (k2, "Total Ganho", f"R$ {total_won:,.0f}"),
            (k3, "Lucro Total", f"R$ {total_profit:,.0f}"),
            (k4, "Negócios este Mês", str(month_deals)),
            (k5, "Taxa Conversão", f"{win_rate:.0f}%"),
            (k6, "Margem Média", f"{avg_margin:.1f}%"),
        ]:
            col.markdown(f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div><div class='kpi-value'>{val}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Monthly Targets ---
        col_target, col_alerts = st.columns([1, 1], gap="large")

        with col_target:
            st.subheader("Meta Mensal")
            month_target = st.number_input("Meta de Vendas (R$)", value=100000.0, min_value=0.0, step=5000.0, format="%.0f", key="month_target", help="Clique +/- para ajustar em R$ 5.000 ou digite o valor desejado")
            month_won = df_won[df_won['created_at_dt'] >= month_start]['v_real'].sum() if not df_won.empty else 0
            month_profit = df_won[df_won['created_at_dt'] >= month_start]['profit'].sum() if not df_won.empty else 0
            progress_pct = min((month_won / month_target * 100), 100) if month_target > 0 else 0
            bar_color = "#059669" if progress_pct >= 80 else "#D97706" if progress_pct >= 50 else "#DC2626"

            st.markdown(f"""
            <div style='margin: 8px 0;'>
                <div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'>
                    <span>R$ {month_won:,.0f} de R$ {month_target:,.0f}</span>
                    <span style='font-weight:700; color:{bar_color};'>{progress_pct:.0f}%</span>
                </div>
                <div class='target-progress'>
                    <div class='target-bar' style='width:{max(progress_pct, 2)}%; background:{bar_color};'></div>
                </div>
                <div style='font-size:12px; color:#6B7280; margin-top:4px;'>
                    Lucro no mês: <strong>R$ {month_profit:,.0f}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Monthly trend chart
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Tendência Mensal")
            df_all['month'] = df_all['created_at_dt'].dt.to_period('M').astype(str)
            monthly = df_all.groupby('month').agg(
                Vendas=('v_real', 'sum'),
                Lucro=('profit', 'sum'),
                Negócios=('id', 'count')
            ).reset_index()
            monthly.columns = ['Mês', 'Vendas (R$)', 'Lucro (R$)', 'Negócios']
            if len(monthly) > 1:
                st.bar_chart(monthly.set_index('Mês')[['Vendas (R$)', 'Lucro (R$)']])
            else:
                st.dataframe(monthly, use_container_width=True, hide_index=True)

        # --- Alerts ---
        with col_alerts:
            st.subheader("Alertas")
            alerts_found = False

            for deal in all_deals:
                if deal['status'] in ['concluido', 'perdido']:
                    continue
                cn = (deal.get('clients', {}) or {}).get('name', '?')
                created = datetime.fromisoformat(deal['created_at'].replace('Z', '+00:00'))
                age_days = (datetime.now(created.tzinfo) - created).days

                if age_days >= 14:
                    alerts_found = True
                    st.markdown(f"<div class='alert-card alert-danger'><strong>{cn}</strong> — {age_days} dias sem movimentação ({status_key_to_label(deal['status'])})</div>", unsafe_allow_html=True)
                elif age_days >= 7:
                    alerts_found = True
                    st.markdown(f"<div class='alert-card alert-warning'><strong>{cn}</strong> — {age_days} dias parado ({status_key_to_label(deal['status'])})</div>", unsafe_allow_html=True)

            # FX rate alert
            fx = st.session_state.dolar_live
            if fx >= 5.50:
                alerts_found = True
                st.markdown(f"<div class='alert-card alert-warning'>Dólar alto: R$ {fx:.3f} — considere aguardar para fechar custos</div>", unsafe_allow_html=True)
            elif fx <= 4.80:
                alerts_found = True
                st.markdown(f"<div class='alert-card alert-info'>Dólar baixo: R$ {fx:.3f} — bom momento para fechar custos</div>", unsafe_allow_html=True)

            if not alerts_found:
                st.markdown("<div class='alert-card alert-info'>Nenhum alerta no momento. Tudo em dia!</div>", unsafe_allow_html=True)

            # --- Top Clients ---
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Clientes Mais Rentáveis")
            if not df_won.empty:
                client_rank = df_won.groupby('client_name').agg(
                    total_profit=('profit', 'sum'),
                    total_revenue=('v_real', 'sum'),
                    deals=('id', 'count'),
                    avg_margin=('margin', 'mean')
                ).sort_values('total_profit', ascending=False).head(5)

                for i, (name, row) in enumerate(client_rank.iterrows(), 1):
                    st.markdown(f"""<div class='client-rank'>
                        <div class='rank-num'>#{i}</div>
                        <div style='flex:1;'>
                            <div style='font-weight:600;'>{name}</div>
                            <div style='font-size:12px; color:#6B7280;'>{int(row['deals'])} neg. | Margem: {row['avg_margin']:.1f}%</div>
                        </div>
                        <div style='text-align:right;'>
                            <div style='font-weight:700; color:#8DAE10;'>R$ {row['total_profit']:,.0f}</div>
                            <div style='font-size:11px; color:#6B7280;'>de R$ {row['total_revenue']:,.0f}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("Conclua negócios para ver o ranking.")

# ============================================================
# TAB 1: MARGIN CALCULATOR
# ============================================================
with tab_list[1]:
    is_editing = st.session_state.selected_deal_id is not None

    if st.session_state.just_loaded:
        st.markdown(f"""<div class='loaded-banner'>
            Editando negócio: <strong>{st.session_state.form_client}</strong>
            — altere os dados e clique "Atualizar Negócio"
        </div>""", unsafe_allow_html=True)
        st.session_state.just_loaded = False
    elif not is_editing:
        st.markdown("""<div style='padding:12px 16px;border-radius:8px;background:#EFF6FF;border:1px solid #93C5FD;color:#1E40AF;font-size:14px;margin-bottom:12px;'>
            Preencha os dados abaixo para simular a margem e criar um novo negócio.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class='loaded-banner'>
            Editando: <strong>{st.session_state.form_client}</strong>
        </div>""", unsafe_allow_html=True)

    col_in, col_out = st.columns([1.8, 1], gap="large")
    with col_in:
        i1, i2 = st.columns(2)
        client_name = i1.text_input("Cliente", key="form_client", help="Nome da empresa ou pessoa jurídica contratante")
        status_deal = i2.selectbox("Status", STATUS_LABELS, index=st.session_state.form_status_idx, help="Fase atual do negócio no pipeline de vendas")
        i3, i4 = st.columns(2)
        qty = i3.number_input("Qtd Testes", key="form_qty", min_value=0, step=1, help="Quantidade de testes/avaliações a serem aplicados neste negócio")
        cost = i4.number_input("Custo Unitário (USD)", key="form_cost", min_value=0.0, step=1.0, format="%.2f", help="Custo GA por teste pago ao fornecedor em dólares americanos — clique no campo e digite o valor")
        v_real = st.number_input("Valor de Venda (R$)", key="form_vreal", min_value=0.0, step=100.0, format="%.2f", help="Valor total cobrado do cliente em reais brasileiros — clique no campo e digite o valor")
        notes = st.text_area("Notas", key="form_notes", height=68, help="Observações internas sobre o negócio (não visível ao cliente)")

    total_tax = total_tax_pct / 100
    custo_brl = qty * cost * st.session_state.dolar_live
    imposto_presumido = v_real * (tax_p / 100)
    imposto_admin = v_real * (adm_p / 100)
    impostos = v_real * total_tax
    profit = v_real - custo_brl - impostos
    margin = (profit / v_real * 100) if v_real > 0 else 0

    if margin >= 30: margin_color, profit_color = "#059669", "#8DAE10"
    elif margin >= 10: margin_color, profit_color = "#D97706", "#D97706"
    else: margin_color, profit_color = "#DC2626", "#DC2626"

    with col_out:
        if v_real > 0:
            st.markdown(f"""<div class='main-card'>
                <p style='color:#9CA3AF; font-size:12px;'>LUCRO LÍQUIDO</p>
                <h1 style='color:{profit_color}; margin:0; font-size:42px;'>R$ {float(profit):,.2f}</h1>
                <p style='color:{margin_color}; font-weight:600;'>{margin:.1f}% Margem Real</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class='main-card'>
                <p style='color:#9CA3AF; font-size:12px;'>LUCRO LÍQUIDO</p>
                <h1 style='color:#9CA3AF; margin:0; font-size:42px;'>R$ 0,00</h1>
                <p style='color:#9CA3AF; font-weight:600;'>Preencha os dados para calcular</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Detalhamento do Cálculo", expanded=(v_real > 0)):
            st.markdown(f"""
| Item | Valor |
|---|---|
| Custo Total (USD) | $ {qty * cost:,.2f} |
| Câmbio USD→BRL | R$ {st.session_state.dolar_live:.3f} |
| **Custo Total (BRL)** | **R$ {custo_brl:,.2f}** |
| Lucro Presumido ({tax_p:.2f}%) | R$ {imposto_presumido:,.2f} |
| Taxa Administração ({adm_p:.2f}%) | R$ {imposto_admin:,.2f} |
| **Total Impostos ({total_tax_pct:.2f}%)** | **R$ {impostos:,.2f}** |
| Venda (BRL) | R$ {v_real:,.2f} |
| **Lucro Líquido** | **R$ {profit:,.2f}** |
""")

        st.markdown("<br>", unsafe_allow_html=True)
        save_label = "ATUALIZAR NEGÓCIO" if is_editing else "CRIAR NEGÓCIO"
        if is_editing:
            c1, c2 = st.columns(2)
        else:
            c1 = st.container()
            c2 = None

        if c1.button(save_label, use_container_width=True):
            if not client_name.strip():
                st.error("Preencha o nome do cliente.")
            elif qty <= 0 or cost <= 0 or v_real <= 0:
                st.error("Valores devem ser maiores que zero.")
            else:
                try:
                    status_key = status_label_to_key(status_deal)
                    client_res = sb.table('clients').upsert({'name': client_name.strip(), 'notes': notes}, on_conflict='name').execute()
                    client_id = client_res.data[0]['id']
                    deal_data = {
                        'client_id': client_id, 'status': status_key, 'qty': qty,
                        'cost_usd': float(cost), 'fx_rate': st.session_state.dolar_live,
                        'v_real': float(v_real), 'tax_presumido': tax_p, 'tax_adm': adm_p,
                        'profit': round(profit, 2), 'margin': round(margin, 1),
                        'closed_at': datetime.now().isoformat() if status_key == 'concluido' else None,
                        'created_by': str(st.session_state.user.id),
                        'created_by_email': st.session_state.user.email,
                    }
                    if is_editing:
                        old = sb.table('deals').select('status').eq('id', st.session_state.selected_deal_id).execute()
                        old_status = old.data[0]['status'] if old.data else None
                        sb.table('deals').update(deal_data).eq('id', st.session_state.selected_deal_id).execute()
                        if old_status and old_status != status_key:
                            sb.table('deal_events').insert({'deal_id': st.session_state.selected_deal_id, 'event_type': 'status_change', 'old_value': old_status, 'new_value': status_key}).execute()
                        st.toast(f"Negócio '{client_name}' atualizado!")
                    else:
                        new_deal = sb.table('deals').insert(deal_data).execute()
                        sb.table('deal_events').insert({'deal_id': new_deal.data[0]['id'], 'event_type': 'created', 'new_value': status_key}).execute()
                        st.toast(f"Negócio '{client_name}' criado!")
                    clear_form()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

        if is_editing and c2 is not None:
            if c2.button("DUPLICAR", use_container_width=True, help="Cria uma cópia deste negócio como novo"):
                st.session_state.selected_deal_id = None
                st.toast("Duplicado! Altere os dados e clique 'Criar Negócio'.")

# ============================================================
# TAB 2: PIPELINE
# ============================================================
with tab_list[2]:
    st.header("Pipeline de Vendas")

    if not all_deals:
        st.info("Nenhum negócio cadastrado.")
    else:
        # --- Filters ---
        fc1, fc2, fc3 = st.columns(3)
        filter_status = fc1.multiselect("Filtrar por Status", STATUS_LABELS, default=[], key="pipe_filter_status")
        filter_client = fc2.text_input("Buscar Cliente", key="pipe_filter_client")
        filter_date = fc3.date_input("A partir de", value=date.today() - timedelta(days=90), key="pipe_filter_date")

        df = pd.DataFrame(all_deals)
        df['client_name'] = df['clients'].apply(lambda c: c.get('name', '?') if c else '?')
        df['created_at_dt'] = pd.to_datetime(df['created_at'], utc=True)

        # Apply filters
        if filter_status:
            filter_keys = [status_label_to_key(s) for s in filter_status]
            df = df[df['status'].isin(filter_keys)]
        if filter_client:
            df = df[df['client_name'].str.contains(filter_client, case=False, na=False)]
        if filter_date:
            df = df[df['created_at_dt'] >= pd.Timestamp(filter_date, tz='UTC')]

        if df.empty:
            st.warning("Nenhum negócio encontrado com os filtros aplicados.")
        else:
            for col in ['v_real','profit','margin']: df[col] = df[col].astype(float)
            tp = df[~df['status'].isin(['concluido','perdido'])]['v_real'].sum()
            won = df[df['status']=='concluido']; lost = df[df['status']=='perdido']
            tw, tl = len(won), len(lost)
            ta = len(df) - tw - tl
            wr = (tw/(tw+tl)*100) if (tw+tl)>0 else 0

            k1,k2,k3,k4,k5 = st.columns(5)
            for col, lbl, val in [(k1,"Pipeline Ativo",f"R$ {tp:,.0f}"),(k2,"Negócios Ativos",str(ta)),(k3,"Taxa Conversão",f"{wr:.0f}%"),(k4,"Ganhos/Perdidos",f"{tw}/{tl}"),(k5,"Total Filtrado",str(len(df)))]:
                col.markdown(f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div><div class='kpi-value'>{val}</div></div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Funil de Conversão")
            sc = df.groupby('status').size().to_dict()
            mx = max(sc.values()) if sc else 1
            for sk in STATUS_KEYS:
                cfg = STATUS_CONFIG[sk]; cnt = sc.get(sk, 0)
                if cnt == 0: continue
                bw = max(int(cnt/mx*100), 8)
                vs = df[df['status']==sk]['v_real'].sum()
                st.markdown(f"<div class='funnel-row'><div style='width:160px;font-size:13px;font-weight:500;'><span style='display:inline-block;width:10px;height:10px;border-radius:50%;background:{cfg['color']};margin-right:6px;'></span>{cfg['label']}</div><div class='funnel-bar' style='width:{bw}%;background:{cfg['color']};'>{cnt} neg. | R$ {vs:,.0f}</div></div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Todos os Negócios")

            # Fix 2: Pipeline with delete buttons per deal
            pipe_deals = [d for d in all_deals if d['id'] in df['id'].values]
            for pd_deal in pipe_deals:
                pd_cn = (pd_deal.get('clients', {}) or {}).get('name', '?')
                pd_sk = pd_deal['status']
                pd_vr = float(pd_deal['v_real'])
                pd_pr = float(pd_deal['profit'])
                pd_mg = float(pd_deal['margin'])
                pd_dt = pd_deal['created_at'][:10] if pd_deal.get('created_at') else ''
                pd_by = pd_deal.get('created_by_email', '')

                pc1, pc2, pc3, pc4, pc5, pc6, pc7 = st.columns([0.8, 2.2, 1.0, 1.3, 1.3, 0.8, 0.6])
                pc1.markdown(f"<small>{status_dot(pd_sk)} {status_key_to_label(pd_sk)}</small>", unsafe_allow_html=True)
                pc2.markdown(f"**{pd_cn}**")
                pc3.markdown(f"<small>R$ {pd_vr:,.0f}</small>", unsafe_allow_html=True)
                pc4.markdown(f"<small>R$ {pd_pr:,.0f} ({pd_mg:.0f}%)</small>", unsafe_allow_html=True)
                pc5.markdown(f"<small>{pd_dt}</small>", unsafe_allow_html=True)
                with pc6:
                    if st.button("Editar", key=f"pipe_edit_{pd_deal['id']}", help=f"Editar {pd_cn}"):
                        load_deal_to_form(pd_deal)
                        st.rerun()
                with pc7:
                    st.markdown("<div class='pipe-del-btn'>", unsafe_allow_html=True)
                    # Fix 6: Two-step delete confirmation
                    confirm_key = f"pipe_confirm_del_{pd_deal['id']}"
                    if st.session_state.get(confirm_key, False):
                        pass  # Handled below
                    elif st.button("X", key=f"pipe_del_{pd_deal['id']}", help=f"Excluir {pd_cn}"):
                        st.session_state[confirm_key] = True
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                # Show confirmation dialog if pending
                confirm_key = f"pipe_confirm_del_{pd_deal['id']}"
                if st.session_state.get(confirm_key, False):
                    st.markdown(f"<div class='confirm-delete'>Tem certeza que deseja excluir <strong>{pd_cn}</strong>?</div>", unsafe_allow_html=True)
                    cc1, cc2, cc3 = st.columns([1, 1, 4])
                    with cc1:
                        if st.button("Sim, excluir", key=f"pipe_yes_{pd_deal['id']}"):
                            try:
                                sb.table('deal_events').delete().eq('deal_id', pd_deal['id']).execute()
                                sb.table('deals').delete().eq('id', pd_deal['id']).execute()
                                if st.session_state.selected_deal_id == pd_deal['id']:
                                    clear_form()
                                st.toast(f"Negócio '{pd_cn}' excluído!")
                                st.session_state[confirm_key] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir: {e}")
                    with cc2:
                        if st.button("Cancelar", key=f"pipe_no_{pd_deal['id']}"):
                            st.session_state[confirm_key] = False
                            st.rerun()

            # Also show as table for sorting/filtering
            with st.expander("Ver como Tabela", expanded=False):
                td = [{'Status': f"{status_dot_text(d['status'])} {status_key_to_label(d['status'])}", 'Cliente': (d.get('clients',{}) or {}).get('name','?'), 'Qtd': d['qty'], 'Venda R$': f"R$ {float(d['v_real']):,.2f}", 'Lucro R$': f"R$ {float(d['profit']):,.2f}", 'Margem': f"{float(d['margin']):.1f}%", 'Criado por': d.get('created_by_email',''), 'Data': d['created_at'][:10] if d.get('created_at') else ''} for d in pipe_deals]
                st.dataframe(pd.DataFrame(td), use_container_width=True, hide_index=True)

# ============================================================
# TAB 3: REPORTS
# ============================================================
with tab_list[3]:
    st.header("Relatórios")

    report_type = st.radio("Tipo de Relatório:", ["Negócios Concluídos", "Rentabilidade por Cliente", "Todos os Negócios"], horizontal=True)

    if report_type == "Negócios Concluídos":
        closed = [d for d in all_deals if d['status']=='concluido']
        if not closed:
            st.warning("Nenhum negócio concluído encontrado.")
        else:
            cdf = pd.DataFrame(closed)
            cdf['client_name'] = cdf['clients'].apply(lambda c: c.get('name','?') if c else '?')
            for c in ['v_real','profit','cost_usd','margin']: cdf[c] = cdf[c].astype(float)
            cdf['qty'] = cdf['qty'].astype(int)
            tc = 'closed_at' if cdf['closed_at'].notna().any() else 'created_at'
            cdf['ts'] = pd.to_datetime(cdf[tc], errors='coerce')
            cdf['month_name'] = cdf['ts'].dt.strftime('%Y-%m')
            cdf['year'] = cdf['ts'].dt.year
            cdf['week_start'] = cdf['ts'].dt.to_period('W').apply(lambda r: r.start_time)

            tr, tpr, tdl, tt = cdf['v_real'].sum(), cdf['profit'].sum(), len(cdf), cdf['qty'].sum()
            am = (tpr/tr*100) if tr>0 else 0

            k1,k2,k3,k4,k5 = st.columns(5)
            for col,lbl,val in [(k1,"Vendas",str(tdl)),(k2,"Faturamento",f"R$ {tr:,.0f}"),(k3,"Lucro",f"R$ {tpr:,.0f}"),(k4,"Margem",f"{am:.1f}%"),(k5,"Testes",f"{tt:,}")]:
                col.markdown(f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div><div class='kpi-value'>{val}</div></div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            view = st.radio("Período:", ["Semanal","Mensal","Anual"], horizontal=True, key="report_period")
            gcol = {'Semanal': 'week_start', 'Mensal': 'month_name', 'Anual': 'year'}[view]
            g = cdf.groupby(gcol).agg(Vendas=('v_real','sum'), Lucro=('profit','sum'), Projetos=('id','count'), Testes=('qty','sum')).reset_index()
            g.columns = ['Período','Vendas (R$)','Lucro (R$)','Projetos','Testes']
            if view == 'Semanal': g['Período'] = g['Período'].dt.strftime('%d/%m/%Y')
            g['Margem (%)'] = (g['Lucro (R$)']/g['Vendas (R$)']*100).round(1)
            st.dataframe(g.sort_values('Período', ascending=False), use_container_width=True, hide_index=True)
            st.bar_chart(g.set_index('Período')[['Vendas (R$)','Lucro (R$)']])

            st.markdown("---")
            st.subheader("Exportar")
            disp = cdf[['ts','client_name','qty','cost_usd','v_real','profit','margin']].copy()
            disp.columns = ['Data','Cliente','Qtd','Custo USD','Venda R$','Lucro R$','Margem (%)']
            disp['Data'] = disp['Data'].dt.strftime('%d/%m/%Y')
            e1, e2 = st.columns(2)
            with e1:
                buf = io.StringIO(); disp.to_csv(buf, index=False)
                st.download_button("Baixar CSV", buf.getvalue(), f"integrity_{date.today()}.csv", "text/csv")
            with e2:
                try:
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine='openpyxl') as w:
                        disp.to_excel(w, sheet_name='Todos', index=False)
                        g.to_excel(w, sheet_name=view, index=False)
                    st.download_button("Baixar Excel", buf.getvalue(), f"integrity_{date.today()}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except ImportError:
                    st.warning("pip install openpyxl")

    elif report_type == "Rentabilidade por Cliente":
        if not all_deals:
            st.warning("Nenhum negócio cadastrado.")
        else:
            rdf = pd.DataFrame(all_deals)
            rdf['client_name'] = rdf['clients'].apply(lambda c: c.get('name', '?') if c else '?')
            for c in ['v_real','profit','margin','cost_usd']: rdf[c] = rdf[c].astype(float)
            rdf['qty'] = rdf['qty'].astype(int)

            client_summary = rdf.groupby('client_name').agg(
                total_vendas=('v_real', 'sum'),
                total_lucro=('profit', 'sum'),
                total_testes=('qty', 'sum'),
                num_negocios=('id', 'count'),
                margem_media=('margin', 'mean'),
                custo_medio_usd=('cost_usd', 'mean'),
            ).sort_values('total_lucro', ascending=False).reset_index()

            client_summary.columns = ['Cliente', 'Vendas (R$)', 'Lucro (R$)', 'Testes', 'Negócios', 'Margem (%)', 'Custo Médio USD']
            client_summary['Vendas (R$)'] = client_summary['Vendas (R$)'].apply(lambda x: f"R$ {x:,.2f}")
            client_summary['Lucro (R$)'] = client_summary['Lucro (R$)'].apply(lambda x: f"R$ {x:,.2f}")
            client_summary['Margem (%)'] = client_summary['Margem (%)'].apply(lambda x: f"{x:.1f}%")
            client_summary['Custo Médio USD'] = client_summary['Custo Médio USD'].apply(lambda x: f"$ {x:.2f}")

            st.dataframe(client_summary, use_container_width=True, hide_index=True)

            # Export
            buf = io.StringIO()
            client_summary.to_csv(buf, index=False)
            st.download_button("Exportar CSV", buf.getvalue(), f"clientes_{date.today()}.csv", "text/csv")

    elif report_type == "Todos os Negócios":
        if not all_deals:
            st.warning("Nenhum negócio cadastrado.")
        else:
            adf = pd.DataFrame(all_deals)
            adf['client_name'] = adf['clients'].apply(lambda c: c.get('name', '?') if c else '?')
            td = [{
                'Status': f"{status_dot_text(d['status'])} {status_key_to_label(d['status'])}",
                'Cliente': (d.get('clients',{}) or {}).get('name','?'),
                'Qtd': d['qty'],
                'Custo USD': f"$ {float(d['cost_usd']):.2f}",
                'Venda R$': f"R$ {float(d['v_real']):,.2f}",
                'Lucro R$': f"R$ {float(d['profit']):,.2f}",
                'Margem': f"{float(d['margin']):.1f}%",
                'Criado por': d.get('created_by_email',''),
                'Data': d['created_at'][:10] if d.get('created_at') else ''
            } for d in all_deals]
            st.dataframe(pd.DataFrame(td), use_container_width=True, hide_index=True)

            buf = io.StringIO()
            pd.DataFrame(td).to_csv(buf, index=False)
            st.download_button("Exportar CSV", buf.getvalue(), f"todos_negocios_{date.today()}.csv", "text/csv")

# ============================================================
# TAB 4: FX HISTORY
# ============================================================
with tab_list[4]:
    st.header("Histórico do Câmbio USD/BRL")

    fx_period = st.radio("Período:", ["7 dias", "30 dias", "90 dias"], horizontal=True, key="fx_period")
    days_map = {"7 dias": 7, "30 dias": 30, "90 dias": 90}
    fx_df = get_fx_history(days_map[fx_period])

    col_fx1, col_fx2, col_fx3 = st.columns(3)
    col_fx1.markdown(f"<div class='kpi-card'><div class='kpi-label'>Atual</div><div class='kpi-value'>R$ {st.session_state.dolar_live:.3f}</div></div>", unsafe_allow_html=True)

    if not fx_df.empty:
        fx_min, fx_max, fx_avg = fx_df['rate'].min(), fx_df['rate'].max(), fx_df['rate'].mean()
        col_fx2.markdown(f"<div class='kpi-card'><div class='kpi-label'>Mín / Máx</div><div class='kpi-value'>R$ {fx_min:.3f} / {fx_max:.3f}</div></div>", unsafe_allow_html=True)
        col_fx3.markdown(f"<div class='kpi-card'><div class='kpi-label'>Média</div><div class='kpi-value'>R$ {fx_avg:.3f}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        chart_df = fx_df.set_index('created_at')[['rate']].rename(columns={'rate': 'USD/BRL'})
        st.line_chart(chart_df)

        # Impact analysis
        st.markdown("---")
        st.subheader("Impacto do Câmbio nos Negócios")
        st.caption("Simulação: como seus negócios ativos seriam afetados por variações no câmbio.")
        active = [d for d in all_deals if d['status'] not in ['concluido','perdido']]
        if active:
            sim_rates = [fx_min, fx_avg, st.session_state.dolar_live, fx_max]
            sim_labels = [f"Mínimo (R$ {fx_min:.3f})", f"Média (R$ {fx_avg:.3f})", f"Atual (R$ {st.session_state.dolar_live:.3f})", f"Máximo (R$ {fx_max:.3f})"]
            sim_data = []
            for rate, label in zip(sim_rates, sim_labels):
                total_cost = sum(float(d['qty']) * float(d['cost_usd']) * rate for d in active)
                total_rev = sum(float(d['v_real']) for d in active)
                total_tax = total_rev * total_tax_pct / 100
                total_profit = total_rev - total_cost - total_tax
                sim_data.append({'Cenário': label, 'Custo Total (BRL)': f"R$ {total_cost:,.0f}", 'Lucro Projetado': f"R$ {total_profit:,.0f}"})
            st.dataframe(pd.DataFrame(sim_data), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum negócio ativo para simular.")
    else:
        col_fx2.markdown("<div class='kpi-card'><div class='kpi-label'>Mín / Máx</div><div class='kpi-value'>—</div></div>", unsafe_allow_html=True)
        col_fx3.markdown("<div class='kpi-card'><div class='kpi-label'>Média</div><div class='kpi-value'>—</div></div>", unsafe_allow_html=True)
        st.info("Dados de câmbio ainda estão sendo coletados. Volte em breve!")

# ============================================================
# TAB 5: ADMIN (only for admins)
# ============================================================
if is_admin() and len(tab_list) > 5:
    with tab_list[5]:
        st.header("Painel Administrativo")

        # --- Create new user ---
        st.subheader("Criar Novo Usuário")
        if not sb_admin:
            st.error("Service role key não configurada. Adicione SUPABASE_SERVICE_KEY nos secrets.")
        else:
            app_url = st.secrets.get("APP_URL", "")
            with st.form("create_user_form"):
                nu_name = st.text_input("Nome completo")
                nu_email = st.text_input("Email")
                nu_pass = st.text_input("Senha temporária", type="password")
                nu_role = st.selectbox("Papel", ["user", "admin"])
                send_email_check = st.checkbox("Enviar email de boas-vindas com credenciais", value=True)
                submitted = st.form_submit_button("Criar Usuário")
                if submitted:
                    if nu_email and nu_pass and nu_name:
                        try:
                            res = sb_admin.auth.admin.create_user({
                                "email": nu_email,
                                "password": nu_pass,
                                "email_confirm": True,
                                "user_metadata": {"full_name": nu_name, "role": nu_role}
                            })
                            st.success(f"Usuário '{nu_name}' ({nu_email}) criado!")

                            # Send welcome email
                            if send_email_check:
                                email_ok, email_err = send_welcome_email(nu_email, nu_name, nu_pass, app_url)
                                if email_ok:
                                    st.success(f"Email de boas-vindas enviado para {nu_email}!")
                                else:
                                    st.warning(f"Usuário criado, mas email não enviado: {email_err}")
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else:
                        st.warning("Preencha todos os campos.")

        # --- User list with full management ---
        st.markdown("---")
        st.subheader("Usuários Cadastrados")
        try:
            users = sb.table('user_profiles').select('*').order('created_at').execute()
            if users.data:
                for u in users.data:
                    u_name = u.get('full_name', '') or u.get('email', '?')
                    u_email = u.get('email', '')
                    u_role = u.get('role', 'user')
                    u_active = u.get('is_active', True)
                    u_date = u.get('created_at', '')[:10] if u.get('created_at') else ''
                    u_id = u.get('id', '')
                    is_self = (u_id == str(st.session_state.user.id))

                    # User card
                    status_color = "#059669" if u_active else "#EF4444"
                    status_text = "Ativo" if u_active else "Inativo"
                    role_badge = "Admin" if u_role == 'admin' else "Usuário"
                    st.markdown(f"""<div style='padding:12px;border-radius:10px;border:1px solid #e2e8f0;margin:6px 0;background:#fafafa;'>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <div>
                                <strong>{u_name}</strong> <span style='color:#6B7280;font-size:13px;'>| {u_email} | {role_badge}</span>
                            </div>
                            <div>
                                <span style='color:{status_color};font-weight:600;font-size:12px;padding:3px 10px;border-radius:12px;background:{status_color}15;'>{status_text}</span>
                                <span style='color:#9CA3AF;font-size:11px;margin-left:8px;'>{u_date}</span>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                    if not is_self and sb_admin:
                        col_a, col_b, col_c, col_d, col_e = st.columns(5)

                        # Toggle active/inactive
                        with col_a:
                            if u_active:
                                if st.button("Desativar", key=f"deact_{u_id}", use_container_width=True):
                                    sb.table('user_profiles').update({'is_active': False}).eq('id', u_id).execute()
                                    st.toast(f"'{u_name}' desativado.")
                                    st.rerun()
                            else:
                                if st.button("Reativar", key=f"react_{u_id}", use_container_width=True):
                                    sb.table('user_profiles').update({'is_active': True}).eq('id', u_id).execute()
                                    st.toast(f"'{u_name}' reativado.")
                                    st.rerun()

                        # Reset password
                        with col_b:
                            if st.button("Resetar Senha", key=f"reset_{u_id}", use_container_width=True):
                                st.session_state[f'show_reset_{u_id}'] = True

                        # Resend invite email
                        with col_c:
                            if st.button("Reenviar Convite", key=f"resend_{u_id}", use_container_width=True):
                                st.session_state[f'show_resend_{u_id}'] = True

                        # Change role
                        with col_d:
                            new_role = "admin" if u_role == "user" else "user"
                            role_label_btn = "Tornar Admin" if u_role == "user" else "Tornar Usuário"
                            if st.button(role_label_btn, key=f"role_{u_id}", use_container_width=True):
                                try:
                                    sb.table('user_profiles').update({'role': new_role}).eq('id', u_id).execute()
                                    sb_admin.auth.admin.update_user_by_id(u_id, {"user_metadata": {"role": new_role}})
                                    st.toast(f"'{u_name}' agora é {new_role}.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")

                        # Delete user
                        with col_e:
                            if st.button("Excluir", key=f"delusr_{u_id}", use_container_width=True):
                                try:
                                    sb_admin.auth.admin.delete_user(u_id)
                                    sb.table('user_profiles').delete().eq('id', u_id).execute()
                                    st.toast(f"'{u_name}' excluído.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")

                        # Reset password form (shown when clicked)
                        if st.session_state.get(f'show_reset_{u_id}', False):
                            with st.form(f"reset_form_{u_id}"):
                                new_pw = st.text_input(f"Nova senha para {u_name}", type="password", key=f"newpw_{u_id}")
                                rc1, rc2 = st.columns(2)
                                if rc1.form_submit_button("Confirmar Reset"):
                                    if new_pw and len(new_pw) >= 6:
                                        try:
                                            sb_admin.auth.admin.update_user_by_id(u_id, {"password": new_pw})
                                            st.success(f"Senha de '{u_name}' resetada!")
                                            st.session_state[f'show_reset_{u_id}'] = False
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Erro: {e}")
                                    else:
                                        st.error("Senha deve ter pelo menos 6 caracteres.")
                                if rc2.form_submit_button("Cancelar"):
                                    st.session_state[f'show_reset_{u_id}'] = False
                                    st.rerun()

                        # Resend invite form (shown when clicked)
                        if st.session_state.get(f'show_resend_{u_id}', False):
                            with st.form(f"resend_form_{u_id}"):
                                resend_pw = st.text_input(f"Senha para enviar a {u_name}", type="password", key=f"resendpw_{u_id}",
                                                          help="Digite a senha atual ou uma nova para incluir no email")
                                rs1, rs2 = st.columns(2)
                                if rs1.form_submit_button("Enviar Email"):
                                    if resend_pw:
                                        # Optionally reset password to the one being sent
                                        try:
                                            sb_admin.auth.admin.update_user_by_id(u_id, {"password": resend_pw})
                                        except:
                                            pass
                                        email_ok, email_err = send_welcome_email(u_email, u_name, resend_pw, app_url)
                                        if email_ok:
                                            st.success(f"Email reenviado para {u_email}!")
                                        else:
                                            st.error(f"Falha: {email_err}")
                                        st.session_state[f'show_resend_{u_id}'] = False
                                        st.rerun()
                                    else:
                                        st.error("Digite uma senha para incluir no email.")
                                if rs2.form_submit_button("Cancelar"):
                                    st.session_state[f'show_resend_{u_id}'] = False
                                    st.rerun()

                    elif is_self:
                        st.caption("(sua conta)")

            else:
                st.info("Nenhum usuário cadastrado ainda.")
        except Exception as e:
            st.info(f"Carregando usuários... {e}")

        # --- Activity log ---
        st.markdown("---")
        st.subheader("Log de Atividades")
        try:
            events = sb.table('deal_events').select('*, deals(clients(name))').order('created_at', desc=True).limit(50).execute()
            if events.data:
                log_data = []
                for ev in events.data:
                    cn = '?'
                    if ev.get('deals') and ev['deals'].get('clients'):
                        cn = ev['deals']['clients'].get('name', '?')
                    log_data.append({
                        'Data': ev['created_at'][:16].replace('T', ' '),
                        'Cliente': cn,
                        'Evento': ev['event_type'],
                        'De': status_key_to_label(ev.get('old_value', '')) if ev.get('old_value') else '-',
                        'Para': status_key_to_label(ev.get('new_value', '')) if ev.get('new_value') else '-',
                    })
                st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum evento registrado.")
        except Exception as e:
            st.info(f"Log: {e}")
