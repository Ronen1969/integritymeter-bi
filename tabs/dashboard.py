"""
tabs/dashboard.py — Tab 0: Painel Principal (Dashboard).
"""
from datetime import datetime

import pandas as pd
import streamlit as st

from data import save_setting
from models import status_key_to_label


def render_dashboard(all_deals: list, sidebar_cfg: dict) -> None:
    st.header("Painel Principal")

    if not all_deals:
        st.info(
            "Bem-vindo! Comece adicionando seu primeiro negócio na aba 'Novo Negócio' acima."
        )
        return

    df_all = pd.DataFrame(all_deals)
    df_all['client_name'] = df_all['clients'].apply(
        lambda c: c.get('name', '?') if c else '?'
    )
    for col in ['v_real', 'profit', 'margin', 'cost_usd']:
        df_all[col] = df_all[col].astype(float)
    df_all['qty']            = df_all['qty'].astype(int)
    df_all['created_at_dt'] = pd.to_datetime(df_all['created_at'], utc=True)

    now         = pd.Timestamp.now(tz='UTC')
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    df_month    = df_all[df_all['created_at_dt'] >= month_start]
    df_active   = df_all[~df_all['status'].isin(['concluido', 'perdido'])]
    df_won      = df_all[df_all['status'] == 'concluido']
    df_lost     = df_all[df_all['status'] == 'perdido']

    # ── KPI row ──────────────────────────────────────────────────────────────
    total_pipeline = df_active['v_real'].sum()
    total_won      = df_won['v_real'].sum()
    total_profit   = df_won['profit'].sum()
    month_deals    = len(df_month)
    win_rate       = (
        len(df_won) / (len(df_won) + len(df_lost)) * 100
        if (len(df_won) + len(df_lost)) > 0 else 0
    )
    avg_margin = df_won['margin'].mean() if not df_won.empty else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    for col, lbl, val in [
        (k1, "Pipeline Ativo",    f"R$ {total_pipeline:,.0f}"),
        (k2, "Total Ganho",       f"R$ {total_won:,.0f}"),
        (k3, "Lucro Total",       f"R$ {total_profit:,.0f}"),
        (k4, "Negócios este Mês", str(month_deals)),
        (k5, "Taxa Conversão",    f"{win_rate:.0f}%"),
        (k6, "Margem Média",      f"{avg_margin:.1f}%"),
    ]:
        col.markdown(
            f"<div class='kpi-card'>"
            f"<div class='kpi-label'>{lbl}</div>"
            f"<div class='kpi-value'>{val}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Monthly targets + trend ──────────────────────────────────────────────
    col_target, col_alerts = st.columns([1, 1], gap="large")

    with col_target:
        st.subheader("Meta Mensal")
        month_target = st.number_input(
            "Meta de Vendas (R$)",
            value=st.session_state._saved_month_target,
            min_value=0.0, step=5_000.0, format="%.0f",
            key="month_target",
            help="Clique +/- para ajustar em R$ 5.000 ou digite o valor desejado",
        )
        if month_target != st.session_state._saved_month_target:
            save_setting('month_target', month_target)
            st.session_state._saved_month_target = month_target

        month_won    = df_won[df_won['created_at_dt'] >= month_start]['v_real'].sum() if not df_won.empty else 0
        month_profit = df_won[df_won['created_at_dt'] >= month_start]['profit'].sum() if not df_won.empty else 0
        progress_pct = min(month_won / month_target * 100, 100) if month_target > 0 else 0
        bar_color    = "#059669" if progress_pct >= 80 else "#D97706" if progress_pct >= 50 else "#DC2626"

        st.markdown(f"""
        <div style='margin:8px 0;'>
            <div style='display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;'>
                <span>R$ {month_won:,.0f} de R$ {month_target:,.0f}</span>
                <span style='font-weight:700;color:{bar_color};'>{progress_pct:.0f}%</span>
            </div>
            <div class='target-progress'>
                <div class='target-bar' style='width:{max(progress_pct, 2)}%;background:{bar_color};'></div>
            </div>
            <div style='font-size:12px;color:#6B7280;margin-top:4px;'>
                Lucro no mês: <strong>R$ {month_profit:,.0f}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Tendência Mensal")
        df_all['month'] = df_all['created_at_dt'].dt.to_period('M').astype(str)
        monthly = df_all.groupby('month').agg(
            Vendas=('v_real', 'sum'),
            Lucro=('profit', 'sum'),
            Negócios=('id', 'count'),
        ).reset_index()
        monthly.columns = ['Mês', 'Vendas (R$)', 'Lucro (R$)', 'Negócios']
        if len(monthly) > 1:
            st.bar_chart(monthly.set_index('Mês')[['Vendas (R$)', 'Lucro (R$)']])
        else:
            st.dataframe(monthly, use_container_width=True, hide_index=True)

    # ── Alerts & insights ───────────────────────────────────────────────────
    with col_alerts:
        st.subheader("Alertas & Insights")
        alerts = []  # (priority, html) — 1=danger, 2=warning, 3=info

        for deal in all_deals:
            if deal['status'] in ['concluido', 'perdido']:
                continue
            cn      = (deal.get('clients', {}) or {}).get('name', '?')
            created = datetime.fromisoformat(deal['created_at'].replace('Z', '+00:00'))
            age     = (datetime.now(created.tzinfo) - created).days
            if age >= 14:
                alerts.append((1, f"<div class='alert-card alert-danger'>⏰ <strong>{cn}</strong> — {age} dias sem movimentação. Ação: entre em contato ou marque como perdido.</div>"))
            elif age >= 7:
                alerts.append((2, f"<div class='alert-card alert-warning'>⏳ <strong>{cn}</strong> — {age} dias parado ({status_key_to_label(deal['status'])}). Considere fazer follow-up.</div>"))

        for deal in all_deals:
            if deal['status'] in ['concluido', 'perdido']:
                continue
            mg = float(deal.get('margin', 0))
            cn = (deal.get('clients', {}) or {}).get('name', '?')
            if 0 < mg < 15:
                alerts.append((2, f"<div class='alert-card alert-warning'>📉 <strong>{cn}</strong> — margem baixa ({mg:.0f}%). Revise preço ou custos.</div>"))

        fx = st.session_state.dolar_live
        if fx >= 5.50:
            alerts.append((2, f"<div class='alert-card alert-warning'>💵 Dólar alto: R$ {fx:.3f} — seus custos em BRL estão elevados. Considere reajustar preços.</div>"))
        elif fx <= 4.80:
            alerts.append((3, f"<div class='alert-card alert-info'>💵 Dólar baixo: R$ {fx:.3f} — bom momento para fechar negócios com margem alta.</div>"))

        if month_target > 0:
            if progress_pct >= 100:
                alerts.append((3, f"<div class='alert-card alert-info' style='background:#F0FDF4;border-color:#BBF7D0;color:#166534;'>🎯 Meta atingida! R$ {month_won:,.0f} de R$ {month_target:,.0f}. Parabéns!</div>"))
            elif progress_pct < 30 and now.day > 15:
                alerts.append((1, f"<div class='alert-card alert-danger'>🎯 Meta em risco: apenas {progress_pct:.0f}% da meta e já passou da metade do mês.</div>"))

        if month_deals == 0:
            alerts.append((2, "<div class='alert-card alert-warning'>📋 Nenhum negócio criado este mês. Hora de prospectar!</div>"))

        if not df_active.empty and len(df_active) > 1:
            client_totals = df_active.groupby('client_name')['v_real'].sum()
            pipeline_total = client_totals.sum()
            if pipeline_total > 0:
                top_client = client_totals.idxmax()
                top_pct    = client_totals.max() / pipeline_total * 100
                if top_pct > 50:
                    alerts.append((2, f"<div class='alert-card alert-warning'>⚠️ <strong>{top_client}</strong> representa {top_pct:.0f}% do pipeline. Diversifique sua carteira.</div>"))

        alerts.sort(key=lambda x: x[0])
        if alerts:
            for _, html in alerts:
                st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown(
                "<div class='alert-card alert-info' style='background:#F0FDF4;"
                "border-color:#BBF7D0;color:#166534;'>✅ Tudo em dia! Nenhum alerta no momento.</div>",
                unsafe_allow_html=True,
            )

        # Top clients
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Clientes Mais Rentáveis")
        if not df_won.empty:
            client_rank = df_won.groupby('client_name').agg(
                total_profit=('profit', 'sum'),
                total_revenue=('v_real', 'sum'),
                deals=('id', 'count'),
                avg_margin=('margin', 'mean'),
            ).sort_values('total_profit', ascending=False).head(5)

            for i, (name, row) in enumerate(client_rank.iterrows(), 1):
                st.markdown(f"""<div class='client-rank'>
                    <div class='rank-num'>#{i}</div>
                    <div style='flex:1;'>
                        <div style='font-weight:600;'>{name}</div>
                        <div style='font-size:12px;color:#6B7280;'>
                            {int(row['deals'])} neg. | Margem: {row['avg_margin']:.1f}%
                        </div>
                    </div>
                    <div style='text-align:right;'>
                        <div style='font-weight:700;color:#8DAE10;'>R$ {row['total_profit']:,.0f}</div>
                        <div style='font-size:11px;color:#6B7280;'>de R$ {row['total_revenue']:,.0f}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Conclua negócios para ver o ranking.")
