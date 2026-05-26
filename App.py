import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v3.8 Ultra Master", page_icon="🎬", layout="centered")

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

# --- LISTA REGRAS DO SITE ---
REGRAS_SISTEMA = [
    "🚫 Estritamente proibido postar conteúdos +18 ou sexualmente explícitos.",
    "❌ Proibido qualquer tipo de discurso de ódio, racismo, bullying ou discriminação.",
    "⚠️ Não exponha informações pessoais ou de saúde de terceiros publicamente.",
    "🔨 O descumprimento de qualquer regra resultará em banimento imediato e permanente por parte da administração."
]

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
    "banner_dorama": {"nome": "🌸 Dorama Lover", "preco": 450, "img": "https://cdn-icons-png.flaticon.com/512/4230/4230633.png"},
    "banner_kpop": {"nome": "🌸 Banner K-Popper Oficial", "preco": 0, "img": "https://cdn-icons-png.flaticon.com/512/2991/2991610.png"}
}

# --- MAPEAMENTO DE CARGOS MANUAIS ---
CARGOS_CUSTOMIZADOS = {
    "Lilica": "Tester",
    "Júlia Guimarães": "Tester",
    "Rafael_oficial": "DEV"
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
    if username_alvo in CARGOS_CUSTOMIZADOS:
        return f" 🎖️ {CARGOS_CUSTOMIZADOS[username_alvo]}"
    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial":
        return " 👑 DEV"
    if cargo_adicional and cargo_adicional != "Nenhum":
        return f" 🎖️ {cargo_adicional}"
    return ""

def renderizar_foto_com_banner(url_foto, username_alvo, user_id_alvo=None, tamanho=90, banner_equipado="Nenhum", shimeji="Nenhum"):
    if not url_foto:
        url_foto = FOTO_PADRAO
    
    shimeji_html = ""
    if shimeji in SHIMEJIS_DISPONIVEIS and SHIMEJIS_DISPONIVEIS[shimeji] != "":
        valor_shimeji = SHIMEJIS_DISPONIVEIS[shimeji]
        shimeji_html = f'<div style="position: absolute; bottom: -5px; right: -5px; font-size: {int(tamanho*0.35)}px; background: white; border-radius: 50%; padding: 2px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); z-index: 12;">{valor_shimeji}</div>'

    if banner_equipado == "Nenhum":
        estilo_css = "border-radius: 50%; object-fit: cover; border: 1px solid #ccc;"
        coroa_html = ''
    elif banner_equipado == "👑 Coroa Suprema DEV" or verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial":
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
    elif banner_equipado == "🌸 Banner K-Popper Oficial":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #ff69b4; box-shadow: 0 0 12px #ff69b4;"
        coroa_html = f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🎤</div>'
    else:
        estilo_css = "border-radius: 50%; object-fit: cover; border: 1px solid #ccc;"
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

    if estilo_caixa == "Nenhum":
        estilo_css = "background-color: #f1f3f4; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #ccc;"
    elif eh_admin or estilo_caixa == "👑 Balão Dourado DEV":
        estilo_css = "background: linear-gradient(135deg, #fff7e6, #ffeaa7); border-left: 5px solid #ffd700; padding: 12px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(255,215,0,0.2);"
    elif estilo_caixa == "🔷 Balão Azul Moderno":
        estilo_css = "background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
    elif estilo_caixa == "🔮 Balão Neon Cyber":
        estilo_css = "background-color: #1a1a2e; border: 1px solid #e94560; color: #fff; padding: 10px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 0 10px #e94560;"
    else:
        estilo_css = "background-color: #f1f3f4; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #ccc;"
        
    conteudo_final = mensagem
    if str(mensagem).startswith("https://"):
        if any(ext in str(mensagem).lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
            conteudo_final = f'<br><img src="{mensagem}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'
        elif any(ext in str(mensagem).lower() for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.webm', '.bin']) or "audio" in str(mensagem).lower():
            conteudo_final = f'<br><audio controls style="max-width: 100%; margin-top: 5px;"><source src="{mensagem}"></audio>'

    st.markdown(f"""
    <div style="{estilo_css}">
        <span style="font-weight: bold; color: #333;">{username}</span> 
        <span style="font-size: 12px; font-weight: bold; color: #d4af37;">{selo}</span>: 
        <span>{conteudo_final}</span>
    </div>
    """, unsafe_allow_html=True)

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat v3.8 🔐</h1>", unsafe_allow_html=True)

# --- FLUXO DE AUTENTICAÇÃO ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = "GERAL"
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
                    if busca.data[0].get("website") == "BANIDO":
                        st.error("Esta conta foi banida permanentemente por violação das diretrizes.")
                    else:
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
                        "url_foto_perfil": FOTO_PADRAO, "ultimo_visto": datetime.now(timezone.utc).isoformat(),
                        "moedas": 0, "banner_ativo": "Nenhum"
                    }).execute()
                    st.success("Conta criada! Faça login.")
                except:
                    st.error("Nome de usuário indisponível.")
else:
    user_atual = st.session_state.usuario_logado
    
    # TRATAMENTO ANTIFALHA CRÍTICO: Garante um UUID/ID válido caso o banco retorne nulo
    u_id = str(user_atual.get("id")) if user_atual.get("id") else None
    if not u_id or u_id == "None":
        u_id = "04daaa3c-63ef-486c-b33e-54d4e80ee9e9" # ID do Desenvolvedor de segurança secundária
        
    u_name = user_atual.get("username", "Membro")
    is_admin = verificar_se_eh_dev(u_id) or u_name == "Rafael_oficial"
    u_cargo = user_atual.get("biografia") if user_atual.get("biografia") else "Nenhum" 
    u_shimeji = user_atual.get("localizacao") if user_atual.get("localizacao") else "Nenhum" 

    # --- BARRA LATERAL ---
    with st.sidebar:
        banner_v = user_atual.get("banner_ativo", "Nenhum")
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, u_name, u_id, tamanho=90, banner_equipado=banner_v, shimeji=u_shimeji)
        
        selo_proprio = obter_selo_texto(u_name, u_id, cargo_adicional=u_cargo)
        st.write(f"**{user_atual.get('apelido') or u_name}** {selo_proprio}")
        st.markdown(f"🪙 **Silver Coins:** {user_atual.get('moedas', 0)}")
        
        try:
            total_seg_data = len(supabase.table("seguidores").select("*").eq("id_seguido", u_id).execute().data)
            st.markdown(f"👥 **Seguidores:** {total_seg_data}")
        except: pass

        with st.expander("🦊 Meus Shimejis / Mascotes"):
            escolha_shim = st.selectbox("Escolha seu Acompanhante:", list(SHIMEJIS_DISPONIVEIS.keys()), index=list(SHIMEJIS_DISPONIVEIS.keys()).index(u_shimeji) if u_shimeji in SHIMEJIS_DISPONIVEIS else 0)
            if st.button("Ativar Mascote ✨", use_container_width=True):
                try:
                    supabase.table("perfis_usuarios").update({"localizacao": escolha_shim}).eq("id", u_id).execute()
                    st.toast("Mascote invocado!")
                    st.rerun()
                except: pass

        with st.expander("🎒 Meu Inventário"):
            opcoes_inventario = ["Nenhum", "🥉 Bronze Estelar", "🥈 Prata Lendária", "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber", "🔥 Mestre Otaku (Anime)", "🌸 Banner K-Popper Oficial"]
            if is_admin:
                opcoes_inventario.extend(["👑 Coroa Suprema DEV", "👑 Balão Dourado DEV"])
                
            escolha_custom = st.selectbox("Selecione para ativar:", opcoes_inventario, index=opcoes_inventario.index(banner_v) if banner_v in opcoes_inventario else 0)
            if st.button("Equipar Cosmético 🛡️", use_container_width=True):
                try:
                    supabase.table("perfis_usuarios").update({"banner_ativo": escolha_custom}).eq("id", u_id).execute()
                    st.toast("Item equipado com sucesso!")
                    st.rerun()
                except: pass

        st.markdown("---")

    def renderizar_lista_filtrada(lista_posts, identificador_formato):
        for idx, v in enumerate(lista_posts):
            if "[GEEK]" in str(v.get("titulo", "")): continue
            autor = v.get('username_autor', 'Membro')
            id_autor_post = v.get('id_autor') if v.get('id_autor') else u_id
            img_autor = v.get('avatar_autor') or FOTO_PADRAO
            video_url = v.get("url_video", "")
            id_post = v.get("id")
            chave_comp = f"feed_{identificador_formato}_{idx}_{id_post}"

            st.markdown("---")
            col_f1, col_f2 = st.columns([1, 5])
            with col_f1: 
                renderizar_foto_com_banner(img_autor, autor, id_autor_post, tamanho=50)
            with col_f2:
                selo_autor = obter_selo_texto(autor, id_autor_post)
                st.markdown(f"**{autor}** {selo_autor}")
                st.caption(v.get("titulo", ""))

            if v.get("tipo_formato") == "vertical":
                st.markdown(f'<div style="display: flex; justify-content: center;"><video width="290" height="515" controls><source src="{video_url}" type="video/mp4"></video></div>', unsafe_allow_html=True)
            else:
                if "[FOTO]" in str(v.get("titulo", "")):
                    st.image(video_url, use_container_width=True)
                elif video_url:
                    st.video(video_url)

            col_b1, col_b2 = st.columns([2, 2])
            with col_b1:
                if st.button(f"❤️ {v.get('curtidas', 0)} Curtidas", key=f"like_{chave_comp}"):
                    if "bot_" not in str(id_post):
                        try: supabase.table("feed_videos").update({"curtidas": v.get('curtidas', 0) + 1}).eq("id", id_post).execute()
                        except: pass
                    st.rerun()
            with col_b2:
                if autor == u_name or is_admin:
                    if st.button("Remover Post 🗑️", key=f"del_{chave_comp}"):
                        if "bot_" not in str(id_post):
                            try: supabase.table("feed_videos").delete().eq("id", id_post).execute()
                            except: pass
                        st.rerun()

    # --- MONTAGEM DAS ABAS PRINCIPAIS ---
    abas_principais = ["📺 Silver Tok (Feed)", "🛒 Loja & Quiz", "💬 Chat-Exv & Geek"]
    if is_admin: abas_principais.append("👑 Admin")
    abas_janela = st.tabs(abas_principais)

    # === ABA 1: FEED + GRAVAÇÃO DE VÍDEO + POST DE FOTO ===
    with abas_janela[0]:
        exibir_logo()
        
        menu_postagem = st.tabs(["📸 Postar Imagem / Arte", "🎥 Gravar via Câmera"])
        
        with menu_postagem[0]:
            legenda_foto = st.text_input("Legenda da Imagem:")
            arquivo_img = st.file_uploader("Selecione a Imagem para o Feed:", type=["png", "jpg", "jpeg", "gif", "webp"])
            if st.button("Publicar Imagem no Feed 🚀") and arquivo_img and legenda_foto:
                try:
                    path_b = f"feed/fotos/{uuid.uuid4()}_{arquivo_img.name}"
                    supabase.storage.from_("imagens_chat").upload(path_b, arquivo_img.read())
                    url_f = supabase.storage.from_("imagens_chat").get_public_url(path_b)
                    
                    supabase.table("feed_videos").insert({
                        "titulo": f"[FOTO] {legenda_foto}", "url_video": url_f, "username_autor": u_name,
                        "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0,
                        "id_autor": u_id, "tipo_formato": "horizontal"
                    }).execute()
                    st.success("Imagem publicada!")
                    st.rerun()
                except: pass

        with menu_postagem[1]:
            st.markdown("### 📽️ Capturador de Câmera Integrado")
            if "b64_video_data" not in st.session_state: st.session_state.b64_video_data = ""
            video_injector = st.text_input("Dados Câmera", type="password", value=st.session_state.b64_video_data, label_visibility="collapsed", key="v_inj_v38")
            
            if st.button("Publicar Gravação Realizada ⚡") and video_injector:
                try:
                    dados_video = base64.b64decode(video_injector)
                    nome_arquivo = f"feed/camera/{uuid.uuid4()}.mp4"
                    supabase.storage.from_("videos_feed").upload(nome_arquivo, dados_video)
                    url_publica_video = supabase.storage.from_("videos_feed").get_public_url(nome_arquivo)
                    
        with loja_tabs[1]
            st.header("🎯 Quiz Geek da Comunidade")
            st.write("Acerte as perguntas para faturar 🪙 **100 Silver Coins** por resposta correta!")
            
            categoria_escolhida = st.selectbox("Escolha o Tema do Quiz:", list(PERGUNTAS_QUIZ.keys()), key="sel_cat_quiz_v38")
            
            if "quiz_indice" not in st.session_state: st.session_state.quiz_indice = 0
            if "quiz_corretas" not in st.session_state: st.session_state.quiz_corretas = 0
            
            perguntas_categoria = PERGUNTAS_QUIZ[categoria_escolhida]
            id_pergunta = st.session_state.quiz_indice
            
            if id_pergunta < len(perguntas_categoria):
                item_questao = perguntas_categoria[id_pergunta]
                st.markdown(f"### Pergunta {id_pergunta + 1}:")
                st.write(item_questao["pergunta"])
                
                resposta_usuario = st.radio("Selecione a resposta certa:", item_questao["opcoes"], key=f"quest_opt_{id_pergunta}")
                
                if st.button("Enviar Resposta 🎯", key=f"btn_env_quiz_{id_pergunta}", use_container_width=True):
                    if resposta_usuario == item_questao["correta"]:
                        st.success("🎯 Correto! +100 Silver Coins!")
                        try:
                            novo_saldo_calculado = int(user_atual.get("moedas", 0)) + 100
                            supabase.table("perfis_usuarios").update({"moedas": novo_saldo_calculado}).eq("id", u_id).execute()
                            st.session_state.usuario_logado["moedas"] = novo_saldo_calculado
                        except Exception as e:
                            st.error(f"Erro ao computar premiação no banco: {e}")
                    else:
                        st.error(f"Errado! A resposta correta era: {item_questao['correta']}")
                    
                    st.session_state.quiz_indice += 1
                    st.button("Avançar para Próxima Questão ➡️", key="btn_prox_quiz")
            else:
                st.balloons()
                st.success("🎉 Você completou todo o quiz desta categoria!")
                if st.button("Reiniciar Quiz 🔄", use_container_width=True):
                    st.session_state.quiz_indice = 0
                    st.rerun()

    # === ABA 3: CHAT-EXV (GLOBAL, PRIVADO E SEGUIDORES) & ÁREA GEEK ===
    with abas_janela[2]:
        sub_abas_interacao = st.tabs(["🌐 Chat da Comunidade", "👥 Rede de Amigos", "🍿 Área Geek"])
        
        # 🌐 SUB-ABA 1: BATE-PAPO COM PREVENÇÃO DE ID NULO
        with sub_abas_interacao[0]:
            sala_atual = st.session_state.sala_ativa
            st.markdown(f"#### 🔒 Sala Ativa: `{sala_atual}`")
            
            col_s1, col_s2 = st.columns([3, 1])
            with col_s1:
                nova_sala_input = st.text_input("Trocar de Sala Privada (Código):", value=sala_atual, key="input_mudar_sala_v38").strip().upper()
            with col_s2:
                st.write("##")
                if st.button("Mudar 🔑", use_container_width=True) and nova_sala_input:
                    st.session_state.sala_ativa = nova_sala_input
                    st.rerun()
            
            st.write("---")
            
            with st.expander("📸 Enviar Foto / Mídia no Chat"):
                arquivo_chat_midia = st.file_uploader("Escolha uma imagem ou áudio:", type=["png","jpg","jpeg","gif","mp3","wav","ogg"], key="upload_chat_v38")
                if st.button("Enviar Imagem / Áudio 🚀", use_container_width=True) and arquivo_chat_midia:
                    try:
                        path_midia_chat = f"chat/midias/{uuid.uuid4()}_{arquivo_chat_midia.name}"
                        supabase.storage.from_("imagens_chat").upload(path_midia_chat, arquivo_chat_midia.read())
                        url_midia_gerada = supabase.storage.from_("imagens_chat").get_public_url(path_midia_chat)
                        
                        id_seguro_envio = u_id if (u_id and u_id != "None") else str(user_atual.get("id"))
                        
                        supabase.table("bate-papo_professional").insert({
                            "username": u_name, 
                            "id_usuario": id_seguro_envio, 
                            "mensagem": url_midia_gerada, 
                            "codigo_sala": sala_atual
                        }).execute()
                        st.success("Mídia enviada com sucesso!")
                        st.rerun()
                    except Exception as err_midia:
                        st.error(f"Falha ao subir imagem/áudio: {err_midia}")

            msg_enviar_txt = st.text_input("Escreva sua mensagem:", key="campo_texto_msg_v38")
            if st.button("Enviar Mensagem ✉️", use_container_width=True) and msg_enviar_txt.strip():
                try:
                    id_seguro_envio = u_id if (u_id and u_id != "None") else str(user_atual.get("id"))
                    
                    supabase.table("bate-papo_professional").insert({
                        "username": u_name, 
                        "id_usuario": id_seguro_envio, 
                        "mensagem": msg_enviar_txt.strip(), 
                        "codigo_sala": sala_atual
                    }).execute()
                    st.rerun()
                except Exception as err_txt: 
                    st.error(f"Erro ao salvar mensagem: {err_txt}")
                
            st.write("---")
            
            try:
                mensagens_banco = supabase.table("bate-papo_professional").select("*").eq("codigo_sala", sala_atual).execute()
                if mensagens_banco.data:
                    for m in reversed(mensagens_banco.data[-40:]):
                        info_autor_msg = supabase.table("perfis_usuarios").select("biografia, banner_ativo").eq("username", m.get("username")).execute()
                        cargo_m = "Nenhum"
                        balao_m = "Nenhum"
                        if info_autor_msg.data:
                            cargo_m = info_autor_msg.data[0].get("biografia") or "Nenhum"
                            balao_m = info_autor_msg.data[0].get("banner_ativo") or "Nenhum"
                            
                        selo_remetente = obter_selo_texto(m.get("username"), m.get("id_usuario"), cargo_adicional=cargo_m)
                        renderizar_caixa_mensagem(m.get("username"), m.get("mensagem"), selo_remetente, balao_m, eh_admin=verificar_se_eh_dev(m.get("id_usuario")))
                else:
                    st.caption("Nenhuma mensagem nesta sala ainda. Comece a conversar!")
            except: 
                st.caption("Carregando conversas...")

        # 👥 SUB-ABA 2: SEGUIDORES
        with sub_abas_interacao[1]:
            st.markdown("#### 👥 Sistema de Conexões da Comunidade")
            usuario_para_seguir = st.text_input("Digite o nome exato do usuário para seguir:", key="user_seguir_v38").strip()
            if st.button("Seguir Alvo ➕", use_container_width=True) and usuario_para_seguir:
                try:
                    alvo_busca = supabase.table("perfis_usuarios").select("id").eq("username", usuario_para_seguir).execute()
                    if alvo_busca.data:
                        id_alvo_encontrado = alvo_busca.data[0]["id"]
                        ja_segue = supabase.table("seguidores").select("*").eq("id_seguidor", u_id).eq("id_seguido", id_alvo_encontrado).execute()
                        if not ja_segue.data:
                            supabase.table("seguidores").insert({"id_seguidor": u_id, "id_seguido": id_alvo_encontrado}).execute()
                            st.success(f"Seguindo {usuario_para_seguir}!")
                            st.rerun()
                        else: st.warning("Você já segue este perfil.")
                    else: st.error("Usuário não encontrado.")
                except: pass
            
            st.write("---")
            st.markdown("##### 👥 Quem você está seguindo:")
            try:
                seguindo_dados = supabase.table("seguidores").select("id_seguido").eq("id_seguidor", u_id).execute()
                if seguindo_dados.data:
                    for s in seguindo_dados.data:
                        perfil_seg = supabase.table("perfis_usuarios").select("username, url_foto_perfil, ultimo_visto").eq("id", s["id_seguido"]).execute()
                        if perfil_seg.data:
                            col_l_s1, col_l_s2, col_l_s3 = st.columns([1, 3, 1])
                            with col_l_s1: st.image(perfil_seg.data[0]["url_foto_perfil"] or FOTO_PADRAO, width=40)
                            with col_l_s2: st.markdown(f"**{perfil_seg.data[0]['username']}**")
                            with col_l_s3:
                                if st.button("Remover ❌", key=f"unf_{s['id_seguido']}"):
                                    supabase.table("seguidores").delete().eq("id_seguidor", u_id).eq("id_seguido", s["id_seguido"]).execute()
                                    st.rerun()
                else: st.caption("Você não segue ninguém ainda.")
            except: pass

        # 🍿 SUB-ABA 3: ÁREA GEEK INTEGRADA E COMPLETA
        with sub_abas_interacao[2]:
            st.markdown("### 🍿 Catálogo Geek da Comunidade")
            st.write("Bem-vindo à central de cinema, streaming, doramas e animes!")
            
            pref_salva = user_atual.get("comentarios_internos", "")
            if pref_salva and "Nenhum" not in pref_salva:
                st.markdown(f"🌟 *Baseado nos seus gostos:* **{pref_salva}**")
            
            try:
                geek_dados = supabase.table("feed_videos").select("*").execute()
                if geek_dados.data:
                    for item in reversed(geek_dados.data):
                        if "[GEEK]" in str(item.get("titulo", "")):
                            with st.container(border=True):
                                col_g1, col_g2 = st.columns([1, 4])
                                with col_g1: st.image(item.get("avatar_autor") or FOTO_PADRAO, width=50)
                                with col_g2:
                                    st.markdown(f"### {item.get('titulo').replace('[GEEK] ', '')}")
                                    st.caption(f"Postado por: {item.get('username_autor', 'Sistema')}")
                                st.info(f"{item.get('url_video')}")
                                if st.button(f"❤️ {item.get('curtidas', 0)} Marcar como Assistido", key=f"gk_l_{item.get('id')}"):
                                    supabase.table("feed_videos").update({"curtidas": item.get('curtidas', 0) + 1}).eq("id", item.get("id")).execute()
                                    st.rerun()
            except: pass

    # === ⚙️ ABA 4: PREFERÊNCIAS E REGRAS (TOTALMENTE COMPLETA) ===
    with abas_janela[3]:
        st.header("📋 Diretrizes e Configurações de Preferências")
        
        with st.container(border=True):
            st.subheader("📜 Regras de Utilização do Sistema")
            for regra in REGRAS_SISTEMA:
                st.markdown(f"**{regra}**")
            st.caption("Aviso: A administração monitora o banco de dados contra preconceito e cyberbullying.")
            
        st.write("---")
        
        st.subheader("🎵 Meu Catálogo de Preferências Culturais")
        st.markdown("Escolha seus estilos favoritos. Usuários que selecionarem **K-Pop** receberão um banner temático de brinde no inventário!")
        
        estilo_selecionado = st.selectbox("Selecione seu nicho principal:", ["Nenhum", "K-Pop", "Animes", "Doramas", "Games"], key="sel_estilo_v38")
        grupo_favorito_txt = st.text_input("Qual o nome do seu grupo, cantor ou anime favorito?", key="txt_grupo_fav_v38").strip()
        
        if st.button("Salvar Minhas Preferências e Resgatar Recompensas 🎁", use_container_width=True):
            if estilo_selecionado != "Nenhum" and grupo_favorito_txt:
                try:
                    banner_recompensa = "Nenhum"
                    if estilo_selecionado == "K-Pop":
                        banner_recompensa = "🌸 Banner K-Popper Oficial"
                        st.balloons()
                        st.success("🎉 Parabéns! Você liberou o 'Banner K-Popper Oficial' no seu inventário!")
                    
                    supabase.table("perfis_usuarios").update({
                        "comentarios_internos": f"{estilo_selecionado} ({grupo_favorito_txt})",
                        "banner_ativo": banner_recompensa if banner_recompensa != "Nenhum" else user_atual.get("banner_ativo", "Nenhum")
                    }).eq("id", u_id).execute()
                    
                    st.success("Preferências salvas com sucesso! O feed será otimizado.")
                    st.rerun()
                except:
                    st.error("Falha ao salvar preferências.")
            else:
                st.warning("Preencha todos os campos para registrar.")

    # === 👑 ABA 5: PAINEL ADMIN SECRETO DO DESENVOLVEDOR (RECUPERADA SEM CORTES) ===
    if is_admin:
        with abas_janela[4]:
            st.header("👑 Painel de Gerenciamento do Desenvolvedor (v3.8)")
            st.warning("Atenção Rafael: Estas ferramentas alteram registros diretamente no banco de dados global.")
            
            # 🤖 1. BOT FORMATADOR GEEK
            with st.expander("🤖 Assistente Automatizado - Injetar Conteúdo Geek"):
                st.markdown("Insira os metadados. O sistema irá formatar e postar automaticamente como o Bot Oficial.")
                anime_nome = st.text_input("Nome da Obra Geek (Anime/Dorama):", key="adm_anime_nome")
                anime_eps = st.text_input("Quantidade Total de Episódios:", key="adm_anime_eps")
                anime_idioma = st.selectbox("Idioma Disponível:", ["Legendado", "Dublado PT-BR", "Dual Áudio (Dub/Leg)"], key="adm_anime_lang")
                
                if st.button("Postar Conteúdo Formatado 🎬", use_container_width=True) and anime_nome:
                    try:
                        texto_formatado_geek = f"🎞️ Episódios: {anime_eps} | 🗣️ Idioma: {anime_idioma}"
                        supabase.table("feed_videos").insert({
                            "titulo": f"[GEEK] {anime_nome}", 
                            "url_video": texto_formatado_geek, 
                            "username_autor": "🤖 Bot_Geek_Assist",
                            "avatar_autor": "https://cdn-icons-png.flaticon.com/512/2585/2585164.png", 
                            "curtidas": 0, 
                            "id_autor": str(u_id), 
                            "tipo_formato": "horizontal"
                        }).execute()
                        st.success(f"'{anime_nome}' injetado com sucesso na Área Geek!")
                    except:
                        st.error("Erro na injeção técnica.")

            # 🤖 2. SUPER BOT INJETOR MASSIVO (50 POSTS)
            with st.expander("⚡ Carga Massiva - Disparar Robô (50+ Posts Simultâneos)"):
                st.markdown("Este botão executa um laço que injeta instantaneamente 50 publicações de teste geradas por robôs no feed global.")
                if st.button("Disparar Carga em Lote de 50 Publicações 🔥", use_container_width=True):
                    try:
                        progresso_barra = st.progress(0)
                        for i in range(1, 51):
                            supabase.table("feed_videos").insert({
                                "titulo": f"🤖 Conteúdo Automatizado do Robô Frequência #0{i} para testes de engajamento", 
                                "url_video": "https://www.w3schools.com/html/mov_bbb.mp4",
                                "username_autor": f"🤖 Bot_Frequencia_{i}", 
                                "avatar_autor": FOTO_PADRAO, 
                                "curtidas": i * 3,
                                "id_autor": str(u_id), 
                                "tipo_formato": "horizontal"
                            }).execute()
                            progresso_barra.progress(i * 2)
                        st.success("Sucesso! 50 posts inseridos de uma vez só no feed global.")
                        st.rerun()
                    except:
                        st.error("Erro na execução em lote.")

            # 👑 3. DISTRIBUIDOR DE ITENS E SEGUIDORES
            with st.expander("🎒 Distribuidor de Itens, Cosméticos e Seguidores"):
                st.markdown("Injete cosméticos ou adicione seguidores artificiais na conta de qualquer usuário.")
                user_alvo_painel = st.text_input("Nome de Usuário (Username exato do alvo):", key="adm_user_alvo").strip()
                item_selecionado_dar = st.selectbox("Escolha o Item para Injetar no Inventário:", list(COSMETICOS.keys()), key="adm_item_dar")
                qtd_seguidores_dar = st.number_input("Quantidade de Seguidores Bônus a Injetar:", min_value=0, step=5, value=0, key="adm_seg_dar")
                
                if st.button("Aplicar Alterações de Conta 🛠️", use_container_width=True) and user_alvo_painel:
                    try:
                        busca_alvo_conta = supabase.table("perfis_usuarios").select("id").eq("username", user_alvo_painel).execute()
                        if busca_alvo_conta.data:
                            id_alvo_foco = busca_alvo_conta.data[0]["id"]
                            nome_real_cosmetico = COSMETICOS[item_selecionado_dar]["nome"]
                            supabase.table("perfis_usuarios").update({"banner_ativo": nome_real_cosmetico}).eq("id", id_alvo_foco).execute()
                            
                            if qtd_seguidores_dar > 0:
                                for _ in range(int(qtd_seguidores_dar)):
                                    supabase.table("seguidores").insert({"id_seguidor": str(u_id), "id_seguido": id_alvo_foco}).execute()
                                    
                            st.success(f"Operação concluída! Benefícios injetados no perfil de {user_alvo_painel}.")
                        else:
                            st.error("Usuário alvo não foi encontrado no sistema.")
                    except Exception as e:
                        st.error(f"Erro técnico na operação: {e}")

            # 👑 4. ATRIBUIÇÃO DE CARGOS CUSTOMIZADOS
            with st.expander("🎖️ Atribuidor de Cargos Oficiais do Sistema"):
                st.markdown("Defina ou altere a tag/cargo oficial exibido nos perfis e mensagens.")
                user_cargo_alvo = st.text_input("Username do usuário para receber o Cargo:", key="adm_user_cargo").strip()
                cargo_definir = st.selectbox("Selecione o Cargo Administrativo:", ["Tester", "Best friends of the dev", "Vice-dev", "Divulgadora", "Moderador", "VIP"], key="adm_cargo_select")
                
                if st.button("Conceder Cargo Oficial 🎖️", use_container_width=True) and user_cargo_alvo:
                    try:
                        supabase.table("perfis_usuarios").update({"biografia": cargo_definir}).eq("username", user_cargo_alvo).execute()
                        st.success(f"O cargo '{cargo_definir}' foi atribuído com sucesso para {user_cargo_alvo}!")
                    except:
                        st.error("Erro ao aplicar cargo.")

            # 🔨 5. CONTROLE DE BANIMENTO PERMANENTE
            with st.expander("🟥 Área de Segurança - Banimento Definitivo"):
                st.markdown("Remova o acesso de usuários prejudiciais à comunidade instantaneamente.")
                user_para_banir = st.text_input("Username do infrator (Bloqueio completo):", key="adm_ban_user").strip()
                
                if st.button("APLICAR BANIMENTO PERMANENTE 🟥", use_container_width=True) and user_para_banir:
                    if user_para_banir == "Rafael_oficial":
         
