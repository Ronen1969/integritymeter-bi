""" styles.py â CSS design system and global JS helpers. Call apply_styles() once at app startup. """
import streamlit as st
import streamlit.components.v1 as components


def apply_styles() -> None:
    """Inject the IntegrityMeter design system CSS."""
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #FFFFFF;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #F3F4F6;
    width: 280px !important;
    min-width: 280px !important;
    transition: margin-left 0.3s ease, opacity 0.3s ease;
}

/* Hide the zero-height components.html iframe label (keep iframe alive for JS) */
[data-testid="stCustomComponentV1"] {
    position: absolute !important;
    top: -9999px !important;
    left: -9999px !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
    pointer-events: none !important;
    opacity: 0 !important;
}

/* ââ Sidebar collapse: main content fills the freed space ââ */
[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 0 !important;
    max-width: 0 !important;
    flex: 0 0 0 !important;
    overflow: hidden !important;
    transition: min-width 0.3s ease, max-width 0.3s ease, flex 0.3s ease !important;
}
[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stAppViewContainer"] {
    padding-left: 0 !important;
    margin-left: 0 !important;
    width: 100% !important;
    transition: padding-left 0.3s ease, margin-left 0.3s ease !important;
}

.stButton>button {
    background-color: #8DAE10 !important;
    color: white !important;
    border-radius: 10px !important;
    min-height: 45px;
    height: auto;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    border: none !important;
    white-space: normal !important;
    line-height: 1.4 !important;
}

.main-card {
    padding: 30px;
    border-radius: 16px;
    background-color: #FFFFFF;
    border: 1px solid #F3F4F6;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.02);
}

.loaded-banner {
    padding: 10px 16px;
    border-radius: 8px;
    background-color: #F0FDF4;
    border: 1px solid #BBF7D0;
    color: #166534;
    font-weight: 500;
    margin-bottom: 8px;
}

.kpi-card {
    padding: 10px 8px;
    border-radius: 12px;
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
    border: 1px solid #e2e8f0;
    text-align: center;
    height: 90px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    box-sizing: border-box;
    width: 100%;
}
.kpi-value {
    font-size: clamp(14px, 1.6vw, 20px);
    font-weight: 700;
    color: #8DAE10;
    margin: 2px 0;
    line-height: 1.2;
    overflow-wrap: break-word;
    word-break: break-word;
    max-width: 100%;
}
.kpi-label {
    font-size: clamp(8px, 0.75vw, 10px);
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    line-height: 1.2;
    overflow-wrap: anywhere;
    word-break: break-word;
    max-width: 100%;
    margin-bottom: 2px;
}

.funnel-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 4px 0;
}
.funnel-bar {
    height: 24px;
    border-radius: 4px;
    background: #8DAE10;
    display: flex;
    align-items: center;
    padding: 0 8px;
    color: white;
    font-size: 11px;
    font-weight: 600;
}

.user-badge {
    padding: 6px 12px;
    border-radius: 20px;
    background: #F0FDF4;
    color: #166534;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 8px;
}

