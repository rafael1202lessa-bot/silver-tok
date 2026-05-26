import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v3.5 Master", page_icon="🎬", layout="centered")

# --- CONFIGURAÇÕES DE MANUTENÇÃO (MODO PRIVADO) ---
MODO_MANUTENCAO = False  
ID_REAL_DEVELOPER = "04daaa3c-63ef-486c-b33e-54d4e80ee9e9"

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

# --- BANCO DE DADOS LOCAL DE SHIMEJIS / MASCOTES ---
SHIMEJIS_DISPONIVEIS = {
    "Nenhum": "",
    "Mascote Espadachim (Livro)": "⚔️",
    "Mago Ancestral (Livro)": "🔮",
    "Raposa de Fogo": "🦊",
    "Mini Robô": "🤖",
    "Gatinho Chibi": "🐱"
}

# --- CONFIGURAÇÃO DE COSMÉTICOS ---
COSMETICOS = {
    "bronze": {"nome": "🥉 Bronze Estelar", "preco": 150, "img": "https://cdn-icons-png.flaticon.com/512/5243/5243422.png"},
    "prata": {"nome": "🥈 Prata Lendária", "preco": 300, "img": "https://cdn-icons-png.flaticon.com/512/5243/5243444.png"},
    "caixa_azul": {"nome": "🔷 Balão Azul Moderno", "preco": 100, "img": "https://cdn-icons-png.flaticon.com/512/2460/2460884.png"},
    "caixa_neon": {"nome": "🔮 Balão Neon Cyber", "preco": 250, "img": "https://cdn-icons-png.flaticon.com/512/2037/2037041.png"},
    "banner_otaku": {"nome": "🔥 Mestre Otaku (Anime)", "preco": 400, "img": "https://cdn-icons-png.flaticon.com/512/2206/2206241.png"},
    "banner_hollywood": {"nome": "🎬 Cinéfilo de Carteirinha", "preco": 400, "img": "https://cdn-icons-png.flaticon.com/512/3172/3172554.png"},
    "banner_dorama": {"nome": "🌸 Dorama Lover", "preco": 450, "img": "https://cdn-icons-png.flaticon.com/512/4230/4230633.png"}
}

