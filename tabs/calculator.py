"""
tabs/calculator.py — Tab 1: Novo Negócio / Margin Calculator.
"""
from datetime import datetime, date

import streamlit as st

from config import sb
from fx import invalidate_deals_cache
from models import STATUS_LABELS, STATUS_KEYS, status_label_to_key
from state import clear_form


def render_calculator(all_deals: list, sidebar_cfg: dict) -> None:
    tax_p         = sidebar_cfg['tax_p']
    adm_p         = sidebar_cfg['adm_p']
    total_tax_pct = sidebar_cfg['total_tax_pct']
    default_cost  = sidebar_cfg['default_cost_usd']

    is_editing = st.session_state.selected_deal_id is not None

    if st.session_state.just_loaded:
        st.markdown(
            f"<div class='loaded-banner'>Editando negócio: "
            f"<strong>{st.session_state.form_client}</strong>"
            f" — altere os dados e clique \"Atualizar Negócio\"</div>",
            unsafe_allow_html=True,
        )
        st.session_state.just_loaded = False
    elif not is_editing:
        st.markdown(
            "<div style='padding:12px 16px;border-radius:8px;background:#EFF6FF;"
            "border:1px solid #93C5FD;color:#1E40AF;font-size:14px;margin-bottom:12px;'>"
            "Preencha os dados abaixo para simular a margem e criar um novo negócio."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='loaded-banner'>Editando: "
            f"<strong>{st.session_state.form_client}</strong></div>",
            unsafe_allow_html=True,
        )

    col_in, col_out = st.columns([1.8, 1], gap="large")

    with col_in:
        i1, i2 = st.columns(2)
        client_name = i1.text_input(
            "Cliente", key="form_client",
            help="Nome da empresa ou pessoa jurídica contratante",
        )
        status_deal = i2.selectbox("Status", STATUS_LABELS, index=st.session_state.form_status_idx)

        i3, i4 = st.columns(2)
        deal_date = i3.date_input("Data", key="form_date", format="DD/MM/YYYY")
        qty       = i4.number_input("Qtd Testes", key="form_qty", min_value=0, step=1)

        i5, i6 = st.columns(2)
        if st.session_state.form_cost == 0.0 and not is_editing:
            st.session_state.form_cost = default_cost
        cost = i5.number_input(
            "Custo Unit. (USD)", key="form_cost", min_value=0.0, step=0.5, format="%.2f",
            help="Padrão da config. lateral — editável por negócio",
        )
        unit_price = i6.number_input(
            "Preço Unit. (R$)", key="form_unit_price", min_value=0.0, step=5.0, format="%.2f",
            help="Preço por teste cobrado do cliente",
        )

        if unit_price > 0 and qty > 0:
            st.session_state.form_vreal = round(unit_price * qty, 2)

        v_real = st.number_input(
            "Valor Total (R$)", key="form_vreal", min_value=0.0, step=100.0, format="%.2f",
            help="Calculado automaticamente: Preço Unit. × Qtd",
        )
        notes = st.text_area("Notas", key="form_notes", height=68)

    # ── Calculations ─────────────────────────────────────────────────────────
    fx          = st.session_state.dolar_live
    custo_brl   = qty * cost * fx
    imp_presumido = v_real * (tax_p / 100)
    imp_admin     = v_real * (adm_p / 100)
    impostos    = v_real * (total_tax_pct / 100)
    profit      = v_real - custo_brl - impostos
    margin      = (profit / v_real * 100) if v_real > 0 else 0

    if margin >= 30:
        margin_color, profit_color = "#059669", "#8DAE10"
    elif margin >= 10:
        margin_color, profit_color = "#D97706", "#D97706"
    else:
        margin_color, profit_color = "#DC2626", "#DC2626"

    with col_out:
        if v_real > 0:
            st.markdown(
                f"<div class='main-card'>"
                f"<p style='color:#9CA3AF;font-size:12px;'>LUCRO LÍQUIDO</p>"
                f"<h1 style='color:{profit_color};margin:0;font-size:42px;'>"
                f"R$ {float(profit):,.2f}</h1>"
                f"<p style='color:{margin_color};font-weight:600;'>"
                f"{margin:.1f}% Margem Real</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='main-card'>"
                "<p style='color:#9CA3AF;font-size:12px;'>LUCRO LÍQUIDO</p>"
                "<h1 style='color:#9CA3AF;margin:0;font-size:42px;'>R$ 0,00</h1>"
                "<p style='color:#9CA3AF;font-weight:600;'>Preencha os dados para calcular</p>"
                "</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Detalhamento do Cálculo", expanded=(v_real > 0)):
            st.markdown(f"""
| Item | Valor |
|---|---|
| Custo Total (USD) | $ {qty * cost:,.2f} |
| Câmbio USD→BRL | R$ {fx:.3f} |
| **Custo Total (BRL)** | **R$ {custo_brl:,.2f}** |
| Lucro Presumido ({tax_p:.2f}%) | R$ {imp_presumido:,.2f} |
| Taxa Administração ({adm_p:.2f}%) | R$ {imp_admin:,.2f} |
| **Total Impostos ({total_tax_pct:.2f}%)** | **R$ {impostos:,.2f}** |
| Venda (BRL) | R$ {v_real:,.2f} |
| **Lucro Líquido** | **R$ {profit:,.2f}** |
""")

        st.markdown("<br>", unsafe_allow_html=True)
        save_label = "ATUALIZAR NEGÓCIO" if is_editing else "CRIAR NEGÓCIO"
        if is_editing:
            c1, c2 = st.columns(2)
        else:
            c1 = st.container()
            c2 = None

        if c1.button(save_label, use_container_width=True):
            if not client_name.strip():
                st.error("Preencha o nome do cliente.")
            elif qty <= 0 or cost <= 0 or v_real <= 0:
                st.error("Valores devem ser maiores que zero.")
            else:
                try:
                    status_key = status_label_to_key(status_deal)
                    client_res = sb.table('clients').upsert(
                        {'name': client_name.strip(), 'notes': notes},
                        on_conflict='name',
                    ).execute()
                    client_id = client_res.data[0]['id']

                    deal_data = {
                        'client_id':    client_id,
                        'status':       status_key,
                        'qty':          qty,
                        'cost_usd':     float(cost),
                        'fx_rate':      fx,
                        'fx_rate_used': round(fx, 4),
                        'v_real':       float(v_real),
                        'tax_presumido': tax_p,
                        'tax_adm':      adm_p,
                        'profit':       round(profit, 2),
                        'margin':       round(margin, 1),
                        'closed_at':    datetime.now().isoformat() if status_key == 'concluido' else None,
                        'created_by':       str(st.session_state.user.id),
                        'created_by_email': st.session_state.user.email,
                    }

                    if is_editing:
                        old = sb.table('deals').select('status') \
                                .eq('id', st.session_state.selected_deal_id).execute()
                        old_status = old.data[0]['status'] if old.data else None
                        sb.table('deals').update(deal_data) \
                          .eq('id', st.session_state.selected_deal_id).execute()
                        if old_status and old_status != status_key:
                            sb.table('deal_events').insert({
                                'deal_id':    st.session_state.selected_deal_id,
                                'event_type': 'status_change',
                                'old_value':  old_status,
                                'new_value':  status_key,
                            }).execute()
                        st.toast(f"Negócio '{client_name}' atualizado!")
                    else:
                        new_deal = sb.table('deals').insert(deal_data).execute()
                        sb.table('deal_events').insert({
                            'deal_id':    new_deal.data[0]['id'],
                            'event_type': 'created',
                            'new_value':  status_key,
                        }).execute()
                        st.toast(f"Negócio '{client_name}' criado!")

                    invalidate_deals_cache()
                    clear_form()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

        if is_editing and c2 is not None:
            if c2.button("DUPLICAR", use_container_width=True,
                         help="Cria uma cópia deste negócio como novo"):
                st.session_state.selected_deal_id = None
                st.toast("Duplicado! Altere os dados e clique 'Criar Negócio'.")
