import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone
import base64

# --- CONFIGURAÇÃO DA PÁGINA & CONEXÃO BANCO DE DADOS ---
st.set_page_config(page_title="Silver Tok v3.8 Ultra Master", page_icon="🎬", layout="centered")

MODO_MANUTENCAO = False  
ID_REAL_DEVELOPER = "04daaa3c-63ef-486c-b33e-54d4e80ee9e9"
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def init_connection():
    try: return create_client(SUPABASE_URL, SUPABASE_KEY)
    except: return None

supabase = init_connection()
if supabase is None:
    st.error("Erro crítico: Não foi possível conectar ao banco de dados Supabase.")
    st.stop()

CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

REGRAS_SISTEMA = [
    "🚫 Estritamente proibido postar conteúdos +18 ou sexualmente explícitos.",
    "❌ Proibido qualquer tipo de discurso de ódio, racismo, bullying ou discriminação.",
    "⚠️ Não exponha informações pessoais ou de saúde de terceiros publicamente.",
    "🔨 O descumprimento de qualquer regra resultará em banimento imediato e permanente por parte da administração."
]

SHIMEJIS_DISPONIVEIS = {
    "Nenhum": "", "Mascote Espadachim (Livro)": "⚔️", "Mago Ancestral (Livro)": "🔮",
    "Raposa de Fogo": "🦊", "Mini Robô": "🤖", "Gatinho Chibi": "🐱"
}

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

CARGOS_CUSTOMIZADOS = {"Lilica": "Tester", "Júlia Guimarães": "Tester", "Rafael_oficial": "DEV"}

