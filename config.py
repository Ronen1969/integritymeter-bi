"""
config.py — Supabase clients, logging, and app-wide configuration.

NOTE: This module calls st.set_page_config() at import time.
It MUST be the first import in app.py.
"""
import streamlit as st
from supabase import create_client
import logging

# Page config — must be the very first Streamlit call
st.set_page_config(page_title="IntegrityMeter BI", layout="wide")

logger = logging.getLogger("integritymeter")

# Credentials loaded from Streamlit secrets — never hardcoded
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = st.secrets.get("SUPABASE_SERVICE_KEY", "")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    st.error(
        "⚠️ Configuração ausente: SUPABASE_URL e SUPABASE_ANON_KEY devem ser "
        "definidos em Settings > Secrets no Streamlit Cloud."
    )
    st.stop()


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
