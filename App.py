import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2.9.2", page_icon="🎬", layout="centered")

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

# --- CONFIGURAÇÕES GERAIS ---
CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
NOME_DEVELOPER = "Rafael_oficial"
COMANDO_BOT_SECRETO = "/gerar_conteudo_bot"

DIC_BANNERS = {
    "Nenhum": 0,
    "🥉 Bronze Estelar": 150,
    "🥈 Prata Lendária": 300,
    "🥇 Ouro Real": 600,
    "🔥 Neon Cyberpunk": 1200
}

VIDEOS_BOT_BOTEY = [
    {"titulo": "🔥 Edit Incrível de Anime (Vertical)", "url": "https://www.w3schools.com/html/mov_bbb.mp4", "formato": "vertical"},
    {"titulo": "🌌 Gameplay Relaxante 4K (Horizontal)", "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", "formato": "horizontal"}
]

# --- FUNÇÕES AUXILIARES ---
def obter_status_emoji(timestamp_str):
    if not timestamp_str: return "⚪ Offline"
    try:
        if "T" in timestamp_str:
            timestamp_str = timestamp_str.split("+")[0]
            dt_usuario = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)
        else:
            dt_usuario = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
        agora = datetime.now(timezone.utc)
        if agora - dt_usuario < timedelta(minutes=3): return "🟢 Online"
    except: pass
    return "⚪ Offline"

def obter_selo_usuario(username, id_usuario):
    if username == NOME_DEVELOPER: return " 👑`DEV`"
    try:
        res = supabase.table("seguidores").select("*", count="exact").eq("id_seguido", id_usuario).execute()
        total = res.count if (hasattr(res, "count") and res.count is not None) else len(res.data)
        if total >= 1000: return " ✔️"
    except: pass
    return ""

def renderizar_foto_com_banner(url_foto, tipo_banner, username_alvo="", tamanho=90):
    estilo_css = "border-radius: 50%; object-fit: cover;"
    mostrar_coroa = False
    
    if username_alvo == NOME_DEVELOPER:
        estilo_css += " border: 5px solid #ffd700; box-shadow: 0 0 25px #ffaa00, inset 0 0 10px #ffd700;"
        mostrar_coroa = True
    else:
        if "Bronze" in tipo_banner: estilo_css += " border: 4px solid #cd7f32; box-shadow: 0 0 10px #cd7f32;"
        elif "Prata" in tipo_banner: estilo_css += " border: 4px solid #c0c0c0; box-shadow: 0 0 12px #c0c0c0;"
        elif "Ouro" in tipo_banner: estilo_css += " border: 5px solid #ffd700; box-shadow: 0 0 15px #ffd700;"
        elif "Neon" in tipo_banner: estilo_css += " border: 4px solid #00f3ff; box-shadow: 0 0 20px #ff007f, inset 0 0 10px #00f3ff;"

    coroa_html = f'<div style="position: absolute; top: -22px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">👑</div>' if mostrar_coroa else ''
    
    html = f"""
    <div style="position: relative; display: inline-block; text-align: center; margin-top: 15px; margin-bottom: 5px;">
        {coroa_html}
        <img src="{url_foto}" width="{tamanho}" height="{tamanho}" style="{estilo_css}">
    </div>
    """
    return st.markdown(html, unsafe_allow_html=True)

def processar_ganho_de_moedas(user_id):
    try:
        res = supabase.table("perfis_usuarios").select("moedas", "ultimo_bonus_tempo").eq("id", user_id).execute()
        if res.data:
            dados = res.data[0]
            moedas_atuais = dados.get("moedas", 0)
            ultimo_tempo_str = dados.get("ultimo_bonus_tempo")
            
            if ultimo_tempo_str:
                ultimo_tempo = datetime.fromisoformat(ultimo_tempo_str.split("+")[0]).replace(tzinfo=timezone.utc)
                agora = datetime.now(timezone.utc)
                minutos_passados = int((agora - ultimo_tempo).total_seconds() / 60)
                
                ciclos = minutos_passados // 2
                if ciclos > 0:
                    novas_moedas = moedas_atuais + (ciclos * 10)
                    supabase.table("perfis_usuarios").update({"moedas": novas_moedas, "ultimo_bonus_tempo": agora.isoformat()}).eq("id", user_id).execute()
                    st.session_state.usuario_logado["moedas"] = novas_moedas
                    st.toast(f"🪙 Ganhaste +{ciclos * 10} moedas por atividade!")
    except: pass

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state: st.session_state.sala_ativa = None
if "perfil_visitado" not in st.session_state: st.session_state.perfil_visitado = None

