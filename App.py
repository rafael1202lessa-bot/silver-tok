import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2.9.1", page_icon="🎬", layout="centered")

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

# Definição dos Banners da Loja (Nome: Preço)
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

# --- FUNÇÕES AUXILIARES CORRIGIDAS ---
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
    """Gera o HTML com CSS personalizado incluindo suporte à Coroa Exclusiva de DEV"""
    estilo_css = "border-radius: 50%; object-fit: cover;"
    mostrar_coroa = False
    
    if username_alvo == NOME_DEVELOPER:
        estilo_css += " border: 5px solid #ffd700; box-shadow: 0 0 25px #ffaa00, inset 0 0 10px #ffd700;"
        mostrar_coroa = True
    else:
        if "Bronze" in tipo_banner:
            estilo_css += " border: 4px solid #cd7f32; box-shadow: 0 0 10px #cd7f32;"
        elif "Prata" in tipo_banner:
            estilo_css += " border: 4px solid #c0c0c0; box-shadow: 0 0 12px #c0c0c0;"
        elif "Ouro" in tipo_banner:
            estilo_css += " border: 5px solid #ffd700; box-shadow: 0 0 15px #ffd700;"
        elif "Neon" in tipo_banner:
            estilo_css += " border: 4px solid #00f3ff; box-shadow: 0 0 20px #ff007f, inset 0 0 10px #00f3ff;"

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
                    supabase.table("perfis_usuarios").update({
                        "moedas": novas_moedas,
                        "ultimo_bonus_tempo": agora.isoformat()
                    }).eq("id", user_id).execute()
                    st.session_state.usuario_logado["moedas"] = novas_moedas
                    st.toast(f"🪙 Ganhaste +{ciclos * 10} moedas por estares active!")
    except: pass

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state: st.session_state.sala_ativa = None
if "perfil_visitado" not in st.session_state: st.session_state.perfil_visitado = None

