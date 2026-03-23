"""
tabs/reports.py — Tab 3: Relatórios.
"""
import io
from datetime import datetime, date

import pandas as pd
import streamlit as st

from models import status_dot_text, status_key_to_label


def render_reports(all_deals: list) -> None:
    st.header("Relatórios")

    # ── Date range filter ────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns(2)
    filter_start = col_f1.date_input(
        "De:",
        value=date(date.today().year, 1, 1),
        format="DD/MM/YYYY",
        key="report_start",
    )
    filter_end = col_f2.date_input(
        "Até:",
        value=date.today(),
        format="DD/MM/YYYY",
        key="report_end",
    )

    def _in_range(d: dict) -> bool:
        try:
            return filter_start <= datetime.fromisoformat(d['created_at'][:10]).date() <= filter_end
        except (ValueError, TypeError, KeyError):
            return True

    filtered_deals = [d for d in all_deals if _in_range(d)]

    if not filtered_deals and all_deals:
        st.warning("Nenhum negócio encontrado no período selecionado.")
        return

    report_type = st.radio(
        "Tipo de Relatório:",
        ["Negócios Concluídos", "Rentabilidade por Cliente", "Todos os Negócios"],
        horizontal=True,
    )

    if report_type == "Negócios Concluídos":
        _render_closed(filtered_deals)
    elif report_type == "Rentabilidade por Cliente":
        _render_by_client(filtered_deals)
    elif report_type == "Todos os Negócios":
        _render_all(filtered_deals)


# ── Sub-reports ───────────────────────────────────────────────────────────────