# --- AUTENTICAÇÃO ---
if st.session_state.usuario_logado is None:
    exibir_logo()
    aba_auth = st.tabs(["Fazer Login", "Criar Nova Conta"])
    with aba_auth[0]:
        st.subheader("Acesse sua Conta")
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        if st.button("Entrar 🚀", use_container_width=True):
            if login_user and login_senha:
                try:
                    busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                    if busca.data and busca.data[0]["senha"] == login_senha:
                        st.session_state.usuario_logado = busca.data[0]
                        st.rerun()
                    else: st.error("Dados incorretos.")
                except Exception as e: st.error(f"Erro: {e}")
                
    with aba_auth[1]:
        st.subheader("Crie seu Perfil")
        cad_user = st.text_input("Escolha um Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie uma Senha:", type="password", key="cad_senha")
        codigo_convite = st.text_input("🔑 Código Secreto:", type="password", key="codigo_convite")
        if st.button("Cadastrar Conta 🎉", use_container_width=True):
            if cad_user and cad_senha and codigo_convite == CHAVE_SECRETA:
                try:
                    supabase.table("perfis_usuarios").insert({
                        "username": cad_user, "apelido": cad_user, "senha": cad_senha, 
                        "url_foto_perfil": FOTO_PADRAO, "ultimo_visto": datetime.now(timezone.utc).isoformat(),
                        "moedas": 100, "banner_ativo": "Nenhum"
                    }).execute()
                    st.success("Conta criada com sucesso!")
                except: st.error("Erro ao cadastrar ou utilizador já existente.")
