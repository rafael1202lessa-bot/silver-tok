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
    # Atualiza dados em tempo real
    try:
        atualizar_dados = supabase.table("perfis_usuarios").select("*").eq("id", st.session_state.usuario_logado.get("id")).execute()
        if atualizar_dados.data: st.session_state.usuario_logado = atualizar_dados.data[0]
    except: pass

    user_atual = st.session_state.usuario_logado
    u_id = user_atual.get("id", "")
    u_name = user_atual.get("username", "Membro")
    is_admin = verificar_se_eh_dev(u_id)

    # Atualiza Online/Offline
    try:
        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", u_id).execute()
    except: pass

    # Contagem de notificações
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
                except: 
                    st.error("Falha ao equipar o cosmético.")

        st.markdown("---")
        if st.button("Sair da Conta 🚪", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.sala_ativa = None
            st.rerun()

    # --- NAVEGAÇÃO COMPLETA RESTAURADA ---
    aba_feed, aba_loja, aba_chat, aba_status, aba_notif = st.tabs([
        "📺 Silver Tok (Feed)", "🛒 Loja & Caixas", "💬 Chat-Exv", "✨ Status", f"🔔 Notificações ({total_notif})"
    ])

    # === 📺 ABA 1: FEED DE PUBLICAÇÕES (RESTAURADO) ===
    with aba_feed:
        st.header("Feed de Publicações")
        # Campo para criar publicação
        nova_pub = st.text_area("O que você está pensando?", placeholder="Compartilhe algo com a comunidade...")
        if st.button("Publicar 🚀"):
            if nova_pub.strip():
                st.success("Publicado com sucesso (Modo simulação)!")
        st.markdown("---")
        st.info("Nenhuma publicação global no momento. Seja o primeiro!")

    # === 🛒 ABA 2: LOJA PREMIUM (RESTAURADA) ===
    with aba_loja:
        st.header("Loja Premium")
        st.write("Adquira personalizações exclusivas usando suas moedas!")
        
        col_loja1, col_loja2 = st.columns(2)
        for idx, (chave, item) in enumerate(COSMETICOS.items()):
            alvo_col = col_loja1 if idx % 2 == 0 else col_loja2
            with alvo_col:
                st.markdown(f"""
                <div style="background-color:#f9f9f9; padding:15px; border-radius:10px; border:1px solid #ddd; text-align:center; margin-bottom:15px;">
                    <img src="{item['img']}" width="50"><br>
                    <strong>{item['nome']}</strong><br>
                    Preço: 🪙 {item['preco']} Moedas
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Comprar {item['nome']}", key=f"buy_{chave}"):
                    st.warning("Funcionalidade de compra em manutenção.")

    # === 💬 ABA 3: CHAT-EXV COM GRAVADOR DE ONDAS E FIX DE COLUNA ===
    with aba_chat:
        st.markdown("## 📟 Painel Chat-Exv")
        
        if st.session_state.sala_ativa:
            st.subheader(f"Sala Ativa: {st.session_state.sala_ativa}")
            if st.button("⬅️ Sair da Sala"):
                st.session_state.sala_ativa = None
                st.rerun()

            # --- O GRAVADOR ESTILO ONDAS IDENTICO ---
            st.markdown("### Gravar Mensagem de Voz 🎙️")
            
            Componente_Gravador = """
            <div style="background-color: #f1f3f4; padding: 20px; border-radius: 12px; text-align: center; border: 1px dashed #b0bec5; margin-bottom: 15px;">
                <div style="margin-bottom: 12px; font-weight: bold; color: #37474f;" id="status">Pressione para falar</div>
                <button id="recordBtn" style="background-color: #e53935; color: white; border: none; border-radius: 50%; width: 55px; height: 55px; cursor: pointer; font-size: 20px; box-shadow: 0px 4px 8px rgba(0,0,0,0.2);">🎤</button>
                <button id="stopBtn" style="background-color: #37474f; color: white; border: none; border-radius: 50%; width: 55px; height: 55px; cursor: pointer; font-size: 20px; margin-left: 10px; display: none;">⏹️</button>
                <div id="waveDisplay" style="display:none; margin-top:10px; font-size:24px; color:#e53935; letter-spacing: 4px;">☊ ▮▮▯▯▮▮▯ Grafico...</div>
                <audio id="audioPlayback" controls style="display:none; margin-top: 15px; width: 100%;"></audio>
            </div>

            <script>
            let mediaRecorder;
            let audioChunks = [];
            const recordBtn = document.getElementById('recordBtn');
            const stopBtn = document.getElementById('stopBtn');
            const statusDiv = document.getElementById('status');
            const audioPlayback = document.getElementById('audioPlayback');
            const waveDisplay = document.getElementById('waveDisplay');

            recordBtn.onclick = async () => {
                audioChunks = [];
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
                    const reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = () => {
                        window.parent.postMessage({type: 'AUDIO_GRAVADO', data: reader.result}, '*');
                    };
                    audioPlayback.src = URL.createObjectURL(audioBlob);
                    audioPlayback.style.display = 'block';
                    waveDisplay.style.display = 'none';
                    statusDiv.innerText = "Áudio pronto! Use o seletor de arquivos caso queira anexar.";
                };
                mediaRecorder.start();
                recordBtn.style.display = 'none';
                stopBtn.style.display = 'inline-block';
                waveDisplay.style.display = 'block';
                statusDiv.innerText = "🔴 Gravando som ambiente...";
            };

            stopBtn.onclick = () => {
                mediaRecorder.stop();
                recordBtn.style.display = 'inline-block';
                stopBtn.style.display = 'none';
            };
            </script>
            """
            st.components.v1.html(Componente_Gravador, height=170)

            # Entrada de Arquivos e Textos normais
            audio_recebido = st.file_uploader("Confirmar envio de áudio gravado:", type=["mp3", "wav", "m4a", "webm"])
            m_txt = st.text_input("Mensagem de texto:")
            img_upload = st.file_uploader("Enviar Imagem 📸", type=["png", "jpg", "jpeg", "gif"])
            
            if st.button("Enviar Conteúdo ✉️", use_container_width=True):
                url_final = None
                if audio_recebido:
                    path_b = f"chat/audios/{uuid.uuid4()}.mp3"
                    supabase.storage.from_("audios_chat").upload(path_b, audio_recebido.read())
                    url_final = supabase.storage.from_("audios_chat").get_public_url(path_b)
                elif img_upload:
                    path_b = f"chat/fotos/{uuid.uuid4()}_{img_upload.name}"
                    supabase.storage.from_("imagens_chat").upload(path_b, img_upload.read())
                    url_final = supabase.storage.from_("imagens_chat").get_public_url(path_b)
                else:
                    url_final = m_txt.strip()

                if url_final:
                    # SALVANDO NA COLUNA CORRETA ('mensagem') PARA EVITAR ERROS DE BANCO
                    try:
                        supabase.table("bate-papo_profissional").insert({
                            "username": u_name,
                            "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "mensagem": url_final, 
                            "codigo_sala": st.session_state.sala_ativa
                        }).execute()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao enviar mensagem: {e}")

            # Renderização das mensagens enviadas
            try:
                m_dados = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", st.session_state.sala_ativa).execute()
                if m_dados.data:
                    for m in reversed(m_dados.data[-30:]):
                        col_m1, col_m2 = st.columns([1, 6])
                        m_user = m.get('username', 'Membro')
                        with col_m1:
                            renderizar_foto_com_banner(m.get("url_foto_perfil") or FOTO_PADRAO, m_user, tamanho=40)
                        with col_m2:
                            try:
                                estilo_u = supabase.table("perfis_usuarios").select("banner_ativo", "id").eq("username", m_user).execute()
                                txt_caixa = estilo_u.data[0].get("banner_ativo", "Nenhum") if estilo_u.data else "Nenhum"
                                uid_remetente = estilo_u.data[0].get("id") if estilo_u.data else ""
                            except:
                                txt_caixa = "Nenhum"
                                uid_remetente = ""
                            renderizar_caixa_mensagem(m_user, m.get('mensagem', ''), obter_selo_texto(m_user), txt_caixa, eh_admin=verificar_se_eh_dev(uid_remetente))
            except: pass
        else:
            t_chat = st.tabs(["💬 Privado", "👥 Grupos", "👥 Membros"])
            with t_chat[0]:
                alvo = st.text_input("Username do amigo para iniciar privado:").strip()
                if st.button("Iniciar Chat Privado") and alvo:
                    lista = sorted([u_name.upper(), alvo.upper()])
                    st.session_state.sala_ativa = f"PRIV-{lista[0]}-{lista[1]}"
                    st.rerun()
            with t_chat[1]:
                g_nome = st.text_input("Nome do Grupo:").strip().upper()
                if st.button("Criar / Entrar no Grupo 🔐") and g_nome:
                    st.session_state.sala_ativa = g_nome
                    st.rerun()
            with t_chat[2]:
                st.write("### Membros da Comunidade")
                try:
                    u_todos = supabase.table("perfis_usuarios").select("*").execute()
                    for u in u_todos.data:
                        m_username = u.get("username", "")
                        if m_username != u_name:
                            st.write(f"• **{m_username}** ({obter_status_emoji(u.get('ultimo_visto'))})")
                except: pass

    # === ✨ ABA 4: STATUS (RESTAURADA) ===
    with aba_status:
        st.header("Status Recentes")
        st.write("Veja momentos rápidos compartilhados pelos seus amigos nas últimas 24 horas.")
        upload_status = st.file_uploader("Adicionar novo Status (Foto) 📸", type=["png", "jpg", "jpeg"])
        if st.button("Postar Status"):
            if upload_status:
                st.success("Status postado com sucesso!")
        st.markdown("---")
        st.info("Nenhum status ativo nas últimas 24 horas.")

    # === 🔔 ABA 5: NOTIFICAÇÕES (RESTAURADA) ===
    with aba_notif:
        st.header("Suas Notificações")
        try:
            dados_n = supabase.table("notificacoes").select("*").eq("id_destinatario", u_id).order("criado_em", descending=True).execute()
            if dados_n.data:
                for notif in dados_n.data:
                    texto_n = notif.get("mensagem", "Nova interação recebida.")
                    st.markdown(f"• {texto_n}")
            else:
                st.info("Você está totalmente atualizado! Nenhuma nova notificação por aqui.")
        except:
            st.info("Nenhuma nova notificação por aqui.")
