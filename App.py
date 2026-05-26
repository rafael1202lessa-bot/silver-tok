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
    user_atual = st.session_state.usuario_logado
    u_id = user_atual.get("id", "")
    u_name = user_atual.get("username", "Membro")
    is_admin = verificar_se_eh_dev(u_id)
    u_cargo = user_atual.get("biografia") if user_atual.get("biografia") else "Nenhum"
    u_shimeji = user_atual.get("localizacao") if user_atual.get("localizacao") else "Nenhum"

    if MODO_MANUTENCAO and not is_admin:
        st.markdown("<h1 style='text-align: center;'>🚧 Silver Tok & Chat 🚧</h1>", unsafe_allow_html=True)
        st.error("O aplicativo está em manutenção para a implementação de novas funções!")
        st.stop()

    try:
        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", u_id).execute()
    except: pass

    total_notif = 0
    try:
        res_n = supabase.table("notificacoes").select("*").eq("id_destinatario", u_id).eq("lida", False).execute()
        total_notif = len(res_n.data) if res_n.data else 0
    except: pass

    # --- BARRA LATERAL ---
    with st.sidebar:
        banner_v = user_atual.get("banner_ativo", "Nenhum")
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, u_name, u_id, tamanho=90, banner_equipado=banner_v, shimeji=u_shimeji)
        
        selo_proprio = obter_selo_texto(u_name, u_id, cargo_adicional=u_cargo)
        st.write(f"**{user_atual.get('apelido') or u_name}** {selo_proprio}")
        st.markdown(f"🪙 **Silver Coins:** {user_atual.get('moedas', 0)}")
        
        with st.expander("🦊 Meus Shimejis / Mascotes"):
            escolha_shim = st.selectbox("Escolha seu Acompanhante:", list(SHIMEJIS_DISPONIVEIS.keys()), index=list(SHIMEJIS_DISPONIVEIS.keys()).index(u_shimeji) if u_shimeji in SHIMEJIS_DISPONIVEIS else 0)
            if st.button("Ativar Mascote ✨", use_container_width=True):
                try:
                    supabase.table("perfis_usuarios").update({"localizacao": escolha_shim}).eq("id", u_id).execute()
                    st.toast("Mascote invocado!")
                    st.rerun()
                except: pass

        with st.expander("🎒 Meu Inventário"):
            opcoes_inventario = ["Nenhum", "🥉 Bronze Estelar", "🥈 Prata Lendária", "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber", "🔥 Mestre Otaku (Anime)", "🎬 Cinéfilo de Carteirinha", "🌸 Dorama Lover"]
            if is_admin:
                opcoes_inventario.insert(1, "👑 Coroa Suprema DEV")
                opcoes_inventario.insert(2, "👑 Balão Dourado DEV")
            escolha_custom = st.selectbox("Selecione para ativar:", opcoes_inventario)
            if st.button("Equipar Cosmético 🛡️"):
                try:
                    supabase.table("perfis_usuarios").update({"banner_ativo": escolha_custom}).eq("id", u_id).execute()
                    st.toast("Equipado!")
                    st.rerun()
                except: pass

        with st.expander("⚙️ Editar Meu Perfil"):
            novo_apelido = st.text_input("Alterar Apelido:", value=user_atual.get("apelido") or u_name)
            nova_foto = st.text_input("URL da Foto de Perfil:", value=user_atual.get("url_foto_perfil") or FOTO_PADRAO)
            if st.button("Salvar Alterações 💾"):
                try:
                    supabase.table("perfis_usuarios").update({"apelido": novo_apelido.strip(), "url_foto_perfil": nova_foto.strip()}).eq("id", u_id).execute()
                    st.rerun()
                except: pass

        if st.button("Sair da Conta 🚪", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()

    # --- LISTAGEM DE POSTS (FUNÇÃO) ---
    def renderizar_lista_filtrada(lista_posts, identificador_formato, termo_busca="", ordenacao=""):
        if termo_busca:
            lista_posts = [p for p in lista_posts if termo_busca.lower() in str(p.get("titulo", "")).lower()]
        for idx, v in enumerate(lista_posts):
            if str(v.get("titulo", "")).startswith("[STATUS]"): continue
            autor = v.get('username_autor', 'Membro')
            id_post = v.get("id")
            st.markdown("---")
            st.markdown(f"**@{autor}** postou:")
            st.write(v.get("titulo", ""))
            if v.get("url_video"):
                if v.get("tipo_formato") == "vertical":
                    st.markdown(f'<div style="text-align:center;"><video width="260" height="460" controls><source src="{v.get("url_video")}"></video></div>', unsafe_allow_html=True)
                else: st.video(v.get("url_video"))

            # Sistema de Comentários Corrigido
            with st.expander("💬 Ver Comentários"):
                cod_discussao = f"POST-{id_post}"
                novo_coment = st.text_input("Escreva algo...", key=f"in_{identificador_formato}_{id_post}")
                if st.button("Comentar 💬", key=f"btn_{identificador_formato}_{id_post}") and novo_coment.strip():
                    supabase.table("bate-papo_profissional").insert({
                        "username": u_name, "id_usuario": u_id, "mensagem": novo_coment.strip(), "codigo_sala": cod_discussao, "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO
                    }).execute()
                    st.rerun()
                try:
                    coms = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", cod_discussao).execute()
                    for c in coms.data:
                        st.markdown(f"**@{c.get('username')}:** {c.get('mensagem')}")
                except: pass

    # --- ABAS PRINCIPAIS ---
    abas_principais = ["📺 Silver Tok (Feed)", "🛒 Loja & Caixas", "💬 Chat-Exv", "🍿 Área Geek", "🧠 Super Quiz", "✨ Status"]
    if is_admin: abas_principais.append("👑 Painel Admin Secreto")
    abas = st.tabs(abas_principais)

    # ABA 1: FEED
    with abas[0]:
        exibir_logo()
        busca_legenda = st.text_input("Buscar posts por legenda:")
        try:
            f_dados = supabase.table("feed_videos").select("*").execute()
            posts_completos = (f_dados.data or []) + VIDEOS_BOT_BOTEY
            renderizar_lista_filtrada(reversed(posts_completos), "global", busca_legenda)
        except: st.info("Sem posts no feed no momento.")

    # ABA 2: LOJA
    with abas[1]:
        st.header("🛒 Loja de Cosméticos Premium")
        saldo_atual = user_atual.get("moedas", 0)
        st.info(f"Seu saldo atual: 🪙 {saldo_atual} Silver Coins")
        col_l1, col_l2 = st.columns(2)
        for idx, (chave, info) in enumerate(COSMETICOS.items()):
            coluna_foco = col_l1 if idx % 2 == 0 else col_l2
            with coluna_foco:
                with st.container(border=True):
                    st.markdown(f"### {info['nome']}")
                    st.write(f"Preço: 🪙 {info['preco']} Coins")
                    if saldo_atual >= info['preco']:
                        if st.button(f"Adquirir", key=f"loja_buy_{chave}"):
                            supabase.table("perfis_usuarios").update({"moedas": int(saldo_atual) - int(info['preco'])}).eq("id", u_id).execute()
                            st.success("Adquirido com sucesso!")
                            st.rerun()

    # ABA 3: CHAT-EXV
    with abas[2]:
        if st.session_state.sala_ativa is None: st.session_state.sala_ativa = "GERAL"
        sala = st.session_state.sala_ativa
        st.subheader(f"Sala de Chat Ativa: `{sala}`")
        
        m_txt = st.text_input("Mensagem para a sala:", key="txt_chat_main")
        if st.button("Enviar Mensagem ✉️") and m_txt.strip():
            supabase.table("bate-papo_profissional").insert({
                "username": u_name, "id_usuario": u_id, "mensagem": m_txt.strip(), "codigo_sala": sala, "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO
            }).execute()
            st.rerun()

        try:
            mensagens_banco = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", sala).execute()
            for m in reversed(mensagens_banco.data[-30:]):
                if "POST-" in str(m.get("codigo_sala")): continue
                st.markdown(f"**@{m.get('username')}:** {m.get('mensagem')}")
        except: pass

    # ABA 4: ÁREA GEEK
    with abas[3]:
        st.header("🍿 Catálogo Geek da Comunidade")
        st.write("Bem-vindo à central de cinema e animes!")

    # ABA 5: QUIZ
    with abas[4]:
        st.header("🧠 Super Quiz Premiado")
        cat_q = st.selectbox("Escolha o Tema do Desafio:", list(PERGUNTAS_QUIZ.keys()))
        pf = PERGUNTAS_QUIZ[cat_q][0]
        st.write(f"**Pergunta:** {pf['pergunta']}")
        r_usr = st.radio("Escolha uma alternativa:", pf["opcoes"])
        if st.button("Enviar Resposta 🎯"):
            if r_usr == pf["correta"]:
                st.success("Parabéns! +100 Silver Coins!")
                try:
                    supabase.table("perfis_usuarios").update({"moedas": int(user_atual.get("moedas", 0)) + 100}).eq("id", u_id).execute()
                except: pass
            else: st.error("Incorreto, tente de novo!")

    # ABA 6: STATUS
    with abas[5]:
        st.header("✨ Status Momentâneos")
        st_in = st.text_input("O que você está pensando agora?")
        if st.button("Publicar Status") and st_in.strip():
            supabase.table("feed_videos").insert({
                "titulo": f"[STATUS] {st_in.strip()}", "url_video": "", "username_autor": u_name, "id_autor": u_id, "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0, "tipo_formato": "horizontal"
            }).execute()
            st.success("Status postado!")
            st.rerun()

    # ABA 7: ADMIN
    if is_admin:
        with abas[6]:
            st.header("👑 Painel de Gerenciamento Geral (Dev)")
            st.write("Controle total da plataforma ativo.")
