"""
sidebar.py — Sidebar rendering.
Returns a dict of config values used by the calculator and pipeline tabs.
"""
import os

import streamlit as st

from auth import logout
from data import get_setting, save_setting
from fx import get_live_fx


def render_sidebar() -> dict:
    """
    Render the sidebar and return configuration values needed by page tabs.

    Returns:
        dict with keys: default_cost_usd, tax_p, adm_p, total_tax_pct
    """
    # ── Load persisted settings once per session ──────────────────────────────
    if '_sidebar_settings_loaded' not in st.session_state:
        st.session_state['default_cost_usd']      = float(get_setting('default_cost_usd', '4.00'))
        st.session_state['tax_presumido']          = float(get_setting('tax_presumido', '16.33'))
        st.session_state['tax_admin']              = float(get_setting('tax_admin', '2.50'))
        st.session_state['_saved_default_cost_usd'] = st.session_state['default_cost_usd']
        st.session_state['_saved_tax_presumido']   = st.session_state['tax_presumido']
        st.session_state['_saved_tax_admin']       = st.session_state['tax_admin']
        st.session_state['_sidebar_settings_loaded'] = True

    with st.sidebar:
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png')
        if not os.path.exists(logo_path):
            # fallback: try Desktop path for local development
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
            "Custo Padrão USD", min_value=0.0, step=0.5, format="%.2f",
            key="default_cost_usd",
            help="Custo unitário padrão em USD — pré-preenchido nos novos negócios",
        )
        tax_p = st.number_input(
            "Lucro Presumido (%)", min_value=0.0, step=0.5, format="%.2f",
            key="tax_presumido",
        )
        adm_p = st.number_input(
            "Taxa Administração (%)", min_value=0.0, step=0.5, format="%.2f",
            key="tax_admin",
        )
        total_tax_pct = tax_p + adm_p
        st.caption(f"Impostos: **{total_tax_pct:.2f}%**")

        # Persist any changes to the database
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