.alert-card {
    padding: 12px 16px;
    border-radius: 10px;
    margin: 6px 0;
    font-size: 13px;
}
.alert-warning { background: #FFF7ED; border: 1px solid #FDBA74; color: #9A3412; }
.alert-danger  { background: #FEF2F2; border: 1px solid #FCA5A5; color: #991B1B; }
.alert-info    { background: #EFF6FF; border: 1px solid #93C5FD; color: #1E40AF; }

.target-progress {
    background: #f1f5f9;
    border-radius: 10px;
    height: 20px;
    overflow: hidden;
}
.target-bar {
    height: 100%;
    border-radius: 10px;
    display: flex;
    align-items: center;
    padding: 0 8px;
    font-size: 11px;
    font-weight: 600;
    color: white;
}

.client-rank {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px;
    border-radius: 8px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    margin: 4px 0;
}
.rank-num {
    font-size: 20px;
    font-weight: 700;
    color: #8DAE10;
    min-width: 30px;
}

/* ââ Unified deal card (Ghost Button Pattern) ââ */
.deal-card {
    display: flex;
    align-items: center;
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid #E8ECF0;
    margin: 3px 0;
    background: #FFFFFF;
    gap: 12px;
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
    position: relative;
    min-height: 56px;
}
.deal-card:hover {
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border-color: #C8D0D8;
    background: #FAFBFC;
}
.deal-mv {
    font-weight: 600;
    font-size: 13px;
    line-height: 1.3;
    color: #111827;
}
.deal-actions {
    display: flex;
    gap: 1px;
    opacity: 0;
    transition: opacity 0.12s ease;
    flex-shrink: 0;
    margin-left: 6px;
}
.deal-card:hover .deal-actions {
    opacity: 1;
}
.deal-action-btn {
    background: transparent;
    border: none;
    outline: none;
    cursor: pointer;
    width: 26px;
    height: 26px;
    border-radius: 5px;
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #6B7280;
    transition: background 0.1s ease, color 0.1s ease;
    padding: 0;
    line-height: 1;
    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif;
}
.deal-action-btn:hover {
    background: #EEF2F7;
    color: #374151;
}
.deal-action-del:hover {
    background: #FEE2E2;
    color: #DC2626;
}

/* Ghost Streamlit buttons â invisible, triggered via JS */
[class*="st-key-icon_"] {
    height: 0 !important;
    overflow: hidden !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 0 !important;
}

/* ââ Normalize filter-row widget heights ââ */
[data-testid="stMultiSelect"] > div,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input {
    min-height: 42px !important;
    box-sizing: border-box !important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child {
    min-height: 42px !important;
    align-items: center;
    border-radius: 8px !important;
    border-color: #e2e8f0 !important;
}
/* Fix: multiselect inner value-container clips placeholder text via overflow:hidden. */
[data-testid="stMultiSelect"] [data-baseweb="select"] > div > div:first-child,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div > div:first-child > div {
    overflow: visible !important;
}
[data-testid="stTextInput"] > div > div,
[data-testid="stDateInput"] > div > div {
    border-radius: 8px !important;
    border-color: #e2e8f0 !important;
}

/* ââ Responsive Streamlit columns: no wrap at any zoom ââ */
[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: 0.5rem !important;
}
[data-testid="stColumn"] {
    min-width: 0 !important;
    flex: 1 1 0 !important;
}
</style>
""", unsafe_allow_html=True)

    # Auto-select number inputs on focus
    # Inject __triggerDeal on parent window so HTML card onclick buttons work
    components.html("""
<script>
var doc = window.parent.document;

doc.addEventListener('focusin', function(e) {
    if (e.target && e.target.tagName === 'INPUT' && e.target.type === 'number') {
        setTimeout(function() { e.target.select(); }, 50);
    }
});

// ââ Ghost button bridge ââ
// Defines window.__triggerDeal() on the Streamlit parent window.
// HTML deal cards call this via onclick; it clicks the hidden Streamlit button.
function registerTrigger() {
    window.parent.__triggerDeal = function(dealId, action) {
        var key = 'icon_' + action + '_' + dealId;
        var container = doc.querySelector('[class*="st-key-' + key + '"]');
        if (container) {
            var btn = container.querySelector('button');
            if (btn) btn.click();
        }
    };
}
registerTrigger();

// Re-register + disable zero-height iframes on every DOM mutation
new MutationObserver(function() {
    registerTrigger();
    doc.querySelectorAll('iframe').forEach(function(f) {
        if (f.height === '0' || f.style.height === '0px' || f.getBoundingClientRect().height < 2) {
            f.style.pointerEvents = 'none';
        }
    });
}).observe(doc.body, {childList: true, subtree: true});
</script>
""", height=0)
