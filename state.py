"""
state.py — Session state initialisation and form management.
"""
from datetime import date

import streamlit as st

from data import get_setting
from fx import get_cached_fx
from models import STATUS_KEYS, _migrate_status

FORM_DEFAULTS = {
    'selected_deal_id': None,
    'form_client':      '',
    'form_qty':         0,
    'form_cost':        0.0,
    'form_unit_price':  0.0,
    'form_vreal':       0.0,
    'form_status_idx':  0,
    'form_date':        date.today(),
    'form_notes':       '',
    'just_loaded':      False,
}


def init_session_state() -> None:
    """Initialise FX rate, month target, and form defaults in session_state."""
    if 'dolar_live' not in st.session_state:
        st.session_state.dolar_live = get_cached_fx()

    if '_month_target_loaded' not in st.session_state:
        saved = get_setting('month_target', '100000')
        try:
            st.session_state._saved_month_target = float(saved)
        except (ValueError, TypeError):
            st.session_state._saved_month_target = 100_000.0
        st.session_state._month_target_loaded = True

    for key, default in FORM_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default


def clear_form() -> None:
    """Schedule a form reset for the next rerun (avoids widget key conflicts)."""
    st.session_state['_pending_clear'] = True


def load_deal_to_form(deal: dict) -> None:
    """Schedule loading a deal into the form for the next rerun."""
    st.session_state['_pending_load'] = deal


def process_pending_form() -> None:
    """
    Apply any pending clear or load operations BEFORE widgets are rendered.
    Must be called once per run, before any tab/widget code.
    """
    if st.session_state.get('_pending_clear', False):
        for key, default in FORM_DEFAULTS.items():
            st.session_state[key] = default
        del st.session_state['_pending_clear']

    if '_pending_load' in st.session_state and st.session_state['_pending_load'] is not None:
        deal = st.session_state['_pending_load']
        cn   = (deal.get('clients', {}) or {}).get('name', '?')

        st.session_state.form_client    = cn
        st.session_state.form_qty       = int(deal['qty'])
        st.session_state.form_cost      = float(deal['cost_usd'])

        qty = int(deal['qty'])
        vr  = float(deal['v_real'])
        st.session_state.form_unit_price = round(vr / qty, 2) if qty > 0 else vr
        st.session_state.form_vreal      = vr

        migrated = _migrate_status(deal['status'])
        st.session_state.form_status_idx = (
            STATUS_KEYS.index(migrated) if migrated in STATUS_KEYS else 0
        )

        try:
            dt_str = deal.get('created_at', '')[:10]
            st.session_state.form_date = date.fromisoformat(dt_str) if dt_str else date.today()
        except (ValueError, TypeError):
            st.session_state.form_date = date.today()

        st.session_state.form_notes       = (deal.get('clients', {}) or {}).get('notes', '') or ''
        st.session_state.selected_deal_id = deal['id']
        st.session_state.just_loaded      = True
        del st.session_state['_pending_load']
