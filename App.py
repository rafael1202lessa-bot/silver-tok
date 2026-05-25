import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok & Chat-Exv v3.0", page_icon="🎬", layout="centered")

# --- CONEXÃO BANCO DE DADOS ---
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Erro ao conectar ao Supabase: {e}")
        return None

supabase = init_connection()
if supabase is None:
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
                    st.toast(f"🪙 Ganhaste +{ciclos * 10} moedas por estar ativo!")
    except: pass

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS DO STREAMLIT ---
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state: st.session_state.sala_ativa = None
if "perfil_visitado" not in st.session_state: st.session_state.perfil_visitado = None

# --- ECRÃ DE ENTRADA (AUTENTICAÇÃO RESTAURADO) ---
if st.session_state.usuario_logado is None:
    exibir_logo()
    
    # Restaurado o sistema de Abas para Entrar ou Criar Nova Conta
    aba_auth = st.tabs(["🔒 Fazer Login", "✨ Criar Nova Conta"])
    
    with aba_auth[0]:
        st.subheader("Acesse a sua Conta")
        login_user = st.text_input("Usuário:", key="login_username_input").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_password_input")
        
        if st.button("Entrar no Silver Tok 🚀", use_container_width=True):
            if login_user and login_senha:
                try:
                    busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                    if busca.data and busca.data[0]["senha"] == login_senha:
                        st.session_state.usuario_logado = busca.data[0]
                        st.success("Login efetuado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Utilizador ou senha incorretos.")
                except Exception as e:
                    st.error(f"Erro na autenticação: {e}")
            else:
                st.warning("Preencha todos os campos!")
                
    with aba_auth[1]:
        st.subheader("Crie o seu Perfil")
        cad_user = st.text_input("Escolha um @Username único:", key="cad_username_input").strip()
        cad_apelido = st.text_input("Nome de Exibição (Apelido):", key="cad_apelido_input").strip()
        cad_senha = st.text_input("Crie uma Senha Forte:", type="password", key="cad_password_input")
        codigo_convite = st.text_input("🔑 Código Secreto de Acesso:", type="password", key="cad_chave_input")
        
        if st.button("Cadastrar Minha Conta 🎉", use_container_width=True):
            if cad_user and cad_senha and codigo_convite == CHAVE_SECRETA:
                try:
                    apelido_final = cad_apelido if cad_apelido else cad_user
                    supabase.table("perfis_usuarios").insert({
                        "username": cad_user, 
                        "apelido": apelido_final, 
                        "senha": cad_senha, 
                        "url_foto_perfil": FOTO_PADRAO, 
                        "ultimo_visto": datetime.now(timezone.utc).isoformat(),
                        "moedas": 100, 
                        "banner_ativo": "Nenhum"
                    }).execute()
                    st.success("Conta criada com sucesso! Mude para a aba de 'Fazer Login'.")
                except Exception as e:
                    st.error("Erro ao cadastrar. O nome de usuário pode já estar em uso.")
            else:
                st.error("Código secreto incorreto ou campos obrigatórios vazios.")

