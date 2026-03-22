"""
IntegrityMeter BI — Entry Point
================================
All logic lives in dedicated modules. This file wires them together.

Module map:
    config.py       — Supabase clients, logging, secrets validation
    styles.py       — CSS design system + JS helpers
    auth.py         — Login / logout / session restore / welcome email
    models.py       — Status definitions and helpers
    fx.py           — FX rate fetching, deal cache
    data.py         — User settings persistence
    state.py        — Session state init + form management
    sidebar.py      — Sidebar rendering → returns sidebar_cfg dict
    tabs/
        dashboard.py   — Tab 0: Painel Principal
        calculator.py  — Tab 1: Novo Negócio / Margin Calculator
        pipeline.py    — Tab 2: Pipeline de Vendas
        reports.py     — Tab 3: Relatórios
        fx_history.py  — Tab 4: Câmbio / FX History
        admin.py       — Tab 5: Admin (admin users only)
"""

# ── config MUST be the very first import — it calls st.set_page_config() ────
import config  # noqa: F401

import streamlit as st

from auth import init_auth, is_admin, render_login
from fx import _fetch_all_deals
from models import _migrate_status
from sidebar import render_sidebar
from state import init_session_state, process_pending_form
from styles import apply_styles
from tabs.admin import render_admin
from tabs.calculator import render_calculator
from tabs.dashboard import render_dashboard
from tabs.fx_history import render_fx_history
from tabs.pipeline import render_pipeline
from tabs.reports import render_reports


def main() -> None:
    apply_styles()

    # Auth guard
    init_auth()
    if not st.session_state.user:
        render_login()
        st.stop()

    # Session state + form operations must run before any widgets
    init_session_state()
    process_pending_form()

    # Load and migrate all deals (cached, 30 s TTL)
    all_deals = _fetch_all_deals()
    for d in all_deals:
        d['status'] = _migrate_status(d['status'])

    # Sidebar — returns tax rates and cost defaults used by calculator / pipeline
    sidebar_cfg = render_sidebar()

    # Main tab navigation
    tab_names = ["Dashboard", "Novo Negócio", "Pipeline", "Relatórios", "Câmbio"]
    if is_admin():
        tab_names.append("Admin")
    tabs = st.tabs(tab_names)

    with tabs[0]:
        render_dashboard(all_deals, sidebar_cfg)
    with tabs[1]:
        render_calculator(all_deals, sidebar_cfg)
    with tabs[2]:
        render_pipeline(all_deals, sidebar_cfg)
    with tabs[3]:
        render_reports(all_deals)
    with tabs[4]:
        render_fx_history(all_deals, sidebar_cfg)
    if is_admin() and len(tabs) > 5:
        with tabs[5]:
            render_admin()


main()
