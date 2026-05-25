import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2.6", page_icon="🎬", layout="centered")

# --- CONEXÃO BANCO DE DADOS ---
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_connection()
if supabase is None:
    st.error("Erro crítico: Não foi possível conectar ao banco de dados Supabase.")
    st.stop()

# --- CONFIGURAÇÕES GERAIS DE SEGURANÇA ---
CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
NOME_DEVELOPER = "Rafael_oficial"

# --- FUNÇÕES AUXILIARES ---
def obter_status_emoji(timestamp_str):
    if not timestamp_str:
        return "⚪ Offline"
    try:
        if "T" in timestamp_str:
            timestamp_str = timestamp_str.split("+")[0]
            dt_usuario = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)
        else:
            dt_usuario = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
        
        agora = datetime.now(timezone.utc)
        if agora - dt_usuario < timedelta(minutes=3):
            return "🟢 Online"
    except:
        pass
    return "⚪ Offline"

def criar_notificacao(id_destinatario, tipo, mensagem):
    if not id_destinatario or st.session_state.usuario_logado is None:
        return
    try:
        supabase.table("notificacoes").insert({
            "id_destinatario": id_destinatario,
            "username_remetente": st.session_state.usuario_logado["username"],
            "tipo": tipo,
            "mensagem": mensagem,
            "lida": False
        }).execute()
    except:
        pass

def obter_selo_texto(username_alvo):
    """Retorna o sufixo de texto com base no cargo ou seguidores do usuário"""
    if username_alvo == NOME_DEVELOPER:
        return " 👑 DEV"
    try:
        dados = supabase.table("perfis_usuarios").select("id").eq("username", username_alvo).execute()
        if dados.data:
            id_u = dados.data[0]["id"]
            res_seg = supabase.table("seguidores").select("*", count="exact").eq("id_seguido", id_u).execute()
            total = res_seg.count if (hasattr(res_seg, "count") and res_seg.count is not None) else len(res_seg.data)
            if total >= 1000:
                return " ✔️"
    except:
        pass
    return ""

def renderizar_foto_com_banner(url_foto, username_alvo, tamanho=90):
    """Renderiza a foto com a borda dourada exclusivamente para o desenvolvedor"""
    if username_alvo == NOME_DEVELOPER:
        estilo_css = "border-radius: 50%; object-fit: cover; border: 4px solid #ffd700; box-shadow: 0 0 20px #ffd700;"
        coroa_html = f'<div style="position: absolute; top: -22px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.38)}px; z-index: 10;">👑</div>'
    else:
        estilo_css = "border-radius: 50%; object-fit: cover;"
        coroa_html = ''
        
    html = f"""
    <div style="position: relative; display: inline-block; text-align: center; margin-top: 10px;">
        {coroa_html}
        <img src="{url_foto}" width="{tamanho}" height="{tamanho}" style="{estilo_css}">
    </div>
    """
    return st.markdown(html, unsafe_allow_html=True)

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = None
if "perfil_visitado" not in st.session_state:
    st.session_state.perfil_visitado = None

# --- FLUXO DE AUTENTICAÇÃO ---
if st.session_state.usuario_logado is None:
    exibir_logo()
    aba_auth = st.tabs(["Fazer Login", "Criar Nova Conta"])
    with aba_auth[0]:
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        if st.button("Entrar 🚀", key="btn_login", use_container_width=True):
            if login_user and login_senha:
                busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                if busca.data and busca.data[0]["senha"] == login_senha:
                    st.session_state.usuario_logado = busca.data[0]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
                    
    with aba_auth[1]:
        cad_user = st.text_input("Escolha um Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie uma Senha:", type="password", key="cad_senha")
        codigo_convite = st.text_input("🔑 Código Secreto:", type="password", key="codigo_convite")
        if st.button("Cadastrar Conta 🎉", key="btn_cad", use_container_width=True):
            if cad_user and cad_senha and codigo_convite == CHAVE_SECRETA:
                try:
                    supabase.table("perfis_usuarios").insert({
                        "username": cad_user, "apelido": cad_user, "senha": cad_senha, 
                        "url_foto_perfil": FOTO_PADRAO, "ultimo_visto": datetime.now(timezone.utc).isoformat()
                    }).execute()
                    st.success("Conta criada! Faça login.")
                except:
                    st.error("Nome de usuário indisponível.")
