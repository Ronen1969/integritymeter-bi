"""
data.py — User settings persistence (app_settings Supabase table).
"""
from datetime import datetime

import streamlit as st

from config import sb, logger


def get_setting(key: str, default: str = "") -> str:
    """Load a per-user setting from the app_settings table."""
    try:
        uid = str(st.session_state.user.id)
        res = sb.table('app_settings').select('value') \
                .eq('user_id', uid).eq('key', key).execute()
        if res.data:
            return res.data[0]['value']
    except Exception as e:
        logger.warning(f"Setting load failed ({key}): {e}")
    return default


def save_setting(key: str, value) -> None:
    """Persist a per-user setting via upsert."""
    try:
        uid = str(st.session_state.user.id)
        sb.table('app_settings').upsert(
            {
                'user_id':    uid,
                'key':        key,
                'value':      str(value),
                'updated_at': datetime.now().isoformat(),
            },
            on_conflict='user_id,key',
        ).execute()
    except Exception as e:
        logger.error(f"Setting save failed ({key}): {e}")