def _render_closed(all_deals: list) -> None:
    closed = [d for d in all_deals if d['status'] == 'concluido']
    if not closed:
        st.warning("Nenhum negócio concluído encontrado.")
        return

    cdf = pd.DataFrame(closed)
    cdf['client_name'] = cdf['clients'].apply(lambda c: c.get('name', '?') if c else '?')
    for c in ['v_real', 'profit', 'cost_usd', 'margin']:
        cdf[c] = cdf[c].astype(float)
    cdf['qty'] = cdf['qty'].astype(int)

    tc = 'closed_at' if cdf['closed_at'].notna().any() else 'created_at'
    cdf['ts']         = pd.to_datetime(cdf[tc], errors='coerce')
    cdf['month_name'] = cdf['ts'].dt.strftime('%Y-%m')
    cdf['year']       = cdf['ts'].dt.year
    cdf['week_start'] = cdf['ts'].dt.to_period('W').apply(lambda r: r.start_time)

    tr, tpr, tdl, tt = cdf['v_real'].sum(), cdf['profit'].sum(), len(cdf), cdf['qty'].sum()
    am = (tpr / tr * 100) if tr > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    for col, lbl, val in [
        (k1, "Vendas",       str(tdl)),
        (k2, "Faturamento",  f"R$ {tr:,.0f}"),
        (k3, "Lucro",        f"R$ {tpr:,.0f}"),
        (k4, "Margem",       f"{am:.1f}%"),
        (k5, "Testes",       f"{tt:,}"),
    ]:
        col.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div>"
            f"<div class='kpi-value'>{val}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    view  = st.radio("Período:", ["Semanal", "Mensal", "Anual"], horizontal=True, key="report_period")
    gcol  = {'Semanal': 'week_start', 'Mensal': 'month_name', 'Anual': 'year'}[view]
    g     = cdf.groupby(gcol).agg(
        Vendas=('v_real', 'sum'),
        Lucro=('profit', 'sum'),
        Projetos=('id', 'count'),
        Testes=('qty', 'sum'),
    ).reset_index()
    g.columns = ['Período', 'Vendas (R$)', 'Lucro (R$)', 'Projetos', 'Testes']
    if view == 'Semanal':
        g['Período'] = g['Período'].dt.strftime('%d/%m/%Y')
    g['Margem (%)'] = (g['Lucro (R$)'] / g['Vendas (R$)'] * 100).round(1)

    st.dataframe(g.sort_values('Período', ascending=False), use_container_width=True, hide_index=True)
    st.bar_chart(g.set_index('Período')[['Vendas (R$)', 'Lucro (R$)']])

    st.markdown("---")
    st.subheader("Exportar")
    disp = cdf[['ts', 'client_name', 'qty', 'cost_usd', 'v_real', 'profit', 'margin']].copy()
    disp.columns = ['Data', 'Cliente', 'Qtd', 'Custo USD', 'Venda R$', 'Lucro R$', 'Margem (%)']
    disp['Data'] = disp['Data'].dt.strftime('%d/%m/%Y')

    e1, e2 = st.columns(2)
    with e1:
        buf = io.StringIO()
        disp.to_csv(buf, index=False)
        st.download_button("Baixar CSV", buf.getvalue(),
                           f"integrity_{date.today()}.csv", "text/csv")
    with e2:
        try:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w:
                disp.to_excel(w, sheet_name='Todos', index=False)
                g.to_excel(w, sheet_name=view, index=False)
            st.download_button(
                "Baixar Excel", buf.getvalue(),
                f"integrity_{date.today()}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except ImportError:
            st.warning("pip install openpyxl")


def _render_by_client(all_deals: list) -> None:
    if not all_deals:
        st.warning("Nenhum negócio cadastrado.")
        return

    rdf = pd.DataFrame(all_deals)
    rdf['client_name'] = rdf['clients'].apply(lambda c: c.get('name', '?') if c else '?')
    for c in ['v_real', 'profit', 'margin', 'cost_usd']:
        rdf[c] = rdf[c].astype(float)
    rdf['qty'] = rdf['qty'].astype(int)

    summary = rdf.groupby('client_name').agg(
        total_vendas=('v_real', 'sum'),
        total_lucro=('profit', 'sum'),
        total_testes=('qty', 'sum'),
        num_negocios=('id', 'count'),
        margem_media=('margin', 'mean'),
        custo_medio_usd=('cost_usd', 'mean'),
    ).sort_values('total_lucro', ascending=False).reset_index()

    summary.columns = ['Cliente', 'Vendas (R$)', 'Lucro (R$)', 'Testes', 'Negócios', 'Margem (%)', 'Custo Médio USD']
    summary['Vendas (R$)']      = summary['Vendas (R$)'].apply(lambda x: f"R$ {x:,.2f}")
    summary['Lucro (R$)']       = summary['Lucro (R$)'].apply(lambda x: f"R$ {x:,.2f}")
    summary['Margem (%)']       = summary['Margem (%)'].apply(lambda x: f"{x:.1f}%")
    summary['Custo Médio USD']  = summary['Custo Médio USD'].apply(lambda x: f"$ {x:.2f}")

    st.dataframe(summary, use_container_width=True, hide_index=True)

    buf = io.StringIO()
    summary.to_csv(buf, index=False)
    st.download_button("Exportar CSV", buf.getvalue(),
                       f"clientes_{date.today()}.csv", "text/csv")


def _render_all(all_deals: list) -> None:
    if not all_deals:
        st.warning("Nenhum negócio cadastrado.")
        return

    rows = [{
        'Status':     f"{status_dot_text(d['status'])} {status_key_to_label(d['status'])}",
        'Cliente':    (d.get('clients', {}) or {}).get('name', '?'),
        'Qtd':        d['qty'],
        'Custo USD':  f"$ {float(d['cost_usd']):.2f}",
        'Venda R$':   f"R$ {float(d['v_real']):,.2f}",
        'Lucro R$':   f"R$ {float(d['profit']):,.2f}",
        'Margem':     f"{float(d['margin']):.1f}%",
        'Criado por': d.get('created_by_email', ''),
        'Data':       datetime.fromisoformat(d['created_at'][:10]).strftime('%d/%m/%Y')
                      if d.get('created_at') else '',
    } for d in all_deals]

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    buf = io.StringIO()
    df.to_csv(buf, index=False)
    st.download_button("Exportar CSV", buf.getvalue(),
                       f"todos_negocios_{date.today()}.csv", "text/csv")
