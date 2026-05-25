import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v3.2 Master", page_icon="🎬", layout="centered")

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

# --- CONFIGURAÇÕES DE SEGURANÇA E CONSTANTES ---
CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
ID_REAL_DEVELOPER = "04daaa3c-63ef-486c-b33e-54d4e80ee9e9"

COSMETICOS = {
    "bronze": {"nome": "🥉 Bronze Estelar", "preco": 150, "img": "https://cdn-icons-png.flaticon.com/512/5243/5243422.png"},
    "prata": {"nome": "🥈 Prata Lendária", "preco": 300, "img": "https://cdn-icons-png.flaticon.com/512/5243/5243444.png"},
    "caixa_azul": {"nome": "🔷 Balão Azul Moderno", "preco": 100, "img": "https://cdn-icons-png.flaticon.com/512/2460/2460884.png"},
    "caixa_neon": {"nome": "🔮 Balão Neon Cyber", "preco": 250, "img": "https://cdn-icons-png.flaticon.com/512/2037/2037041.png"}
}

VIDEOS_BOT_BOTEY = [
    {"id": "bot_1", "titulo": "⚡ Edit Suprema de Naruto!", "url_video": "https://www.w3schools.com/html/mov_bbb.mp4", "username_autor": "🤖 Bot_Animes", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4213/4213732.png", "curtidas": 142, "tipo_formato": "vertical"},
    {"id": "bot_2", "titulo": "🌌 Relaxing Cinematic View 4K", "url_video": "https://media.w3.org/2010/05/sintel/trailer_hd.mp4", "username_autor": "🤖 Bot_Natureza", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4213/4213732.png", "curtidas": 98, "tipo_formato": "horizontal"}
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
        if datetime.now(timezone.utc) - dt_usuario < timedelta(minutes=3):
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
            id_u = dados.data[0].get("id")
            if id_u:
                res_seg = supabase.table("seguidores").select("*", count="exact").eq("id_seguido", id_u).execute()
                total = res_seg.count if (hasattr(res_seg, "count") and res_seg.count is not None) else len(res_seg.data)
                if total >= 1000: return " ✔️"
    except: pass
    return ""

def renderizar_foto_com_banner(url_foto, username_alvo, user_id_alvo=None, tamanho=90, banner_equipado="Nenhum"):
    if not url_foto: url_foto = FOTO_PADRAO
    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial" or banner_equipado == "👑 Coroa Suprema DEV":
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
        
    st.markdown(f"""
    <div style="position: relative; display: inline-block; text-align: center; margin-top: 10px;">
        {coroa_html}
        <img src="{url_foto}" width="{tamanho}" height="{tamanho}" style="{estilo_css}">
    </div>
    """, unsafe_allow_html=True)

def renderizar_caixa_mensagem(username, mensagem, selo, estilo_caixa, eh_admin=False):
    if eh_admin or estilo_caixa == "👑 Balão Dourado DEV":
        estilo_css = "background: linear-gradient(135deg, #fff7e6, #ffeaa7); border-left: 5px solid #ffd700; padding: 12px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(255,215,0,0.2);"
    elif estilo_caixa == "🔷 Balão Azul Moderno":
        estilo_css = "background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
    elif estilo_caixa == "🔮 Balão Neon Cyber":
        estilo_css = "background-color: #1a1a2e; border: 1px solid #e94560; color: #fff; padding: 10px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 0 10px #e94560;"
    else:
        estilo_css = "background-color: #f1f3f4; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
        
    conteudo_mensagem = mensagem
    if "https://" in str(mensagem):
        if any(ext in str(mensagem).lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']) or "/imagens_chat" in str(mensagem):
            conteudo_mensagem = f'<br><img src="{mensagem}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'
        elif any(ext in str(mensagem).lower() for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.webm']) or "/audios_chat" in str(mensagem):
            conteudo_mensagem = f'<br><audio controls style="max-width: 100%; margin-top: 5px;"><source src="{mensagem}"></audio>'

    st.markdown(f"""
    <div style="{estilo_css}">
        <span style="font-weight: bold; color: {'#d4af37' if (eh_admin or estilo_caixa == '👑 Balão Dourado DEV') else '#333'};">{username}</span> 
        <span style="font-size: 12px; font-weight: bold;">{selo}</span>: 
        <span style="color: {'#111' if estilo_caixa != '🔮 Balão Neon Cyber' else '#fff'};">{conteudo_mensagem}</span>
    </div>
    """, unsafe_allow_html=True)

# --- ESTADOS DO STREAMLIT ---
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state: st.session_state.sala_ativa = None
if "perfil_visitado" not in st.session_state: st.session_state.perfil_visitado = None

# --- FLUXO AUTENTICAÇÃO ---
if st.session_state.usuario_logado is None:
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)
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
                    st.error("Este nome de usuário é reservado.")
                    st.stop()
                try:
                    supabase.table("perfis_usuarios").insert({
                        "username": cad_user, "apelido": cad_user, "senha": cad_senha, 
                        "url_foto_perfil": FOTO_PADRAO, "ultimo_visto": datetime.now(timezone.utc).isoformat(),
                        "moedas": 0, "banner_ativo": "Nenhum"
                    }).execute()
                    st.success("Conta criada! Faça login.")
                except: st.error("Nome de usuário indisponível.")
else:
    try:
        atualizar_dados = supabase.table("perfis_usuarios").select("*").eq("id", st.session_state.usuario_logado.get("id")).execute()
        if atualizar_dados.data: st.session_state.usuario_logado = atualizar_dados.data[0]
    except: pass

    user_atual = st.session_state.usuario_logado
    u_id = user_atual.get("id", "")
    u_name = user_atual.get("username", "Membro")
    is_admin = verificar_se_eh_dev(u_id)

    try:
        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", u_id).execute()
    except: pass

    total_notif = 0
    try:
        res_n = supabase.table("notificacoes").select("*", count="exact").eq("id_destinatario", u_id).eq("lida", False).execute()
        total_notif = res_n.count if (hasattr(res_n, "count") and res_n.count is not None) else len(res_n.data)
    except: pass

    # --- SIDEBAR COMPLETA ---
    with st.sidebar:
        banner_v = user_atual.get("banner_ativo", "Nenhum")
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, u_name, u_id, tamanho=90, banner_equipado=banner_v)
        st.write(f"**{user_atual.get('apelido') or u_name}** {obter_selo_texto(u_name, u_id)}")
        st.markdown(f"🪙 **Saldo:** {user_atual.get('moedas', 0)} Moedas")
        
        with st.expander("🎒 Meu Inventário"):
            st.write(f"**Ativo no momento:** {banner_v}")
            opcoes_inventario = ["Nenhum", "🥉 Bronze Estelar", "🥈 Prata Lendária", "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber"]
            if is_admin:
                opcoes_inventario.insert(1, "👑 Coroa Suprema DEV")
                opcoes_inventario.insert(2, "👑 Balão Dourado DEV")
            escolha_custom = st.selectbox("Selecione para ativar:", opcoes_inventario)
            if st.button("Equipar Cosmético 🛡️"):
                try:
                    supabase.table("perfis_usuarios").update({"banner_ativo": escolha_custom}).eq("id", u_id).execute()
                    st.success("Item equipado com sucesso!")
                    st.rerun()
                except: st.error("Falha ao equipar.")

        st.markdown("---")
        if st.button("Sair da Conta 🚪", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.sala_ativa = None
            st.rerun()

    # --- ABA DE NAVEGAÇÃO PRINCIPAL ---
    aba_feed, aba_loja, aba_chat, aba_status, aba_notif = st.tabs([
        "📺 Silver Tok (Feed)", "🛒 Loja & Caixas", "💬 Chat-Exv", "✨ Status", f"🔔 Notificações ({total_notif})"
    ])

    # === 📺 ABA 1: SILVER TOK (FEED REAL) ===
    with aba_feed:
        st.markdown("### 📺 Silver Tok Global")
        with st.expander("➕ Publicar Novo Conteúdo"):
            t_pub = st.text_input("Legenda do post:", key="leg_feed_nova")
            f_midia = st.file_uploader("Escolha um Vídeo ou Imagem:", type=["mp4", "png", "jpg", "jpeg"])
            fmt = st.selectbox("Formato do Post:", ["Horizontal / Padrão", "Vertical / Shorts"])
            fmt_db = "vertical" if "Vertical" in fmt else "horizontal"
            
            if st.button("Publicar no Feed 🚀") and f_midia and t_pub:
                bucket = "videos_feed" if fmt_db == "vertical" or f_midia.name.endswith(".mp4") else "imagens_chat"
                path_b = f"feed/{uuid.uuid4()}_{f_midia.name}"
                try:
                    supabase.storage.from_(bucket).upload(path_b, f_midia.read())
                    url_f = supabase.storage.from_(bucket).get_public_url(path_b)
                    
                    supabase.table("feed_videos").insert({
                        "titulo": t_pub, "url_video": url_f, "username_autor": u_name,
                        "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0,
                        "id_autor": u_id, "tipo_formato": fmt_db
                    }).execute()
                    st.success("Conteúdo publicado com sucesso!")
                    st.rerun()
                except Exception as e: st.error(f"Erro no envio: {e}")

        # Carregar posts em tempo real do banco de dados
        try:
            f_dados = supabase.table("feed_videos").select("*").execute()
            todos_posts = (f_dados.data or []) + VIDEOS_BOT_BOTEY
            for idx, post in enumerate(reversed(todos_posts)):
                if str(post.get("titulo", "")).startswith("[STATUS]"): continue
                st.markdown("---")
                col_p1, col_p2 = st.columns([1, 5])
                with col_p1:
                    renderizar_foto_com_banner(post.get("avatar_autor") or FOTO_PADRAO, post.get("username_autor"), post.get("id_autor"), tamanho=50)
                with col_p2:
                    st.markdown(f"**{post.get('username_autor')}** {obter_selo_texto(post.get('username_autor'), post.get('id_autor'))}")
                    st.caption(post.get("titulo", ""))
                
                v_url = post.get("url_video", "")
                if post.get("tipo_formato") == "vertical":
                    st.markdown(f'<div style="text-align:center;"><video width="280" height="490" controls><source src="{v_url}" type="video/mp4"></video></div>', unsafe_allow_html=True)
                else:
                    if any(ext in str(v_url).lower() for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                        st.image(v_url, use_container_width=True)
                    elif v_url: st.video(v_url)
        except: st.info("Nenhum post disponível no feed no momento.")

    # === 🛒 ABA 2: LOJA PREMIUM (REAL) ===
    with aba_loja:
        st.header("🛒 Loja de Cosméticos")
        col_l1, col_l2 = st.columns(2)
        for idx, (chave, info) in enumerate(COSMETICOS.items()):
            coluna_foco = col_l1 if idx % 2 == 0 else col_l2
            with coluna_foco:
                st.markdown(f"""
                <div style="background-color:#fafafa; padding:12px; border-radius:8px; border:1px solid #eee; text-align:center;">
                    <img src="{info['img']}" width="50"><br>
                    <strong>{info['nome']}</strong><br>
                    Saldo necessário: 🪙 {info['preco']} moedas
                </div>
                """, unsafe_allow_html=True)
                if user_atual.get("moedas", 0) >= info['preco']:
                    if st.button(f"Adquirir {info['nome']}", key=f"loja_b_{chave}", use_container_width=True):
                        try:
                            supabase.table("perfis_usuarios").update({"moedas": user_atual["moedas"] - info['preco']}).eq("id", u_id).execute()
                            st.success("Adquirido!")
                            st.rerun()
                        except: st.error("Erro na transação.")
                else:
                    st.button("Saldo Insuficiente", key=f"inv_{chave}", disabled=True, use_container_width=True)

    # === 💬 ABA 3: CHAT-EXV (GRAVAÇÃO E ENVIO DIRETO SEM PASSOS EXTRAS) ===
    with aba_chat:
        if st.session_state.sala_ativa:
            st.subheader(f"Sala: {st.session_state.sala_ativa}")
            if st.button("⬅️ Voltar para a Lista de Salas"):
                st.session_state.sala_ativa = None
                st.rerun()

            # GRAVADOR DE ÁUDIO DE UM CLIQUE INTEGRADO
            st.markdown("### 🎙️ Enviar Áudio Gravado")
            
            # Novo script de gravação direta: grava o áudio e ejeta direto para o processamento do Streamlit
            gravador_completo_html = """
            <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; text-align: center;">
                <button id="startRec" style="background-color: #2e7d32; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; cursor: pointer;">🎙️ Iniciar Gravação</button>
                <button id="stopRec" style="background-color: #d32f2f; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; cursor: pointer; display: none; margin-left: 8px;">⏹️ Parar e Enviar</button>
                <div id="statusTxt" style="margin-top: 8px; font-size: 13px; color: #666;">Clique para começar a falar...</div>
            </div>
            <script>
            let chunks = [];
            let recorder;
            const startBtn = document.getElementById('startRec');
            const stopBtn = document.getElementById('stopRec');
            const statusTxt = document.getElementById('statusTxt');

            startBtn.onclick = async () => {
                chunks = [];
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                recorder = new MediaRecorder(stream);
                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'audio/mp3' });
                    const reader = new FileReader();
                    reader.readAsDataURL(blob);
                    reader.onloadend = () => {
                        window.parent.postMessage({ type: 'ENVIO_AUDIO_DIRETO', data: reader.result }, '*');
                    };
                    statusTxt.innerText = "Processando arquivo de áudio...";
                };
                recorder.start();
                startBtn.style.display = 'none';
                stopBtn.style.display = 'inline-block';
                statusTxt.innerText = "🔴 Gravando áudio do dispositivo...";
            };

            stopBtn.onclick = () => {
                recorder.stop();
                startBtn.style.display = 'inline-block';
                stopBtn.style.display = 'none';
                statusTxt.innerText = "Enviado com sucesso!";
            };
            </script>
            """
            st.components.v1.html(gravador_completo_html, height=110)

            # Input tradicional alternativo
            m_txt = st.text_input("Mensagem de texto complementar:", placeholder="Ou digite sua mensagem aqui...")
            img_f = st.file_uploader("Enviar uma Foto 📸", type=["png", "jpg", "jpeg", "gif"])
            
            if st.button("Enviar Mensagem ✉️", use_container_width=True):
                url_banco = None
                if img_f:
                    p_b = f"chat/fotos/{uuid.uuid4()}_{img_f.name}"
                    supabase.storage.from_("imagens_chat").upload(p_b, img_f.read())
                    url_banco = supabase.storage.from_("imagens_chat").get_public_url(p_b)
                elif m_txt.strip():
                    url_banco = m_txt.strip()

                if url_banco:
                    supabase.table("bate-papo_profissional").insert({
                        "username": u_name, "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                        "mensagem": url_banco, "codigo_sala": st.session_state.sala_ativa
                    }).execute()
                    st.rerun()

            # Renderização das mensagens enviadas
            try:
                m_dados = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", st.session_state.sala_ativa).execute()
                for m in reversed(m_dados.data[-35:]):
                    col_m1, col_m2 = st.columns([1, 6])
                    with col_m1:
                        renderizar_foto_com_banner(m.get("url_foto_perfil") or FOTO_PADRAO, m.get("username"), tamanho=40)
                    with col_m2:
                        renderizar_caixa_mensagem(m.get("username"), m.get("mensagem"), obter_selo_texto(m.get("username")), "Nenhum")
            except: pass
        else:
            t_chat = st.tabs(["💬 Privado", "👥 Grupos", "👥 Membros da Rede"])
            with t_chat[0]:
                alvo = st.text_input("Username do amigo:").strip()
                if st.button("Abrir Chat Privado") and alvo:
                    lista = sorted([u_name.upper(), alvo.upper()])
                    st.session_state.sala_ativa = f"PRIV-{lista[0]}-{lista[1]}"
                    st.rerun()
            with t_chat[1]:
                g_nome = st.text_input("Nome do Grupo:").strip().upper()
                if st.button("Entrar no Canal 🔐") and g_nome:
                    st.session_state.sala_ativa = g_nome
                    st.rerun()
            with t_chat[2]:
                try:
                    u_todos = supabase.table("perfis_usuarios").select("*").execute()
                    for u in u_todos.data:
                        if u.get("username") != u_name:
                            st.write(f"• **{u.get('username')}** ({obter_status_emoji(u.get('ultimo_visto'))})")
                except: pass

    # === ✨ ABA 4: STATUS TEMPORÁRIOS ===
    with aba_status:
        st.header("✨ Status do Dia")
        txt_st = st.text_input("Como está o seu dia hoje?")
        if st.button("Atualizar Meu Status") and txt_st.strip():
            try:
                supabase.table("feed_videos").insert({
                    "titulo": f"[STATUS] {txt_st.strip()}", "url_video": "", "username_autor": u_name,
                    "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0, "id_autor": u_id, "tipo_formato": "horizontal"
                }).execute()
                st.success("Status postado!")
                st.rerun()
            except: pass

    # === 🔔 ABA 5: NOTIFICAÇÕES (CONECTADA) ===
    with aba_notif:
        st.header("🔔 Suas Notificações")
        try:
            dados_n = supabase.table("notificacoes").select("*").eq("id_destinatario", u_id).execute()
            if dados_n.data:
                for n in reversed(dados_n.data):
                    st.markdown(f"• {n.get('mensagem')}")
            else: st.info("Tudo limpo por aqui!")
        except: st.info("Sem notificações recentes.")
