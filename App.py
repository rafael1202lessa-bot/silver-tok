import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v3.7 Final Master", page_icon="🎬", layout="centered")

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

# --- BANCO DE DADOS DE SHIMEJIS / MASCOTES DO LIVRO ---
# Rafael, substitua o link abaixo pela URL pública do seu dragão quando subir no Storage do Supabase!
SHIMEJIS_DISPONIVEIS = {
    "Nenhum": "",
    "🐲 Dragão Azul (Seu Livro)": "https://i.ibb.co/6R0yF6C/dragao-azul.png",
    "⚔️ Mascote Espadachim": "⚔️",
    "🔮 Mago Ancestral": "🔮",
    "🦊 Raposa de Fogo": "🦊",
    "🤖 Mini Robô": "🤖"
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

# --- PERGUNTAS DO QUIZ GEEK ---
PERGUNTAS_QUIZ = {
    "Anime e Animações": [
        {"pergunta": "Qual é o objetivo principal de Luffy em One Piece?", "opcoes": ["Se tornar Hokage", "Encontrar o All Blue", "Ser o Rei dos Piratas", "Derrotar Madara"], "correta": "Ser o Rei dos Piratas"},
        {"pergunta": "Quem é conhecido como o Alquimista de Aço?", "opcoes": ["Roy Mustang", "Edward Elric", "Alphonse Elric", "Saitama"], "correta": "Edward Elric"}
    ],
    "Filmes e Séries / Doramas": [
        {"pergunta": "Em Round 6 (Squid Game), qual é o prêmio final?", "opcoes": ["Um carro de luxo", "45,6 bilhões de wons", "A liberdade eterna", "1 milhão de dólares"], "correta": "45,6 bilhões de wons"},
        {"pergunta": "Qual é a casa de Harry Potter em Hogwarts?", "opcoes": ["Sonserina", "Corvinal", "Lufa-Lufa", "Grifinória"], "correta": "Grifinória"}
    ]
}

# --- FUNÇÕES AUXILIARES ---
def verificar_se_eh_dev(user_id):
    return str(user_id) == ID_REAL_DEVELOPER

def obter_status_emoji(timestamp_str):
    if not timestamp_str: return "⚪ Offline"
    try:
        dt_usuario = datetime.fromisoformat(timestamp_str.split("+")[0]).replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - dt_usuario < timedelta(minutes=3): return "🟢 Online"
    except: pass
    return "⚪ Offline"

def obter_selo_texto(username_alvo, user_id_alvo=None, cargo_adicional="Nenhum"):
    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial":
        return " 👑 DEV"
    if cargo_adicional and cargo_adicional != "Nenhum" and cargo_adicional != "Membro Comum":
        return f" 🎖️ {cargo_adicional}"
    return ""

def renderizar_foto_com_banner(url_foto, username_alvo, user_id_alvo=None, tamanho=80, banner_equipado="Nenhum", shimeji="Nenhum"):
    if not url_foto: url_foto = FOTO_PADRAO
    
    shimeji_html = ""
    if shimeji in SHIMEJIS_DISPONIVEIS and SHIMEJIS_DISPONIVEIS[shimeji] != "":
        val_shimeji = SHIMEJIS_DISPONIVEIS[shimeji]
        if val_shimeji.startswith("http"):
            shimeji_html = f'<img src="{val_shimeji}" style="position: absolute; bottom: -10px; right: -10px; width: {int(tamanho*0.45)}px; height: {int(tamanho*0.45)}px; border-radius: 50%; background: white; padding: 1px; box-shadow: 0 2px 5px rgba(0,0,0,0.4); z-index: 99;">'
        else:
            shimeji_html = f'<div style="position: absolute; bottom: -8px; right: -8px; font-size: {int(tamanho*0.4)}px; background: #fff; border-radius: 50%; padding: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); z-index: 99;">{val_shimeji}</div>'

    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial" or banner_equipado == "👑 Coroa Suprema DEV":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 4px solid #ffd700; box-shadow: 0 0 15px #ffd700;"
        coroa_html = f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.4)}px; z-index: 10;">👑</div>'
    elif "Bronze" in str(banner_equipado):
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #cd7f32;"
        coroa_html = ''
    elif "Prata" in str(banner_equipado):
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #c0c0c0; box-shadow: 0 0 8px #c0c0c0;"
        coroa_html = ''
    elif "Otaku" in str(banner_equipado):
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #ff4500; box-shadow: 0 0 10px #ff4500;"
        coroa_html = f'<div style="position: absolute; top: -18px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🦊</div>'
    elif "Dorama" in str(banner_equipado) or "🌸" in str(banner_equipado):
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #ff69b4; box-shadow: 0 0 10px #ff69b4;"
        coroa_html = f'<div style="position: absolute; top: -18px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🌸</div>'
    else:
        estilo_css = "border-radius: 50%; object-fit: cover; border: 2px solid #ccc;"
        coroa_html = ''
        
    html = f"""
    <div style="position: relative; display: inline-block; text-align: center; margin-top: 15px; margin-bottom: 5px;">
        {coroa_html}
        <img src="{url_foto}" width="{tamanho}" height="{tamanho}" style="{estilo_css}">
        {shimeji_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def renderizar_caixa_mensagem(username, mensagem, selo, estilo_caixa, eh_admin=False):
    if not mensagem or str(mensagem).lower() == "none": return

    if eh_admin or estilo_caixa == "👑 Balão Dourado DEV":
        estilo_css = "background: linear-gradient(135deg, #fff7e6, #ffeaa7); border-left: 5px solid #ffd700; padding: 12px; border-radius: 8px; margin-bottom: 8px;"
    elif "Azul" in str(estilo_caixa):
        estilo_css = "background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
    elif "Neon" in str(estilo_caixa):
        estilo_css = "background-color: #1a1a2e; border: 1px solid #e94560; color: #fff; padding: 10px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 0 8px #e94560;"
    else:
        estilo_css = "background-color: #f1f3f4; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #ccc;"
        
    conteudo_final = mensagem
    if str(mensagem).startswith("https://") and any(ext in str(mensagem).lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
        conteudo_final = f'<br><img src="{mensagem}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'
    elif str(mensagem).startswith("https://") and any(ext in str(mensagem).lower() for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.bin']):
        conteudo_final = f'<br><audio controls style="max-width: 100%; margin-top: 5px;"><source src="{mensagem}"></audio>'

    st.markdown(f"""
    <div style="{estilo_css}">
        <span style="font-weight: bold; color: #333;">{username}</span> 
        <span style="font-size: 11px; font-weight: bold; color: #d4af37;">{selo}</span>: 
        <span style="color: {'#111' if 'Neon' not in str(estilo_caixa) else '#fff'};">{conteudo_final}</span>
    </div>
    """, unsafe_allow_html=True)

# --- GERENCIAMENTO DE ESTADO ---
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state: st.session_state.sala_ativa = None
if "shimeji_local" not in st.session_state: st.session_state.shimeji_local = "Nenhum"
if "perfil_visitado" not in st.session_state: st.session_state.perfil_visitado = None

# --- FLUXO DE ENTRADA / AUTH ---
if st.session_state.usuario_logado is None:
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)
    aba_auth = st.tabs(["Fazer Login", "Criar Nova Conta"])
    
    with aba_auth[0]:
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        if st.button("Entrar 🚀", key="btn_login", use_container_width=True):
            busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
            if busca.data and busca.data[0].get("senha") == login_senha:
                st.session_state.usuario_logado = busca.data[0]
                st.rerun()
            else: st.error("Incorreto.")
                    
    with aba_auth[1]:
        cad_user = st.text_input("Escolha um Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie uma Senha:", type="password", key="cad_senha")
        codigo_convite = st.text_input("🔑 Código Secreto:", type="password", key="codigo_convite")
        if st.button("Cadastrar 🎉", use_container_width=True):
            if codigo_convite == CHAVE_SECRETA:
                try:
                    supabase.table("perfis_usuarios").insert({"username": cad_user, "apelido": cad_user, "senha": cad_senha, "url_foto_perfil": FOTO_PADRAO, "moedas": 0, "banner_ativo": "Nenhum", "biografia": "Tester"}).execute()
                    st.success("Criado!")
                except: st.error("Erro ou Usuário indisponível.")
else:
    user_atual = st.session_state.usuario_logado
    u_id = user_atual.get("id")
    u_name = user_atual.get("username", "Membro")
    is_admin = verificar_se_eh_dev(u_id)
    u_cargo = user_atual.get("biografia") if user_atual.get("biografia") else "Tester"
    u_moedas = user_atual.get("moedas") if user_atual.get("moedas") is not None else 0

    try: supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", u_id).execute()
    except: pass

    # --- BARRA LATERAL MESTRE ---
    with st.sidebar:
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil"), u_name, u_id, tamanho=90, banner_equipado=user_atual.get("banner_ativo", "Nenhum"), shimeji=st.session_state.shimeji_local)
        st.write(f"**{user_atual.get('apelido') or u_name}** {obter_selo_texto(u_name, u_id, u_cargo)}")
        st.markdown(f"🪙 **Silver Coins:** {u_moedas}")
        
        # Invocador de Shimeji
        st.session_state.shimeji_local = st.selectbox("🐲 Shimeji Companheiro:", list(SHIMEJIS_DISPONIVEIS.keys()), index=list(SHIMEJIS_DISPONIVEIS.keys()).index(st.session_state.shimeji_local) if st.session_state.shimeji_local in SHIMEJIS_DISPONIVEIS else 0)
        
        with st.expander("🎒 Meu Inventário"):
            opcoes_inv = ["Nenhum", "🥉 Bronze Estelar", "🥈 Prata Lendária", "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber", "🔥 Mestre Otaku (Anime)", "🌸 Dorama Lover"]
            if is_admin: opcoes_inv.extend(["👑 Coroa Suprema DEV", "👑 Balão Dourado DEV"])
            escolha_c = st.selectbox("Equipar:", opcoes_inv)
            if st.button("Confirmar 🛡️"):
                supabase.table("perfis_usuarios").update({"banner_ativo": escolha_c}).eq("id", u_id).execute()
                user_atual["banner_ativo"] = escolha_c
                st.rerun()

        if st.button("Sair da Conta 🚪", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()

    # --- INTERFACE DE ABAS ---
    abas_menu = ["📺 Silver Tok (Feed)", "🛒 Loja Premium", "💬 Chat-Exv", "🍿 Área Geek", "🧠 Super Quiz", "✨ Status"]
    if is_admin: abas_menu.append("👑 Painel Admin")
    abas = st.tabs(abas_menu)

    # === 1. FEED COMPLETO RESTAURADO COM COMENTÁRIOS ===
    with abas[0]:
        if not st.session_state.perfil_visitado:
            st.title("Feed Silver Tok Global")
            with st.expander("➕ Publicar no Feed"):
                t_pub = st.text_input("Legenda do Vídeo/Foto:")
                f_midia = st.file_uploader("Upload Mídia:", type=["mp4", "png", "jpg", "jpeg"])
                fmt = st.selectbox("Formato:", ["Horizontal", "Vertical"])
                if st.button("Publicar Post 🚀") and f_midia and t_pub:
                    path_b = f"feed/{uuid.uuid4()}_{f_midia.name}"
                    supabase.storage.from_("imagens_chat").upload(path_b, f_midia.read())
                    url_f = supabase.storage.from_("imagens_chat").get_public_url(path_b)
                    supabase.table("feed_videos").insert({"titulo": t_pub, "url_video": url_f, "username_autor": u_name, "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0, "id_autor": u_id, "tipo_formato": fmt.lower()}).execute()
                    st.rerun()

            try:
                feed_dados = supabase.table("feed_videos").select("*").execute()
                if feed_dados.data:
                    for v in reversed(feed_dados.data):
                        if str(v.get("titulo")).startswith("[STATUS]"): continue
                        with st.container(border=True):
                            col_p1, col_p2 = st.columns([1, 5])
                            with col_p1:
                                renderizar_foto_com_banner(v.get("avatar_autor"), v.get("username_autor"), tamanho=45)
                                if st.button("👤", key=f"p_{v.get('id')}"):
                                    st.session_state.perfil_visitado = v.get("username_autor")
                                    st.rerun()
                            with col_p2:
                                st.markdown(f"**@{v.get('username_autor')}**")
                                st.write(v.get("titulo"))
                            
                            if v.get("url_video"):
                                if v.get("tipo_formato") == "vertical":
                                    st.markdown(f'<div style="text-align:center;"><video width="260" height="460" controls><source src="{v.get("url_video")}"></video></div>', unsafe_allow_html=True)
                                else: st.video(v.get("url_video"))
                            
                            c_b1, c_b2 = st.columns(2)
                            with c_b1:
                                if st.button(f"❤️ {v.get('curtidas', 0)} Curtidas", key=f"l_{v.get('id')}"):
                                    supabase.table("feed_videos").update({"curtidas": v.get("curtidas") + 1}).eq("id", v.get("id")).execute()
                                    st.rerun()
                            with c_b2:
                                if v.get("username_autor") == u_name or is_admin:
                                    if st.button("Deletar 🗑️", key=f"del_{v.get('id')}"):
                                        supabase.table("feed_videos").delete().eq("id", v.get("id")).execute()
                                        st.rerun()

                            # Seção de Comentários do Post
                            with st.expander("💬 Comentários"):
                                cod_disc = f"POST-{v.get('id')}"
                                c_in = st.text_input("Comentar algo:", key=f"in_c_{v.get('id')}")
                                if st.button("Enviar 💬", key=f"btn_c_{v.get('id')}") and c_in.strip():
                                    supabase.table("bate-papo_profissional").insert({"username": u_name, "mensagem": c_in.strip(), "codigo_sala": cod_disc, "id_usuario": u_id, "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO}).execute()
                                    st.rerun()
                                    
                                try:
                                    coms = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", cod_disc).execute()
                                    for cm in coms.data:
                                        st.markdown(f"**@{cm.get('username')}:** {cm.get('mensagem')}")
                                except: pass
            except: pass
        else:
            st.button("⬅️ Voltar ao Feed", on_click=lambda: st.session_state.replace(perfil_visitado=None))
            st.subheader(f"Perfil de @{st.session_state.perfil_visitado}")
            # Dados do perfil visitado simplificado
            st.info("Mostrando feed focado e customizações ativas.")

    # === 2. LOJA PREMIUM ===
    with abas[1]:
        st.header("🛒 Loja Premium")
        st.write(f"Seu Saldo: 🪙 {u_moedas} Silver Coins")
        col_l1, col_l2 = st.columns(2)
        for idx, (chave, info) in enumerate(COSMETICOS.items()):
            col_fogo = col_l1 if idx % 2 == 0 else col_l2
            with col_fogo:
                with st.container(border=True):
                    st.markdown(f"### {info['nome']}")
                    st.write(f"Preço: 🪙 {info['preco']} Coins")
                    if u_moedas >= info['preco']:
                        if st.button(f"Comprar {info['nome']}", key=f"loj_{chave}"):
                            supabase.table("perfis_usuarios").update({"moedas": int(u_moedas) - int(info['preco'])}).eq("id", u_id).execute()
                            st.success("Adquirido!")
                            st.rerun()
                    else: st.caption("Saldo Insuficiente")

    # === 3. CHAT-EXV CORRIGIDO COM PROTOCOLO DE ID ===
    with abas[2]:
        st.header("💬 Chat-Exv Comunidade")
        if st.session_state.sala_ativa is None: st.session_state.sala_ativa = "GERAL"
        sala = st.session_state.sala_ativa
        st.caption(f"Sala Atual: `{sala}`")
        
        m_txt = st.text_input("Mensagem para o grupo:")
        if st.button("Enviar Mensagem ✉️", use_container_width=True) and m_txt.strip():
            supabase.table("bate-papo_profissional").insert({"username": u_name, "mensagem": m_txt.strip(), "codigo_sala": sala, "id_usuario": u_id, "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO}).execute()
            st.rerun()

        with st.expander("📸 Enviar Imagem"):
            arq = st.file_uploader("Escolha foto:", type=["png", "jpg", "jpeg", "gif"])
            if st.button("Postar Imagem 🚀") and arq:
                p_img = f"chat/{uuid.uuid4()}_{arq.name}"
                supabase.storage.from_("imagens_chat").upload(p_img, arq.read())
                url_p = supabase.storage.from_("imagens_chat").get_public_url(p_img)
                supabase.table("bate-papo_profissional").insert({"username": u_name, "mensagem": url_p, "codigo_sala": sala, "id_usuario": u_id, "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO}).execute()
                st.rerun()

        st.markdown("---")
        try:
            mensagens_banco = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", sala).execute()
                st.rerun()

        st.markdown("---")
        try:
            mensagens_banco = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", sala).execute()
            for m in reversed(mensagens_banco.data[-30:]):
                if str(m.get("codigo_sala")).startswith("CATALOGO"): continue
                col_m1, col_m2 = st.columns([1, 7])
                with col_m1:
                    st.markdown(f'<img src="{m.get("url_foto_perfil") or FOTO_PADRAO}" width="35" style="border-radius:50%;">', unsafe_allow_html=True)
                with col_m2:
                    renderizar_caixa_mensagem(m.get("username"), m.get("mensagem"), "", "Nenhum", eh_admin=(m.get("username") == "Rafael_oficial"))
        except: pass

    # === 4. ÁREA GEEK CONECTADA AO BOT ===
    with abas[3]:
        st.header("🍿 Catálogo Geek & Literário")
        abas_geek = st.tabs(["⛩️ Animes", "🎬 Filmes", "📺 Séries & Desenhos", "🌸 Doramas", "📖 Livros e Mangás"])
        cats = ["ANIMES", "FILMES", "SERIES_DESENHOS", "DORAMAS", "LIVROS_MANGAS"]
        
        for id_g, nome_g in enumerate(cats):
            with abas_geek[id_g]:
                try:
                    res_cat = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", f"CATALOGO-{nome_g}").execute()
                    if res_cat.data:
                        for item in reversed(res_cat.data):
                            with st.container(border=True):
                                st.markdown(item.get("mensagem"))
                                st.caption(f"Postado por: @{item.get('username')}")
                    else: st.info("Nenhuma obra registrada aqui pelo Bot do Admin ainda.")
                except: pass

    # === 5. QUIZ COM SISTEMA DE PREMIAÇÃO INTEGRADO ===
    with abas[4]:
        st.header("🧠 Quiz Geek valendo Coins")
        cat_q = st.selectbox("Escolha o tema:", list(PERGUNTAS_QUIZ.keys()))
        pf = PERGUNTAS_QUIZ[cat_q][0]
        st.write(pf["pergunta"])
        r_usr = st.radio("Sua resposta:", pf["opcoes"])
        if st.button("Validar Resposta 🎯"):
            if r_usr == pf["correta"]:
                st.success("Correto! +100 Coins adicionadas.")
                supabase.table("perfis_usuarios").update({"moedas": int(u_moedas) + 100}).eq("id", u_id).execute()
                st.balloons()
            else: st.error("Incorreto.")

    # === 6. STATUS TEMPORÁRIOS RESTAURADO ===
    with abas[5]:
        st.header("✨ Status da Comunidade")
        st_in = st.text_input("O que está rolando agora?")
        if st.button("Atualizar Status 📝") and st_in.strip():
            supabase.table("feed_videos").insert({"titulo": f"[STATUS] {st_in.strip()}", "url_video": "", "username_autor": u_name, "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0, "id_autor": u_id, "tipo_formato": "horizontal"}).execute()
            st.success("Status Postado!")
            st.rerun()
            
        try:
            all_st = supabase.table("feed_videos").select("*").execute()
            for s in reversed(all_st.data):
                if "[STATUS]" in str(s.get("titulo")):
                    st.markdown(f"💬 **@{s.get('username_autor')}:** {str(s.get('titulo')).replace('[STATUS]', '')}")
        except: pass

    # === 7. PAINEL ADMIN SECRETO DO RAFAEL COM BOT DE CADASTRO AUTOMÁTICO ===
    if is_admin:
        with abas[6]:
            st.header("👑 Painel Supremo de Controle (Rafael)")
            
            # BOT INTELIGENTE DE CADASTRO
            st.subheader("🤖 Bot de Cadastro Automático")
            with st.container(border=True):
                b_tipo = st.selectbox("Tipo da Obra:", ["Animes", "Filmes", "Séries & Desenhos", "Doramas", "Livros e Mangás"])
                b_map = {"Animes": "ANIMES", "Filmes": "FILMES", "Séries & Desenhos": "SERIES_DESENHOS", "Doramas": "DORAMAS", "Livros e Mangás": "LIVROS_MANGAS"}
                b_nome = st.text_input("Nome da Obra:")
                b_caps = st.text_input("Nº de Episódios ou Páginas:")
                b_dub = st.text_input("Dublagem / Editora:")
                
                if st.button("Adicionar Automaticamente via Bot ⚡", use_container_width=True):
                    msg_final = f"### 🎬 {b_nome}\n• **Volume/Episódios:** {b_caps} \n• **Especificações:** {b_dub}"
                    supabase.table("bate-papo_profissional").insert({"username": "🤖 Bot_Catalogador", "mensagem": msg_final, "codigo_sala": f"CATALOGO-{b_map[b_tipo]}", "id_usuario": u_id, "url_foto_perfil": FOTO_PADRAO}).execute()
                    st.success("Obra cadastrada e enviada automaticamente para o catálogo correspondente!")
            
            # GERENCIADOR DE CONTAS, DINHEIRO E CARGOS
            st.subheader("💸 Gerenciador de Moedas & Cargos")
            try:
                ulist = supabase.table("perfis_usuarios").select("*").execute()
                for usr in ulist.data:
                    with st.container(border=True):
                        st.write(f"👤 @{usr.get('username')} | Cargo: `{usr.get('biografia')}`")
                        c1, c2 = st.columns(2)
                        with c1: n_coin = st.number_input(f"Coins de @{usr.get('username')}", min_value=0, value=int(usr.get('moedas') or 0), key=f"ad_m_{usr.get('id')}")
                        with c2: n_carg = st.selectbox(f"Cargo de @{usr.get('username')}", ["Tester", "Best Friends of the dev", "Vice-dev", "Membro Comum"], key=f"ad_c_{usr.get('id')}")
                        if st.button("Aplicar Configurações ⚙️", key=f"b_ad_{usr.get('id')}"):
                            supabase.table("perfis_usuarios").update({"moedas": n_coin, "biografia": n_carg}).eq("id", usr.get("id")).execute()
                            st.toast("Modificações salvas!")
                            st.rerun()
            except: pass
        
