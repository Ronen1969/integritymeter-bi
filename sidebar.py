"""
sidebar.py — Sidebar rendering.
Returns a dict of config values used by the calculator and pipeline tabs.
"""
import os

import streamlit as st

from auth import logout
from fx import get_live_fx


def render_sidebar() -> dict:
    """
    Render the sidebar and return configuration values needed by page tabs.

    Returns:
        dict with keys: default_cost_usd, tax_p, adm_p, total_tax_pct
    """
    # Collapsible sidebar toggle button (pure HTML/CSS, no iframes)
    st.markdown("""
<div id="im-sidebar-toggle" onclick="(function(){
    var sb = document.querySelector('[data-testid=\\'stSidebar\\']');
    var ctrl = document.querySelector('[data-testid=\\'stSidebarCollapsedControl\\']');
    var btn = document.getElementById('im-sidebar-toggle');
    if (sb && sb.style.display !== 'none') {
        sb.style.display = 'none';
        if(ctrl) ctrl.style.display = 'none';
        btn.textContent = '▖';
    } else if (sb) {
        sb.style.display = '';
        if(ctrl) ctrl.style.display = '';
        btn.textContent = '◀';
    }
})()" style="position:fixed;top:68px;left:5px;z-index:999999;background:#f1f5f9;
border:1px solid #e2e8f0;border-radius:8px;width:32px;height:32px;cursor:pointer;
display:flex;align-items:center;justify-content:center;font-size:16px;color:#6B7280;
box-shadow:0 1px 3px rgba(0,0,0,0.1);user-select:none;" title="Ocultar/mostrar barra lateral">◀</div>
""", unsafe_allow_html=True)

    with st.sidebar:
        logo_path = os.path.expanduser("~/Desktop/integrity-meter-logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path)

        # User info + logout
        user_name  = st.session_state.user_profile.get('full_name', '') or st.session_state.user.email
        user_role  = st.session_state.user_profile.get('role', 'user')
        role_label = "Admin" if user_role == 'admin' else "Usuário"

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
        st.caption("CÂMBIO USD/BRL")

        # Sync widget key if a live fetch just happened
        if '_fx_new_rate' in st.session_state:
            st.session_state['fx_rate_input'] = st.session_state.pop('_fx_new_rate')
        if 'fx_rate_input' not in st.session_state:
            st.session_state['fx_rate_input'] = st.session_state.dolar_live

        fx_value = st.number_input(
            "Taxa câmbio", min_value=0.01, step=0.01, format="%.4f",
            key="fx_rate_input",
            help="Edite manualmente ou clique Att. para buscar online",
            label_visibility="collapsed",
        )
        st.session_state.dolar_live = fx_value

        if st.button("Att. Câmbio Online", help="Buscar taxa atual USD/BRL", use_container_width=True):
            new_rate = get_live_fx()
            if new_rate:
                st.session_state['_fx_new_rate'] = new_rate
                st.toast(f"Câmbio atualizado: R$ {new_rate:.4f}")
            else:
                st.toast("APIs indisponíveis. Edite manualmente.")
            st.rerun()

        st.markdown("---")
        st.caption("CONFIGURAÇÕES")

        default_cost_usd = st.number_input(
            "Custo Padrão USD", value=4.00, min_value=0.0, step=0.5, format="%.2f",
            key="default_cost_usd",
            help="Custo unitário padrão em USD — pré-preenchido nos novos negócios",
        )
        tax_p = st.number_input(
            "Lucro Presumido (%)", value=16.33, min_value=0.0, step=0.5, format="%.2f",
            key="tax_presumido",
        )
        adm_p = st.number_input(
            "Taxa Administração (%)", value=2.50, min_value=0.0, step=0.5, format="%.2f",
            key="tax_admin",
        )
        total_tax_pct = tax_p + adm_p
        st.caption(f"Impostos: **{total_tax_pct:.2f}%**")

    return {
        'default_cost_usd': default_cost_usd,
        'tax_p':            tax_p,
        'adm_p':            adm_p,
        'total_tax_pct':    total_tax_pct,
    }
