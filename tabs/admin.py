"""
tabs/admin.py — Tab 5: Painel Administrativo (admin users only).
"""
import streamlit as st

from auth import send_welcome_email
from config import sb, sb_admin
from models import status_key_to_label


def render_admin() -> None:
    st.header("Painel Administrativo")

    # ── Change own password ───────────────────────────────────────────────────
    with st.expander("Alterar Minha Senha"):
        with st.form("change_password_form"):
            new_pw     = st.text_input("Nova senha",           type="password")
            confirm_pw = st.text_input("Confirmar nova senha", type="password")
            if st.form_submit_button("Salvar Nova Senha"):
                if not new_pw or len(new_pw) < 6:
                    st.error("Senha deve ter pelo menos 6 caracteres.")
                elif new_pw != confirm_pw:
                    st.error("Senhas não conferem.")
                else:
                    try:
                        sb.auth.update_user({"password": new_pw})
                        st.success("Senha alterada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro: {e}")

    st.markdown("---")

    # ── Create new user ───────────────────────────────────────────────────────
    st.subheader("Criar Novo Usuário")
    if not sb_admin:
        st.error("Service role key não configurada. Adicione SUPABASE_SERVICE_KEY nos secrets.")
    else:
        app_url = st.secrets.get("APP_URL", "")
        with st.form("create_user_form"):
            nu_name  = st.text_input("Nome completo")
            nu_email = st.text_input("Email")
            nu_pass  = st.text_input("Senha temporária", type="password")
            nu_role  = st.selectbox("Papel", ["user", "admin"])
            send_email_check = st.checkbox("Enviar email de boas-vindas com credenciais", value=True)

            if st.form_submit_button("Criar Usuário"):
                if nu_email and nu_pass and nu_name:
                    try:
                        sb_admin.auth.admin.create_user({
                            "email":          nu_email,
                            "password":       nu_pass,
                            "email_confirm":  True,
                            "user_metadata":  {"full_name": nu_name, "role": nu_role},
                        })
                        st.success(f"Usuário '{nu_name}' ({nu_email}) criado!")
                        if send_email_check:
                            ok, err = send_welcome_email(nu_email, nu_name, nu_pass, app_url)
                            if ok:
                                st.success(f"Email de boas-vindas enviado para {nu_email}!")
                            else:
                                st.warning(f"Usuário criado, mas email não enviado: {err}")
                    except Exception as e:
                        st.error(f"Erro: {e}")
                else:
                    st.warning("Preencha todos os campos.")

    # ── User list ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Usuários Cadastrados")
    try:
        users = sb.table('user_profiles').select('*').order('created_at').execute()
        if not users.data:
            st.info("Nenhum usuário cadastrado ainda.")
            return

        app_url = st.secrets.get("APP_URL", "")
        for u in users.data:
            u_name   = u.get('full_name', '') or u.get('email', '?')
            u_email  = u.get('email', '')
            u_role   = u.get('role', 'user')
            u_active = u.get('is_active', True)
            u_date   = u.get('created_at', '')[:10] if u.get('created_at') else ''
            u_id     = u.get('id', '')
            is_self  = (u_id == str(st.session_state.user.id))

            status_color = "#059669" if u_active else "#EF4444"
            status_text  = "Ativo"   if u_active else "Inativo"
            role_badge   = "Admin"   if u_role == 'admin' else "Usuário"

            st.markdown(f"""
<div style='padding:12px;border-radius:10px;border:1px solid #e2e8f0;margin:6px 0;background:#fafafa;'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <div>
            <strong>{u_name}</strong>
            <span style='color:#6B7280;font-size:13px;'>| {u_email} | {role_badge}</span>
        </div>
        <div>
            <span style='color:{status_color};font-weight:600;font-size:12px;padding:3px 10px;
                         border-radius:12px;background:{status_color}15;'>{status_text}</span>
            <span style='color:#9CA3AF;font-size:11px;margin-left:8px;'>{u_date}</span>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

            if is_self:
                st.caption("(sua conta)")
                continue

            if not sb_admin:
                continue

            col_a, col_b, col_c, col_d, col_e = st.columns(5)

            # Toggle active / inactive
            with col_a:
                if u_active:
                    if st.button("Desativar", key=f"deact_{u_id}", use_container_width=True):
                        sb.table('user_profiles').update({'is_active': False}).eq('id', u_id).execute()
                        st.toast(f"'{u_name}' desativado.")
                        st.rerun()
                else:
                    if st.button("Reativar", key=f"react_{u_id}", use_container_width=True):
                        sb.table('user_profiles').update({'is_active': True}).eq('id', u_id).execute()
                        st.toast(f"'{u_name}' reativado.")
                        st.rerun()

            # Reset password
            with col_b:
                if st.button("Resetar Senha", key=f"reset_{u_id}", use_container_width=True):
                    st.session_state[f'show_reset_{u_id}'] = True

            # Resend invite
            with col_c:
                if st.button("Reenviar Convite", key=f"resend_{u_id}", use_container_width=True):
                    st.session_state[f'show_resend_{u_id}'] = True

            # Change role
            with col_d:
                new_role   = "admin" if u_role == "user" else "user"
                role_label = "Tornar Admin" if u_role == "user" else "Tornar Usuário"
                if st.button(role_label, key=f"role_{u_id}", use_container_width=True):
                    try:
                        sb.table('user_profiles').update({'role': new_role}).eq('id', u_id).execute()
                        sb_admin.auth.admin.update_user_by_id(
                            u_id, {"user_metadata": {"role": new_role}}
                        )
                        st.toast(f"'{u_name}' agora é {new_role}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

            # Delete user
            with col_e:
                if st.button("Excluir", key=f"delusr_{u_id}", use_container_width=True):
                    try:
                        sb_admin.auth.admin.delete_user(u_id)
                        sb.table('user_profiles').delete().eq('id', u_id).execute()
                        st.toast(f"'{u_name}' excluído.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

            # Reset password form
            if st.session_state.get(f'show_reset_{u_id}', False):
                with st.form(f"reset_form_{u_id}"):
                    new_pw = st.text_input(f"Nova senha para {u_name}", type="password", key=f"newpw_{u_id}")
                    rc1, rc2 = st.columns(2)
                    if rc1.form_submit_button("Confirmar Reset"):
                        if new_pw and len(new_pw) >= 6:
                            try:
                                sb_admin.auth.admin.update_user_by_id(u_id, {"password": new_pw})
                                st.success(f"Senha de '{u_name}' resetada!")
                                st.session_state[f'show_reset_{u_id}'] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                        else:
                            st.error("Senha deve ter pelo menos 6 caracteres.")
                    if rc2.form_submit_button("Cancelar"):
                        st.session_state[f'show_reset_{u_id}'] = False
                        st.rerun()

            # Resend invite form
            if st.session_state.get(f'show_resend_{u_id}', False):
                with st.form(f"resend_form_{u_id}"):
                    resend_pw = st.text_input(
                        f"Senha para enviar a {u_name}", type="password", key=f"resendpw_{u_id}",
                        help="Digite a senha atual ou nova para incluir no email",
                    )
                    rs1, rs2 = st.columns(2)
                    if rs1.form_submit_button("Enviar Email"):
                        if resend_pw:
                            try:
                                sb_admin.auth.admin.update_user_by_id(u_id, {"password": resend_pw})
                            except Exception as ex:
                                pass  # non-fatal
                            ok, err = send_welcome_email(u_email, u_name, resend_pw, app_url)
                            if ok:
                                st.success(f"Email reenviado para {u_email}!")
                            else:
                                st.error(f"Falha: {err}")
                            st.session_state[f'show_resend_{u_id}'] = False
                            st.rerun()
                        else:
                            st.error("Digite uma senha para incluir no email.")
                    if rs2.form_submit_button("Cancelar"):
                        st.session_state[f'show_resend_{u_id}'] = False
                        st.rerun()

    except Exception as e:
        st.info(f"Carregando usuários... {e}")

    # ── Activity log ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Log de Atividades")
    try:
        events = sb.table('deal_events').select('*, deals(clients(name))') \
                   .order('created_at', desc=True).limit(50).execute()
        if events.data:
            log_data = []
            for ev in events.data:
                cn = '?'
                if ev.get('deals') and ev['deals'].get('clients'):
                    cn = ev['deals']['clients'].get('name', '?')
                log_data.append({
                    'Data':    ev['created_at'][:16].replace('T', ' '),
                    'Cliente': cn,
                    'Evento':  ev['event_type'],
                    'De':      status_key_to_label(ev.get('old_value', '')) if ev.get('old_value') else '-',
                    'Para':    status_key_to_label(ev.get('new_value', '')) if ev.get('new_value') else '-',
                })
            import pandas as pd
            st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum evento registrado.")
    except Exception as e:
        st.info(f"Log: {e}")
