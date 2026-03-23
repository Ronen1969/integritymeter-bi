""" tabs/pipeline.py â Tab 2: Pipeline de Vendas. """
from datetime import datetime, date, timedelta

import pandas as pd
import streamlit as st

from config import sb
from fx import invalidate_deals_cache
from models import (
    STATUS_CONFIG,
    STATUS_KEYS,
    STATUS_LABELS,
    _migrate_status,
    status_dot,
    status_key_to_label,
    status_label_to_key,
)
from state import clear_form


def render_pipeline(all_deals: list, sidebar_cfg: dict) -> None:
    tax_p = sidebar_cfg['tax_p']
    adm_p = sidebar_cfg['adm_p']
    total_tax_pct = sidebar_cfg['total_tax_pct']

    st.header("Pipeline de Vendas")

    if not all_deals:
        st.info("Nenhum negÃ³cio cadastrado.")
        return

    # ââ Filters ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    fc1, fc2, fc3 = st.columns(3)
    filter_status = fc1.multiselect(
        "Filtrar por Status",
        STATUS_LABELS,
        default=[],
        placeholder="Selecione o status...",
        key="pipe_filter_status",
    )
    filter_client = fc2.text_input("Buscar por Cliente", key="pipe_filter_client")
    filter_date = fc3.date_input(
        "A partir de",
        value=date.today() - timedelta(days=90),
        format="DD/MM/YYYY",
        key="pipe_filter_date",
    )

    df = pd.DataFrame(all_deals)
    df['client_name'] = df['clients'].apply(lambda c: c.get('name', '?') if c else '?')
    df['created_at_dt'] = pd.to_datetime(df['created_at'], utc=True)

    if filter_status:
        filter_keys = [status_label_to_key(s) for s in filter_status]
        df = df[df['status'].isin(filter_keys)]
    if filter_client:
        df = df[df['client_name'].str.contains(filter_client, case=False, na=False)]
    if filter_date:
        df = df[df['created_at_dt'] >= pd.Timestamp(filter_date, tz='UTC')]

    if df.empty:
        st.warning("Nenhum negÃ³cio encontrado com os filtros aplicados.")
        return

    for col in ['v_real', 'profit', 'margin']:
        df[col] = df[col].astype(float)

    won = df[df['status'] == 'concluido']
    lost = df[df['status'] == 'perdido']
    tw, tl = len(won), len(lost)
    ta = len(df) - tw - tl
    wr = (tw / (tw + tl) * 100) if (tw + tl) > 0 else 0
    tp = df[~df['status'].isin(['concluido', 'perdido'])]['v_real'].sum()

    # ââ KPIs âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    k1, k2, k3, k4, k5 = st.columns(5)
    for col, lbl, val in [
        (k1, "Pipeline Ativo",   f"R$ {tp:,.0f}"),
        (k2, "NegÃ³cios Ativos",  str(ta)),
        (k3, "Taxa ConversÃ£o",   f"{wr:.0f}%"),
        (k4, "Ganhos/Perdidos",  f"{tw}/{tl}"),
        (k5, "Total Filtrado",   str(len(df))),
    ]:
        col.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>{lbl}</div>"
            f"<div class='kpi-value'>{val}</div></div>",
            unsafe_allow_html=True,
        )

    # ââ Funnel âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Funil de ConversÃ£o")
    sc = df.groupby('status').size().to_dict()
    mx = max(sc.values()) if sc else 1
    for sk in STATUS_KEYS:
        cfg = STATUS_CONFIG[sk]
        cnt = sc.get(sk, 0)
        if cnt == 0:
            continue
        bw = max(int(cnt / mx * 100), 8)
        vs = df[df['status'] == sk]['v_real'].sum()
        st.markdown(
            f"<div class='funnel-row'>"
            f"<div style='width:160px;font-size:13px;font-weight:500;'>"
            f"<span style='display:inline-block;width:10px;height:10px;border-radius:50%;"
            f"background:{cfg['color']};margin-right:6px;'></span>{cfg['label']}</div>"
            f"<div class='funnel-bar' style='width:{bw}%;background:{cfg['color']};'>"
            f"{cnt} neg. | R$ {vs:,.0f}</div></div>",
            unsafe_allow_html=True,
        )

    # ââ Deal list ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Todos os NegÃ³cios")
    pipe_ids = set(df['id'].tolist())
    pipe_deals = [d for d in all_deals if d['id'] in pipe_ids]

    for pd_deal in pipe_deals:
        cn      = (pd_deal.get('clients', {}) or {}).get('name', '?')
        sk      = pd_deal['status']
        vr      = float(pd_deal['v_real'])
        pr      = float(pd_deal['profit'])
        mg      = float(pd_deal['margin'])
        qt      = int(pd_deal['qty'])
        up      = round(vr / qt, 2) if qt > 0 else vr
        deal_id = pd_deal['id']

        try:
            dt_str = pd_deal['created_at'][:10] if pd_deal.get('created_at') else ''
            dt_fmt = datetime.fromisoformat(dt_str).strftime('%d/%m/%Y') if dt_str else ''
        except (ValueError, TypeError):
            dt_fmt = pd_deal.get('created_at', '')[:10]

        mg_color  = "#059669" if mg >= 30 else "#D97706" if mg >= 10 else "#DC2626"
        edit_key  = f"pipe_editing_{deal_id}"
        del_key   = f"pipe_deleting_{deal_id}"
        note_key  = f"pipe_noting_{deal_id}"

        # ââ Unified card â Ghost Button Pattern ââââââââââââââââââââââââââââââ
        # Visual action buttons are HTML; they call window.__triggerDeal()
        # which clicks the invisible Streamlit ghost buttons below.
        st.markdown(f"""<div class='deal-card'>
  <div style='flex:0 0 10px;margin-right:2px;'>{status_dot(sk)}</div>
  <div style='flex:2;min-width:100px;'>
    <div style='font-weight:600;font-size:14px;line-height:1.3;'>{cn}</div>
    <small style='color:#9CA3AF;font-size:11px;'>{status_key_to_label(sk)}</small>
  </div>
  <div style='flex:0.55;text-align:center;'>
    <div class='deal-mv'>{qt}</div>
    <small style='color:#9CA3AF;font-size:11px;'>Qtd.</small>
  </div>
  <div style='flex:1;text-align:right;'>
    <div class='deal-mv'>R$ {up:,.2f}</div>
    <small style='color:#9CA3AF;font-size:11px;'>PreÃ§o Unit.</small>
  </div>
  <div style='flex:1;text-align:right;'>
    <div class='deal-mv'>R$ {vr:,.0f}</div>
    <small style='color:#9CA3AF;font-size:11px;'>Total</small>
  </div>
  <div style='flex:1;text-align:right;'>
    <div class='deal-mv' style='color:{mg_color};'>R$ {pr:,.0f}</div>
    <small style='color:#9CA3AF;font-size:11px;'>Lucro ({mg:.0f}%)</small>
  </div>
  <div style='flex:0.65;text-align:right;color:#9CA3AF;font-size:11px;white-space:nowrap;'>{dt_fmt}</div>
  <div class='deal-actions'>
    <button class='deal-action-btn' onclick="window.__triggerDeal('{deal_id}','pe')" title='Editar negÃ³cio'>&#9998;</button>
    <button class='deal-action-btn deal-action-del' onclick="window.__triggerDeal('{deal_id}','pd')" title='Excluir negÃ³cio'>&#128465;</button>
    <button class='deal-action-btn' onclick="window.__triggerDeal('{deal_id}','pno')" title='Adicionar nota'>&#128203;</button>
  </div>
</div>""", unsafe_allow_html=True)

        # Ghost Streamlit buttons â invisible (height:0), triggered by JS above
        _gc1, _gc2, _gc3, _ = st.columns([1, 1, 1, 100])
        with _gc1:
            if st.button("e", key=f"icon_pe_{deal_id}", help="Editar negÃ³cio"):
                current = st.session_state.get(edit_key, False)
                st.session_state[edit_key] = not current
                for d in pipe_deals:
                    if d['id'] != deal_id:
                        st.session_state.pop(f"pipe_editing_{d['id']}", None)
                st.session_state.pop(del_key, None)
                st.session_state.pop(note_key, None)
                st.rerun()
        with _gc2:
            if st.button("d", key=f"icon_pd_{deal_id}", help="Excluir negÃ³cio"):
                current = st.session_state.get(del_key, False)
                st.session_state[del_key] = not current
                st.session_state.pop(edit_key, None)
                st.session_state.pop(note_key, None)
                st.rerun()
        with _gc3:
            if st.button("n", key=f"icon_pno_{deal_id}", help="Adicionar nota"):
                current = st.session_state.get(note_key, False)
                st.session_state[note_key] = not current
                st.session_state.pop(edit_key, None)
                st.session_state.pop(del_key, None)
                st.rerun()

        # ââ Inline edit form ââââââââââââââââââââââââââââââââââââââââââââââââââ
        if st.session_state.get(edit_key, False):
            st.markdown(
                "<div style='padding:4px 0 8px 0;border-left:3px solid #8DAE10;"
                "padding-left:16px;margin:4px 0;'>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Editando: {cn}**")
            _notes = (pd_deal.get('clients', {}) or {}).get('notes', '') or ''
            with st.form(f"edit_form_{deal_id}"):
                en1, en2 = st.columns([1, 2])
                edit_cn    = en1.text_input("Cliente",       value=cn,       key=f"ecn_{deal_id}")
                edit_notes = en2.text_input("ObservaÃ§Ãµes",   value=_notes,  key=f"eno_{deal_id}")

                ef1, ef2, ef3 = st.columns(3)
                edit_qty  = ef1.number_input("Qtd. Testes",    value=int(pd_deal['qty']),        min_value=0,   step=1,   key=f"eq_{deal_id}")
                edit_cost = ef2.number_input("Custo UnitÃ¡rio (USD)",     value=float(pd_deal['cost_usd']), min_value=0.0, step=0.5, format="%.2f", key=f"ec_{deal_id}")
                edit_unit = ef3.number_input("PreÃ§o UnitÃ¡rio (R$)", value=up,                        min_value=0.0, step=5.0, format="%.2f", key=f"eu_{deal_id}")

                ef4, ef5, ef6 = st.columns(3)
                auto_total = round(edit_unit * edit_qty, 2) if (edit_unit > 0 and edit_qty > 0) else float(pd_deal['v_real'])
                edit_vreal  = ef4.number_input("Total R$",  value=auto_total, min_value=0.0, step=100.0, format="%.2f", key=f"ev_{deal_id}")
                _mig_sk     = _migrate_status(sk)
                edit_status = ef5.selectbox(
                    "Status", STATUS_LABELS,
                    index=STATUS_KEYS.index(_mig_sk) if _mig_sk in STATUS_KEYS else 0,
                    key=f"es_{deal_id}",
                )
                try:
                    _edt = date.fromisoformat(pd_deal['created_at'][:10]) if pd_deal.get('created_at') else date.today()
                except (ValueError, TypeError):
                    _edt = date.today()
                edit_date = ef6.date_input("Data", value=_edt, format="DD/MM/YYYY", key=f"edt_{deal_id}")

                sf1, sf2 = st.columns(2)
                if sf1.form_submit_button("Salvar", use_container_width=True):
                    try:
                        edit_sk = status_label_to_key(edit_status)
                        fx = st.session_state.dolar_live
                        new_cost_brl  = edit_qty * edit_cost * fx
                        new_impostos  = edit_vreal * total_tax_pct / 100
                        new_profit    = edit_vreal - new_cost_brl - new_impostos
                        new_margin    = (new_profit / edit_vreal * 100) if edit_vreal > 0 else 0
                        update_data   = {
                            'status':        edit_sk,
                            'qty':           edit_qty,
                            'cost_usd':      float(edit_cost),
                            'v_real':        float(edit_vreal),
                            'fx_rate':       fx,
                            'fx_rate_used':  round(fx, 4),
                            'tax_presumido': tax_p,
                            'tax_adm':       adm_p,
                            'profit':        round(new_profit, 2),
                            'margin':        round(new_margin, 1),
                            'closed_at':     datetime.now().isoformat() if edit_sk == 'concluido' else None,
                        }
                        if sk != edit_sk:
                            sb.table('deal_events').insert({
                                'deal_id':    deal_id,
                                'event_type': 'status_change',
                                'old_value':  sk,
                                'new_value':  edit_sk,
                            }).execute()
                        if edit_cn.strip():
                            client_res = sb.table('clients').upsert(
                                {'name': edit_cn.strip(), 'notes': edit_notes.strip()},
                                on_conflict='name',
                            ).execute()
                            if client_res.data:
                                update_data['client_id'] = client_res.data[0]['id']
                        if edit_cn.strip() == cn:
                            old_cid = pd_deal.get('client_id')
                            if old_cid:
                                sb.table('clients').update({'notes': edit_notes.strip()}) \
                                    .eq('id', old_cid).execute()
                        sb.table('deals').update(update_data).eq('id', deal_id).execute()
                        invalidate_deals_cache()
                        st.session_state[edit_key] = False
                        st.toast(f"NegÃ³cio '{edit_cn.strip()}' atualizado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                if sf2.form_submit_button("Cancelar", use_container_width=True):
                    st.session_state[edit_key] = False
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # ââ Delete confirmation âââââââââââââââââââââââââââââââââââââââââââââââ
        if st.session_state.get(del_key, False):
            st.warning(f"Excluir **{cn}**? Esta aÃ§Ã£o nÃ£o pode ser desfeita.")
            dc1, dc2, _ = st.columns([1, 1, 4])
            if dc1.button("Sim, excluir", key=f"py_{deal_id}"):
                try:
                    sb.table('deal_events').delete().eq('deal_id', deal_id).execute()
                    sb.table('deals').delete().eq('id', deal_id).execute()
                    invalidate_deals_cache()
                    if st.session_state.selected_deal_id == deal_id:
                        clear_form()
                    st.toast(f"NegÃ³cio '{cn}' excluÃ­do com sucesso!")
                    st.session_state[del_key] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
            if dc2.button("Cancelar", key=f"pn_{deal_id}"):
                st.session_state[del_key] = False
                st.rerun()

        # ââ Quick note panel ââââââââââââââââââââââââââââââââââââââââââââââââââ
        if st.session_state.get(note_key, False):
            _notes = (pd_deal.get('clients', {}) or {}).get('notes', '') or ''
            st.markdown(
                "<div style='padding:4px 0 8px 0;border-left:3px solid #8DAE10;"
                "padding-left:16px;margin:4px 0;'>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Nota â {cn}**")
            with st.form(f"note_form_{deal_id}"):
                new_notes = st.text_area(
                    "ObservaÃ§Ãµes", value=_notes,
                    key=f"nt_{deal_id}", height=80,
                    placeholder="Adicione observaÃ§Ãµes sobre este negÃ³cio ou cliente...",
                )
                nf1, nf2 = st.columns(2)
                if nf1.form_submit_button("Salvar nota", use_container_width=True):
                    try:
                        old_cid = pd_deal.get('client_id')
                        if old_cid:
                            sb.table('clients').update({'notes': new_notes.strip()}) \
                                .eq('id', old_cid).execute()
                            st.toast(f"ObservaÃ§Ã£o de '{cn}' salva com sucesso!")
                        else:
                            st.warning("Cliente nÃ£o encontrado para salvar a nota.")
                        st.session_state[note_key] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                if nf2.form_submit_button("Cancelar", use_container_width=True):
                    st.session_state[note_key] = False
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
