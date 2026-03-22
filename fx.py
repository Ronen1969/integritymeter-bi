"""
fx.py — FX rate fetching, caching, history, and deal data cache.
"""
import json
import urllib.request
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import yfinance as yf

from config import sb, logger


# ── Live FX rate ─────────────────────────────────────────────────────────────

def get_live_fx() -> float:
    """Fetch live USD/BRL rate with three fallback sources. Saves snapshot to DB."""
    rate = None
    source = None

    # Source 1: yfinance
    try:
        ticker = yf.Ticker("USDBRL=X")
        rate   = float(ticker.fast_info['last_price'])
        source = 'yfinance'
    except Exception as e:
        logger.warning(f"FX yfinance failed: {e}")

    # Source 2: exchangerate-api.com
    if rate is None:
        try:
            url = "https://open.er-api.com/v6/latest/USD"
            req = urllib.request.Request(url, headers={'User-Agent': 'IntegrityMeter/1.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get('result') == 'success' and 'BRL' in data.get('rates', {}):
                    rate   = float(data['rates']['BRL'])
                    source = 'exchangerate-api'
        except Exception as e:
            logger.warning(f"FX exchangerate-api failed: {e}")

    # Source 3: frankfurter.app (ECB data)
    if rate is None:
        try:
            url = "https://api.frankfurter.app/latest?from=USD&to=BRL"
            req = urllib.request.Request(url, headers={'User-Agent': 'IntegrityMeter/1.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if 'rates' in data and 'BRL' in data['rates']:
                    rate   = float(data['rates']['BRL'])
                    source = 'frankfurter'
        except Exception as e:
            logger.warning(f"FX frankfurter failed: {e}")

    if rate is not None:
        try:
            sb.table('fx_snapshots').insert({'rate': rate, 'source': source}).execute()
        except Exception as e:
            logger.error(f"FX snapshot save failed: {e}")
        return rate

    # Final fallback: last DB snapshot
    try:
        res = sb.table('fx_snapshots').select('rate').order('created_at', desc=True).limit(1).execute()
        if res.data:
            return float(res.data[0]['rate'])
    except Exception as e:
        logger.error(f"FX DB fallback failed: {e}")

    return 5.30


def get_cached_fx() -> float:
    """Return cached rate if fresh (< 10 min), otherwise fetch live."""
    try:
        res = sb.table('fx_snapshots').select('rate,created_at') \
                .order('created_at', desc=True).limit(1).execute()
        if res.data:
            cached_time = datetime.fromisoformat(
                res.data[0]['created_at'].replace('Z', '+00:00')
            )
            if (datetime.now(cached_time.tzinfo) - cached_time).total_seconds() < 600:
                return float(res.data[0]['rate'])
    except Exception as e:
        logger.warning(f"FX cache check failed: {e}")
    return get_live_fx()


# ── Deal cache ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def _fetch_all_deals() -> list:
    """Cached deal fetcher — TTL 30 s to reduce DB calls on every interaction."""
    try:
        res = sb.table('deals').select('*, clients(name, notes)') \
                .order('updated_at', desc=True).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Failed to fetch deals: {e}")
        return []


def invalidate_deals_cache() -> None:
    """Call after any deal write to force a fresh fetch on next load."""
    _fetch_all_deals.clear()


# ── FX history ───────────────────────────────────────────────────────────────

def get_fx_history(days: int = 30) -> pd.DataFrame:
    """Return a DataFrame of FX snapshots for the last N days."""
    try:
        since = (datetime.now() - timedelta(days=days)).isoformat()
        res   = sb.table('fx_snapshots').select('rate,created_at') \
                  .gte('created_at', since).order('created_at').execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['rate']       = df['rate'].astype(float)
            return df
    except Exception as e:
        logger.warning(f"FX history fetch failed: {e}")
    return pd.DataFrame()