# --- FLUXO DE AUTENTICAÇÃO ---
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
                        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat(), "ultimo_bonus_tempo": datetime.now(timezone.utc).isoformat()}).eq("id", busca.data[0]["id"]).execute()
                        st.success("Login efetuado!")
                        st.rerun()
                    else: st.error("Incorreto.")
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
                    st.success("Conta criada! Faça login.")
                except: st.error("Erro ao cadastrar.")
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

    # CHAMADAS CORRIGIDAS AQUI (De espanhol para português)
    selo_lateral = obter_selo_usuario(user_atual["username"], user_atual["id"])

    # --- PAINEL LATERAL (SIDEBAR) ---
    st.sidebar.markdown("<p style='text-align:center; font-weight:bold; margin-bottom:0;'>Meu Perfil</p>", unsafe_allow_html=True)
    
    renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, user_atual.get("banner_ativo", "Nenhum"), username_alvo=user_atual["username"])
    
    nome_exibicao = user_atual.get("apelido") or user_atual["username"]
    st.sidebar.markdown(f"<h3 style='text-align:center; margin-top:0; margin-bottom:0;'>{nome_exibicao}{selo_lateral}</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center; color:gray; margin-top:0;'>@{user_atual['username']}</p>", unsafe_allow_html=True)
    st.sidebar.markdown(f"### 🪙 Carteira: **{user_atual.get('moedas', 0)}** moedas")

    if user_atual["username"] == NOME_DEVELOPER:
        with st.sidebar.expander("🤖 Comandos do Desenvolvedor", expanded=False):
            st.code(COMANDO_BOT_SECRETO, language="text")
            comando_exec = st.text_input("Digitar o comando especial aqui:")
            if st.button("Executar Comando ⚡", use_container_width=True):
                if comando_exec.strip() == COMANDO_BOT_SECRETO:
                    sucesso_envios = 0
                    for v_item in VIDEOS_BOT_BOTEY:
                        try:
                            supabase.table("feed_videos").insert({
                                "titulo": v_item["titulo"], "url_video": v_item["url"],
                                "username_autor": "System_Bot", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4712/4712035.png",
                                "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": v_item["formato"]
                            }).execute()
                            sucesso_envios += 1
                        except: pass
                    if sucesso_envios > 0:
                        st.success("O Bot gerou publicações com sucesso!")
                        st.rerun()

    if st.sidebar.button("Sair da Conta 🚪", use_container_width=True):
        st.session_state.usuario_logado = None
        st.session_state.sala_ativa = None
        st.session_state.perfil_visitado = None
        st.rerun()

    # --- NAVEGAÇÃO PRINCIPAL ---
    aba_feed, aba_loja, aba_chat = st.tabs(["📺 Silver Tok (Feed)", "🛒 Loja de Banners", "💬 Chat-Exv"])
    
    # === 📺 ABA SILVER TOK (FEED) ===
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
                else: st.error("Perfil não encontrado.")
            except: pass
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
                        st.markdown(f'<div style="display: flex; justify-content: center; background-color: #000; border-radius: 12px; padding: 5px; margin-bottom: 10px;"><video width="290" height="515" controls style="border-radius: 8px;"><source src="{video_url}" type="video/mp4"></video></div>', unsafe_allow_html=True)
                    else:
                        if video_url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) or "/fotos_feed/" in video_url: st.image(video_url, use_container_width=True)
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

                    # Comentários estruturados com a função certa
                    with st.expander(f"💬 Comentários"):
                        with st.form(key=f"f_c_{chave_comp}", clear_on_submit=True):
                            novo_coment = st.text_input("Escreve um comentário:")
                            if st.form_submit_button("Comentar ✉️") and novo_coment.strip():
                                try:
                                    supabase.table("comentarios_feed").insert({"id_video": id_post, "id_autor": user_atual["id"], "username_autor": user_atual["username"], "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "comentario": novo_coment.strip()}).execute()
                                    st.rerun()
                                except: pass

                        try:
                            lista_c = supabase.table("comentarios_feed").select("*").eq("id_video", id_post).order("criado_em", descending=True).execute()
                            if lista_c.data:
                                for c in lista_c.data:
                                    col_c1, col_c2 = st.columns([1, 8])
                                    
                                    banner_comentador = "Nenhum"
                                    if c.get("id_autor"):
                                        try:
                                            res_bc = supabase.table("perfis_usuarios").select("banner_ativo").eq("id", c["id_autor"]).execute()
                                            if res_bc.data: banner_comentador = res_bc.data[0].get("banner_ativo", "Nenhum")
                                        except: pass
                                        
                                    with col_c1:
                                        renderizar_foto_com_banner(c.get("avatar_autor") or FOTO_PADRAO, banner_comentador, username_alvo=c['username_autor'], tamanho=40)
                                    with col_c2:
                                        selo_comentador = obter_selo_usuario(c['username_autor'], c.get('id_autor'))
                                        st.markdown(f"**{c['username_autor']}**{selo_comentador}: {c['comentario']}")
                        except: pass

            try:
                query_feed = supabase.table("feed_videos").select("*")
                if termo_pesquisa: query_feed = query_feed.ilike("titulo", f"%{termo_pesquisa}%")
                query_feed = query_feed.order("curtidas" if "Populares" in ordem_feed else "criado_em", descending=True)
                dados = query_feed.execute()
                if dados.data:
                    with aba_formato_mini:
                        v_verts = [p for p in dados.data if p.get("tipo_formato") == "vertical"]
                        renderizar_lista_filtrada(v_verts, "vertical")
                    with aba_formato_longo:
                        v_horiz = [p for p in dados.data if p.get("tipo_formato") != "vertical"]
                        renderizar_lista_filtrada(v_horiz, "horizontal")
            except: pass

    # === 🛒 ABA: LOJA DE BANNERS ===
    with aba_loja:
        st.header("🛒 Loja de Molduras de Perfil")
        st.write(f"Suas Moedas Atuais: 🪙 **{user_atual.get('moedas', 0)}**")
        st.markdown("---")
        
        if user_atual["username"] == NOME_DEVELOPER:
            st.info("👑 Como Desenvolvedor principal, tu já tens a Coroa Suprema equipada permanentemente!")
        
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
                if nome_b in banners_desbloqueados: st.caption("✅ Adquirido")
                else: st.caption(f"Preço: 🪙 {preco} moedas")
            with col_l3:
                if nome_b in banners_desbloqueados:
                    if user_atual.get("banner_ativo") == nome_b and user_atual["username"] != NOME_DEVELOPER:
                        st.button("Equipado ✓", key=f"eq_{nome_b}", disabled=True, use_container_width=True)
                    else:
                        if st.button("Equipar", key=f"btn_eq_{nome_b}", use_container_width=True):
                            supabase.table("perfis_usuarios").update({"banner_ativo": nome_b}).eq("id", user_atual["id"]).execute()
                            st.rerun()
                else:
                    pode_comprar = user_atual.get("moedas", 0) >= preco
                    if st.button(f"Comprar", key=f"buy_{nome_b}", disabled=not pode_comprar, use_container_width=True, type="primary"):
                        try:
                            novo_saldo = user_atual["moedas"] - preco
                            supabase.table("perfis_usuarios").update({"moedas": novo_saldo}).eq("id", user_atual["id"]).execute()
                            supabase.table("banners_comprados").insert({"id_usuario": user_atual["id"], "nome_banner": nome_b}).execute()
                            st.rerun()
                        except: pass
            st.markdown("---")

    # === 💬 ABA CHAT ===
    with aba_chat:
        st.subheader("Salas de Chat Privadas")
        cod_d = st.text_input("Insira o código do chat:").strip().upper()
        if st.button("Entrar 🚪", use_container_width=True) and cod_d:
            st.session_state.sala_ativa = cod_d
            st.rerun()
     