else:
    user_atual = st.session_state.usuario_logado
    try:
        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", user_atual["id"]).execute()
    except:
        pass

    total_notif = 0
    try:
        res_n = supabase.table("notificacoes").select("*", count="exact").eq("id_destinatario", user_atual["id"]).eq("lida", False).execute()
        total_notif = res_n.count if (hasattr(res_n, "count") and res_n.count is not None) else len(res_n.data)
    except:
        pass

    # --- BARRA LATERAL ---
    with st.sidebar:
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, user_atual["username"], tamanho=90)
        selo_proprio = obter_selo_texto(user_atual["username"])
        st.write(f"**{user_atual.get('apelido') or user_atual['username']}** {selo_proprio}")
        
        if st.button("Sair da Conta 🚪", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.sala_ativa = None
            st.session_state.perfil_visitado = None
            st.rerun()

    # --- NAVEGAÇÃO PRINCIPAL ---
    aba_feed, aba_loja, aba_chat, aba_status, aba_notif = st.tabs([
        "📺 Silver Tok (Feed)", "🛒 Loja de Banners", "💬 Chat-Exv", "✨ Status", f"🔔 Notificações ({total_notif})"
    ])

    def renderizar_lista_filtrada(lista_posts, identificador_formato):
        for idx, v in enumerate(lista_posts):
            if str(v.get("titulo", "")).startswith("[STATUS]"): continue
            autor = v.get('username_autor', 'Membro')
            img_autor = v.get('avatar_autor') or FOTO_PADRAO
            video_url = v["url_video"]
            id_post = v.get("id")
            chave_comp = f"feed_{identificador_formato}_{idx}_{id_post}"

            st.markdown("---")
            col_f1, col_f2 = st.columns([1, 5])
            with col_f1: 
                renderizar_foto_com_banner(img_autor, autor, tamanho=50)
                if st.button("👤", key=f"btn_perfil_f_{chave_comp}"):
                    st.session_state.perfil_visitado = autor
                    st.rerun()
            with col_f2:
                selo_autor = obter_selo_texto(autor)
                st.markdown(f"**{autor}** {selo_autor}")
                st.caption(v["titulo"])

            if v.get("tipo_formato") == "vertical":
                st.markdown(f'<div style="display: flex; justify-content: center;"><video width="290" height="515" controls><source src="{video_url}" type="video/mp4"></video></div>', unsafe_allow_html=True)
            else:
                if str(video_url).lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    st.image(video_url, use_container_width=True)
                else:
                    st.video(video_url)

            # Comentários por Postagem
            with st.expander("💬 Comentários"):
                with st.form(key=f"form_c_{chave_comp}", clear_on_submit=True):
                    text_c = st.text_input("Adicionar comentário:")
                    if st.form_submit_button("Enviar") and text_c.strip():
                        try:
                            supabase.table("comentarios_feed").insert({
                                "id_video": id_post,
                                "username_autor": user_atual["username"], 
                                "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                "comentario": text_c.strip()
                            }).execute()
                        except:
                            st.error("Erro ao inserir comentário no banco.")
                        st.rerun()

                try:
                    c_dados = supabase.table("comentarios_feed").select("*").eq("id_video", id_post).execute()
                    if c_dados.data:
                        for c in c_dados.data:
                            col_c1, col_c2 = st.columns([1, 8])
                            with col_c1:
                                renderizar_foto_com_banner(c.get("avatar_autor") or FOTO_PADRAO, c['username_autor'], tamanho=30)
                            with col_c2:
                                s_com = obter_selo_texto(c['username_autor'])
                                st.markdown(f"**{c['username_autor']}** {s_com}: {c['comentario']}")
                except:
                    pass

    # === 📺 ABA SILVER TOK ===
    with aba_feed:
        if st.session_state.perfil_visitado:
            autor_vis = st.session_state.perfil_visitado
            if st.button("⬅️ Voltar ao Feed Global"):
                st.session_state.perfil_visitado = None
                st.rerun()
            
            p_dados = supabase.table("perfis_usuarios").select("*").eq("username", autor_vis).execute()
            if p_dados.data:
                p_info = p_dados.data[0]
                col_p1, col_p2 = st.columns([1, 3])
                with col_p1:
                    renderizar_foto_com_banner(p_info.get("url_foto_perfil") or FOTO_PADRAO, autor_vis, tamanho=80)
                with col_p2:
                    s_vis = obter_selo_texto(autor_vis)
                    st.subheader(f"{p_info.get('apelido') or autor_vis} {s_vis}")
                    
                    if autor_vis != user_atual["username"]:
                        ja_segue = supabase.table("seguidores").select("*").eq("id_seguidor", user_atual["id"]).eq("id_seguido", p_info["id"]).execute()
                        if ja_segue.data:
                            if st.button("Seguindo ✓"):
                                supabase.table("seguidores").delete().eq("id_seguidor", user_atual["id"]).eq("id_seguido", p_info["id"]).execute()
                                st.rerun()
                        else:
                            # CORREÇÃO CRÍTICA DO ERRO DA LINHA 257 (Trocado ',' por ':')
                            if st.button("Seguir ➕", type="primary"):
                                supabase.table("seguidores").insert({"id_seguidor": user_atual["id"], "id_seguido": p_info["id"]}).execute()
                                st.rerun()

                st.write("### Publicações do Usuário")
                v_dados = supabase.table("feed_videos").select("*").eq("username_autor", autor_vis).execute()
                if v_dados.data:
                    renderizar_lista_filtrada(reversed(v_dados.data), "perfil")
                else:
                    st.info("Nenhuma publicação encontrada.")
            else:
                st.error("Perfil não encontrado.")
        else:
            exibir_logo()
            with st.expander("➕ Publicar Novo Conteúdo"):
                t_pub = st.text_input("Legenda:")
                f_midia = st.file_uploader("Arquivo de Vídeo ou Imagem:", type=["mp4", "png", "jpg", "jpeg"])
                fmt = st.selectbox("Formato:", ["Horizontal / Padrão", "Vertical / Shorts"])
                fmt_db = "vertical" if "Vertical" in fmt else "horizontal"
                
                if st.button("Publicar Post 🚀") and f_midia and t_pub:
                    bucket = "videos_feed" if fmt_db == "vertical" or f_midia.name.endswith(".mp4") else "imagens_chat"
                    path_b = f"feed/{uuid.uuid4()}_{f_midia.name}"
                    supabase.storage.from_(bucket).upload(path_b, f_midia.read())
                    url_f = supabase.storage.from_(bucket).get_public_url(path_b)
                    
                    supabase.table("feed_videos").insert({
                        "titulo": t_pub, "url_video": url_f, "username_autor": user_atual["username"],
                        "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0,
                        "id_autor": user_atual["id"], "tipo_formato": fmt_db
                    }).execute()
                    st.success("Publicado!")
                    st.rerun()

            try:
                f_dados = supabase.table("feed_videos").select("*").execute()
                if f_dados.data:
                    renderizar_lista_filtrada(reversed(f_dados.data), "global")
            except:
                st.info("Nenhuma publicação no feed global.")

    # === 🛒 ABA LOJA DE BANNERS ===
    with aba_loja:
        st.header("🛒 Loja de Cosméticos")
        st.caption("Personalize sua moldura de exibição e conquiste novos visuais.")
        
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.subheader("🥉 Bronze Estelar")
            st.write("Preço: 🪙 150 moedas")
            st.button("Adquirir Borda", key="l_brnz", use_container_width=True)
        with col_l2:
            st.subheader("🥈 Prata Lendária")
            st.write("Preço: 🪙 300 moedas")
            st.button("Adquirir Borda", key="l_slvr", use_container_width=True)

    # === 💬 ABA CHAT-EXV ===
    with aba_chat:
        if st.session_state.sala_ativa:
            st.subheader(f"Sala: {st.session_state.sala_ativa}")
            if st.button("⬅️ Sair da Sala"):
                st.session_state.sala_ativa = None
                st.rerun()

            with st.form(key="chat_msg_form", clear_on_submit=True):
                m_txt = st.text_input("Mensagem:")
                if st.form_submit_button("Enviar ✉️") and m_txt.strip():
                    supabase.table("bate-papo_profissional").insert({
                        "username": user_atual["username"],
                        "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                        "mensagem": m_txt.strip(), "codigo_sala": st.session_state.sala_ativa
                    }).execute()
                    st.rerun()

            try:
                m_dados = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", st.session_state.sala_ativa).execute()
                if m_dados.data:
                    for m in reversed(m_dados.data[-30:]):
                        col_m1, col_m2 = st.columns([1, 6])
                        with col_m1:
                            renderizar_foto_com_banner(m.get("url_foto_perfil") or FOTO_PADRAO, m['username'], tamanho=40)
                        with col_m2:
                            s_msg = obter_selo_texto(m['username'])
                            st.markdown(f"**{m['username']}** {s_msg}: {m['mensagem']}")
            except:
                pass
        else:
            st.title("🎛️ Painel Chat-Exv")
            t_chat = st.tabs(["💬 Privado", "👨‍👩‍👦 Grupos", "👥 Membros"])
            
            with t_chat[0]:
                alvo = st.text_input("Username do amigo:").strip()
                if st.button("Abrir Chat Privado") and alvo:
                    lista = sorted([user_atual['username'].upper(), alvo.upper()])
                    st.session_state.sala_ativa = f"PRIV-{lista[0]}-{lista[1]}"
                    st.rerun()
            
            with t_chat[1]:
                g_nome = st.text_input("Nome do Grupo:").strip().upper()
                if st.button("Entrar / Criar Grupo") and g_nome:
                    st.session_state.sala_ativa = g_nome
                    st.rerun()

            with t_chat[2]:
                st.subheader("Membros da Comunidade")
                try:
                    u_todos = supabase.table("perfis_usuarios").select("*").execute()
                    if u_todos.data:
                        for u in u_todos.data:
                            if u["username"] != user_atual["username"]:
                                col_u1, col_u2, col_u3 = st.columns([1, 4, 2])
                                with col_u1:
                                    renderizar_foto_com_banner(u.get("url_foto_perfil") or FOTO_PADRAO, u["username"], tamanho=40)
                                with col_u2:
                                    s_u = obter_selo_texto(u["username"])
                                    st.write(f"**{u['username']}** {s_u}")
                                    st.caption(obter_status_emoji(u.get("ultimo_visto")))
                                with col_u3:
                                    if st.button("Chat 💬", key=f"u_ch_{u['username']}"):
                                        lista = sorted([user_atual['username'].upper(), u['username'].upper()])
                                        st.session_state.sala_ativa = f"PRIV-{lista[0]}-{lista[1]}"
                                        st.rerun()
                except:
                    pass

    # === ✨ ABA STATUS ===
    with aba_status:
        st.header("✨ Status Temporários")
        stat_txt = st.text_input("O que você está pensando?")
        if st.button("Postar Status") and stat_txt.strip():
            supabase.table("feed_videos").insert({
                "titulo": f"[STATUS] {stat_txt.strip()}", "url_video": "", "username_autor": user_atual["username"],
                "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": "horizontal"
            }).execute()
            st.success("Status atualizado!")
            st.rerun()

    # === 🔔 ABA NOTIFICAÇÕES ===
    with aba_notif:
        st.header("🔔 Suas Notificações")
        try:
            n_lista = supabase.table("notificacoes").select("*").eq("id_destinatario", user_atual["id"]).execute()
            if n_lista.data:
                for n in reversed(n_lista.data):
                    st.write(f"• {n['mensagem']}")
            else:
                st.info("Nenhuma notificação por aqui.")
        except:
            st.info("Crie a tabela 'notificacoes' no painel SQL do seu Supabase para ativar este recurso.")
    
