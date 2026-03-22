"""
styles.py — CSS design system and global JS helpers.
Call apply_styles() once at app startup.
"""
import streamlit as st
import streamlit.components.v1 as components


def apply_styles() -> None:
    """Inject the IntegrityMeter design system CSS."""
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }
[data-testid="stSidebar"] {
    background-color: #FFFFFF; border-right: 1px solid #F3F4F6;
    width: 280px !important; min-width: 280px !important;
    transition: margin-left 0.3s ease, opacity 0.3s ease;
}
.stButton>button {
    background-color: #8DAE10 !important; color: white !important;
    border-radius: 10px !important; min-height: 45px; height: auto;
    padding: 10px 20px !important; font-weight: 600 !important;
    border: none !important; white-space: normal !important;
    line-height: 1.4 !important;
}
.main-card {
    padding: 30px; border-radius: 16px; background-color: #FFFFFF;
    border: 1px solid #F3F4F6;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.02);
}
.loaded-banner {
    padding: 10px 16px; border-radius: 8px; background-color: #F0FDF4;
    border: 1px solid #BBF7D0; color: #166534; font-weight: 500; margin-bottom: 8px;
}
.kpi-card {
    padding: 16px; border-radius: 12px;
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
    border: 1px solid #e2e8f0; text-align: center;
}
.kpi-value  { font-size: 28px; font-weight: 700; color: #8DAE10; margin: 4px 0; }
.kpi-label  { font-size: 11px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; }
.funnel-row { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
.funnel-bar {
    height: 24px; border-radius: 4px; background: #8DAE10;
    display: flex; align-items: center; padding: 0 8px;
    color: white; font-size: 11px; font-weight: 600;
}
.user-badge {
    padding: 6px 12px; border-radius: 20px; background: #F0FDF4;
    color: #166534; font-size: 12px; font-weight: 600;
    display: inline-block; margin-bottom: 8px;
}
.alert-card    { padding: 12px 16px; border-radius: 10px; margin: 6px 0; font-size: 13px; }
.alert-warning { background: #FFF7ED; border: 1px solid #FDBA74; color: #9A3412; }
.alert-danger  { background: #FEF2F2; border: 1px solid #FCA5A5; color: #991B1B; }
.alert-info    { background: #EFF6FF; border: 1px solid #93C5FD; color: #1E40AF; }
.target-progress { background: #f1f5f9; border-radius: 10px; height: 20px; overflow: hidden; }
.target-bar {
    height: 100%; border-radius: 10px;
    display: flex; align-items: center; padding: 0 8px;
    font-size: 11px; font-weight: 600; color: white;
}
.client-rank {
    display: flex; align-items: center; gap: 12px; padding: 10px;
    border-radius: 8px; background: #f8fafc; border: 1px solid #e2e8f0; margin: 4px 0;
}
.rank-num { font-size: 20px; font-weight: 700; color: #8DAE10; min-width: 30px; }
.stColumn:has(> div > div > .stButton) .stButton > button {
    min-height: 36px !important; padding: 4px 8px !important;
}
</style>
""", unsafe_allow_html=True)

    # Auto-select number inputs on focus + disable zero-height iframes
    components.html("""
<script>
var doc = window.parent.document;
doc.addEventListener('focusin', function(e) {
    if (e.target && e.target.tagName === 'INPUT' && e.target.type === 'number') {
        setTimeout(function() { e.target.select(); }, 50);
    }
});
(function disableIframes() {
    doc.querySelectorAll('iframe').forEach(function(f) {
        if (f.height === '0' || f.style.height === '0px' || f.getBoundingClientRect().height < 2) {
            f.style.pointerEvents = 'none';
        }
    });
})();
new MutationObserver(function() {
    doc.querySelectorAll('iframe').forEach(function(f) {
        if (f.height === '0' || f.style.height === '0px' || f.getBoundingClientRect().height < 2) {
            f.style.pointerEvents = 'none';
        }
    });
}).observe(doc.body, {childList: true, subtree: true});
</script>
""", height=0)
