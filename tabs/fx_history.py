"""
tabs/fx_history.py — Tab 4: Histórico do Câmbio USD/BRL.
"""
import pandas as pd
import streamlit as st

from fx import get_fx_history


def render_fx_history(all_deals: list, sidebar_cfg: dict) -> None:
    total_tax_pct = sidebar_cfg['total_tax_pct']

    st.header("Histórico do Câmbio USD/BRL")

    fx_period = st.radio("Período:", ["7 dias", "30 dias", "90 dias"],
                         horizontal=True, key="fx_period")
    days_map  = {"7 dias": 7, "30 dias": 30, "90 dias": 90}
    fx_df     = get_fx_history(days_map[fx_period])

    col1, col2, col3 = st.columns(3)
    col1.markdown(
        f"<div class='kpi-card'><div class='kpi-label'>Atual</div>"
        f"<div class='kpi-value'>R$ {st.session_state.dolar_live:.3f}</div></div>",
        unsafe_allow_html=True,
    )

    if not fx_df.empty:
        fx_min = fx_df['rate'].min()
        fx_max = fx_df['rate'].max()
        fx_avg = fx_df['rate'].mean()

        col2.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Mín / Máx</div>"
            f"<div class='kpi-value'>R$ {fx_min:.3f} / {fx_max:.3f}</div></div>",
            unsafe_allow_html=True,
        )
        col3.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Média</div>"
            f"<div class='kpi-value'>R$ {fx_avg:.3f}</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.line_chart(fx_df.set_index('created_at')[['rate']].rename(columns={'rate': 'USD/BRL'}))

        # FX impact simulation on active deals
        st.markdown("---")
        st.subheader("Impacto do Câmbio nos Negócios")
        st.caption("Simulação: como seus negócios ativos seriam afetados por variações no câmbio.")

        active = [d for d in all_deals if d['status'] not in ['concluido', 'perdido']]
        if active:
            sim_rates  = [fx_min, fx_avg, st.session_state.dolar_live, fx_max]
            sim_labels = [
                f"Mínimo (R$ {fx_min:.3f})",
                f"Média (R$ {fx_avg:.3f})",
                f"Atual (R$ {st.session_state.dolar_live:.3f})",
                f"Máximo (R$ {fx_max:.3f})",
            ]
            sim_data = []
            for rate, label in zip(sim_rates, sim_labels):
                total_cost   = sum(float(d['qty']) * float(d['cost_usd']) * rate for d in active)
                total_rev    = sum(float(d['v_real']) for d in active)
                total_tax    = total_rev * total_tax_pct / 100
                total_profit = total_rev - total_cost - total_tax
                sim_data.append({
                    'Cenário':           label,
                    'Custo Total (BRL)': f"R$ {total_cost:,.0f}",
                    'Lucro Projetado':   f"R$ {total_profit:,.0f}",
                })
            st.dataframe(pd.DataFrame(sim_data), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum negócio ativo para simular.")

    else:
        col2.markdown(
            "<div class='kpi-card'><div class='kpi-label'>Mín / Máx</div>"
            "<div class='kpi-value'>—</div></div>",
            unsafe_allow_html=True,
        )
        col3.markdown(
            "<div class='kpi-card'><div class='kpi-label'>Média</div>"
            "<div class='kpi-value'>—</div></div>",
            unsafe_allow_html=True,
        )
        st.info("Dados de câmbio ainda estão sendo coletados. Volte em breve!")