VIDEOS_BOT_BOTEY = [
    {"id": "bot_1", "titulo": "⚡ Edit Suprema de Naruto!", "url_video": "https://www.w3schools.com/html/mov_bbb.mp4", "username_autor": "🤖 Bot_Animes", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4213/4213732.png", "curtidas": 142, "tipo_formato": "vertical"},
    {"id": "bot_2", "titulo": "🌌 Relaxing Cinematic View 4K", "url_video": "https://media.w3.org/2010/05/sintel/trailer_hd.mp4", "username_autor": "🤖 Bot_Natureza", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4213/4213732.png", "curtidas": 98, "tipo_formato": "horizontal"}
]

# --- PERGUNTAS DO QUIZ GEEK ---
PERGUNTAS_QUIZ = {
    "Anime e Animações": [
        {"pergunta": "Qual é o objetivo principal de Luffy em One Piece?", "opcoes": ["Se tornar Hokage", "Encontrar o All Blue", "Ser o Rei dos Piratas", "Derrotar Madara"], "correta": "Ser o Rei dos Piratas"},
        {"pergunta": "Quem é conhecido como o Alquimista de Aço?", "opcoes": ["Roy Mustang", "Edward Elric", "Alphonse Elric", "Saitama"], "correta": "Edward Elric"}
    ],
    "Filmes e Séries / Doramas": [
        {"pergunta": "Em Round 6 (Squid Game), qual é o prêmio final?", "opcoes": ["Um carro de luxo", "45,6 bilhões de wons", "A liberdade eterna", "1 milhão de dólares"], "correta": "45,6 bilhões de wons"},
        {"pergunta": "Qual é a casa de Harry Potter em Hogwarts?", "opcoes": ["Sonserina", "Corvinal", "Lufa-Lufa", "Grifinória"], "correta": "Grifinória"}
    ],
    "Conteúdo Geral": [
        {"pergunta": "Qual empresa desenvolveu o Streamlit?", "opcoes": ["Google", "Snowflake", "Meta", "Microsoft"], "correta": "Snowflake"},
        {"pergunta": "Quantos minutos tem um tempo regulamentar de futebol?", "opcoes": ["40 minutos", "45 minutos", "50 minutos", "60 minutos"], "correta": "45 minutos"}
    ]
}

# --- FUNÇÕES AUXILIARES ANTIFALHA ---
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

def obter_selo_texto(username_alvo, user_id_alvo=None, cargo_adicional="Nenhum"):
    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial":
        return " 👑 DEV"
    if cargo_adicional and cargo_adicional != "Nenhum":
        return f" 🎖️ {cargo_adicional}"
    try:
        dados = supabase.table("perfis_usuarios").select("id").eq("username", username_alvo).execute()
        if dados.data:
            id_u = dados.data[0].get("id")
            if id_u:
                res_seg = supabase.table("seguidores").select("*").eq("id_seguido", id_u).execute()
                total = len(res_seg.data) if res_seg.data else 0
                if total >= 1000:
                    return " ✔️"
    except: pass
    return ""

def renderizar_foto_com_banner(url_foto, username_alvo, user_id_alvo=None, tamanho=90, banner_equipado="Nenhum", shimeji="Nenhum"):
    if not url_foto:
        url_foto = FOTO_PADRAO
    
    # Renderização de Shimejis/Mascotes Flutuantes
    shimeji_html = ""
    if shimeji in SHIMEJIS_DISPONIVEIS and SHIMEJIS_DISPONIVEIS[shimeji] != "":
        shimeji_html = f'<div style="position: absolute; bottom: -5px; right: -5px; font-size: {int(tamanho*0.35)}px; background: white; border-radius: 50%; padding: 2px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); z-index: 12;">{SHIMEJIS_DISPONIVEIS[shimeji]}</div>'

    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial" or banner_equipado == "👑 Coroa Suprema DEV":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 4px solid #ffd700; box-shadow: 0 0 20px #ffd700;"
        coroa_html = f'<div style="position: absolute; top: -22px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.38)}px; z-index: 10;">👑</div>'
    elif banner_equipado == "🥉 Bronze Estelar":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #cd7f32;"
        coroa_html = ''
    elif banner_equipado == "🥈 Prata Lendária":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #c0c0c0; box-shadow: 0 0 8px #c0c0c0;"
        coroa_html = ''
    elif banner_equipado == "🔥 Mestre Otaku (Anime)":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #ff4500; box-shadow: 0 0 12px #ff4500;"
        coroa_html = f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🦊</div>'
    elif banner_equipado == "🎬 Cinéfilo de Carteirinha":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #1e90ff; box-shadow: 0 0 12px #1e90ff;"
        coroa_html = f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🎥</div>'
    elif banner_equipado == "🌸 Dorama Lover":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #ff69b4; box-shadow: 0 0 12px #ff69b4;"
        coroa_html = f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🌸</div>'
    else:
        estilo_css = "border-radius: 50%; object-fit: cover;"
        coroa_html = ''
        
    html = f"""
    <div style="position: relative; display: inline-block; text-align: center; margin-top: 10px;">
        {coroa_html}
        <img src="{url_foto}" width="{tamanho}" height="{tamanho}" style="{estilo_css}">
        {shimeji_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def renderizar_caixa_mensagem(username, mensagem, selo, estilo_caixa, eh_admin=False):
    if mensagem is None or str(mensagem).lower() == "none":
        return

    if eh_admin or estilo_caixa == "👑 Balão Dourado DEV":
        estilo_css = "background: linear-gradient(135deg, #fff7e6, #ffeaa7); border-left: 5px solid #ffd700; padding: 12px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(255,215,0,0.2);"
    elif estilo_caixa == "🔷 Balão Azul Moderno":
        estilo_css = "background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
    elif estilo_caixa == "🔮 Balão Neon Cyber":
        estilo_css = "background-color: #1a1a2e; border: 1px solid #e94560; color: #fff; padding: 10px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 0 10px #e94560;"
    else:
        estilo_css = "background-color: #f1f3f4; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
        
    conteudo_final = mensagem
    if str(mensagem).startswith("https://"):
        if any(ext in str(mensagem).lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
            conteudo_final = f'<br><img src="{mensagem}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'
        elif any(ext in str(mensagem).lower() for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.webm', '.bin']) or "audio" in str(mensagem).lower():
            conteudo_final = f'<br><audio controls style="max-width: 100%; margin-top: 5px;"><source src="{mensagem}"></audio>'

    st.markdown(f"""
    <div style="{estilo_css}">
        <span style="font-weight: bold; color: {'#d4af37' if (eh_admin or estilo_caixa == '👑 Balão Dourado DEV') else '#333'};">{username}</span> 
        <span style="font-size: 12px; font-weight: bold; color: #d4af37;">{selo}</span>: 
        <span style="color: {'#111' if estilo_caixa != '🔮 Balão Neon Cyber' else '#fff'};">{conteudo_final}</span>
    </div>
    """, unsafe_allow_html=True)

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)

# --- FLUXO DE AUTENTICAÇÃO ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = None
if "perfil_visitado" not in st.session_state:
    st.session_state.perfil_visitado = None

if st.session_state.usuario_logado is None:
    exibir_logo()
    aba_auth = st.tabs(["Fazer Login", "Criar Nova Conta"])
    with aba_auth[0]:
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        if st.button("Entrar 🚀", key="btn_login", use_container_width=True):
            if login_user and login_senha:
                busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                if busca.data and busca.data[0].get("senha") == login_senha:
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
    u_id = st.session_state.usuario_logado.get("id") if st.session_state.usuario_logado else None
    
    if MODO_MANUTENCAO and str(u_id) != ID_REAL_DEVELOPER:
        st.markdown("<h1 style='text-align: center;'>🚧 Silver Tok & Chat 🚧</h1>", unsafe_allow_html=True)
        st.error("O aplicativo está em manutenção para a implementação de novas funções! Voltamos em breve para a Grande Estreia. 🎬🚀")
        st.stop()
        
    try:
        if st.session_state.usuario_logado and isinstance(st.session_state.usuario_logado, dict) and "id" in st.session_state.usuario_logado:
            atualizar_dados = supabase.table("perfis_usuarios").select("*").eq("id", st.session_state.usuario_logado.get("id")).execute()
            if atualizar_dados.data and len(atualizar_dados.data) > 0:
                st.session_state.usuario_logado = atualizar_dados.data[0]
            else:
                st.session_state.usuario_logado = None
                st.rerun()
        else:
            st.session_state.usuario_logado = None
            st.rerun()
    except: pass

    if st.session_state.usuario_logado is None:
        st.rerun()

    user_atual = st.session_state.usuario_logado
    u_id = user_atual.get("id", "")
    if not u_id:
        u_id = str(uuid.uuid4())
        
    u_name = user_atual.get("username", "Membro")
    is_admin = verificar_se_eh_dev(u_id)
    u_cargo = user_atual.get("biografia") if user_atual.get("biografia") else "Nenhum" # Utilizando biografia temporariamente como storage de cargos injetados
    u_shimeji = user_atual.get("localizacao") if user_atual.get("localizacao") else "Nenhum" # Utilizando localizacao temporariamente como storage do shimeji ativo

    try:
        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", u_id).execute()
    except: pass

    total_notif = 0
    try:
        res_n = supabase.table("notificacoes").select("*").eq("id_destinatario", u_id).eq("lida", False).execute()
        total_notif = len(res_n.data) if res_n.data else 0
    except: pass

    # --- BARRA LATERAL (Sidebar unificada) ---
    with st.sidebar:
        banner_v = user_atual.get("banner_ativo", "Nenhum")
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, u_name, u_id, tamanho=90, banner_equipado=banner_v, shimeji=u_shimeji)
        
        selo_proprio = obter_selo_texto(u_name, u_id, cargo_adicional=u_cargo)
        st.write(f"**{user_atual.get('apelido') or u_name}** {selo_proprio}")
        st.markdown(f"🪙 **Silver Coins:** {user_atual.get('moedas', 0)}")
        
        # --- SELETOR DE SHIMEJIS PROPRIOS ---
        with st.expander("🦊 Meus Shimejis / Mascotes"):
            escolha_shim = st.selectbox("Escolha seu Acompanhante:", list(SHIMEJIS_DISPONIVEIS.keys()), index=list(SHIMEJIS_DISPONIVEIS.keys()).index(u_shimeji) if u_shimeji in SHIMEJIS_DISPONIVEIS else 0)
            if st.button("Ativar Mascote ✨", use_container_width=True):
                try:
                    supabase.table("perfis_usuarios").update({"localizacao": escolha_shim}).eq("id", u_id).execute()
                    st.toast("Mascote invocado!")
                    st.rerun()
                except: pass

        # --- INVENTÁRIO ---    
        with st.expander("🎒 Meu Inventário"):
            st.caption("Equipe suas customizações salvas:")
            st.write(f"Ativo no momento: **{user_atual.get('banner_ativo', 'Nenhum')}**")
            
            opcoes_inventario = [
                "Nenhum", "残留 Banners", "🥉 Bronze Estelar", "🥈 Prata Lendária", 
                "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber", 
                "🔥 Mestre Otaku (Anime)", "🎬 Cinéfilo de Carteirinha", "🌸 Dorama Lover"
            ]
            
            data_atual = datetime.now().date()
            data_inicio = datetime.strptime("2026-05-25", "%Y-%m-%d").date()
            data_fim = datetime.strptime("2026-05-31", "%Y-%m-%d").date()
            
            if data_inicio <= data_atual <= data_fim:
                opcoes_inventario.insert(1, "🚀 Estreante Oficial")
            elif user_atual.get('banner_ativo') == "🚀 Estreante Oficial":
                opcoes_inventario.insert(1, "🚀 Estreante Oficial")
                
            if is_admin:
                opcoes_inventario.insert(1, "👑 Coroa Suprema DEV")
                opcoes_inventario.insert(2, "👑 Balão Dourado DEV")
                
            escolha_custom = st.selectbox("Selecione para ativar:", opcoes_inventario, key="select_custom_inv")
            if st.button("Equipar Cosmético 🛡️", key="btn_equipar_inv_fix"):
                try:
                    resposta = supabase.table("perfis_usuarios").update({"banner_ativo": escolha_custom}).eq("id", u_id).execute()
                    if resposta.data:
                        st.toast("Item equipado com sucesso! 🛡️")
                        st.rerun()
                except Exception:
                    st.toast("Falha ao conectar.")

        # --- MENU EDITAR PERFIL ---
        with st.expander("⚙️ Editar Meu Perfil"):
            novo_apelido = st.text_input("Alterar Apelido:", value=user_atual.get("apelido") or u_name)
            nova_foto = st.text_input("URL da Foto de Perfil:", value=user_atual.get("url_foto_perfil") or FOTO_PADRAO)
            if st.button("Salvar Alterações 💾"):
                try:
                    supabase.table("perfis_usuarios").update({
                        "apelido": novo_apelido.strip(),
                        "url_foto_perfil": nova_foto.strip()
                    }).eq("id", u_id).execute()
                    st.success("Perfil atualizado!")
                    st.rerun()
                except: st.error("Erro ao salvar dados.")

        st.markdown("---")
        if st.button("Sair da Conta 🚪", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.sala_ativa = None
            st.session_state.perfil_visitado = None
            st.rerun()

    # --- NAVEGAÇÃO PRINCIPAL ---
    abas_principais = ["📺 Silver Tok (Feed)", "🛒 Loja & Caixas", "💬 Chat-Exv", "🍿 Área Geek", "🧠 Super Quiz", "✨ Status", f"🔔 Notificações ({total_notif})"]
    if is_admin:
        abas_principais.append("👑 Painel Admin Secreto")
        
    abas = st.tabs(abas_principais)
    aba_feed, aba_loja, aba_chat, aba_entretenimento, aba_quiz, aba_status, aba_notif = abas[0], abas[1], abas[2], abas[3], abas[4], abas[5], abas[6]

    # --- LISTAGEM DO FEED COM SEÇÃO DE COMENTÁRIOS ---
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
            video_url = v.get("url_video", "")
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
                st.caption(v.get("titulo", ""))

            if v.get("tipo_formato") == "vertical":
                st.markdown(f'<div style="display: flex; justify-content: center;"><video width="290" height="515" controls><source src="{video_url}" type="video/mp4"></video></div>', unsafe_allow_html=True)
            else:
                if str(video_url).lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    st.image(video_url, use_container_width=True)
                elif video_url:
                    st.video(video_url)

            col_b1, col_b2 = st.columns([2, 2])
            with col_b1:
                if st.button(f"❤️ {v.get('curtidas', 0)} Curtidas", key=f"like_{chave_comp}"):
                    if "bot_" not in str(id_post):
                        try:
                            supabase.table("feed_videos").update({"curtidas": v.get('curtidas', 0) + 1}).eq("id", id_post).execute()
                        except: pass
                    st.rerun()
            with col_b2:
                if autor == u_name or verificar_se_eh_dev(u_id):
                    if st.button("Remover Post 🗑️", key=f"del_{chave_comp}"):
                        if "bot_" not in str(id_post):
                            try:
                                supabase.table("feed_videos").delete().eq("id", id_post).execute()
                            except: pass
                        st.rerun()

            with st.expander(f"💬 Ver Comentários do Post"):
                cod_discussao = f"POST-{id_post}"
                novo_coment = st.text_input("Escreva um comentário...", key=f"in_coment_{chave_comp}")
                if st.button("Comentar 💬", key=f"btn_coment_{chave_comp}"):
                    if novo_coment.strip():
                        try:
                            supabase.table("bate-papo_profissional").insert({
                                "username": u_name,
                                "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                "mensagem": novo_coment.strip(),
                                "codigo_sala": cod_discussao
                            }).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar comentário: {e}")

                try:
                    comentarios = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", cod_discussao).execute()
                    if comentarios.data:
                        for c in comentarios.data:
                            c_user = c.get('username')
                            c_msg = c.get('mensagem')
                            if c_msg and str(c_msg).lower() != "none":
                                col_c1, col_c2 = st.columns([1, 6])
                                try:
                                    estilo_c = supabase.table("perfis_usuarios").select("banner_ativo", "id", "url_foto_perfil", "biografia").eq("username", c_user).execute()
                                    txt_caixa_c = estilo_c.data[0].get("banner_ativo", "Nenhum") if estilo_c.data else "Nenhum"
                                    uid_c = estilo_c.data[0].get("id") if estilo_c.data else None
                                    foto_c = estilo_c.data[0].get("url_foto_perfil") or FOTO_PADRAO
                                    cargo_c = estilo_c.data[0].get("biografia") if estilo_c.data else "Nenhum"
                                except:
                                    txt_caixa_c = "Nenhum"
                                    uid_c = None
                                    foto_c = FOTO_PADRAO
                                    cargo_c = "Nenhum"
                                    
                                with col_c1:
                                    renderizar_foto_com_banner(foto_c, c_user, uid_c, tamanho=40, banner_equipado=txt_caixa_c)
                                with col_c2:
                                    selo_c = obter_selo_texto(c_user, uid_c, cargo_adicional=cargo_c)
                                    renderizar_caixa_mensagem(c_user, c_msg, selo_c, txt_caixa_c, eh_admin=verificar_se_eh_dev(uid_c))
                    else:
                        st.caption("Ninguém comentou ainda.")
                except: pass

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
                vis_id = p_info.get("id", "")
                col_p1, col_p2 = st.columns([1, 3])
                with col_p1:
                    renderizar_foto_com_banner(p_info.get("url_foto_perfil") or FOTO_PADRAO, autor_vis, vis_id, tamanho=80, banner_equipado=p_info.get("banner_ativo", "Nenhum"), shimeji=p_info.get("localizacao", "Nenhum"))
                with col_p2:
                    s_vis = obter_selo_texto(autor_vis, vis_id, cargo_adicional=p_info.get("biografia", "Nenhum"))
                    st.subheader(f"{p_info.get('apelido') or autor_vis} {s_vis}")
                    
                    if autor_vis != u_name and vis_id:
                        try:
                            ja_segue = supabase.table("seguidores").select("*").eq("id_seguidor", u_id).eq("id_seguido", vis_id).execute()
                            if ja_segue.data:
                                if st.button("Seguindo ✓"):
                                    supabase.table("seguidores").delete().eq("id_seguidor", u_id).eq("id_seguido", vis_id).execute()
                                    st.rerun()
                            else:
                                if st.button("Seguir ➕", type="primary"):
                                    supabase.table("seguidores").insert({"id_seguidor": u_id, "id_seguido": vis_id}).execute()
                                    st.rerun()
                        except: pass

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
                    posts_completos = (f_dados.data or []) + [b for b in VIDEOS_BOT_BOTEY if b.get("tipo_formato") == "vertical"]
                    renderizar_lista_filtrada(reversed(posts_completos), "vertical_global", busca_legenda, ordenar_por)
                except: pass

            with aba_midia[1]:
                with st.expander("➕ Publicar Novo Conteúdo"):
                    t_pub = st.text_input("Legenda:", key="leg_nova")
                    f_midia = st.file_uploader("Arquivo de Vídeo ou Imagem:", type=["mp4", "png", "jpg", "jpeg"])
                    fmt = st.selectbox("Formato:", ["Horizontal / Padrão", "Vertical / Shorts"])
                    fmt_db = "vertical" if "Vertical" in fmt else "horizontal"
                    
                    if st.button("Publicar Post 🚀") and f_midia and t_pub:
                        try:
                            bucket = "videos_feed" if fmt_db == "vertical" or f_midia.name.endswith(".mp4") else "imagens_chat"
                            path_b = f"feed/{uuid.uuid4()}_{f_midia.name}"
                            supabase.storage.from_(bucket).upload(path_b, f_midia.read())
                            url_f = supabase.storage.from_(bucket).get_public_url(path_b)
                            
                            supabase.table("feed_videos").insert({
                                "titulo": t_pub, "url_video": url_f, "username_autor": u_name,
                                "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0,
                                "id_autor": u_id, "tipo_formato": fmt_db
                            }).execute()
                            st.success("Publicado!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao publicar: {e}")

                try:
                    f_dados = supabase.table("feed_videos").select("*").eq("tipo_formato", "horizontal").execute()
                    posts_completos_h = (f_dados.data or []) + [b for b in VIDEOS_BOT_BOTEY if b.get("tipo_formato") == "horizontal"]
                    renderizar_lista_filtrada(reversed(posts_completos_h), "horizontal_global", busca_legenda, ordenar_por)
                except: pass

    # === 🛒 ABA LOJA (PREÇOS EM SILVER COINS) ===
    with aba_loja:
        st.header("🛒 Loja de Cosméticos Premium")
        saldo_atual = user_atual.get("moedas", 0) if user_atual else 0
        st.info(f"Seu saldo atual: 🪙 {saldo_atual} Silver Coins")
        
        col_l1, col_l2 = st.columns(2)
        for idx, (chave, info) in enumerate(COSMETICOS.items()):
            coluna_foco = col_l1 if idx % 2 == 0 else col_l2
            with coluna_foco:
                with st.container(border=True):
                    if info.get("img"):
                        st.image(info["img"], width=60)
                    st.markdown(f"### {info['nome']}")
                    st.write(f"Preço: 🪙 {info['preco']} Silver Coins")
                    
                    if saldo_atual >= info['preco']:
                        if st.button(f"Adquirir Item", key=f"loja_buy_{chave}", use_container_width=True):
                            try:
                                novo_saldo = int(saldo_atual) - int(info['preco'])
                                supabase.table("perfis_usuarios").update({"moedas": novo_saldo}).eq("id", u_id).execute()
                                st.success(f"Você adquiriu: {info['nome']}! Acesse seu Inventário na barra lateral.")
                                st.rerun()
                            except: st.error("Erro ao processar a compra.")
                    else:
                        st.button("Silver Coins Insuficientes ❌", key=f"insuf_{chave}", disabled=True, use_container_width=True)

    # === 💬 ABA CHAT-EXV ===
    with aba_chat:
        sala_atual = st.session_state.sala_ativa

        if sala_atual:
            st.subheader(f"Sala: {sala_atual}")
            if st.button("⬅️ Sair da Sala"):
                st.session_state.sala_ativa = None
                st.rerun()

            with st.expander("📸 Enviar Foto / Mídia"):
                arquivo_chat = st.file_uploader("Escolha uma imagem:", type=["png", "jpg", "jpeg", "gif", "webp"])
                if st.button("Enviar Imagem 🚀") and arquivo_chat:
                    try:
                        nome_da_foto = f"chat/imagens/{uuid.uuid4()}_{arquivo_chat.name}"
                        supabase.storage.from_("imagens_chat").upload(nome_da_foto, arquivo_chat.read())
                        url_da_foto = supabase.storage.from_("imagens_chat").get_public_url(nome_da_foto)
                        
                        supabase.table("bate-papo_profissional").insert({
                            "username": u_name,
                            "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "mensagem": url_da_foto, 
                            "codigo_sala": sala_atual
                        }).execute()
                        st.success("Mídia enviada!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Falha ao subir imagem: {e}")

            st.markdown("### 🎙️ Áudio")
            if "b64_audio_data" not in st.session_state:
                st.session_state.b64_audio_data = ""
                
            audio_base64 = st.text_input("Dados do Gravador", type="password", value=st.session_state.b64_audio_data, label_visibility="collapsed", key="audio_b64_injector")
            
            if st.button("Clique aqui se o áudio não subir automático ⚡", use_container_width=True, key="btn_hidden_upload") or (audio_base64 and audio_base64 != st.session_state.b64_audio_data):
                if audio_base64:
                    try:
                        dados_audio = base64.b64decode(audio_base64)
                        nome_arquivo = f"chat/audios/{uuid.uuid4()}.wav"
                        supabase.storage.from_("audios_chat").upload(nome_arquivo, dados_audio)
                        url_publica_audio = supabase.storage.from_("audios_chat").get_public_url(nome_arquivo)
                        
                        supabase.table("bate-papo_profissional").insert({
                            "username": u_name,
                            "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "mensagem": url_publica_audio, 
                            "codigo_sala": sala_atual
                        }).execute()
                        st.session_state.b64_audio_data = ""
                        st.rerun()
                    except: pass

            gravador_html = """
            <div style="display: flex; gap: 10px; justify-content: center; padding: 5px 0;">
                <button id="startBtn" style="background-color: #24a0ed; color: white; border: none; padding: 12px 20px; border-radius: 25px; font-weight: bold; width: 45%; cursor: pointer; font-size: 14px;">🎙️ Gravar</button>
                <button id="stopBtn" style="background-color: #ff4b4b; color: white; border: none; padding: 12px 20px; border-radius: 25px; font-weight: bold; width: 45%; cursor: pointer; display: none; font-size: 14px;">⏹️ Enviar</button>
            </div>
            <div id="statusLabel" style="text-align: center; color: #777; font-size: 12px; margin-top: 5px;">Pressione Gravar para falar</div>
            <script>
            let mediaRecorder; let audioChunks = [];
            const startBtn = document.getElementById('startBtn'); const stopBtn = document.getElementById('stopBtn'); const statusLabel = document.getElementById('statusLabel');
            startBtn.onclick = async () => {
                audioChunks = [];
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
                    mediaRecorder.onstop = () => {
                        statusLabel.innerText = "Processando áudio...";
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const reader = new FileReader(); reader.readAsDataURL(audioBlob);
                        reader.onloadend = () => {
                            const base64String = reader.result.split(',')[1];
                            const inputs = window.parent.document.querySelectorAll('input[type="password"]');
                            if(inputs.length > 0) {
                                let targetInput = inputs[0]; targetInput.value = base64String;
                                targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                                setTimeout(() => {
                                    const botoes = window.parent.document.querySelectorAll('button');
                                    for (let btn of botoes) { if (btn.innerText.includes("Clique aqui se o áudio")) { btn.click(); break; } }
                                }, 400);
                            }
                        };
                    };
                    mediaRecorder.start(); startBtn.style.display = 'none'; stopBtn.style.display = 'inline-block'; statusLabel.innerText = "🔴 Gravando...";
                } catch(err) { statusLabel.innerText = "Permissão de microfone negada."; }
            };
            stopBtn.onclick = () => { mediaRecorder.stop(); startBtn.style.display = 'inline-block'; stopBtn.style.display = 'none'; statusLabel.innerText = "Enviando..."; };
            </script>
            """
            st.components.v1.html(gravador_html, height=85)
            st.markdown("---")

            m_txt = st.text_input("Mensagem:", key="input_texto_chat_direto", placeholder="Digite sua mensagem aqui...")
            if st.button("Enviar Mensagem ✉️", use_container_width=True):
                if m_txt.strip():
                    try:
                        supabase.table("bate-papo_profissional").insert({
                            "username": u_name,
                            "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "mensagem": m_txt.strip(), 
                            "codigo_sala": sala_atual
                        }).execute()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar mensagem: {e}")

            try:
                m_dados = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", sala_atual).execute()
                if m_dados.data:
                    for m in reversed(m_dados.data[-40:]):
                        m_user = m.get('username', 'Membro')
                        m_msg = m.get('mensagem', '')
                        
                        if m_msg and str(m_msg).lower() != "none":
                            col_m1, col_m2 = st.columns([1, 6])
                            with col_m1:
                                renderizar_foto_com_banner(m.get("url_foto_perfil") or FOTO_PADRAO, m_user, tamanho=40)
                            with col_m2:
                                s_msg = obter_selo_texto(m_user)
                                try:
                                    estilo_u = supabase.table("perfis_usuarios").select("banner_ativo", "id").eq("username", m_user).execute()
                                    txt_caixa = estilo_u.data[0].get("banner_ativo", "Nenhum") if estilo_u.data else "Nenhum"
                                    uid_remetente = estilo_u.data[0].get("id") if estilo_u.data else ""
                                except:
                                    txt_caixa = "Nenhum"
                                    uid_remetente = ""
                                    
                                renderizar_caixa_mensagem(m_user, m_msg, s_msg, txt_caixa, eh_admin=verificar_se_eh_dev(uid_remetente))
            except: pass
        else:
            st.title("🎛️ Painel Chat-Exv")
            t_chat = st.tabs(["💬 Privado", "🔑 Entrar", "👥 Grupos", "👥 Membros", "➕ Adicionar"])
            
            with t_chat[0]:
                alvo = st.text_input("Username do amigo para iniciar privado:").strip()
                if st.button("Iniciar Chat Privado") and alvo:
                    lista = sorted([u_name.upper(), alvo.upper()])
                    st.session_state.sala_ativa = f"PRIV-{lista[0]}-{lista[1]}"
                    st.rerun()
            
            with t_chat[1]:
                st.subheader("Entrar em uma Sala Existente")
                cod_entrar = st.text_input("Insira o código do chat:", placeholder="Ex: GRUPO-VIP")
                if st.button("Entrar na Sala 🚪") and cod_entrar:
                    st.session_state.sala_ativa = cod_entrar.strip().upper()
                    st.rerun()
            
            with t_chat[2]:
                g_nome = st.text_input("Nome do Grupo para Criar:").strip().upper()
                if st.button("Criar Grupo 🔐") and g_nome:
                    st.session_state.sala_ativa = g_nome
                    st.rerun()

            with t_chat[3]:
                st.subheader("Membros da Comunidade")
                try:
                    u_todos = supabase.table("perfis_usuarios").select("*").execute()
                    if u_todos.data:
                        for u in u_todos.data:
                            m_username = u.get("username", "")
                            if m_username and m_username != u_name:
                                col_u1, col_u2, col_u3 = st.columns([1, 4, 2])
                                with col_u1:
                                    renderizar_foto_com_banner(u.get("url_foto_perfil") or FOTO_PADRAO, m_username, u.get("id"), tamanho=50, banner_equipado=u.get("banner_ativo", "Nenhum"))
                                with col_u2:
                                    s_u = obter_selo_texto(m_username, u.get("id"), cargo_adicional=u.get("biografia", "Nenhum"))
                                    st.markdown(f"**{m_username}** {s_u}")
                                    st.caption(obter_status_emoji(u.get("ultimo_visto")))
                                with col_u3:
                                    if st.button("Chat 💬", key=f"u_ch_{m_username}"):
                                        lista = sorted([u_name.upper(), m_username.upper()])
                                        st.session_state.sala_ativa = f"PRIV-{lista[0]}-{lista[1]}"
                                        st.rerun()
                except: pass

            with t_chat[4]:
                st.subheader("Adicionar Novos Amigos")
                busca_amigo = st.text_input("Digitar Username do Usuário:", key="busca_amigo_input")
                if st.button("Buscar e Seguir ➕"):
                    if busca_amigo.strip():
                        try:
                            verif = supabase.table("perfis_usuarios").select("id").eq("username", busca_amigo.strip()).execute()
                            if verif.data:
                                am_id = verif.data[0]["id"]
                                supabase.table("seguidores").insert({"id_seguidor": u_id, "id_seguido": am_id}).execute()
                                st.success(f"Você agora está seguindo {busca_amigo.strip()}!")
                        except: st.error("Incompatibilidade ou falha ao seguir.")

    # === 🍿 ABA: ÁREA GEEK (CATÁLOGO EXPANDIDO COM LIVROS E MANGÁS) ===
    with aba_entretenimento:
        st.header("🍿 Central Geek & Literária")
        st.caption("Veja as obras oficiais adicionadas pelo Admin e pela comunidade!")
        
        tabs_geek = st.tabs(["⛩️ Animes", "🎬 Filmes", "📺 Séries & Desenhos", "🌸 Doramas", "📖 Livros & Mangás"])
        categorias_mapeamento = ["Animes", "Filmes", "Séries e Desenhos", "Doramas", "Livros e Mangás"]
        
        for idx_t, nome_cat in enumerate(categorias_mapeamento):
            with tabs_geek[idx_t]:
                st.subheader(f"Catálogo de {nome_cat}")
                try:
                    dados_cat = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", f"CATALOGO-{nome_cat.upper()}").execute()
                    if dados_cat.data:
                        for item in reversed(dados_cat.data):
                            with st.container(border=True):
                                st.caption(f"📌 Postado por: @{item.get('username')}")
                                msg_completa = item.get('mensagem', '')
                                
                                linhas = msg_completa.split("\n\n")
                                st.markdown(linhas[0])
                                if len(linhas) > 1:
                                    st.write(linhas[1])
                                if len(linhas) > 2 and linhas[2].startswith("http"):
                                    st.image(linhas[2], width=180)
                    else:
                        st.info(f"Nenhum conteúdo em {nome_cat} por enquanto.")
                except: pass

    # === 🧠 ABA: SUPER QUIZ (SISTEMA DE GANHO DE RECOMPENSAS) ===
    with aba_quiz:
        st.header("🧠 Desafio Quiz Silver Coins")
        st.caption("Acerte e leve 🪙 100 Silver Coins!")
        
        cat_quiz_escolhido = st.selectbox("Escolha um Tema para Jogar:", list(PERGUNTAS_QUIZ.keys()))
        perguntas_tema = PERGUNTAS_QUIZ[cat_quiz_escolhido]
        
        key_index_quiz = f"quiz_idx_{cat_quiz_escolhido.replace(' ', '_')}"
        if key_index_quiz not in st.session_state:
            st.session_state[key_index_quiz] = 0
            
        atual_idx = st.session_state[key_index_quiz]
        
        if atual_idx < len(perguntas_tema):
            item_quiz = perguntas_tema[atual_idx]
            st.markdown(f"### Pergunta {atual_idx + 1}:")
            st.write(item_quiz["pergunta"])
            
            resposta_usuario = st.radio("Selecione a resposta certa:", item_quiz["opcoes"], key=f"radio_q_{cat_quiz_escolhido}_{atual_idx}")
            
            if st.button("Enviar Resposta 🎯", use_container_width=True):
                if resposta_usuario == item_quiz["correta"]:
                    st.balloons()
                    st.success("🎯 Correto! +100 Silver Coins!")
                    try:
                        saldo_atualizado = int(user_atual.get("moedas", 0)) + 100
                        supabase.table("perfis_usuarios").update({"moedas": saldo_atualizado}).eq("id", u_id).execute()
                        st.session_state[key_index_quiz] += 1
                        st.rerun()
                    except: st.error("Erro ao computar premiação.")
                else:
                    st.error("❌ Resposta incorreta! Tente novamente.")
        else:
            st.success(f"🎉 Você concluiu tudo de {cat_quiz_escolhido}!")
            if st.button("Reiniciar este Quiz 🔄"):
                st.session_state[key_index_quiz] = 0
                st.rerun()

    # === ✨ ABA STATUS ===
    with aba_status:
        st.header("✨ Status Temporários")
        stat_txt = st.text_input("O que você está pensando?")
        if st.button("Postar Status") and stat_txt.strip():
            try:
                supabase.table("feed_videos").insert({
                    "titulo": f"[STATUS] {stat_txt.strip()}", "url_video": "", "username_autor": u_name,
                    "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0, "id_autor": u_id, "tipo_formato": "horizontal"
                }).execute()
                st.success("Status updated!")
                st.rerun()
            except: pass

    # === 🔔 ABA NOTIFICAÇÕES ===
    with aba_notif:
        st.header("🔔 Suas Notificações")
        try:
            n_lista = supabase.table("notificacoes").select("*").eq("id_destinatario", u_id).execute()
            if n_lista.data:
                for n in reversed(n_lista.data):
                    st.write(f"• {n.get('mensagem', '')}")
            else: st.info("Nenhuma notificação por aqui.")
        except: pass

    # === 👑 ABA EXCLUSIVA DO RAFAEL: PAINEL ADMIN SECRETO ===
    if is_admin:
        aba_adm = abas[-1]
        with aba_adm:
            st.header("👑 Painel Secreto de Controle do Rafael")
            
            # 1. BOT DE CADASTRO AUTOMÁTICO DE OBRAS
            st.subheader("🤖 Bot Inteligente de Cadastro de Conteúdo")
            with st.container(border=True):
                bot_tipo = st.selectbox("Escolha onde Adicionar:", ["Animes", "Filmes", "Séries e Desenhos", "Doramas", "Livros e Mangás"], key="bot_tipo")
                bot_nome = st.text_input("Nome exato da Obra / Título:", key="bot_nome")
                
                # Adaptação dinâmica de texto baseado na escolha
                txt_contagem = "Quantidade de Páginas/Volumes:" if bot_tipo == "Livros e Mangás" else "Quantidade de Episódios/Temporadas:"
                bot_caps = st.text_input(txt_contagem, placeholder="Ex: 24 episódios / 3 volumes", key="bot_caps")
                
                txt_dub = "Idioma / Editora:" if bot_tipo == "Livros e Mangás" else "Tipo de Dublagem / Idioma:"
                bot_dub = st.text_input(txt_dub, placeholder="Ex: Dublado PT-BR / Panini", key="bot_dub")
                bot_img = st.text_input("URL da Imagem de Capa/Poster (Opcional):", key="bot_img")
                
                if st.button("Executar Cadastro pelo Bot ⚡", use_container_width=True):
                    if bot_nome.strip() and bot_caps.strip():
                        try:
                            cod_catalogo = f"CATALOGO-{bot_tipo.upper()}"
                            msg_montada = f"### {bot_nome.strip()} ✨\n• **Info:** {bot_caps.strip()} | **Specs:** {bot_dub.strip()}"
                            if bot_img.strip():
                                msg_montada += f"\n\n{bot_img.strip()}"
                                
                            supabase.table("bate-papo_profissional").insert({
                                "username": "🤖 Bot_Catalogador",
                                "url_foto_perfil": "https://cdn-icons-png.flaticon.com/512/2206/2206241.png",
                                "mensagem": msg_montada,
                                "codigo_sala": cod_catalogo
                            }).execute()
                            st.success(f"🤖 Bot: '{bot_nome}' adicionado com sucesso à aba {bot_tipo}!")
                        except: st.error("Falha na execução do bot.")
                    else: st.warning("Preencha o nome e dados mínimos.")
            
            # 2. INJETOR DE DINHEIRO E CARGOS EM QUALQUER CONTA
            st.subheader("💸 Gerenciador de Usuários, Moedas & Cargos")
            try:
                todos_usuarios = supabase.table("perfis_usuarios").select("*").execute()
                if todos_usuarios.data:
                    for u_comp in todos_usuarios.data:
                        username_alvo = u_comp.get("username")
                        id_alvo = u_comp.get("id")
                        saldo_alvo = u_comp.get("moedas", 0)
                        cargo_atual = u_comp.get("biografia") if u_comp.get("biografia") else "Tester"
                        
                        with st.container(border=True):
                            st.write(f"👤 **Usuário:** @{username_alvo} | Saldo Atual: 🪙 {saldo_alvo} | Cargo: {cargo_atual}")
                            
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                novo_money = st.number_input(f"Injetar Moedas em @{username_alvo}", min_value=0, max_value=999999, value=int(saldo_alvo), step=100, key=f"mon_{id_alvo}")
                            with c2:
                                cargo_novo = st.selectbox(f"Mudar Cargo", ["Tester", "Best Friends of the dev", "Vice-dev", "Membro Comum"], key=f"carg_{id_alvo}")
                            with c3:
                                st.write("##")
                                if st.button("Aplicar Alterações ⚙️", key=f"save_adm_{id_alvo}", use_container_width=True):
                                    supabase.table("perfis_usuarios").update({
                                        "moedas": novo_money,
                                        "biografia": cargo_novo
                                    }).eq("id", id_alvo).execute()
                                    st.toast("Modificações aplicadas!")
                                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao carregar painel de controle: {e}")