VIDEOS_BOT_BOTEY = [
    {"id": "bot_1", "titulo": "⚡ Edit Suprema de Naruto!", "url_video": "https://www.w3schools.com/html/mov_bbb.mp4", "username_autor": "🤖 Bot_Animes", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4213/4213732.png", "curtidas": 142, "tipo_formato": "vertical"},
    {"id": "bot_2", "titulo": "🌌 Relaxing Cinematic View 4K", "url_video": "https://media.w3.org/2010/05/sintel/trailer_hd.mp4", "username_autor": "🤖 Bot_Natureza", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4213/4213732.png", "curtidas": 98, "tipo_formato": "horizontal"}
]

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

# --- FUNÇÕES COMPLEMENTARES DE RENDERIZAÇÃO & LEITURA ---
def obter_status_emoji(timestamp_str):
    if not timestamp_str: return "⚪ Offline"
    try:
        if "T" in timestamp_str:
            timestamp_str = timestamp_str.split("+")[0]
            dt_usuario = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)
        else:
            dt_usuario = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - dt_usuario < timedelta(minutes=3): return "🟢 Online"
    except: pass
    return "⚪ Offline"

def verificar_se_eh_dev(user_id): return str(user_id) == ID_REAL_DEVELOPER

def obter_selo_texto(username_alvo, user_id_alvo=None, cargo_adicional="Nenhum"):
    if username_alvo in CARGOS_CUSTOMIZADOS: return f" 🎖️ {CARGOS_CUSTOMIZADOS[username_alvo]}"
    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial": return " 👑 DEV"
    if cargo_adicional and cargo_adicional != "Nenhum": return f" 🎖️ {cargo_adicional}"
    return ""

def renderizar_foto_com_banner(url_foto, username_alvo, user_id_alvo=None, tamanho=90, banner_equipado="Nenhum", shimeji="Nenhum"):
    if not url_foto: url_foto = FOTO_PADRAO
    shimeji_html = f'<div style="position: absolute; bottom: -5px; right: -5px; font-size: {int(tamanho*0.35)}px; background: white; border-radius: 50%; padding: 2px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); z-index: 12;">{SHIMEJIS_DISPONIVEIS[shimeji]}</div>' if shimeji in SHIMEJIS_DISPONIVEIS and SHIMEJIS_DISPONIVEIS[shimeji] else ""
    
    coroa_html, estilo_css = "", "border-radius: 50%; object-fit: cover; border: 1px solid #ccc;"
    if banner_equipado == "👑 Coroa Suprema DEV" or verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial":
        estilo_css, coroa_html = "border-radius: 50%; object-fit: cover; border: 4px solid #ffd700; box-shadow: 0 0 20px #ffd700;", f'<div style="position: absolute; top: -22px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.38)}px; z-index: 10;">👑</div>'
    elif banner_equipado == "🥉 Bronze Estelar": estilo_css = "border-radius: 50%; object-fit: cover; border: 3px solid #cd7f32;"
    elif banner_equipado == "🥈 Prata Lendária": estilo_css = "border-radius: 50%; object-fit: cover; border: 3px solid #c0c0c0; box-shadow: 0 0 8px #c0c0c0;"
    elif banner_equipado == "🔥 Mestre Otaku (Anime)": estilo_css, coroa_html = "border-radius: 50%; object-fit: cover; border: 3px solid #ff4500; box-shadow: 0 0 12px #ff4500;", f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🦊</div>'
    elif banner_equipado == "🌸 Banner K-Popper Oficial": estilo_css, coroa_html = "border-radius: 50%; object-fit: cover; border: 3px solid #ff69b4; box-shadow: 0 0 12px #ff69b4;", f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🎤</div>'
        
    st.markdown(f'<div style="position: relative; display: inline-block; text-align: center; margin-top: 10px;">{coroa_html}<img src="{url_foto}" width="{tamanho}" height="{tamanho}" style="{estilo_css}">{shimeji_html}</div>', unsafe_allow_html=True)

def renderizar_caixa_mensagem(username, mensagem, selo, estilo_caixa, eh_admin=False):
    if mensagem is None or str(mensagem).lower() == "none": return
    estilo_css = "background-color: #f1f3f4; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #ccc;"
    if eh_admin or estilo_caixa == "👑 Balão Dourado DEV": estilo_css = "background: linear-gradient(135deg, #fff7e6, #ffeaa7); border-left: 5px solid #ffd700; padding: 12px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(255,215,0,0.2);"
    elif estilo_caixa == "🔷 Balão Azul Moderno": estilo_css = "background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
    elif estilo_caixa == "🔮 Balão Neon Cyber": estilo_css = "background-color: #1a1a2e; border: 1px solid #e94560; color: #fff; padding: 10px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 0 10px #e94560;"
        
    conteudo_final = mensagem
    if str(mensagem).startswith("https://"):
        if any(ext in str(mensagem).lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']): conteudo_final = f'<br><img src="{mensagem}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'
        elif any(ext in str(mensagem).lower() for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.webm', '.bin']) or "audio" in str(mensagem).lower(): conteudo_final = f'<br><audio controls style="max-width: 100%; margin-top: 5px;"><source src="{mensagem}"></audio>'
    st.markdown(f'<div style="{estilo_css}"><span style="font-weight: bold; color: #333;">{username}</span> <span style="font-size: 12px; font-weight: bold; color: #d4af37;">{selo}</span>: <span>{conteudo_final}</span></div>', unsafe_allow_html=True)

def exibir_logo(): st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat v3.8 🔐</h1>", unsafe_allow_html=True)

# --- SISTEMA DE LOGIN E CADASTRO ---
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state: st.session_state.sala_ativa = "GERAL"

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
                    if busca.data[0].get("website") == "BANIDO": st.error("Esta conta foi banida permanentemente.")
                    else: st.session_state.usuario_logado = busca.data[0]; st.rerun()
                else: st.error("Usuário ou senha incorretos.")
    with aba_auth[1]:
        cad_user = st.text_input("Escolha um Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie uma Senha:", type="password", key="cad_senha")
        codigo_convite = st.text_input("🔑 Código Secreto:", type="password", key="codigo_convite")
        if st.button("Cadastrar Conta 🎉", key="btn_cad", use_container_width=True):
            if cad_user and cad_senha and codigo_convite == CHAVE_SECRETA:
                try:
                    supabase.table("perfis_usuarios").insert({"username": cad_user, "apelido": cad_user, "senha": cad_senha, "url_foto_perfil": FOTO_PADRAO, "ultimo_visto": datetime.now(timezone.utc).isoformat(), "moedas": 0, "banner_ativo": "Nenhum"}).execute()
                    st.success("Conta criada! Faça login.")
                except: st.error("Nome de usuário indisponível.")
else:
    user_atual = st.session_state.usuario_logado
    u_id = str(user_atual.get("id")) if user_atual.get("id") else "04daaa3c-63ef-486c-b33e-54d4e80ee9e9"
    u_name = user_atual.get("username", "Membro")
    is_admin = verificar_se_eh_dev(u_id) or u_name == "Rafael_oficial"
    u_cargo, u_shimeji = user_atual.get("biografia", "Nenhum"), user_atual.get("localizacao", "Nenhum")

    # --- BARRA LATERAL ---
    with st.sidebar:
        banner_v = user_atual.get("banner_ativo", "Nenhum")
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, u_name, u_id, tamanho=90, banner_equipado=banner_v, shimeji=u_shimeji)
        st.write(f"**{user_atual.get('apelido') or u_name}** {obter_selo_texto(u_name, u_id, cargo_adicional=u_cargo)}")
        st.markdown(f"🪙 **Silver Coins:** {user_atual.get('moedas', 0)}")
        try: st.markdown(f"👥 **Seguidores:** {len(supabase.table('seguidores').select('*').eq('id_seguido', u_id).execute().data)}")
        except: pass

        with st.expander("🦊 Meus Shimejis / Mascotes"):
            escolha_shim = st.selectbox("Escolha seu Acompanhante:", list(SHIMEJIS_DISPONIVEIS.keys()), index=list(SHIMEJIS_DISPONIVEIS.keys()).index(u_shimeji) if u_shimeji in SHIMEJIS_DISPONIVEIS else 0)
            if st.button("Ativar Mascote ✨", use_container_width=True):
                try: supabase.table("perfis_usuarios").update({"localizacao": escolha_shim}).eq("id", u_id).execute(); st.rerun()
                except: pass

        with st.expander("🎒 Meu Inventário"):
            opcoes_inventario = ["Nenhum", "🥉 Bronze Estelar", "🥈 Prata Lendária", "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber", "🔥 Mestre Otaku (Anime)", "🌸 Banner K-Popper Oficial"]
            if is_admin: opcoes_inventario.extend(["👑 Coroa Suprema DEV", "👑 Balão Dourado DEV"])
            escolha_custom = st.selectbox("Selecione para ativar:", opcoes_inventario, index=opcoes_inventario.index(banner_v) if banner_v in opcoes_inventario else 0)
            if st.button("Equipar Cosmético 🛡️", use_container_width=True):
                try: supabase.table("perfis_usuarios").update({"banner_ativo": escolha_custom}).eq("id", u_id).execute(); st.rerun()
                except: pass

    def renderizar_lista_filtrada(lista_posts, identificador_formato):
        for idx, v in enumerate(lista_posts):
            if "[GEEK]" in str(v.get("titulo", "")): continue
            autor, id_autor_post, img_autor, video_url, id_post = v.get('username_autor', 'Membro'), v.get('id_autor') or u_id, v.get('avatar_autor') or FOTO_PADRAO, v.get("url_video", ""), v.get("id")
            chave_comp = f"feed_{identificador_formato}_{idx}_{id_post}"
            st.markdown("---")
            col_f1, col_f2 = st.columns([1, 5], vertical_alignment="bottom")
            with col_f1: renderizar_foto_com_banner(img_autor, autor, id_autor_post, tamanho=50)
            with col_f2: st.markdown(f"**{autor}** {obter_selo_texto(autor, id_autor_post)}"); st.caption(v.get("titulo", ""))
            if v.get("tipo_formato") == "vertical": st.markdown(f'<div style="display: flex; justify-content: center;"><video width="290" height="515" controls><source src="{video_url}" type="video/mp4"></video></div>', unsafe_allow_html=True)
            else:
                if "[FOTO]" in str(v.get("titulo", "")): st.image(video_url, use_container_width=True)
                elif video_url: st.video(video_url)
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
    abas_principais = ["📺 Silver Tok (Feed)", "🛒 Loja & Quiz", "💬 Chat-Exv & Geek", "📋 Preferências"]
    if is_admin: abas_principais.append("👑 Admin")
    abas_janela = st.tabs(abas_principais)

    # === ABA 1: FEED + ENVIOS ===
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
                    supabase.table("feed_videos").insert({"titulo": f"[FOTO] {legenda_foto}", "url_video": supabase.storage.from_("imagens_chat").get_public_url(path_b), "username_autor": u_name, "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0, "id_autor": u_id, "tipo_formato": "horizontal"}).execute()
                    st.success("Imagem publicada!"); st.rerun()
                except: pass
        with menu_postagem[1]:
            st.markdown("### 📽️ Capturador de Câmera Integrado")
            if "b64_video_data" not in st.session_state: st.session_state.b64_video_data = ""
            video_injector = st.text_input("Dados Câmera", type="password", value=st.session_state.b64_video_data, label_visibility="collapsed", key="v_inj_v38")
            if st.button("Publicar Gravação Realizada ⚡") and video_injector:
                try:
                    dados_video = base64.b64decode(video_injector); nome_arquivo = f"feed/camera/{uuid.uuid4()}.mp4"
                    supabase.storage.from_("videos_feed").upload(nome_arquivo, dados_video)
                    supabase.table("feed_videos").insert({"titulo": f"[GRAVADO AO VIVO] Clip de {u_name}", "url_video": supabase.storage.from_("videos_feed").get_public_url(nome_arquivo), "username_autor": u_name, "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0, "id_autor": u_id, "tipo_formato": "vertical"}).execute()
                    st.session_state.b64_video_data = ""; st.success("Vídeo gravado publicado!"); st.rerun()
                except Exception as e: st.error(f"Erro no upload: {e}")
            
            st.components.v1.html("""
            <div style="display: flex; gap: 10px; justify-content: center; padding: 5px 0;">
                <video id="preview" width="200" height="150" autoplay muted style="border:1px solid #ccc; background:#000; border-radius:8px;"></video>
                <div style="display:flex; flex-direction:column; justify-content:center; gap:5px;">
                    <button id="startVidBtn" style="background-color: #24a0ed; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer;">🎥 Abrir Câmera</button>
                    <button id="stopVidBtn" style="background-color: #ff4b4b; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; display: none;">⏹️ Salvar</button>
                </div>
            </div>
            <script>
            let recorder; let chunks = []; let stream;
            const preview = document.getElementById('preview');
            const startVidBtn = document.getElementById('startVidBtn');
            const stopVidBtn = document.getElementById('stopVidBtn');
            startVidBtn.onclick = async () => {
                chunks = []; stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                preview.srcObject = stream; recorder = new MediaRecorder(stream);
                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'video/mp4' });
                    const r = new FileReader(); r.readAsDataURL(blob);
                    r.onloadend = () => {
                        const inputs = window.parent.document.querySelectorAll('input[type="password"]');
                        if(inputs.length > 1) { inputs[1].value = r.result.split(',')[1]; inputs[1].dispatchEvent(new Event('input', { bubbles: true })); }
                    };
                };
                recorder.start(); startVidBtn.style.display = 'none'; stopVidBtn.style.display = 'block';
            };
            stopVidBtn.onclick = () => { recorder.stop(); stream.getTracks().forEach(t => t.stop()); startVidBtn.style.display = 'block'; stopVidBtn.style.display = 'none'; };
            </script>
            """, height=180)
        try: renderizar_lista_filtrada(reversed((supabase.table("feed_videos").select("*").execute().data or []) + VIDEOS_BOT_BOTEY), "global")
        except: pass

    # === ABA 2: LOJA & QUIZ ===
    with abas_janela[1]:
        loja_tabs = st.tabs(["🛒 Comprar Itens", "🎯 Responder Quiz"])
        with loja_tabs[0]:
            st.header("🛒 Loja de Customizações")
            saldo_atual = user_atual.get("moedas", 0)
            st.info(f"Seu saldo: 🪙 {saldo_atual} Silver Coins")
            col_l1, col_l2 = st.columns(2)
            for idx, (chave, info) in enumerate(COSMETICOS.items()):
                with (col_l1 if idx % 2 == 0 else col_l2):
                    with st.container(border=True):
                        if info.get("img"): st.image(info["img"], width=50)
                        st.markdown(f"### {info['nome']}"); st.write(f"Preço: 🪙 {info['preco']} Coins")
                        if saldo_atual >= info['preco']:
                            if st.button("Comprar", key=f"loja_b_{chave}", use_container_width=True):
                                try: supabase.table("perfis_usuarios").update({"moedas": int(saldo_atual) - int(info['preco'])}).eq("id", u_id).execute(); st.rerun()
                                except: pass
                        else: st.button("Saldo Insuficiente", key=f"insuf_{chave}", disabled=True, use_container_width=True)
        with loja_tabs[1]:
            st.header("🎯 Quiz Geek")
            categoria_escolhida = st.selectbox("Tema do Quiz:", list(PERGUNTAS_QUIZ.keys()))
            if "quiz_indice" not in st.session_state: st.session_state.quiz_indice = 0
            preg_cat = PERGUNTAS_QUIZ[categoria_escolhida]
            id_p = st.session_state.quiz_indice
            if id_p < len(preg_cat):
                st.write(preg_cat[id_p]["pergunta"])
                resp_u = st.radio("Selecione:", preg_cat[id_p]["opcoes"], key=f"q_{id_p}")
                if st.button("Enviar Resposta 🎯", use_container_width=True):
                    if resp_u == preg_cat[id_p]["correta"]:
                        st.success("Correto! +100 Silver Coins")
                        try:
                            nsaldo = int(user_atual.get("moedas", 0)) + 100
                            supabase.table("perfis_usuarios").update({"moedas": nsaldo}).eq("id", u_id).execute()
                            st.session_state.usuario_logado["moedas"] = nsaldo
                        except: pass
                    else: st.error(f"Incorreto. Resposta certa: {preg_cat[id_p]['correta']}")
                    st.session_state.quiz_indice += 1; st.button("Próxima ➡️")
            else:
                st.balloons(); st.success("Quiz finalizado!")
                if st.button("Reiniciar Quiz 🔄"): st.session_state.quiz_indice = 0; st.rerun()

    # === ABA 3: CHAT & GEEK ===
    with abas_janela[2]:
        sub_abas_interacao = st.tabs(["🌐 Chat", "👥 Seguidores", "🍿 Área Geek"])
        with sub_abas_interacao[0]:
            sala_atual = st.session_state.sala_ativa
            st.markdown(f"#### 🔒 Sala: `{sala_atual}`")
            col_s1, col_s2 = st.columns([3, 1], vertical_alignment="bottom")
            with col_s1: nova_sala_input = st.text_input("Mudar Sala Secreta:", value=sala_atual).strip().upper()
            with col_s2:
                if st.button("Mudar 🔑", use_container_width=True) and nova_sala_input: st.session_state.sala_ativa = nova_sala_input; st.rerun()
            
            with st.expander("📸 Enviar Imagem / Áudio"):
                arq_chat = st.file_uploader("Arquivo:", type=["png","jpg","jpeg","gif","mp3","wav","ogg"])
                if st.button("Enviar Arquivo 🚀", use_container_width=True) and arq_chat:
                    try:
                        p_chat = f"chat/midias/{uuid.uuid4()}_{arq_chat.name}"
                        supabase.storage.from_("imagens_chat").upload(p_chat, arq_chat.read())
                        supabase.table("bate-papo_professional").insert({"username": u_name, "id_usuario": u_id, "mensagem": supabase.storage.from_("imagens_chat").get_public_url(p_chat), "codigo_sala": sala_atual}).execute()
                        st.rerun()
                    except: pass

            msg_txt = st.text_input("Mensagem:", key="msg_t")
            if st.button("Enviar Mensagem ✉️", use_container_width=True) and msg_txt.strip():
                try: supabase.table("bate-papo_professional").insert({"username": u_name, "id_usuario": u_id, "mensagem": msg_txt.strip(), "codigo_sala": sala_atual}).execute(); st.rerun()
                except: pass
            
            try:
                for m in reversed(supabase.table("bate-papo_professional").select("*").eq("codigo_sala", sala_atual).execute().data[-40:]):
                    inf_a = supabase.table("perfis_usuarios").select("biografia, banner_ativo").eq("username", m.get("username")).execute()
                    c_m, b_m = (inf_a.data[0].get("biografia", "Nenhum"), inf_a.data[0].get("banner_ativo", "Nenhum")) if inf_a.data else ("Nenhum", "Nenhum")
                    renderizar_caixa_mensagem(m.get("username"), m.get("mensagem"), obter_selo_texto(m.get("username"), m.get("id_usuario"), cargo_adicional=c_m), b_m, eh_admin=verificar_se_eh_dev(m.get("id_usuario")))
            except: pass

        with sub_abas_interacao[1]:
            st.markdown("#### Conexões")
            u_seg = st.text_input("Username para seguir:").strip()
            if st.button("Seguir Alvo ➕") and u_seg:
                try:
                    alvo = supabase.table("perfis_usuarios").select("id").eq("username", u_seg).execute()
                    if alvo.data and not supabase.table("seguidores").select("*").eq("id_seguidor", u_id).eq("id_seguido", alvo.data[0]["id"]).execute().data:
                        supabase.table("seguidores").insert({"id_seguidor": u_id, "id_seguido": alvo.data[0]["id"]}).execute()
                        st.success("Seguindo!"); st.rerun()
                except: pass
            try:
                for s in supabase.table("seguidores").select("id_seguido").eq("id_seguidor", u_id).execute().data:
                    p_s = supabase.table("perfis_usuarios").select("username, url_foto_perfil").eq("id", s["id_seguido"]).execute()
                    if p_s.data:
                        c1, c2, c3 = st.columns([1, 3, 1], vertical_alignment="bottom")
                        with c1: st.image(p_s.data[0]["url_foto_perfil"] or FOTO_PADRAO, width=40)
                        with c2: st.markdown(f"**{p_s.data[0]['username']}**")
                        with c3:
                            if st.button("Deixar ❌", key=f"unf_{s['id_seguido']}"): supabase.table("seguidores").delete().eq("id_seguidor", u_id).eq("id_seguido", s["id_seguido"]).execute(); st.rerun()
            except: pass

        with sub_abas_interacao[2]:
            st.markdown("### 🍿 Catálogo Geek")
            pref_salva = user_atual.get("comentarios_internos", "")
            if pref_salva and "Nenhum" not in pref_salva: st.markdown(f"🌟 *Sugestões baseadas no seu nicho:* **{pref_salva}**")
            try:
                for item in reversed(supabase.table("feed_videos").select("*").execute().data):
                    if "[GEEK]" in str(item.get("titulo", "")):
                        with st.container(border=True):
                            c_g1, c_g2 = st.columns([1, 4], vertical_alignment="bottom")
                            with c_g1: st.image(item.get("avatar_autor") or FOTO_PADRAO, width=50)
                            with c_g2: st.markdown(f"### {item.get('titulo').replace('[GEEK] ', '')}"); st.caption(f"Por: {item.get('username_autor')}")
                            st.info(item.get('url_video'))
                            if st.button(f"❤️ {item.get('curtidas', 0)} Assistido", key=f"gk_{item.get('id')}"):
                                supabase.table("feed_videos").update({"curtidas": item.get('curtidas', 0) + 1}).eq("id", item.get("id")).execute(); st.rerun()
            except: pass

    # === ABA 4: PREFERÊNCIAS ===
    with abas_janela[3]:
        st.header("📋 Configurações e Regras")
        with st.container(border=True):
            st.subheader("📜 Regras do Sistema")
            for r in REGRAS_SISTEMA: st.markdown(f"**{r}**")
        st.write("---")
        st.subheader("🎵 Preferências Culturais")
        estilo_sel = st.selectbox("Nicho principal:", ["Nenhum", "K-Pop", "Animes", "Doramas", "Games"])
        g_fav = st.text_input("Favorito (Grupo/Anime/Cantor):").strip()
        if st.button("Salvar e Resgatar Recompensas 🎁", use_container_width=True):
            if estilo_sel != "Nenhum" and g_fav:
                try:
                    b_rec = "🌸 Banner K-Popper Oficial" if estilo_sel == "K-Pop" else user_atual.get("banner_ativo", "Nenhum")
                    if estilo_sel == "K-Pop": st.balloons()
                    supabase.table("perfis_usuarios").update({"comentarios_internos": f"{estilo_sel} ({g_fav})", "banner_ativo": b_rec}).eq("id", u_id).execute()
                    st.success("Preferências salvas!"); st.rerun()
                except: pass

    # === ABA 5: PAINEL ADMIN ===
    if is_admin:
        with abas_janela[4]:
            st.header("👑 Painel do Desenvolvedor")
            
            # 1. BOT GEEK
            with st.expander("🤖 Injetar Conteúdo Geek"):
                a_n = st.text_input("Nome da Obra:")
                a_e = st.text_input("Episódios:")
                a_i = st.selectbox("Idioma:", ["Legendado", "Dublado PT-BR", "Dual Áudio"])
                if st.button("Postar Geek 🎬", use_container_width=True) and a_n:
                    try: supabase.table("feed_videos").insert({"titulo": f"[GEEK] {a_n}", "url_video": f"🎞️ Episódios: {a_e} | 🗣️ Idioma: {a_i}", "username_autor": "🤖 Bot_Geek_Assist", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/2585/2585164.png", "curtidas": 0, "id_autor": str(u_id), "tipo_formato": "horizontal"}).execute(); st.success("Injetado!")
                    except: pass

            # 2. INJETOR MASSIVO 50 POSTS
            with st.expander("⚡ Carga Massiva (50 Posts)"):
                if st.button("Disparar 50 Publicações 🔥", use_container_width=True):
                    try:
                        bar = st.progress(0)
                        for i in range(1, 51):
                            supabase.table("feed_videos").insert({"titulo": f"🤖 Post Automático de Teste #{i}", "url_video": "https://www.w3schools.com/html/mov_bbb.mp4", "username_autor": f"🤖 Bot_{i}", "avatar_autor": FOTO_PADRAO, "curtidas": i, "id_autor": str(u_id), "tipo_formato": "horizontal"}).execute()
                            bar.progress(i * 2)
                        st.success("Concluído!"); st.rerun()
                    except: pass

            # 3. DISTRIBUIDOR DE ITENS E SEGUIDORES
            with st.expander("🎒 Dar Itens e Seguidores"):
                alv_p = st.text_input("Username do Alvo:").strip()
                itm_p = st.selectbox("Item:", list(COSMETICOS.keys()))
                seg_p = st.number_input("Seguidores Bônus:", min_value=0, step=5)
                if st.button("Aplicar Benefícios 🛠️", use_container_width=True) and alv_p:
                    try:
                        b_alv = supabase.table("perfis_usuarios").select("id").eq("username", alv_p).execute()
                        if b_alv.data:
                            supabase.table("perfis_usuarios").update({"banner_ativo": COSMETICOS[itm_p]["nome"]}).eq("id", b_alv.data[0]["id"]).execute()
                            for _ in range(int(seg_p)): supabase.table("seguidores").insert({"id_seguidor": str(u_id), "id_seguido": b_alv.data[0]["id"]}).execute()
                            st.success("Aplicado!")
                    except: pass

            # 4. CARGOS OFICIAIS
            with st.expander("🎖️ Atribuir Cargos Oficiais"):
                u_car = st.text_input("Username para Cargo:").strip()
                c_def = st.selectbox("Cargo:", ["Tester", "Best friends of the dev", "Vice-dev", "Divulgadora", "Moderador", "VIP"])
                if st.button("Conceder Cargo 🎖️", use_container_width=True) and u_car:
                    try: supabase.table("perfis_usuarios").update({"biografia": c_def}).eq("username", u_car).execute(); st.success("Cargo Atualizado!")
                    except: pass

            # 5. BANIMENTO DEFINITIVO
            with st.expander("🟥 Banimento Permanente"):
                u_ban = st.text_input("Username do Infrator:").strip()
                if st.button("BANIR USUÁRIO PERMANENTEMENTE 🟥", use_container_width=True) and u_ban:
                    if u_ban == "Rafael_oficial": st.error("Impossível banir o DEV principal.")
                    else:
                        try: supabase.table("perfis_usuarios").update({"website": "BANIDO"}).eq("username", u_ban).execute(); st.error("Usuário Banido!")
                        except: pass

    try: supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", u_id).execute()
    except: pass
          
