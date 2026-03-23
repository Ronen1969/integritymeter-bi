""" sidebar.py â Barra lateral. Retorna um dicionÃ¡rio de configuraÃ§Ãµes usadas pelas abas. """
import os
import streamlit as st
from auth import logout
from data import get_setting, save_setting
from fx import get_live_fx


def render_sidebar() -> dict:
    """
    Renderiza a barra lateral e retorna os valores de configuraÃ§Ã£o.
    Retorna dict com: default_cost_usd, tax_p, adm_p, total_tax_pct
    """
    if '_sidebar_settings_loaded' not in st.session_state:
        st.session_state['default_cost_usd'] = float(get_setting('default_cost_usd', '4.00'))
        st.session_state['tax_presumido']     = float(get_setting('tax_presumido', '16.33'))
        st.session_state['tax_admin']         = float(get_setting('tax_admin', '2.50'))
        st.session_state['_saved_default_cost_usd'] = st.session_state['default_cost_usd']
        st.session_state['_saved_tax_presumido']    = st.session_state['tax_presumido']
        st.session_state['_saved_tax_admin']        = st.session_state['tax_admin']
        st.session_state['_sidebar_settings_loaded'] = True

    with st.sidebar:
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png')
        if not os.path.exists(logo_path):
            logo_path = os.path.expanduser("~/Desktop/integrity-meter-logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path)

        # InformaÃ§Ãµes do usuÃ¡rio + botÃ£o sair
        user_name  = st.session_state.user_profile.get('full_name', '') or st.session_state.user.email
        user_role  = st.session_state.user_profile.get('role', 'user')
        role_label = "Administrador" if user_role == 'admin' else "UsuÃ¡rio"
        st.markdown(
            f"<div style='display:flex;align-items:center;justify-content:space-between;"
            f"margin-bottom:8px;'>"
            f"<span style='font-weight:600;font-size:14px;'>{user_name}</span>"
            f"<span style='color:#9CA3AF;font-size:12px;'>{role_label}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<style>.sair-btn button { background:transparent !important; "
            "color:#EF4444 !important; border:none !important; padding:2px 0 !important; "
            "min-height:28px !important; font-size:13px !important; "
            "text-decoration:underline !important; }</style>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='sair-btn'>", unsafe_allow_html=True)
        if st.button("Sair", key="logout_btn"):
            logout()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.caption("CÃMBIO USD/BRL")

        if '_fx_new_rate' in st.session_state:
            st.session_state['fx_rate_input'] = st.session_state.pop('_fx_new_rate')
        if 'fx_rate_input' not in st.session_state:
            st.session_state['fx_rate_input'] = st.session_state.dolar_live

        fx_value = st.number_input(
            "Taxa de cÃ¢mbio",
            min_value=0.01,
            step=0.01,
            format="%.4f",
            key="fx_rate_input",
            help="Edite manualmente ou clique em 'Atualizar' para buscar o valor online",
            label_visibility="collapsed",
        )
        st.session_state.dolar_live = fx_value

        if st.button("Atualizar CÃ¢mbio", help="Buscar taxa atual USD/BRL", use_container_width=True):
            new_rate = get_live_fx()
            if new_rate:
                st.session_state['_fx_new_rate'] = new_rate
                st.toast(f"CÃ¢mbio atualizado: R$ {new_rate:.4f}")
            else:
                st.toast("ServiÃ§o indisponÃ­vel. Edite manualmente.")
            st.rerun()

        st.markdown("---")
        st.caption("CONFIGURAÃÃES")

        default_cost_usd = st.number_input(
            "Custo PadrÃ£o (USD)",
            min_value=0.0,
            step=0.5,
            format="%.2f",
            key="default_cost_usd",
            help="Custo unitÃ¡rio padrÃ£o em USD â prÃ©-preenchido nos novos negÃ³cios",
        )
        tax_p = st.number_input(
            "Lucro Presumido (%)",
            min_value=0.0,
            step=0.5,
            format="%.2f",
            key="tax_presumido",
        )
        adm_p = st.number_input(
            "Taxa de AdministraÃ§Ã£o (%)",
            min_value=0.0,
            step=0.5,
            format="%.2f",
            key="tax_admin",
        )
        total_tax_pct = tax_p + adm_p
        st.caption(f"Total de impostos: **{total_tax_pct:.2f}%**")

        # Persistir alteraÃ§Ãµes no banco
        if default_cost_usd != st.session_state.get('_saved_default_cost_usd'):
            save_setting('default_cost_usd', default_cost_usd)
            st.session_state['_saved_default_cost_usd'] = default_cost_usd
        if tax_p != st.session_state.get('_saved_tax_presumido'):
            save_setting('tax_presumido', tax_p)
            st.session_state['_saved_tax_presumido'] = tax_p
        if adm_p != st.session_state.get('_saved_tax_admin'):
            save_setting('tax_admin', adm_p)
            st.session_state['_saved_tax_admin'] = adm_p

    return {
        'default_cost_usd': default_cost_usd,
        'tax_p':            tax_p,
        'adm_p':            adm_p,
        'total_tax_pct':    total_tax_pct,
    }
