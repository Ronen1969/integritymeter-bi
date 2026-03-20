import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta
from supabase import create_client
import os
import io

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
    """Admin client with service_role key for user management."""
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
[data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #F3F4F6; width: 400px !important; }
.stButton>button { background-color: #8DAE10 !important; color: white !important; border-radius: 10px !important; height: 45px; font-weight: 600 !important; border: none !important; }
.main-card { padding: 30px; border-radius: 16px; background-color: #FFFFFF; border: 1px solid #F3F4F6; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.02); }
.delete-btn button { background-color: #EF4444 !important; font-size: 12px !important; height: 32px !important; padding: 0 8px !important; }
.loaded-banner { padding: 10px 16px; border-radius: 8px; background-color: #F0FDF4; border: 1px solid #BBF7D0; color: #166534; font-weight: 500; margin-bottom: 8px; }
.kpi-card { padding: 16px; border-radius: 12px; background: linear-gradient(135deg, #f8fafc, #f1f5f9); border: 1px solid #e2e8f0; text-align: center; }
.kpi-value { font-size: 28px; font-weight: 700; color: #8DAE10; margin: 4px 0; }
.kpi-label { font-size: 11px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; }
.funnel-row { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
.funnel-bar { height: 24px; border-radius: 4px; background: #8DAE10; display: flex; align-items: center; padding: 0 8px; color: white; font-size: 11px; font-weight: 600; }
.login-container { max-width: 400px; margin: 80px auto; padding: 40px; border-radius: 16px; border: 1px solid #F3F4F6; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
.user-badge { padding: 6px 12px; border-radius: 20px; background: #F0FDF4; color: #166534; font-size: 12px; font-weight: 600; display: inline-block; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

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
        # Load profile
        profile = sb.table('user_profiles').select('*').eq('id', res.user.id).execute()
        if profile.data:
            if not profile.data[0].get('is_active', True):
                st.session_state.user = None
                return False, "Conta desativada. Contate o administrador."
            st.session_state.user_profile = profile.data[0]
        return True, None
    except Exception as e:
        return False, str(e)

def logout():
    try:
        sb.auth.sign_out()
    except:
        pass
    st.session_state.user = None
    st.session_state.user_profile = None

def is_admin():
    return st.session_state.user_profile and st.session_state.user_profile.get('role') == 'admin'

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
    'proposta_enviada':   {'label': 'Proposta Enviada',   'emoji': '📩', 'color': '#6B7280', 'order': 1},
    'em_negociacao':      {'label': 'Em Negociação',      'emoji': '🤝', 'color': '#3B82F6', 'order': 2},
    'aprovado':           {'label': 'Aprovado',           'emoji': '✅', 'color': '#10B981', 'order': 3},
    'contrato_assinado':  {'label': 'Contrato Assinado',  'emoji': '📝', 'color': '#8B5CF6', 'order': 4},
    'em_execucao':        {'label': 'Em Execução',        'emoji': '⚙️', 'color': '#F59E0B', 'order': 5},
    'concluido':          {'label': 'Concluído',          'emoji': '🏆', 'color': '#059669', 'order': 6},
    'perdido':            {'label': 'Perdido',            'emoji': '❌', 'color': '#EF4444', 'order': 7},
}
STATUS_LABELS = [v['label'] for v in sorted(STATUS_CONFIG.values(), key=lambda x: x['order'])]
STATUS_KEYS = [k for k in sorted(STATUS_CONFIG, key=lambda x: STATUS_CONFIG[x]['order'])]

def status_key_to_label(key): return STATUS_CONFIG.get(key, {}).get('label', key)
def status_label_to_key(label):
    for k, v in STATUS_CONFIG.items():
        if v['label'] == label: return k
    return 'proposta_enviada'
def status_emoji(key): return STATUS_CONFIG.get(key, {}).get('emoji', '📋')

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

# ============================================================
# 6. SESSION STATE
# ============================================================
if 'dolar_live' not in st.session_state:
    st.session_state.dolar_live = get_cached_fx()
for key, default in [('selected_deal_id', None), ('form_client', ''), ('form_qty', 200),
                      ('form_cost', 4.0), ('form_vreal', 14000.0), ('form_status_idx', 0),
                      ('form_notes', ''), ('just_loaded', False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================
# 7. SIDEBAR
# ============================================================
with st.sidebar:
    logo_path = os.path.expanduser("~/Desktop/integrity-meter-logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path)

    # User info
    user_name = st.session_state.user_profile.get('full_name', '') or st.session_state.user.email
    user_role = st.session_state.user_profile.get('role', 'user')
    role_label = "Admin" if user_role == 'admin' else "Usuário"
    st.markdown(f"<div class='user-badge'>👤 {user_name} ({role_label})</div>", unsafe_allow_html=True)

    if st.button("🚪 Sair", key="logout_btn"):
        logout()
        st.rerun()

    st.markdown("---")
    st.caption("CÂMBIO EM TEMPO REAL")
    col_v, col_r = st.columns([2, 1])
    col_v.markdown(f"### R$ {st.session_state.dolar_live:.3f}")
    if col_r.button("🔄", help="Atualizar câmbio"):
        old = st.session_state.dolar_live
        st.session_state.dolar_live = get_live_fx()
        st.toast(f"Câmbio: R$ {st.session_state.dolar_live:.3f}" if st.session_state.dolar_live != old else "Câmbio já atualizado.")
        st.rerun()

    st.markdown("---")
    st.subheader("Configurações Fiscais")
    tax_p = st.number_input("Lucro Presumido (%)", value=16.33)
    adm_p = st.number_input("Taxa Adm (%)", value=3.00)

    st.markdown("---")
    st.caption("NEGÓCIOS SALVOS")
    try:
        deals_res = sb.table('deals').select('*, clients(name, notes)').order('updated_at', desc=True).execute()
        all_deals = deals_res.data or []
    except:
        all_deals = []

    if not all_deals:
        st.info("Nenhum negócio salvo.")
    else:
        for deal in all_deals:
            col_load, col_del = st.columns([4, 1])
            cn = deal.get('clients', {}).get('name', '?') if deal.get('clients') else '?'
            sk = deal['status']
            dd = deal['created_at'][:10] if deal.get('created_at') else ''

            if col_load.button(f"{status_emoji(sk)} {cn} | {dd}", key=f"btn_{deal['id']}"):
                st.session_state.form_client = cn
                st.session_state.form_qty = int(deal['qty'])
                st.session_state.form_cost = float(deal['cost_usd'])
                st.session_state.form_vreal = float(deal['v_real'])
                st.session_state.form_status_idx = STATUS_KEYS.index(sk) if sk in STATUS_KEYS else 0
                st.session_state.form_notes = (deal.get('clients', {}) or {}).get('notes', '') or ''
                st.session_state.selected_deal_id = deal['id']
                st.session_state.just_loaded = True
                st.rerun()

            with col_del:
                st.markdown("<div class='delete-btn'>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{deal['id']}"):
                    sb.table('deals').delete().eq('id', deal['id']).execute()
                    if st.session_state.selected_deal_id == deal['id']:
                        st.session_state.selected_deal_id = None
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 8. MAIN TABS
# ============================================================
tabs = ["🛡️ Gestão de Margem", "📊 Pipeline & Conversão", "📈 Relatório & Exportação"]
if is_admin():
    tabs.append("⚙️ Admin")
tab_list = st.tabs(tabs)

# ============================================================
# TAB 1: MARGIN CALCULATOR
# ============================================================
with tab_list[0]:
    if st.session_state.just_loaded:
        st.markdown(f"<div class='loaded-banner'>✅ Negócio carregado: <strong>{st.session_state.form_client}</strong></div>", unsafe_allow_html=True)
        st.session_state.just_loaded = False

    col_in, col_out = st.columns([1.8, 1], gap="large")
    with col_in:
        i1, i2 = st.columns(2)
        client_name = i1.text_input("Cliente", key="form_client")
        status_deal = i2.selectbox("Status", STATUS_LABELS, index=st.session_state.form_status_idx)
        i3, i4 = st.columns(2)
        qty = i3.number_input("Qtd Testes", key="form_qty", min_value=0)
        cost = i4.number_input("Custo (USD)", key="form_cost", min_value=0.0, format="%.2f")
        v_real = st.number_input("Venda (R$)", key="form_vreal", min_value=0.0, format="%.2f")
        notes = st.text_area("Notas", key="form_notes", height=68)

    total_tax = (tax_p + adm_p) / 100
    custo_brl = qty * cost * st.session_state.dolar_live
    impostos = v_real * total_tax
    profit = v_real - custo_brl - impostos
    margin = (profit / v_real * 100) if v_real > 0 else 0

    if margin >= 30: margin_color, profit_color = "#059669", "#8DAE10"
    elif margin >= 10: margin_color, profit_color = "#D97706", "#D97706"
    else: margin_color, profit_color = "#DC2626", "#DC2626"

    with col_out:
        st.markdown(f"""<div class='main-card'>
            <p style='color:#9CA3AF; font-size:12px;'>LUCRO LÍQUIDO</p>
            <h1 style='color:{profit_color}; margin:0; font-size:42px;'>R$ {float(profit):,.2f}</h1>
            <p style='color:{margin_color}; font-weight:600;'>{margin:.1f}% Margem Real</p>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📊 Detalhamento do Cálculo"):
            st.markdown(f"""
| Item | Valor |
|---|---|
| Custo Total (USD) | $ {qty * cost:,.2f} |
| Câmbio USD→BRL | R$ {st.session_state.dolar_live:.3f} |
| **Custo Total (BRL)** | **R$ {custo_brl:,.2f}** |
| Impostos ({tax_p + adm_p:.2f}%) | R$ {impostos:,.2f} |
| Venda (BRL) | R$ {v_real:,.2f} |
| **Lucro Líquido** | **R$ {profit:,.2f}** |
""")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("💾 SALVAR OU ATUALIZAR"):
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
                    if st.session_state.selected_deal_id:
                        old = sb.table('deals').select('status').eq('id', st.session_state.selected_deal_id).execute()
                        old_status = old.data[0]['status'] if old.data else None
                        sb.table('deals').update(deal_data).eq('id', st.session_state.selected_deal_id).execute()
                        if old_status and old_status != status_key:
                            sb.table('deal_events').insert({'deal_id': st.session_state.selected_deal_id, 'event_type': 'status_change', 'old_value': old_status, 'new_value': status_key}).execute()
                    else:
                        new_deal = sb.table('deals').insert(deal_data).execute()
                        st.session_state.selected_deal_id = new_deal.data[0]['id']
                        sb.table('deal_events').insert({'deal_id': new_deal.data[0]['id'], 'event_type': 'created', 'new_value': status_key}).execute()
                    st.success(f"Negócio '{client_name}' salvo!")
                    # Clear form for next entry
                    st.session_state.form_client = ''
                    st.session_state.form_qty = 200
                    st.session_state.form_cost = 4.0
                    st.session_state.form_vreal = 14000.0
                    st.session_state.form_status_idx = 0
                    st.session_state.form_notes = ''
                    st.session_state.selected_deal_id = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
        if c2.button("📋 DUPLICAR"):
            st.session_state.selected_deal_id = None
            st.toast("Duplicado! Altere e salve como novo.")

# ============================================================
# TAB 2: PIPELINE
# ============================================================
with tab_list[1]:
    st.header("📊 Pipeline de Vendas")
    if not all_deals:
        st.info("Nenhum negócio cadastrado.")
    else:
        df = pd.DataFrame(all_deals)
        df['client_name'] = df['clients'].apply(lambda c: c.get('name', '?') if c else '?')
        tp = df[~df['status'].isin(['concluido','perdido'])]['v_real'].astype(float).sum()
        won = df[df['status']=='concluido']; lost = df[df['status']=='perdido']
        tw, tl = len(won), len(lost)
        ta = len(df) - tw - tl
        wr = (tw/(tw+tl)*100) if (tw+tl)>0 else 0
        if not won.empty:
            wc = won.copy(); wc['cd'] = pd.to_datetime(wc['created_at']); wc['cld'] = pd.to_datetime(wc['closed_at'])
            v = wc.dropna(subset=['cld']); ac = (v['cld']-v['cd']).dt.days.mean() if not v.empty else 0
        else: ac = 0

        k1,k2,k3,k4,k5 = st.columns(5)
        for col, lbl, val in [(k1,"Pipeline Ativo",f"R$ {tp:,.0f}"),(k2,"Negócios Ativos",str(ta)),(k3,"Taxa Conversão",f"{wr:.0f}%"),(k4,"Ganhos/Perdidos",f"{tw}/{tl}"),(k5,"Ciclo Médio",f"{ac:.0f}d")]:
            col.markdown(f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div><div class='kpi-value'>{val}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🔽 Funil de Conversão")
        sc = df.groupby('status').size().to_dict()
        mx = max(sc.values()) if sc else 1
        for sk in STATUS_KEYS:
            cfg = STATUS_CONFIG[sk]; cnt = sc.get(sk, 0)
            if cnt == 0: continue
            bw = max(int(cnt/mx*100), 8)
            vs = df[df['status']==sk]['v_real'].astype(float).sum()
            st.markdown(f"<div class='funnel-row'><div style='width:160px;font-size:13px;font-weight:500;'>{cfg['emoji']} {cfg['label']}</div><div class='funnel-bar' style='width:{bw}%;background:{cfg['color']};'>{cnt} neg. | R$ {vs:,.0f}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 Todos os Negócios")
        td = [{'Status': f"{status_emoji(d['status'])} {status_key_to_label(d['status'])}", 'Cliente': (d.get('clients',{}) or {}).get('name','?'), 'Qtd': d['qty'], 'Venda R$': f"R$ {float(d['v_real']):,.2f}", 'Lucro R$': f"R$ {float(d['profit']):,.2f}", 'Margem': f"{float(d['margin']):.1f}%", 'Criado por': d.get('created_by_email',''), 'Data': d['created_at'][:10] if d.get('created_at') else ''} for d in all_deals]
        st.dataframe(pd.DataFrame(td), use_container_width=True, hide_index=True)

# ============================================================
# TAB 3: REPORTS
# ============================================================
with tab_list[2]:
    st.header("📈 Relatório de Negócios Concluídos")
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

        tr, tpr, tdl, am, tt = cdf['v_real'].sum(), cdf['profit'].sum(), len(cdf), 0, cdf['qty'].sum()
        am = (tpr/tr*100) if tr>0 else 0

        k1,k2,k3,k4,k5 = st.columns(5)
        for col,lbl,val in [(k1,"Vendas",str(tdl)),(k2,"Faturamento",f"R$ {tr:,.0f}"),(k3,"Lucro",f"R$ {tpr:,.0f}"),(k4,"Margem",f"{am:.1f}%"),(k5,"Testes",f"{tt:,}")]:
            col.markdown(f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div><div class='kpi-value'>{val}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        view = st.radio("Período:", ["Semanal","Mensal","Anual"], horizontal=True)
        gcol = {'Semanal': 'week_start', 'Mensal': 'month_name', 'Anual': 'year'}[view]
        g = cdf.groupby(gcol).agg(Vendas=('v_real','sum'), Lucro=('profit','sum'), Projetos=('id','count'), Testes=('qty','sum')).reset_index()
        g.columns = ['Período','Vendas (R$)','Lucro (R$)','Projetos','Testes']
        if view == 'Semanal': g['Período'] = g['Período'].dt.strftime('%d/%m/%Y')
        g['Margem (%)'] = (g['Lucro (R$)']/g['Vendas (R$)']*100).round(1)
        st.dataframe(g.sort_values('Período', ascending=False), use_container_width=True, hide_index=True)
        st.bar_chart(g.set_index('Período')[['Vendas (R$)','Lucro (R$)']])

        st.markdown("---")
        st.subheader("📥 Exportar")
        disp = cdf[['ts','client_name','qty','cost_usd','v_real','profit','margin']].copy()
        disp.columns = ['Data','Cliente','Qtd','Custo USD','Venda R$','Lucro R$','Margem (%)']
        disp['Data'] = disp['Data'].dt.strftime('%d/%m/%Y')
        e1, e2 = st.columns(2)
        with e1:
            buf = io.StringIO(); disp.to_csv(buf, index=False)
            st.download_button("⬇️ CSV", buf.getvalue(), f"integrity_{date.today()}.csv", "text/csv")
        with e2:
            try:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as w:
                    disp.to_excel(w, sheet_name='Todos', index=False)
                    g.to_excel(w, sheet_name=view, index=False)
                st.download_button("⬇️ Excel", buf.getvalue(), f"integrity_{date.today()}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except ImportError:
                st.warning("pip install openpyxl")

# ============================================================
# TAB 4: ADMIN (only for admins)
# ============================================================
if is_admin() and len(tab_list) > 3:
    with tab_list[3]:
        st.header("⚙️ Painel Administrativo")

        # --- Create new user ---
        st.subheader("➕ Criar Novo Usuário")
        if not sb_admin:
            st.error("Service role key não configurada. Adicione SUPABASE_SERVICE_KEY nos secrets.")
        else:
            with st.form("create_user_form"):
                nu_name = st.text_input("Nome completo")
                nu_email = st.text_input("Email")
                nu_pass = st.text_input("Senha temporária", type="password")
                nu_role = st.selectbox("Papel", ["user", "admin"])
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
                            st.success(f"Usuário '{nu_name}' ({nu_email}) criado! Senha temporária: enviar ao funcionário.")
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else:
                        st.warning("Preencha todos os campos.")

        # --- User list ---
        st.markdown("---")
        st.subheader("👥 Usuários Cadastrados")
        try:
            users = sb.table('user_profiles').select('*').order('created_at').execute()
            if users.data:
                udf = pd.DataFrame(users.data)
                udf = udf[['full_name', 'email', 'role', 'is_active', 'created_at']]
                udf.columns = ['Nome', 'Email', 'Papel', 'Ativo', 'Criado em']
                udf['Criado em'] = pd.to_datetime(udf['Criado em']).dt.strftime('%d/%m/%Y')
                udf['Ativo'] = udf['Ativo'].map({True: '✅', False: '❌'})
                st.dataframe(udf, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum usuário cadastrado ainda.")
        except Exception as e:
            st.info(f"Carregando usuários... {e}")

        # --- Activity log ---
        st.markdown("---")
        st.subheader("📜 Log de Atividades")
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