else:
    user_atual = st.session_state.usuario_logado
    
    try:
        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", user_atual["id"]).execute()
        processar_ganho_de_moedas(user_atual["id"])
    except: pass

    try:
        dados_frescos = supabase.table("perfis_usuarios").select("moedas", "banner_ativo").eq("id", user_atual["id"]).execute()
        if dados_frescos.data:
            user_atual["moedas"] = dados_frescos.data[0]["moedas"]
            user_atual["banner_ativo"] = dados_frescos.data[0]["banner_ativo"]
    except: pass

    selo_lateral = obter_selo_usuario(user_atual["username"], user_atual["id"])

    # --- SIDEBAR (PERFIL) ---
    st.sidebar.markdown("<p style='text-align:center; font-weight:bold; margin-bottom:0;'>Meu Perfil</p>", unsafe_allow_html=True)
    renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, user_atual.get("banner_ativo", "Nenhum"), username_alvo=user_atual["username"])
    
    nome_exibicao = user_atual.get("apelido") or user_atual["username"]
    st.sidebar.markdown(f"<h3 style='text-align:center; margin-top:0; margin-bottom:0;'>{nome_exibicao}{selo_lateral}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center; color:gray; margin-top:0;'>@{user_atual['username']}</p>", unsafe_allow_html=True)
    st.sidebar.markdown(f"### 🪙 Carteira: **{user_atual.get('moedas', 0)}** moedas")

    if user_atual["username"] == NOME_DEVELOPER:
        with st.sidebar.expander("🤖 Comandos de Developer", expanded=False):
            st.code(COMANDO_BOT_SECRETO, language="text")
            comando_exec = st.text_input("Digitar comando especial:")
            if st.button("Executar Comando ⚡", use_container_width=True):
                if comando_exec.strip() == COMANDO_BOT_SECRETO:
                    for v_item in VIDEOS_BOT_BOTEY:
                        try:
                            supabase.table("feed_videos").insert({
                                "titulo": v_item["titulo"], "url_video": v_item["url"],
                                "username_autor": "System_Bot", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4712/4712035.png",
                                "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": v_item["formato"]
                            }).execute()
                        except: pass
                    st.success("Conteúdo gerado pelo bot!")
                    st.rerun()

    if st.sidebar.button("Sair da Conta 🚪", use_container_width=True):
        st.session_state.usuario_logado = None
        st.session_state.sala_ativa = None
        st.session_state.perfil_visitado = None
        st.rerun()

    # --- 🗂️ RESTAURAÇÃO DAS 4 ABAS SUPERIORES GLOBAIS ---
    aba_feed, aba_chat_exv, aba_status, aba_notif, aba_loja = st.tabs([
        "📺 Silver Tok (Feed)", "💬 Chat-Exv", "✨ Status", "🔔 Notificações (0)", "🛒 Loja de Banners"
    ])
    
    # === 📺 ABA 1: FEED GALERIA ===
    with aba_feed:
        if st.session_state.perfil_visitado is not None:
            autor_vis = st.session_state.perfil_visitado
            if st.button("⬅️ Voltar para o Feed Global"):
                st.session_state.perfil_visitado = None
                st.rerun()
            st.write(f"A visualizar perfil de: **@{autor_vis}**")
        else:
            exibir_logo()
            termo_pesquisa = st.text_input("Buscar posts por legenda:", placeholder="Ex: Bleach, Naruto...").strip()
            ordem_feed = st.radio("Ordenar por:", ["📅 Mais Recentes", "🔥 Mais Populares"], horizontal=True)

            aba_formato_mini, aba_formato_longo = st.tabs(["📱 Mini Vídeos", "🖥️ Vídeos Longos / Fotos"])

            def renderizar_lista_filtrada(lista_posts, identificador_formato):
                for idx, v in enumerate(lista_posts):
                    autor = v.get('username_autor', 'Membro')
                    img_autor = v.get('avatar_autor') or FOTO_PADRAO
                    video_url = v["url_video"]
                    likes = v.get("curtidas", 0)
                    id_post = v.get("id")
                    chave_comp = f"feed_{identificador_formato}_{idx}_{id_post}"

                    st.markdown("---")
                    col_f1, col_f2 = st.columns([1, 5])
                    with col_f1: 
                        renderizar_foto_com_banner(img_autor, "Nenhum", username_alvo=autor, tamanho=55)
                        if st.button("👤", key=f"p_{chave_comp}"):
                            st.session_state.perfil_visitado = autor
                            st.rerun()
                    with col_f2:
                        st.markdown(f"**{autor}**")
                        st.caption(v["titulo"])

                    if identificador_formato == "vertical":
                        st.markdown(f'<div style="text-align:center; background:#000; padding:5px; border-radius:12px;"><video width="280" height="490" controls><source src="{video_url}" type="video/mp4"></video></div>', unsafe_allow_html=True)
                    else:
                        st.video(video_url)

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button(f"❤️ {likes} Curtidas", key=f"lk_{chave_comp}"):
                            supabase.table("feed_videos").update({"curtidas": likes + 1}).eq("id", id_post).execute()
                            st.rerun()
                    with col_b2:
                        if autor == user_atual["username"] and st.button("Remover 🗑️", key=f"del_{chave_comp}"):
                            supabase.table("feed_videos").delete().eq("id", id_post).execute()
                            st.rerun()

                    with st.expander("💬 Comentários"):
                        with st.form(key=f"f_c_{chave_comp}", clear_on_submit=True):
                            novo_coment = st.text_input("Escreve um comentário:")
                            if st.form_submit_button("Comentar ✉️") and novo_coment.strip():
                                try:
                                    supabase.table("comentarios_feed").insert({
                                        "id_video": id_post, "id_autor": user_atual["id"], 
                                        "username_autor": user_atual["username"], "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, 
                                        "comentario": novo_coment.strip()
                                    }).execute()
                                    st.rerun()
                                except: pass

                        try:
                            lista_c = supabase.table("comentarios_feed").select("*").eq("id_video", id_post).order("criado_em", descending=True).execute()
                            if lista_c.data:
                                for c in lista_c.data:
                                    st.markdown(f"**{c['username_autor']}**: {c['comentario']}")
                        except: pass

            try:
                query_feed = supabase.table("feed_videos").select("*")
                if termo_pesquisa: query_feed = query_feed.ilike("titulo", f"%{termo_pesquisa}%")
                query_feed = query_feed.order("curtidas" if "Populares" in ordem_feed else "criado_em", descending=True)
                dados = query_feed.execute()
                if dados.data:
                    with aba_formato_mini:
                        renderizar_lista_filtrada([p for p in dados.data if p.get("tipo_formato") == "vertical"], "vertical")
                    with aba_formato_longo:
                        renderizar_lista_filtrada([p for p in dados.data if p.get("tipo_formato") != "vertical"], "horizontal")
            except: pass

    # === 💬 ABA 2: RESTAURAÇÃO COMPLETA DO PAINEL CHAT-EXV ===
    with aba_chat_exv:
        st.markdown("## 🎛️ Painel Chat-Exv")
        
        # Sub-abas internas originais resgatadas!
        sub_chat_privado, sub_chat_grupo, sub_chat_entrar, sub_chat_amigos, sub_chat_adicionar = st.tabs([
            "💬 Privado", "👥 Novo Grupo", "🔑 Entrar", "👥 Amigos", "➕ Adicionar"
        ])
        
        with sub_chat_privado:
            st.info("Selecione um amigo listado na aba 'Amigos' e abra o canal privado.")
            
        with sub_chat_grupo:
            st.subheader("Criar Novo Grupo de Conversa")
            st.text_input("Nome do Grupo:", placeholder="Ex: Desenvolvedores, Amigos do Anime...")
            st.button("Criar Grupo 👥")
            
        with sub_chat_entrar:
            st.subheader("Entrar numa Sala Existente")
            cod_sala = st.text_input("Insira o código do chat ou ID:", key="cod_sala_entrar").strip().upper()
            if st.button("Entrar na Sala 🚪") and cod_sala:
                st.session_state.sala_ativa = cod_sala
                st.success(f"Conectado à sala {cod_sala}!")
                
        with sub_chat_amigos:
            st.subheader("Lista de Amigos")
            st.caption("Nenhum amigo online de momento.")
            
        with sub_chat_adicionar:
            st.subheader("Adicionar Novos Amigos")
            st.text_input("Introduza o @username do utilizador:")
            st.button("Enviar Pedido de Amizade 🤝")

    # === ✨ ABA 3: RESTAURAÇÃO DA ABA STATUS ===
    with aba_status:
        st.subheader("✨ Status Recentes")
        st.write("Área destinada para atualizações de Status temporários de 24 horas.")
        st.text_input("O que está a pensar hoje?", placeholder="Escreva o seu status temporário aqui...")
        st.button("Publicar Status 🚀")

    # === 🔔 ABA 4: RESTAURAÇÃO DA ABA NOTIFICAÇÕES ===
    with aba_notif:
        st.subheader("🔔 Central de Notificações")
        st.info("Sem notificações complexas ativas.")

    # === 🛒 ABA 5: LOJA DE BANNERS ===
    with aba_loja:
        st.header("🛒 Loja de Molduras de Perfil")
        st.write(f"Suas Moedas: 🪙 **{user_atual.get('moedas', 0)}**")
        st.markdown("---")
        
        for nome_b, preco in DIC_BANNERS.items():
            if nome_b == "Nenhum": continue
            col_l1, col_l2, col_l3 = st.columns([1, 2, 2])
            with col_l1: renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, nome_b, tamanho=60)
            with col_l2: st.write(f"**{nome_b}**\nPreço: 🪙 {preco}")
            with col_l3:
                if st.button(f"Adquirir {nome_b}", key=f"loja_{nome_b}"):
                    st.toast("Funcionalidade da loja carregada!")
         