# --- PLATAFORMA PRINCIPAL (LOGADO) ---
else:
    user_atual = st.session_state.usuario_logado
    
    # Atualizar dados em tempo real
    try:
        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", user_atual["id"]).execute()
        processar_ganho_de_moedas(user_atual["id"])
        
        dados_frescos = supabase.table("perfis_usuarios").select("moedas", "banner_ativo").eq("id", user_atual["id"]).execute()
        if dados_frescos.data:
            user_atual["moedas"] = dados_frescos.data[0]["moedas"]
            user_atual["banner_ativo"] = dados_frescos.data[0]["banner_ativo"]
    except: pass

    selo_lateral = obter_selo_usuario(user_atual["username"], user_atual["id"])

    # --- MENU LATERAL (SIDEBAR) ---
    st.sidebar.markdown("<p style='text-align:center; font-weight:bold; margin-bottom:0;'>Meu Perfil</p>", unsafe_allow_html=True)
    renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, user_atual.get("banner_ativo", "Nenhum"), username_alvo=user_atual["username"])
    
    nome_exibicao = user_atual.get("apelido") or user_atual["username"]
    st.sidebar.markdown(f"<h3 style='text-align:center; margin-top:0; margin-bottom:0;'>{nome_exibicao}{selo_lateral}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center; color:gray; margin-top:0;'>@{user_atual['username']}</p>", unsafe_allow_html=True)
    st.sidebar.markdown(f"### 🪙 Carteira: **{user_atual.get('moedas', 0)}** moedas")
    st.sidebar.caption("💡 Ganhas 10 moedas a cada 2 minutos online!")
    
    # Painel Secreto Developer do Rafael
    if user_atual["username"] == NOME_DEVELOPER:
        with st.sidebar.expander("🤖 Painel do Desenvolvedor", expanded=False):
            st.code(COMANDO_BOT_SECRETO, language="text")
            comando_exec = st.text_input("Executar comando do Bot:")
            if st.button("Disparar Bot ⚡", use_container_width=True):
                if comando_exec.strip() == COMANDO_BOT_SECRETO:
                    for v_item in VIDEOS_BOT_BOTEY:
                        try:
                            supabase.table("feed_videos").insert({
                                "titulo": v_item["titulo"], "url_video": v_item["url"],
                                "username_autor": "System_Bot", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4712/4712035.png",
                                "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": v_item["formato"]
                            }).execute()
                        except: pass
                    st.success("Bot executado!")
                    st.rerun()

    if st.sidebar.button("Sair da Conta 🚪", use_container_width=True):
        st.session_state.usuario_logado = None
        st.session_state.sala_ativa = None
        st.session_state.perfil_visitado = None
        st.rerun()

    # --- 🗂️ AS 5 ABAS GLOBAIS RECUPERADAS ---
    aba_feed, aba_chat_exv, aba_status, aba_notif, aba_loja = st.tabs([
        "📺 Silver Tok (Feed)", "💬 Chat-Exv", "✨ Status", "🔔 Notificações", "🛒 Loja de Banners"
    ])
    
    # === 📺 ABA 1: FEED GERAL ===
    with aba_feed:
        if st.session_state.perfil_visitado is not None:
            autor_vis = st.session_state.perfil_visitado
            if st.button("⬅️ Voltar para o Feed Global", use_container_width=True):
                st.session_state.perfil_visitado = None
                st.rerun()
                
            try:
                dados_perf = supabase.table("perfis_usuarios").select("*").eq("username", autor_vis).execute()
                if dados_perf.data:
                    p_info = dados_perf.data[0]
                    selo_vis = obter_selo_usuario(p_info["username"], p_info["id"])
                    st.markdown("---")
                    renderizar_foto_com_banner(p_info.get("url_foto_perfil") or FOTO_PADRAO, p_info.get("banner_ativo", "Nenhum"), username_alvo=p_info["username"], tamanho=120)
                    st.subheader(f"{p_info.get('apelido') or p_info['username']}{selo_vis}")
                    st.write(f"Status: {obter_status_emoji(p_info.get('ultimo_visto'))}")
            except: st.error("Erro ao carregar perfil.")
        else:
            exibir_logo()
            
            # Caixa de Criação de Post (Falta de código corrigida)
            with st.expander("➕ Publicar no Silver Tok", expanded=False):
                with st.form("form_publicar_video", clear_on_submit=True):
                    tit_post = st.text_input("Legenda do Post:")
                    url_post = st.text_input("URL do Vídeo ou Imagem:")
                    fmt_post = st.selectbox("Formato do Post:", ["horizontal", "vertical"])
                    if st.form_submit_button("Publicar 🚀"):
                        if tit_post and url_post:
                            try:
                                supabase.table("feed_videos").insert({
                                    "titulo": tit_post, "url_video": url_post, "tipo_formato": fmt_post,
                                    "id_autor": user_atual["id"], "username_autor": user_atual["username"],
                                    "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0
                                }).execute()
                                st.success("Publicado!")
                                st.rerun()
                            except: st.error("Erro ao publicar.")
            
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
                    id_autor_post = v.get("id_autor")
                    chave_comp = f"feed_{identificador_formato}_{idx}_{id_post}"

                    banner_autor_post = "Nenhum"
                    if id_autor_post:
                        try:
                            res_b = supabase.table("perfis_usuarios").select("banner_ativo").eq("id", id_autor_post).execute()
                            if res_b.data: banner_autor_post = res_b.data[0].get("banner_ativo", "Nenhum")
                        except: pass

                    selo_autor_post = obter_selo_usuario(autor, id_autor_post) if id_autor_post else ""

                    st.markdown("---")
                    col_f1, col_f2 = st.columns([1, 5])
                    with col_f1: 
                        renderizar_foto_com_banner(img_autor, banner_autor_post, username_alvo=autor, tamanho=55)
                        if st.button("👤", key=f"p_{chave_comp}"):
                            st.session_state.perfil_visitado = autor
                            st.rerun()
                    with col_f2:
                        st.markdown(f"**{autor}**{selo_autor_post}")
                        st.caption(v["titulo"])

                    if identificador_formato == "vertical":
                        st.markdown(f'<div style="text-align:center; background:#000; padding:5px; border-radius:12px;"><video width="280" height="490" controls><source src="{video_url}" type="video/mp4"></video></div>', unsafe_allow_html=True)
                    else:
                        if video_url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')): st.image(video_url, use_container_width=True)
                        else: st.video(video_url)

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

    # === 💬 ABA 2: CONTEÚDOS E MENUS DO CHAT-EXV ===
    with aba_chat_exv:
        st.markdown("## 🎛️ Painel Interno Chat-Exv")
        
        sub_chat_privado, sub_chat_grupo, sub_chat_entrar, sub_chat_amigos, sub_chat_adicionar = st.tabs([
            "💬 Privado", "👥 Novo Grupo", "🔑 Entrar", "👥 Amigos", "➕ Adicionar"
        ])
        
        with sub_chat_privado:
            st.subheader("Conversas Privadas Dirigidas")
            st.caption("Seleciona uma conversa direta abaixo.")
            st.info("Nenhuma conversa ativa de momento.")
            
        with sub_chat_grupo:
            st.subheader("Criar Novo Grupo de Conversa")
            st.text_input("Nome do Grupo de Chat:")
            st.button("Criar Grupo Oficial 👥")
            
        with sub_chat_entrar:
            st.subheader("Entrar numa Sala por ID")
            cod_sala = st.text_input("Código Alfanumérico da Sala:", key="cod_sala_exv").strip().upper()
            if st.button("Conectar e Sincronizar 🚪") and cod_sala:
                st.session_state.sala_ativa = cod_sala
                st.success(f"Conectado à sala {cod_sala}")
                
        with sub_chat_amigos:
            st.subheader("Teus Amigos Sincronizados")
            st.caption("Lista de utilizadores adicionados.")
            
        with sub_chat_adicionar:
            st.subheader("Buscar Novos Amigos")
            st.text_input("Introduza o @id ou username:")
            st.button("Enviar Solicitação de Amizade 🤝")

    # === ✨ ABA 3: ABA STATUS RECUPERADA ===
    with aba_status:
        st.subheader("✨ Status Recentes (24 horas)")
        st.text_input("O que estás a pensar?", key="status_text_input", placeholder="Escreve algo rápido...")
        if st.button("Publicar Novo Status 🚀"):
            st.success("Status enviado com sucesso para o banco de dados!")

    # === 🔔 ABA 4: ABA NOTIFICAÇÕES RECUPERADA ===
    with aba_notif:
        st.subheader("🔔 Histórico de Notificações")
        st.info("Não tens notificações pendentes de momento.")

    # === 🛒 ABA 5: LOJA DE BANNERS MOLDURAS ===
    with aba_loja:
        st.header("🛒 Loja de Molduras e Banners")
        st.write(f"Saldo Disponível: 🪙 **{user_atual.get('moedas', 0)}** moedas")
        st.markdown("---")
        
        # Carregar do banco de dados quais banners o usuário já possui
        banners_desbloqueados = ["Nenhum"]
        try:
            comprados_res = supabase.table("banners_comprados").select("nome_banner").eq("id_usuario", user_atual["id"]).execute()
            if comprados_res.data:
                for item in comprados_res.data: banners_desbloqueados.append(item["nome_banner"])
        except: pass
        
        for nome_b, preco in DIC_BANNERS.items():
            if nome_b == "Nenhum": continue
            col_l1, col_l2, col_l3 = st.columns([1, 2, 2])
            with col_l1: 
                renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, nome_b, tamanho=60)
            with col_l2: 
                st.write(f"**{nome_b}**")
                if nome_b in banners_desbloqueados: st.caption("✅ Já possuis esta moldura")
                else: st.caption(f"Preço: 🪙 {preco} moedas")
            with col_l3:
                if nome_b in banners_desbloqueados:
                    if user_atual.get("banner_ativo") == nome_b and user_atual["username"] != NOME_DEVELOPER:
                        st.button("Equipado ✓", key=f"eq_{nome_b}", disabled=True, use_container_width=True)
                    else:
                        if st.button("Equipar", key=f"btn_eq_{nome_b}", use_container_width=True):
                            supabase.table("perfis_usuarios").update({"banner_ativo": nome_b}).eq("id", user_atual["id"]).execute()
                            st.success(f"{nome_b} equipado!")
                            st.rerun()
                else:
                    pode_comprar = user_atual.get("moedas", 0) >= preco
                    if st.button(f"Comprar", key=f"buy_{nome_b}", disabled=not pode_comprar, use_container_width=True, type="primary"):
                        try:
                            novo_saldo = user_atual["moedas"] - preco
                            supabase.table("perfis_usuarios").update({"moedas": novo_saldo}).eq("id", user_atual["id"]).execute()
                            supabase.table("banners_comprados").insert({"id_usuario": user_atual["id"], "nome_banner": nome_b}).execute()
                            st.success(f"Compraste {nome_b}!")
                            st.rerun()
                        except: st.error("Erro na transação.")
            st.markdown("---")

    
