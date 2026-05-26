import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v3.8 Ultra Master", page_icon="🎬", layout="centered")

# --- CONFIGURAÇÕES DE MANUTENÇÃO ---
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
    "🔨 O descumprimento de qualquer regra resultará em banimento imediato e permanente."
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

# --- FUNÇÕES AUXILIARES ---
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

    # CORREÇÃO TÉCNICA: Se o usuário selecionou deliberadamente "Nenhum", removemos a estilização forçada
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
        elif any(ext in str(mensagem).lower() for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.webm', '.bin', '.mp4']):
            conteudo_final = f'<br><video width="320" height="240" controls><source src="{mensagem}"></video>'

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
                    # Sistema antifalha de banimento check
                    if busca.data[0].get("website") == "BANIDO":
                        st.error("Esta conta foi suspensa permanentemente por violação das diretrizes de segurança.")
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
    u_id = str(user_atual.get("id", ""))
    u_name = user_atual.get("username", "Membro")
    is_admin = verificar_se_eh_dev(u_id)
    u_cargo = user_atual.get("biografia") if user_atual.get("biografia") else "Nenhum" 
    u_shimeji = user_atual.get("localizacao") if user_atual.get("localizacao") else "Nenhum" 

    # --- BARRA LATERAL ---
    with st.sidebar:
        banner_v = user_atual.get("banner_ativo", "Nenhum")
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, u_name, u_id, tamanho=90, banner_equipado=banner_v, shimeji=u_shimeji)
        
        selo_proprio = obter_selo_texto(u_name, u_id, cargo_adicional=u_cargo)
        st.write(f"**{user_atual.get('apelido') or u_name}** {selo_proprio}")
        st.markdown(f"🪙 **Silver Coins:** {user_atual.get('moedas', 0)}")
        
        # Exibição estática de seguidores baseada no banco
        try:
            total_seg_data = len(supabase.table("seguidores").select("*").eq("id_seguido", u_id).execute().data)
            st.markdown(f"👥 **Seguidores:** {total_seg_data}")
        except: pass

        with st.expander("🎒 Meu Inventário"):
            opcoes_inventario = ["Nenhum", "🥉 Bronze Estelar", "🥈 Prata Lendária", "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber", "🔥 Mestre Otaku (Anime)", "🌸 Banner K-Popper Oficial"]
            if is_admin:
                opcoes_inventario.extend(["👑 Coroa Suprema DEV", "👑 Balão Dourado DEV"])
            
            escolha_custom = st.selectbox("Selecione para ativar:", opcoes_inventario, index=opcoes_inventario.index(banner_v) if banner_v in opcoes_inventario else 0)
            if st.button("Equipar 🛡️"):
                try:
                    supabase.table("perfis_usuarios").update({"banner_ativo": escolha_custom}).eq("id", u_id).execute()
                    st.toast("Item atualizado!")
                    st.rerun()
                except: pass

        if st.button("Sair da Conta 🚪", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.sala_ativa = "GERAL"
            st.session_state.perfil_visitado = None
            st.rerun()

    # --- NAVEGAÇÃO PRINCIPAL ---
    abas_principais = ["📺 Silver Tok", "💬 Chat-Exv", "🍿 Área Geek", "⚙️ Preferências & Regras"]
    if is_admin:
        abas_principais.append("👑 Painel Admin Secreto")
        
    abas = st.tabs(abas_principais)

    # === 📺 ABA 1: FEED + GRAVAÇÃO E FOTOS ===
    with abas[0]:
        st.subheader("Explore Publicações")
        
        with st.expander("📸 Postar Foto ou Arte Estática"):
            legenda_foto = st.text_input("Legenda da Imagem:")
            arquivo_img = st.file_uploader("Selecione a Imagem:", type=["png", "jpg", "jpeg", "gif", "webp"])
            if st.button("Publicar Imagem 🚀") and arquivo_img and legenda_foto:
                try:
                    path_b = f"feed/fotos/{uuid.uuid4()}_{arquivo_img.name}"
                    supabase.storage.from_("imagens_chat").upload(path_b, arquivo_img.read())
                    url_f = supabase.storage.from_("imagens_chat").get_public_url(path_b)
                    
                    supabase.table("feed_videos").insert({
                        "titulo": f"[FOTO] {legenda_foto}", "url_video": url_f, "username_autor": u_name,
                        "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0,
                        "id_autor": str(u_id), "tipo_formato": "horizontal"
                    }).execute()
                    st.success("Foto enviada ao Feed!")
                    st.rerun()
                except: pass

        with st.expander("🎥 Gravar Mini Vídeo com a Câmera"):
            st.markdown("### 📽️ Captura de Câmera Integrada")
            if "b64_video_data" not in st.session_state:
                st.session_state.b64_video_data = ""
                
            video_injector = st.text_input("Dados Câmera", type="password", value=st.session_state.b64_video_data, label_visibility="collapsed", key="video_injector_input")
            
            if st.button("Processar e Publicar Gravação ⚡") and video_injector:
                try:
                    dados_video = base64.b64decode(video_injector)
                    nome_arquivo = f"feed/camera/{uuid.uuid4()}.mp4"
                    supabase.storage.from_("videos_feed").upload(nome_arquivo, dados_video)
                    url_publica_video = supabase.storage.from_("videos_feed").get_public_url(nome_arquivo)
                    
                    supabase.table("feed_videos").insert({
                        "titulo": f"[GRAVADO AO VIVO] Clip de {u_name}", "url_video": url_publica_video, "username_autor": u_name,
                        "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0,
                        "id_autor": str(u_id), "tipo_formato": "vertical"
                    }).execute()
                    st.session_state.b64_video_data = ""
                    st.success("Vídeo gravado publicado com sucesso!")
                    st.rerun()
                except Exception as e: st.error(f"Erro ao processar vídeo: {e}")

            gravador_video_html = """
            <div style="display: flex; gap: 10px; justify-content: center; padding: 5px 0;">
                <video id="preview" width="200" height="150" autoplay muted style="border:1px solid #ccc; background:#000; border-radius:8px;"></video>
                <div style="display:flex; flex-direction:column; justify-content:center; gap:5px;">
                    <button id="startVidBtn" style="background-color: #24a0ed; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer;">🎥 Iniciar Câmera</button>
                    <button id="stopVidBtn" style="background-color: #ff4b4b; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; display: none;">⏹️ Parar & Gravar</button>
                </div>
            </div>
            <script>
            let recorder; let chunks = []; let stream;
            const preview = document.getElementById('preview');
            const startVidBtn = document.getElementById('startVidBtn');
            const stopVidBtn = document.getElementById('stopVidBtn');
            
            startVidBtn.onclick = async () => {
                chunks = [];
                stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                preview.srcObject = stream;
                recorder = new MediaRecorder(stream);
                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'video/mp4' });
                    const r = new FileReader(); r.readAsDataURL(blob);
                    r.onloadend = () => {
                        const base64Str = r.result.split(',')[1];
                        const inputs = window.parent.document.querySelectorAll('input[type="password"]');
                        if(inputs.length > 1) { inputs[1].value = base64Str; inputs[1].dispatchEvent(new Event('input', { bubbles: true })); }
                    };
                };
                recorder.start();
                startVidBtn.style.display = 'none'; stopVidBtn.style.display = 'block';
            };
            stopVidBtn.onclick = () => {
                recorder.stop();
                stream.getTracks().forEach(track => track.stop());
                startVidBtn.style.display = 'block'; stopVidBtn.style.display = 'none';
            };
            </script>
            """
            st.components.v1.html(gravador_video_html, height=180)

        # Listagem do Feed
        try:
            f_dados = supabase.table("feed_videos").select("*").execute()
            if f_dados.data:
                for item in reversed(f_dados.data):
                    if "[GEEK]" in str(item.get("titulo", "")): continue
                    with st.container(border=True):
                        st.markdown(f"**{item.get('username_autor')}**")
                        st.caption(item.get("titulo"))
                        v_url = item.get("url_video", "")
                        if v_url:
                            if "[FOTO]" in str(item.get("titulo", "")):
                                st.image(v_url, use_container_width=True)
                            else:
                                st.video(v_url)
        except: pass

    # === 💬 ABA 2: CHAT-EXV COMPLETO COM PRIVADO ===
    with abas[1]:
        st.subheader("Salas e Direct Messages")
        sala_atual = st.session_state.sala_ativa
        st.info(f"Conectado em: `{sala_atual}`")
        
        c_abas = st.tabs(["🌐 Mensagens", "🔑 Mudar Sala", "👥 Amigos"])
        with c_abas[0]:
            m_txt = st.text_input("Enviar mensagem no chat:", key="msg_chat_v38")
            if st.button("Enviar ✉️") and m_txt.strip():
                try:
                    supabase.table("bate-papo_professional").insert({
                        "username": u_name, "id_usuario": str(u_id), "mensagem": m_txt.strip(), "codigo_sala": sala_atual
                    }).execute()
                    st.rerun()
                except: pass
                
            try:
                msgs = supabase.table("bate-papo_professional").select("*").eq("codigo_sala", sala_atual).execute()
                for m in reversed(msgs.data[-30:]):
                    renderizar_caixa_mensagem(m.get("username"), m.get("mensagem"), obter_selo_texto(m.get("username")), "Nenhum")
            except: pass
            
        with c_abas[1]:
            nova_s = st.text_input("Código do Chat Privado (Ex: VIP-RAFAEL):")
            if st.button("Entrar na Sala 🚪") and nova_s:
                st.session_state.sala_ativa = nova_s.strip().upper()
                st.rerun()
                
        with c_abas[2]:
            st.caption("Controle de Conexões e Relacionamentos")
            nome_amigo = st.text_input("Adicionar ID ou Nome do Usuário para seguir:")
            if st.button("Seguir Usuário ➕") and nome_amigo:
                try:
                    alvo = supabase.table("perfis_usuarios").select("id").eq("username", nome_amigo).execute()
                    if alvo.data:
                        supabase.table("seguidores").insert({"id_seguidor": u_id, "id_seguido": alvo.data[0]["id"]}).execute()
                        st.success("Seguindo!")
                except: pass

    # === 🍿 ABA 3: ÁREA GEEK + BOT FORMATADOR ===
    with abas[2]:
        st.subheader("Catálogo Geek")
        
        # Filtro K-Pop preferencial automático
        pref_atual = user_atual.get("comentarios_internos", "")
        if pref_atual:
            st.markdown(f"🌟 *Exibindo conteúdo otimizado para sua preferência:* **{pref_atual}**")
            
        try:
            g_dados = supabase.table("feed_videos").select("*").execute()
            for item in reversed(g_dados.data):
                if "[GEEK]" in str(item.get("titulo", "")):
                    with st.container(border=True):
                        st.markdown(f"### {item.get('titulo').replace('[GEEK] ', '')}")
                        st.write(item.get("url_video")) # Armazena os dados de episódios/idioma formatados
        except: pass

    # === ⚙️ ABA 4: PREFERÊNCIAS + REGRAS OFICIAIS ===
    with abas[3]:
        st.subheader("📋 Regras da Comunidade Silver Tok")
        for regra in REGRAS_SISTEMA:
            st.markdown(f"*{regra}*")
            
        st.write("---")
        st.subheader("🎶 Catálogo de Preferências Musicais & Culturais")
        estilo_pref = st.selectbox("Escolha seu Estilo Favorito:", ["Nenhum", "K-Pop", "Animes", "Doramas", "Games"])
        detalhe_grupo = st.text_input("Qual seu Grupo/Obra favorito? (Ex: BTS, Twice, Naruto):")
        
        if st.button("Salvar Preferências e Resgatar Bônus 🎁"):
            try:
                banner_recompensa = "🌸 Banner K-Popper Oficial" if estilo_pref == "K-Pop" else "Nenhum"
                supabase.table("perfis_usuarios").update({
                    "comentarios_internos": f"{estilo_pref} - {detalhe_grupo}",
                    "banner_ativo": banner_recompensa
                }).eq("id", u_id).execute()
                st.success("Preferência registrada! Verifique seu inventário de cosméticos.")
                st.rerun()
            except: pass

    # === 👑 ABA 5: PAINEL ADMIN EXPANDIDO v3.8 ===
    if is_admin:
        with abas[4]:
            st.subheader("Painel Geral de Controle do Desenvolvedor")
            
            # 1. Bot Técnico Inteligente (Anime/Episódios/Idioma)
            st.markdown("### 🤖 Configurar Assistente de Conteúdo Geek")
            b_nome = st.text_input("Nome da Obra:")
            b_eps = st.text_input("Quantidade de Episódios:")
            b_lang = st.selectbox("Idioma do Áudio:", ["Legendado", "Dublado PT-BR", "Dual Áudio"])
            if st.button("Injetar Obra Formatada 🎬") and b_nome:
                try:
                    formato_texto = f"🎞️ Episódios: {b_eps} | 🗣️ Idioma: {b_lang}"
                    supabase.table("feed_videos").insert({
                        "titulo": f"[GEEK] {b_nome}", "url_video": formato_texto, "username_autor": "🤖 Bot_Geek_Assist",
                        "avatar_autor": FOTO_PADRAO, "curtidas": 0, "id_autor": str(u_id), "tipo_formato": "horizontal"
                    }).execute()
                    st.success("Obra adicionada com formatação padronizada!")
                except: pass

            # 2. Super Bot Injetor Massivo (50 Vídeos em Lote)
            st.markdown("### ⚡ Carga Massiva do Robô (50+ Posts)")
            if st.button("Disparar Injeção de 50 Publicações Simultâneas 🔥"):
                try:
                    for i in range(1, 51):
                        supabase.table("feed_videos").insert({
                            "titulo": f"🤖 Post do Robô Automatizado #{i} de Testes", "url_video": "https://www.w3schools.com/html/mov_bbb.mp4",
                            "username_autor": f"🤖 Bot_Frequencia_{i}", "avatar_autor": FOTO_PADRAO, "curtidas": i * 2,
                            "id_autor": str(u_id), "tipo_formato": "horizontal"
                        }).execute()
                    st.success("Injeção em lote concluída com sucesso no feed global!")
                except: pass

            # 3. Dar Itens Directos e Injetor de Seguidores Fictícios
            st.markdown("### 🎒 Gerenciador Global de Inventários e Seguidores")
            u_alvo_itens = st.text_input("Nome exato do Usuário Alvo:")
            item_dar = st.selectbox("Cosmético a Conceder:", list(COSMETICOS.keys()))
            qtd_seg_injetar = st.number_input("Injetar Seguidores Bônus:", min_value=0, value=0)
            
            if st.button("Executar Alterações Administrativas ⚡"):
                try:
                    busca_alvo = supabase.table("perfis_usuarios").select("id").eq("username", u_alvo_itens).execute()
                    if busca_alvo.data:
                        id_alvo_user = busca_alvo.data[0]["id"]
                        # Concede item alterando a coluna de cosméticos ativo
                        supabase.table("perfis_usuarios").update({"banner_ativo": COSMETICOS[item_dar]["nome"]}).eq("id", id_alvo_user).execute()
                        # Simulação de injeção de seguidores populando a tabela de junção
                        for _ in range(qtd_seg_injetar):
                            supabase.table("seguidores").insert({"id_seguidor": str(u_id), "id_seguido": id_alvo_user}).execute()
                        st.success("Mudanças salvas no perfil do usuário!")
                except: pass

            # 4. Painel de Controle de Segurança (Banimentos)
            st.markdown("### 🔨 Moderação e Banimento Rigoroso")
            u_banir = st.text_input("Nome do Usuário para Banir permanentemente:")
            if st.button("Aplicar Banimento Permanente 🟥"):
                try:
                    supabase.table("perfis_usuarios").update({"website": "BANIDO"}).eq("username", u_banir).execute()
                    st.success(f"O usuário {u_banir} foi banido e bloqueado com sucesso.")
                except: pass
