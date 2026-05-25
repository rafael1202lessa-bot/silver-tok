import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2.7 Pro", page_icon="🎬", layout="centered")

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

# --- CONFIGURAÇÕES DE SEGURANÇA MÁXIMA ---
CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# ID Mestre do Rafael - Totalmente protegido contra falsificações
ID_REAL_DEVELOPER = "04daaa3c-63ef-486c-b33e-54d4e80ee9e9"

# --- CONFIGURAÇÃO DE COSMÉTICOS (LOJA) ---
COSMETICOS = {
    "bronze": {"nome": "🥉 Bronze Estelar", "preco": 150},
    "prata": {"nome": "🥈 Prata Lendária", "preco": 300},
    "caixa_azul": {"nome": "🔷 Balão Azul Moderno", "preco": 100},
    "caixa_neon": {"nome": "🔮 Balão Neon Cyber", "preco": 250}
}

# --- BANCO DE DADOS DO BOT ---
VIDEOS_BOT_BOTEY = [
    {"id": "bot_1", "titulo": "⚡ Edit Suprema de Naruto!", "url_video": "https://www.w3schools.com/html/mov_bbb.mp4", "username_autor": "🤖 Bot_Animes", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4213/4213732.png", "curtidas": 142, "tipo_formato": "vertical"},
    {"id": "bot_2", "titulo": "🌌 Relaxing Cinematic View 4K", "url_video": "https://media.w3.org/2010/05/sintel/trailer_hd.mp4", "username_autor": "🤖 Bot_Natureza", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4213/4213732.png", "curtidas": 98, "tipo_formato": "horizontal"}
]

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
    except: pass
    return "⚪ Offline"

def verificar_se_eh_dev(user_id):
    return str(user_id) == ID_REAL_DEVELOPER

def obter_selo_texto(username_alvo, user_id_alvo=None):
    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial":
        return " 👑 DEV"
    try:
        dados = supabase.table("perfis_usuarios").select("id").eq("username", username_alvo).execute()
        if dados.data:
            id_u = dados.data[0]["id"]
            res_seg = supabase.table("seguidores").select("*", count="exact").eq("id_seguido", id_u).execute()
            total = res_seg.count if (hasattr(res_seg, "count") and res_seg.count is not None) else len(res_seg.data)
            if total >= 1000:
                return " ✔️"
    except: pass
    return ""

def renderizar_foto_com_banner(url_foto, username_alvo, user_id_alvo=None, tamanho=90, banner_equipado="Nenhum"):
    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 4px solid #ffd700; box-shadow: 0 0 20px #ffd700;"
        coroa_html = f'<div style="position: absolute; top: -22px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.38)}px; z-index: 10;">👑</div>'
    elif banner_equipado == "🥉 Bronze Estelar":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #cd7f32;"
        coroa_html = ''
    elif banner_equipado == "🥈 Prata Lendária":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #c0c0c0; box-shadow: 0 0 8px #c0c0c0;"
        coroa_html = ''
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

def renderizar_caixa_mensagem(username, mensagem, selo, estilo_caixa, eh_admin=False):
    if eh_admin:
        estilo_css = "background: linear-gradient(135deg, #fff7e6, #ffeaa7); border-left: 5px solid #ffd700; padding: 12px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(255,215,0,0.2);"
    elif estilo_caixa == "🔷 Balão Azul Moderno":
        estilo_css = "background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
    elif estilo_caixa == "🔮 Balão Neon Cyber":
        estilo_css = "background-color: #1a1a2e; border: 1px solid #e94560; color: #fff; padding: 10px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 0 10px #e94560;"
    else:
        estilo_css = "background-color: #f1f3f4; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
        
    st.markdown(f"""
    <div style="{estilo_css}">
        <span style="font-weight: bold; color: {'#d4af37' if eh_admin else '#333'};">{username}</span> 
        <span style="font-size: 12px; font-weight: bold;">{selo}</span>: 
        <span style="color: {'#111' if estilo_caixa != '🔮 Balão Neon Cyber' else '#fff'};">{mensagem}</span>
    </div>
    """, unsafe_allow_html=True)

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
                if cad_user.lower() == "rafael_oficial":
                    st.error("Este nome de usuário é reservado do sistema.")
                    st.stop()
                try:
                    supabase.table("perfis_usuarios").insert({
                        "username": cad_user, "apelido": cad_user, "senha": cad_senha, 
                        "url_foto_perfil": FOTO_PADRAO, "ultimo_visto": datetime.now(timezone.utc).isoformat(),
                        "moedas": 0, "banner_ativo": "Nenhum"
                    }).execute()
                    st.success("Conta criada! Faça login.")
                except:
                    st.error("Nome de usuário indisponível.")
else:
    # Recarrega dados do usuário em tempo real para sincronizar moedas e inventário
    try:
        atualizar_dados = supabase.table("perfis_usuarios").select("*").eq("id", st.session_state.usuario_logado["id"]).execute()
        if atualizar_dados.data:
            st.session_state.usuario_logado = atualizar_dados.data[0]
    except: pass

    user_atual = st.session_state.usuario_logado
    is_admin = verificar_se_eh_dev(user_atual["id"])

    try:
        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", user_atual["id"]).execute()
    except: pass

    total_notif = 0
    try:
        res_n = supabase.table("notificacoes").select("*", count="exact").eq("id_destinatario", user_atual["id"]).eq("lida", False).execute()
        total_notif = res_n.count if (hasattr(res_n, "count") and res_n.count is not None) else len(res_n.data)
    except: pass

    # --- BARRA LATERAL (Sidebar) ---
    with st.sidebar:
        banner_v = user_atual.get("banner_ativo", "Nenhum")
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, user_atual["username"], user_atual["id"], tamanho=90, banner_equipado=banner_v)
        
        selo_proprio = obter_selo_texto(user_atual["username"], user_atual["id"])
        st.write(f"**{user_atual.get('apelido') or user_atual['username']}** {selo_proprio}")
        st.markdown(f"🪙 **Saldo:** {user_atual.get('moedas', 0)} Moedas")
        
        # --- INVENTÁRIO DE COSMÉTICOS ---
        with st.expander("🎒 Meu Inventário"):
            st.caption("Equipe seus cosméticos adquiridos na loja:")
            estilo_atual = user_atual.get("banner_ativo", "Nenhum")
            st.write(f"Equipado: **{estilo_atual}**")
            
            escolha_custom = st.selectbox("Escolha uma customização:", ["Nenhum", "🥉 Bronze Estelar", "🥈 Prata Lendária", "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber"])
            if st.button("Equipar Item 🛡️"):
                try:
                    supabase.table("perfis_usuarios").update({"banner_ativo": escolha_custom}).eq("id", user_atual["id"]).execute()
                    st.success("Cosmético alterado!")
                    st.rerun()
                except: st.error("Erro ao equipar item.")

        # --- MENU EDITAR PERFIL ---
        with st.expander("⚙️ Editar Meu Perfil"):
            novo_apelido = st.text_input("Alterar Apelido:", value=user_atual.get("apelido") or user_atual["username"])
            nova_foto = st.text_input("URL da Foto de Perfil:", value=user_atual.get("url_foto_perfil") or FOTO_PADRAO)
            if st.button("Salvar Alterações 💾"):
                try:
                    supabase.table("perfis_usuarios").update({
                        "apelido": novo_apelido.strip(),
                        "url_foto_perfil": nova_foto.strip()
                    }).eq("id", user_atual["id"]).execute()
                    st.success("Perfil atualizado!")
                    st.rerun()
                except: st.error("Erro ao atualizar dados.")

        # --- PAINEL DE ADMINISTRADOR MASTER ---
        if is_admin:
            st.markdown("---")
            st.markdown("### 👑 Painel Secreto Master")
            with st.expander("🚀 Comandos de Admin"):
                qtd_moedas = st.number_input("Quantidade de Moedas:", min_value=0, max_value=1000000, value=1000)
                
                try:
                    membros_db = supabase.table("perfis_usuarios").select("username").execute()
                    lista_membros = [u["username"] for u in membros_db.data] if membros_db.data else [user_atual["username"]]
                except:
                    lista_membros = [user_atual["username"]]
                    
                alvo_moedas = st.selectbox("Dar moedas para:", lista_membros)
                
                if st.button("Injetar Moedas 💸", type="primary"):
                    try:
                        dados_alvo = supabase.table("perfis_usuarios").select("moedas").eq("username", alvo_moedas).execute()
                        saldo_atual = dados_alvo.data[0].get("moedas", 0) if dados_alvo.data else 0
                        
                        supabase.table("perfis_usuarios").update({"moedas": saldo_atual + qtd_moedas}).eq("username", alvo_moedas).execute()
                        st.success(f"Moedas injetadas com sucesso em {alvo_moedas}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao injetar fundos: {e}")

        st.markdown("---")
        if st.button("Sair da Conta 🚪", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.sala_ativa = None
            st.session_state.perfil_visitado = None
            st.rerun()

    # --- NAVEGAÇÃO PRINCIPAL ---
    aba_feed, aba_loja, aba_chat, aba_status, aba_notif = st.tabs([
        "📺 Silver Tok (Feed)", "🛒 Loja & Caixas", "💬 Chat-Exv", "✨ Status", f"🔔 Notificações ({total_notif})"
    ])

    def renderizar_lista_filtrada(lista_posts, identificador_formato, termo_busca="", ordenacao=""):
        if termo_busca:
            lista_posts = [p for p in lista_posts if termo_busca.lower() in str(p.get("titulo", "")).lower()]
        if ordenacao == "🔥 Mais Populares":
            lista_posts = sorted(lista_posts, key=lambda x: x.get("curtidas", 0), reverse=True)

        for idx, v in enumerate(lista_posts):
            if str(v.get("titulo", "")).startswith("[STATUS]"): continue
            autor = v.get('username_autor', 'Membro')
            id_autor_post = v.get('id_autor')
            img_autor = v.get('avatar_autor') or FOTO_PADRAO
            video_url = v["url_video"]
            id_post = v.get("id")
            chave_comp = f"feed_{identificador_formato}_{idx}_{id_post}"

            st.markdown("---")
            col_f1, col_f2 = st.columns([1, 5])
            with col_f1: 
                renderizar_foto_com_banner(img_autor, autor, id_autor_post, tamanho=50)
                if st.button("👤", key=f"btn_perfil_f_{chave_comp}"):
                    st.session_state.perfil_visitado = autor
                    st.rerun()
            with col_f2:
                selo_autor = obter_selo_texto(autor, id_autor_post)
                st.markdown(f"**{autor}** {selo_autor}")
                st.caption(v["titulo"])

            if v.get("tipo_formato") == "vertical":
                st.markdown(f'<div style="display: flex; justify-content: center;"><video width="290" height="515" controls><source src="{video_url}" type="video/mp4"></video></div>', unsafe_allow_html=True)
            else:
                if str(video_url).lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    st.image(video_url, use_container_width=True)
                else:
                    st.video(video_url)

            # Botões Curtir e Excluir
            col_b1, col_b2 = st.columns([2, 2])
            with col_b1:
                if st.button(f"❤️ {v.get('curtidas', 0)} Curtidas", key=f"like_{chave_comp}"):
                    if "bot_" not in str(id_post):
                        try:
                            supabase.table("feed_videos").update({"curtidas": v.get('curtidas', 0) + 1}).eq("id", id_post).execute()
                        except: pass
                    st.rerun()
            with col_b2:
                if autor == user_atual["username"] or verificar_se_eh_dev(user_atual["id"]):
                    if st.button("Remover Post 🗑️", key=f"del_{chave_comp}"):
                        if "bot_" not in str(id_post):
                            try:
                                supabase.table("feed_videos").delete().eq("id", id_post).execute()
                            except: pass
                        st.rerun()

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
                    renderizar_foto_com_banner(p_info.get("url_foto_perfil") or FOTO_PADRAO, autor_vis, p_info["id"], tamanho=80, banner_equipado=p_info.get("banner_ativo", "Nenhum"))
                with col_p2:
                    s_vis = obter_selo_texto(autor_vis, p_info["id"])
                    st.subheader(f"{p_info.get('apelido') or autor_vis} {s_vis}")
                    
                    if autor_vis != user_atual["username"]:
                        ja_segue = supabase.table("seguidores").select("*").eq("id_seguidor", user_atual["id"]).eq("id_seguido", p_info["id"]).execute()
                        if ja_segue.data:
                            if st.button("Seguindo ✓"):
                                supabase.table("seguidores").delete().eq("id_seguidor", user_atual["id"]).eq("id_seguido", p_info["id"]).execute()
                                st.rerun()
                        else:
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
            exibir_logo()
            busca_legenda = st.text_input("Buscar posts por legenda:", placeholder="Ex: Bleach, Naruto...")
            ordenar_por = st.radio("Ordenar por:", ["📅 Mais Recentes", "🔥 Mais Populares"], horizontal=True)
            
            aba_midia = st.tabs(["📱 Mini Vídeos", "🖥️ Vídeos Longos / Fotos"])
            
            with aba_midia[0]:
                try:
                    f_dados = supabase.table("feed_videos").select("*").eq("tipo_formato", "vertical").execute()
                    posts_completos = (f_dados.data or []) + [b for b in VIDEOS_BOT_BOTEY if b["tipo_formato"] == "vertical"]
                    renderizar_lista_filtrada(reversed(posts_completos), "vertical_global", busca_legenda, ordenar_por)
                except: pass

            with aba_midia[1]:
                with st.expander("➕ Publicar Novo Conteúdo"):
                    t_pub = st.text_input("Legenda:", key="leg_nova")
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
                    f_dados = supabase.table("feed_videos").select("*").eq("tipo_formato", "horizontal").execute()
                    posts_completos_h = (f_dados.data or []) + [b for b in VIDEOS_BOT_BOTEY if b["tipo_formato"] == "horizontal"]
                    renderizar_lista_filtrada(reversed(posts_completos_h), "horizontal_global", busca_legenda, ordenar_por)
                except: pass

    # === 🛒 ABA LOJA DE BANNERS E CAIXAS ===
    with aba_loja:
        st.header("🛒 Loja de Cosméticos Premium")
        st.caption("Adquira novas molduras e caixas de mensagens personalizadas.")
        
        col_l1, col_l2 = st.columns(2)
        
        for idx, (chave, info) in enumerate(COSMETICOS.items()):
            coluna_foco = col_l1 if idx % 2 == 0 else col_l2
            with coluna_foco:
                st.markdown(f"### {info['nome']}")
                st.write(f"Preço: 🪙 {info['preco']} moedas")
                
                if user_atual.get("moedas", 0) >= info['preco']:
                    if st.button(f"Comprar", key=f"loja_buy_{chave}", use_container_width=True):
                        novo_saldo = user_atual["moedas"] - info['preco']
                        try:
                            supabase.table("perfis_usuarios").update({"moedas": novo_saldo}).eq("id", user_atual["id"]).execute()
                            st.success(f"Você comprou: {info['nome']}! Equipe no seu inventário.")
                            st.rerun()
                        except: st.error("Erro na transação.")
                else:
                    st.button("Saldo Insuficiente ❌", key=f"insuf_{chave}", disabled=True, use_container_width=True)

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
                            
                            try:
                                estilo_u = supabase.table("perfis_usuarios").select("banner_ativo", "id").eq("username", m['username']).execute()
                                txt_caixa = estilo_u.data[0].get("banner_ativo", "Nenhum") if estilo_u.data else "Nenhum"
                                uid_remetente = estilo_u.data[0].get("id") if estilo_u.data else ""
                            except:
                                txt_caixa = "Nenhum"
                                uid_remetente = ""
                                
                            renderizar_caixa_mensagem(m['username'], m['mensagem'], s_msg, txt_caixa, eh_admin=verificar_se_eh_dev(uid_remetente))
            except: pass
        else:
            st.title("🎛️ Painel Chat-Exv")
            t_chat = st.tabs(["💬 Privado", "👥 Grupos", "👥 Membros"])
            
            with t_chat[0]:
                alvo = st.text_input("Username do amigo para iniciar privado:").strip()
                if st.button("Iniciar Chat Privado") and alvo:
                    lista = sorted([user_atual['username'].upper(), alvo.upper()])
                    st.session_state.sala_ativa = f"PRIV-{lista[0]}-{lista[1]}"
                    st.rerun()
            
            with t_chat[1]:
                g_nome = st.text_input("Nome do Grupo:").strip().upper()
                if st.button("Criar / Entrar no Grupo 🔐") and g_nome:
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
                                    renderizar_foto_com_banner(u.get("url_foto_perfil") or FOTO_PADRAO, u["username"], u["id"], tamanho=50, banner_equipado=u.get("banner_ativo", "Nenhum"))
                                with col_u2:
                                    s_u = obter_selo_texto(u["username"], u["id"])
                                    st.markdown(f"**{u['username']}** {s_u}")
                                    st.caption(obter_status_emoji(u.get("ultimo_visto")))
                                with col_u3:
                                    if st.button("Chat 💬", key=f"u_ch_{u['username']}"):
                                        lista = sorted([user_atual['username'].upper(), u['username'].upper()])
                                        st.session_state.sala_ativa = f"PRIV-{lista[0]}-{lista[1]}"
                                        st.rerun()
                except: pass

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
            st.info("Notificações desativadas ou tabela ausente.")
