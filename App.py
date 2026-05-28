import streamlit as st
from supabase import create_client, Client
import random
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2", page_icon="🚀", layout="centered")

# --- CONEXÃO COM SUPABASE ---
url = "https://ldjtqgeyorkzbvuichjj.supabase.co"
key = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Erro crítico de conexão: {str(e)}")
    st.stop()

# --- ESTADO DE DESENVOLVIMENTO ---
ESTADO_DESENVOLVIMENTO = True 

# --- INICIALIZAÇÃO DA SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "perfil_visitado" not in st.session_state:
    st.session_state.perfil_visitado = None
if "historico_ia" not in st.session_state:
    st.session_state.historico_ia = []
if "chat_privado_salas" not in st.session_state:
    st.session_state.chat_privado_salas = {} 
if "chat_grupos" not in st.session_state:
    st.session_state.chat_grupos = {} 
if "sala_privada_atual" not in st.session_state:
    st.session_state.sala_privada_atual = None
if "codigo_grupo_atual" not in st.session_state:
    st.session_state.codigo_grupo_atual = None
if "live_ativa" not in st.session_state:
    st.session_state.live_ativa = False
if "live_chat" not in st.session_state:
    st.session_state.live_chat = []
if "live_alertas" not in st.session_state:
    st.session_state.live_alertas = []

CODIGO_CORRETO = "ChatPrivado2026"

TITULOS = {
    "rafael_oficial": "👑 Desenvolvedor",
    "rafael_secundario": "⚔️ Vice-Dev",
    "amiga_divulgadora": "📢 Divulgadora",
}

# --- 1. FUNÇÃO QUE FAZ O NAVEGADOR FALAR ---
def emitir_alerta_voz(texto_mensagem):
    """Injeta um script JavaScript discreto para ler a mensagem em voz alta."""
    js_code = f"""
    <script>
    if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel(); 
        var msg = new SpeechSynthesisUtterance({repr(texto_mensagem)});
        msg.lang = 'pt-BR';
        msg.rate = 1.1; 
        window.speechSynthesis.speak(msg);
    }}
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

# --- 2. FUNÇÃO QUE CHECA AS MOEDAS NO BANCO DE DADOS ---
def checar_e_ler_alertas_da_live(live_id_atual):
    try:
        alertas_nao_lidos = supabase.table("live_alertas").select("*").eq("live_id", live_id_atual).eq("lido_status", False).order("criado_em", desc=False).execute()
        for alerta in alertas_nao_lidos.data:
            usuario = alerta.get("enviado_por")
            coins = alerta.get("quantidade_coins")
            msg_texto = alerta.get("mensagem", "")
            
            texto_para_falar = f"{usuario} enviou {coins} Silver Coins! Mensagem: {msg_texto}"
            emitir_alerta_voz(texto_para_falar)
            
            supabase.table("live_alertas").update({"lido_status": True}).eq("id", alerta.get("id")).execute()
            st.toast(f"📢 Voz lendo doação de @{usuario}!", icon="🔊")
    except: 
        pass

# --- FUNÇÃO PARA GERAR ID DE SALA PRIVADA ÚNICA ---
def obter_id_sala_privada(userA, userB):
    return "_".join(sorted([userA, userB]))

# --- FUNÇÃO PARA GERAR SELO E MOLDURA DE PERFIL ---
def aplicar_moldura_e_selo(username, titulo, itens_usuario=None, seguidores=0):
    selo = ""
    if seguidores >= 1000: selo += " ⚡[VERIFICADO]"
    if username == "rafael_oficial": selo += " ✨[👑 DEV]"
    elif "Dev" in str(titulo) or "Desenvolvedor" in str(titulo): selo += " 🛠️[DEV]"
    elif titulo == "🏅 best friends of the dev": selo += " 🌟"
        
    estilo_moldura = "border-radius: 50%; object-fit: cover;"
    if itens_usuario and isinstance(itens_usuario, list):
        if "[EQUIPADO] 🖼️ Moldura de Fogo 🔥" in itens_usuario:
            estilo_moldura = "border-radius: 50%; object-fit: cover; border: 4px solid #FF4500; box-shadow: 0 0 15px #FF8C00;"
        elif "[EQUIPADO] 💎 Moldura de Diamante ✨" in itens_usuario:
            estilo_moldura = "border-radius: 50%; object-fit: cover; border: 4px solid #00FFFF; box-shadow: 0 0 15px #00BFFF;"
    return selo, estilo_moldura

# --- SIMULAÇÃO DA IA SILVER INTELIGENTE ---
def responder_ia(pergunta):
    pergunta_lower = pergunta.lower()
    if "ideia" in pergunta_lower or "video" in pergunta_lower or "feed" in pergunta_lower:
        return ("💡 **Ideias de Vídeo do Silver:**\n\n1. **Bastidores do Dev:** Mostre como funciona o Live Pix do Silver Tok!\n2. **Tour pelo App:** Mostre a Loja do Site e como equipar a Moldura de Fogo 🔥.\n3. **Desafio Tech:** Pergunte aos seguidores o que eles querem na v3.")
    elif "live" in pergunta_lower or "coins" in pergunta_lower or "pix" in pergunta_lower:
        return ("🪙 **Dica do Silver para Lives:**\n\nO sistema de **Live Pix** lê mensagens em voz alta! Crie metas de Silver Coins na tela para engajar seu público.")
    elif "oi" in pergunta_lower or "ola" in pergunta_lower or "ajuda" in pergunta_lower:
        return (f"Olá, Rafael! Eu sou o **Silver**, seu assistente oficial. Como vamos projetar o app agora?")
    else:
        return ("🧠 **Análise do Silver:** Entendi sua dúvida! Recomendo aplicar essa ideia integrando os componentes visuais do Streamlit com o banco de dados do Supabase.")

# --- FUNÇÃO DE CRIAÇÃO DE CONTA COM SISTEMA DE CONVITES ---
def criar_conta(username, password, nickname, codigo_manual, indicador_url):
    try:
        existe = supabase.table("perfis_usuarios").select("*").eq("username", username).execute()
        if existe.data:
            return "Este nome de usuário já está em uso."
        
        quem_convidou = None
        
        if indicador_url:
            if indicador_url == "rafael_oficial":
                quem_convidou = "rafael_oficial"
            else:
                checar_dono = supabase.table("perfis_usuarios").select("username", "convites_restantes").eq("username", indicador_url).execute()
                if checar_dono.data:
                    creditos = checar_dono.data[0].get("convites_restantes", 0)
                    if creditos > 0:
                        quem_convidou = indicador_url
                        if indicador_url != "rafael_oficial":
                            supabase.table("perfis_usuarios").update({"convites_restantes": creditos - 1}).eq("username", indicador_url).execute()
                    else:
                        return f"O link de convite de @{indicador_url} já atingiu o limite de 3 usos!"
                else:
                    return "Este link de convite é inválido ou o usuário não existe."
        else:
            if codigo_manual != CODIGO_CORRETO:
                return "Código de convite inválido! Use um link de amigo ou peça o código mestre."

        titulo = TITULOS.get(username, "Usuário")
        
        novo_usuario = {
            "username": username, "senha": password, "nickname": nickname, "titulo": titulo,
            "seguidores": 0, "seguindo": 0, "dinheiro": 0, "verificado": False,
            "foto_perfil": "https://img.icons8.com/colors/150/test-account.png",
            "bio": "Olá! Estou usando o Silver Tok.", "itens_exclusivos": [], "lista_amigos": [],
            "convites_restantes": 3, "convidado_por": quem_convidou
        }
        supabase.table("perfis_usuarios").insert(novo_usuario).execute()
        return "Sucesso"
    except Exception as e:
        return f"Erro ao criar conta: {str(e)}"

# --- TELA DE LOGIN / CADASTRO ---
if not st.session_state.logado:
    st.title("Welcome to Silver Tok v2 🚀")
    
    parametros_url = st.query_params
    referencia_convite = parametros_url.get("ref", None)
    
    aba_login, aba_cadastro = st.tabs(["🔐 Entrar", "📝 Criar Conta"])
    
    with aba_login:
        user_in = st.text_input("Usuário", key="login_user").strip()
        pass_in = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar", use_container_width=True):
            try:
                resultado = supabase.table("perfis_usuarios").select("*").eq("username", user_in).eq("senha", pass_in).execute()
                if resultado.data:
                    st.session_state.logado = True
                    st.session_state.user_data = resultado.data[0]
                    st.rerun()
                else: st.error("Usuário ou senha incorretos.")
            except Exception as e: st.error(f"Erro de conexão: {str(e)}")
                
    with aba_cadastro:
        if referencia_convite:
            st.success(f"✨ **Link Ativo:** Você está sendo convidado por **@{referencia_convite}**! O código secreto foi pulado automaticamente.")
        
        new_user = st.text_input("Escolha seu Usuário (@)", key="cad_user").strip()
        new_nick = st.text_input("Nome de Exibição (Nickname)", key="cad_nick")
        new_pass = st.text_input("Escolha sua Senha", type="password", key="cad_pass")
        
        convite_manual = ""
        if not referencia_convite:
            convite_manual = st.text_input("Código de Convite Secreto (Manual)", type="password", key="cad_code")
        
        if st.button("Cadastrar Nova Conta", use_container_width=True):
            if not new_user or not new_pass or not new_nick: 
                st.warning("Preencha todos os campos!")
            else:
                status = criar_conta(new_user, new_pass, new_nick, convite_manual, referencia_convite)
                if status == "Sucesso": 
                    st.success("🎉 Conta criada com sucesso! Faça login na aba ao lado.")
                    st.query_params.clear()
                else: 
                    st.error(status)
    st.stop()

def atualizar_sessao():
    try:
        res = supabase.table("perfis_usuarios").select("*").eq("username", st.session_state.user_data['username']).execute()
        if res.data: st.session_state.user_data = res.data[0]
    except: pass

atualizar_sessao()
user_atual = st.session_state.user_data

if user_atual.get("titulo") == "❌ BANIDO":
    st.title("🚫 Conta Bloqueada")
    st.error("Você foi banido deste aplicativo pela administração.")
    st.stop()

if ESTADO_DESENVOLVIMENTO and user_atual.get("titulo") not in ["👑 Desenvolvedor", "🧪 Tester"]:
    st.title("🚧 Aplicativo em Manutenção")
    if st.button("Sair da Conta"):
        st.session_state.logado = False
        st.rerun()
    st.stop()

# --- SIDEBAR (BARRA LATERAL) ---
foto_side = user_atual.get('foto_perfil')
if not foto_side or str(foto_side).strip() in ["0", "None", ""] or not str(foto_side).startswith("http"):
    foto_side = "https://img.icons8.com/colors/150/test-account.png"

meus_itens_sidebar = user_atual.get('itens_exclusivos', [])
if not isinstance(meus_itens_sidebar, list): meus_itens_sidebar = []

selo_sidebar, estilo_da_moldura = aplicar_moldura_e_selo(user_atual.get('username', ''), user_atual.get('titulo', ''), meus_itens_sidebar, user_atual.get('seguidores', 0))

st.sidebar.markdown(f'<img src="{foto_side}" style="{estilo_da_moldura}" width="100">', unsafe_allow_html=True)
st.sidebar.write("") 
st.sidebar.title(f"@{user_atual.get('username', '')}{selo_sidebar}")
st.sidebar.markdown(f"🪙 **Silver Coins:** {user_atual.get('dinheiro', 0)}")
if st.sidebar.button("Sair da Conta"):
    st.session_state.logado = False
    st.rerun()

# --- MENU PRINCIPAL ---
abas = ["📱 Feed", "🎥 Gravar/Postar", "💬 Chat EXV", "🧠 Silver IA", "🛒 Loja do Site", "👤 Meu Perfil"]
if st.session_state.perfil_visitado: abas.append("👀 Ver Perfil")
if user_atual.get('username') == "rafael_oficial": abas.append("⚡ Painel Dev")

aba_ativa = st.radio("Menu", abas, horizontal=True)
st.write("---")

# --- 1. ABA FEED ---
if aba_ativa == "📱 Feed":
    st.title("📱 Feed de Vídeos")
    try:
        dados_feed = supabase.table("feed_videos").select("*").order("id", desc=True).execute()
        videos = dados_feed.data if dados_feed else []
        
        if videos:
            for vid in videos:
                st.write(f"👤 **{vid.get('nickname', 'Usuário')}** (@{vid.get('username', 'user')})")
                link_final = vid.get('url') or vid.get('video_url')
                if link_final:
                    st.video(link_final)
                else:
                    st.warning("Link do vídeo não encontrado.")
                st.write(f"❤️ {vid.get('curtidas', 0)} curtidas")
                st.write("---")
        else:
            st.info("Nenhum vídeo publicado ainda. Seja o primeiro a postar na aba 🎥 Gravar/Postar!")
    except Exception as e:
        st.error(f"Erro ao carregar o Feed: {str(e)}")       
        videos = []

    if not videos:
        st.info("Nenhum vídeo publicado ainda. Seja o primeiro a postar na aba 🎥 Gravar/Postar!")

    for vid in videos:
        v_username = vid.get('username', 'anonimo')
        v_nickname = vid.get('nickname', 'Usuário')
        v_legenda = vid.get('legenda', '')
        v_url = vid.get('url', '')  # Verificado com a coluna do banco de dados
        v_curtidas = vid.get('curtidas', 0)
        v_id = vid.get('id')
        
        if not termo or termo in v_legenda.lower() or termo in v_username.lower() or termo in v_nickname.lower():
            with st.container():
                foto_autor, titulo_autor, itens_autor, seg_autor = "https://img.icons8.com/colors/150/test-account.png", "Usuário", [], 0
                try:
                    autor_req = supabase.table("perfis_usuarios").select("*").eq("username", v_username).execute()
                    if autor_req.data:
                        foto_autor = autor_req.data[0].get('foto_perfil', foto_autor)
                        if not foto_autor or str(foto_autor).strip() in ["0", "None", ""]: foto_autor = "https://img.icons8.com/colors/150/test-account.png"
                        titulo_autor = autor_req.data[0].get('titulo', 'Usuário')
                        itens_autor = autor_req.data[0].get('itens_exclusivos', [])
                        seg_autor = autor_req.data[0].get('seguidores', 0)
                except: pass
                
                selo_post, moldura_post = aplicar_moldura_e_selo(v_username, titulo_autor, itens_autor, seg_autor)
                col_foto, col_nome = st.columns([1, 5])
                with col_foto: st.markdown(f'<img src="{foto_autor}" style="{moldura_post}" width="50">', unsafe_allow_html=True)
                with col_nome:
                    if st.button(f"**{v_nickname}** (@{v_username}){selo_post}", key=f"u_{v_id}"):
                        st.session_state.perfil_visitado = v_username
                        st.rerun()
                
                if v_legenda: st.write(v_legenda)
                if v_url:
                    try: st.video(v_url)
                    except: st.error("Vídeo indisponível.")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button(f"❤️ {v_curtidas}", key=f"l_{v_id}", use_container_width=True):
                        try:
                            supabase.table("feed_videos").update({"curtidas": v_curtidas + 1}).eq("id", v_id).execute()
                            st.rerun()
                        except: pass
                with c2: st.button("🔗 Copiar", key=f"s_{v_id}", use_container_width=True)
                with c3: abrir_comentarios = st.checkbox("💬 Comentários", key=f"tab_c_{v_id}")
                
                if abrir_comentarios: st.write("**@rafael_oficial:** Esse vídeo ficou brabo! 🔥")
                
                if user_atual.get('username') == v_username or user_atual.get('username') == "rafael_oficial":
                    if st.button(f"🗑️ Apagar Vídeo", key=f"d_{v_id}", use_container_width=True):
                        try:
                            supabase.table("feed_videos").delete().eq("id", v_id).execute()
                            st.rerun()
                        except: pass
                st.write("---")

if aba_ativa == "🎥 Gravar/Postar":
    # 1. Título da aba de gravação
    st.title("🎥 Postar Novo Conteúdo")
    
    # Certifique-se de que definiu os três nomes antes do '='
aba_gravar, aba_link, aba_central = st.tabs(["🔴 Gravar Post", "🔗 Postar por Link", "🚨 Central do..."])
     
    # Se quiseres colocar um botão de teste para a câmara do Streamlit:
    # foto_ou_video = st.camera_input("Tire uma foto para o post")
with aba_link:
        legenda = st.text_input("Legenda do post:", key="leg_link")
        url_do_video = st.text_input("Link do vídeo (.mp4):", key="url_mp4")
        if st.button("Publicar Vídeo por Link", use_container_width=True):
            if url_do_video:
                try:
                    supabase.table("feed_videos").insert({
                        "username": user_atual.get('username'), 
                        "nickname": user_atual.get('nickname'), 
                        "url": url_do_video, 
                        "curtidas": 0
                    }).execute()
                    st.success("Publicado com sucesso no Feed! Atualizando...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {str(e)}")                
        with aba_central:
        st.write("Configurações adicionais e monitoramento de lives.")
 
        if not st.session_state.live_ativa:
            titulo_live = st.text_input("Título da sua Live:", placeholder="Ex: Programando o Silver Tok v2! 🔥")
            if st.button("🔴 INICIAR LIVE GLOBAL", use_container_width=True):
                if titulo_live:
                    try:
                        supabase.table("lives_ativas").delete().eq("streamer_username", user_atual.get('username')).execute()
                        supabase.table("lives_ativas").insert({"streamer_username": user_atual.get('username'), "streamer_nickname": user_atual.get('nickname'), "titulo_live": titulo_live, "status": "online"}).execute()
                        st.session_state.live_ativa = True
                        st.session_state.live_chat = [{"remetente": "Sistema", "conteudo": "Sua transmissão está pública no feed!"}]
                        st.session_state.live_alertas = []
                        st.rerun()
                    except Exception as e: st.error(f"Erro ao abrir transmissão: {str(e)}")
        else:
            st.success("🎥 VOCÊ ESTÁ AO VIVO!")
            if st.button("⏹️ Encerrar Transmissão", use_container_width=True):
                st.session_state.live_ativa = False
                try: supabase.table("lives_ativas").delete().eq("streamer_username", user_atual.get('username')).execute()
                except: pass
                st.rerun()
            
            try:
                live_req = supabase.table("lives_ativas").select("id").eq("streamer_username", user_atual.get('username')).execute()
                if live_req.data:
                    checar_e_ler_alertas_da_live(live_req.data[0]["id"])
            except: pass
            
            st.write("---")
            col_video_retorno, col_chat_live = st.columns([4, 3])
            
            with col_video_retorno:
                st.markdown("### 🖥️ Retorno de Vídeo")
                st.camera_input("Monitor", key="monitor_live_cam")
            with col_chat_live:
                st.markdown("### 💬 Chat da Live")
                with st.container(border=True, height=200):
                    for msg_l in st.session_state.live_chat: 
                        st.write(f"**@{msg_l['remetente']}:** {msg_l['conteudo']}")

# --- 3. ABA CHAT EXV ---
elif aba_ativa == "💬 Chat EXV":
    st.title("💬 Chat EXV")
    aba_dm, aba_grp = st.tabs(["🔒 Conversas Privadas", "👥 Grupos por Código"])
    
    with aba_dm:
        try:
            todos_req = supabase.table("perfis_usuarios").select("username, nickname").execute()
            lista_usuarios = [u for u in todos_req.data if u['username'] != user_atual.get('username')]
        except: 
            lista_usuarios = []
        
        if lista_usuarios:
            opcoes_usuarios = {u['username']: f"{u['nickname']} (@{u['username']})" for u in lista_usuarios}
            usuario_selecionado = st.selectbox("Abrir sala com:", list(opcoes_usuarios.keys()), format_func=lambda x: opcoes_usuarios[x])
            if st.button("🚪 Entrar na Sala Privada", use_container_width=True):
                st.session_state.sala_privada_atual = obter_id_sala_privada(user_atual.get('username'), usuario_selecionado)
                st.session_state.codigo_grupo_atual = None
        
        if st.session_state.sala_privada_atual:
            sala_id = st.session_state.sala_privada_atual
            outro_usuario = sala_id.replace(user_atual.get('username'), "").replace("_", "")
            st.markdown(f"### 💬 Sala: **@{user_atual.get('username')}** & **@{outro_usuario}**")
            
            if sala_id not in st.session_state.chat_privado_salas: 
                st.session_state.chat_privado_salas[sala_id] = []
                
            for msg in st.session_state.chat_privado_salas[sala_id]:
                # --- BUSCA A FOTO DO REMETENTE DA MENSAGEM ---
                foto_avatar = "https://img.icons8.com/colors/150/test-account.png"
                if msg['remetente'] == user_atual.get('username'):
                    if user_atual.get('foto_perfil') and str(user_atual.get('foto_perfil')).startswith("http"):
                        foto_avatar = user_atual.get('foto_perfil')
                else:
                    try:
                        outro_req = supabase.table("perfis_usuarios").select("foto_perfil").eq("username", msg['remetente']).execute()
                        if outro_req.data and outro_req.data[0].get('foto_perfil'):
                            if str(outro_req.data[0].get('foto_perfil')).startswith("http"):
                                foto_avatar = outro_req.data[0].get('foto_perfil')
                    except:
                        pass
                
                # --- EXIBE O BALÃO COM A FOTO CORRETA ---
                with st.chat_message("user" if msg['remetente'] == user_atual.get('username') else "assistant", avatar=foto_avatar):
                    st.write(f"**@{msg['remetente']}:** {msg['conteudo']}")
            
            txt = st.text_input("Mensagem:", key="msg_p_input")
            if st.button("Enviar", use_container_width=True) and txt:
                st.session_state.chat_privado_salas[sala_id].append({"remetente": user_atual.get('username'), "conteudo": txt})
                st.rerun()

    with aba_grp:
        st.subheader("👥 Grupos por Código")
        cg1, cg2 = st.columns(2)
        with cg1:
            nome_novo_grp = st.text_input("Nome do Grupo:")
            cod_novo_grp = st.text_input("Código Secreto:", type="password", key="new_grp_cod")
            if st.button("🏗️ Criar Grupo", use_container_width=True) and nome_novo_grp and cod_novo_grp:
                st.session_state.chat_grupos[cod_novo_grp] = {"nome": nome_novo_grp, "mensagens": []}
                st.success("Grupo criado!")
        with cg2:
            cod_inserido = st.text_input("Digitar Código:", type="password", key="join_grp_cod")
            if st.button("🚪 Entrar", use_container_width=True) and cod_inserido in st.session_state.chat_grupos:
                st.session_state.codigo_grupo_atual = cod_inserido
                st.session_state.sala_privada_atual = None
                
        if st.session_state.codigo_grupo_atual:
            cod_g = st.session_state.codigo_grupo_atual
            st.markdown(f"### Grupo: **{st.session_state.chat_grupos[cod_g]['nome']}**")
            for m_g in st.session_state.chat_grupos[cod_g]['mensagens']: 
                st.write(f"**@{m_g['remetente']}:** {m_g['conteudo']}")
            msg_g = st.text_input("Escrever...", key="input_msg_grp")
            if st.button("Enviar Grupo") and msg_g:
                st.session_state.chat_grupos[cod_g]['mensagens'].append({"remetente": user_atual.get('username'), "conteudo": msg_g})
                st.rerun()
            
# --- 4. ABA SILVER IA ---
elif aba_ativa == "🧠 Silver IA":
    st.title("🧠 Silver IA")
    prompt_usuario = st.text_input("O que deseja saber?", placeholder="Ex: Me dê ideias de vídeos para o meu feed")
    if st.button("Perguntar", use_container_width=True) and prompt_usuario:
        resposta = responder_ia(prompt_usuario)
        st.session_state.historico_ia.insert(0, {"pergunta": prompt_usuario, "resposta": resposta})
        st.rerun()
    for chat in st.session_state.historico_ia:
        st.info(f"❓ **Você:** {chat['pergunta']}")
        st.success(f"🤖 **Silver:** {chat['resposta']}")

# --- 5. ABA LOJA DO SITE ---
elif aba_ativa == "🛒 Loja do Site":
    st.title("🛒 Loja de Customizações")
    st.write(f"🪙 **Carteira:** {user_atual.get('dinheiro', 0)} Silver Coins")
    st.write("---")

    customizacoes = {
        "🖼️ Moldura de Fogo 🔥": 1000, "💎 Moldura de Diamante ✨": 2500,
        "🖼️ Banner Estelar (Perfil)": 1500, "💬 Caixa de Texto Neon (Feed)": 2000, "🌈 Nickname Dourado": 5000
    }

    for item, preco in customizacoes.items():
        with st.container():
            col_info, col_btn = st.columns([3, 1])
            with col_info: st.markdown(f"### {item}\n🪙 Custo: **{preco} Coins**")
            with col_btn:
                st.write("<br>", unsafe_allow_html=True)
                meus_visuais = user_atual.get('itens_exclusivos', [])
                if not isinstance(meus_visuais, list): meus_visuais = []
                meus_visuais = [x for x in meus_visuais if x]
                
                if item in meus_visuais or f"[EQUIPADO] {item}" in meus_visuais:
                    st.button("✅ Adquirido", key=f"loja_{item}", disabled=True, use_container_width=True)
                else:
                    if st.button(f"🛒 Adquirir", key=f"comprar_{item}", use_container_width=True):
                        saldo = user_atual.get('dinheiro', 0)
                        if saldo >= preco:
                            try:
                                meus_visuais.append(item)
                                supabase.table("perfis_usuarios").update({"dinheiro": saldo - preco, "itens_exclusivos": meus_visuais}).eq("username", user_atual.get('username')).execute()
                                st.success(f"🎉 Adquirido!")
                                st.rerun()
                            except Exception as e: st.error(f"Erro: {str(e)}")
                        else: st.error("❌ Saldo insuficiente!")
            st.write("---")

# --- 6. ABA MEU PERFIL ---
elif aba_ativa == "👤 Meu Perfil":
    meus_itens_perfil = user_atual.get('itens_exclusivos', [])
    if not isinstance(meus_itens_perfil, list): meus_itens_perfil = []
    meus_itens_perfil = [x for x in meus_itens_perfil if x]
    
    if "[EQUIPADO] 🖼️ Banner Estelar (Perfil)" in meus_itens_perfil:
        st.markdown('<div style="background: linear-gradient(135deg, #1e0034 0%, #340068 50%, #ff007f 100%); height: 120px; border-radius: 12px 12px 0px 0px; margin-bottom: -60px;"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%); height: 100px; border-radius: 12px 12px 0px 0px; margin-bottom: -50px;"></div>', unsafe_allow_html=True)

    selo_meu_perfil, moldura_meu_perfil = aplicar_moldura_e_selo(user_atual.get('username'), user_atual.get('titulo'), meus_itens_perfil, user_atual.get('seguidores', 0))
    col_foto, col_stats = st.columns([1, 2])
    with col_foto:
        f_perfil = user_atual.get('foto_perfil', '')
        if not f_perfil or str(f_perfil).strip() in ["0", "None", ""]: f_perfil = "https://img.icons8.com/colors/150/test-account.png"
        st.markdown(f'<div style="padding-top: 10px; text-align: center;"><img src="{f_perfil}" style="{moldura_meu_perfil} background-color: #0e1117;" width="120"></div>', unsafe_allow_html=True)
            
    with col_stats:
        st.write("<br>" * 2, unsafe_allow_html=True)
        st.header(f"{user_atual.get('nickname', 'Usuário')}{selo_meu_perfil}")
        st.caption(f"🆔 **@{user_atual.get('username', '')}** | Cargo: *{user_atual.get('titulo', 'Usuário')}*")
        m1, m2, m3 = st.columns(3)
        m1.metric("Seguidores", f"👥 {user_atual.get('seguidores', 0)}")
        m2.metric("Seguindo", f"🏃 {user_atual.get('seguindo', 0)}")
        m3.metric("Saldo", f"🪙 {user_atual.get('dinheiro', 0)}")
    
    st.write("---")
        # 1. LINHA CORRIGIDA DAS ABAS (Usando sub_aba_seguidores que seu código precisa)
    sub_aba_perfil, sub_aba_inventario, sub_aba_editar, sub_aba_convites, sub_aba_seguidores = st.tabs(["📋 Meus Dados", "🎒 Meu Inventário", "⚙️ Editar Perfil", "✉️ Convites", "👥 Amigos"])
    
    # 2. SEU INVENTÁRIO (Note as 4 posições de espaço para a direita, colocando ele DENTRO da aba)
    with sub_aba_inventario:
        if meus_itens_perfil:
            # Filtra e limpa a lista para exibição
            itens_exib = list(set([i.replace("[EQUIPADO] ", "") for i in meus_itens_perfil if i]))
            for it in itens_exib:
                col_n, col_a = st.columns([3, 1])
                eq = f"[EQUIPADO] {it}" in meus_itens_perfil
                with col_n: 
                    st.markdown(f"🟢 **{it}**" if eq else f"⚪ {it}")
                with col_a:
                    if eq:
                        if st.button("Desequipar", key=f"d_{it}", use_container_width=True):
                            nl = [x for x in meus_itens_perfil if x != f"[EQUIPADO] {it}"]
                            if it not in nl: 
                                nl.append(it)
                            supabase.table("perfis_usuarios").update({"itens_exclusivos": nl}).eq("username", user_atual.get('username')).execute()
                            st.rerun()
                    else:
                        if st.button("Equipar", key=f"e_{it}", use_container_width=True):
                            nl = []
                            for x in meus_itens_perfil:
                                if "Moldura" in x and "[EQUIPADO]" in x:
                                    nl.append(x.replace("[EQUIPADO] ", ""))
                                else:
                                    nl.append(x)
                            if it in nl: 
                                nl.remove(it)
                            nl.append(f"[EQUIPADO] {it}")
                            supabase.table("perfis_usuarios").update({"itens_exclusivos": nl}).eq("username", user_atual.get('username')).execute()
                            st.rerun()
        else:
            st.info("Inventário vazio.")
                
    with sub_aba_editar:
        n_nick = st.text_input("Nickname:", value=user_atual.get('nickname'))
        n_foto = st.text_input("URL Foto:", value=user_atual.get('foto_perfil'))
        n_bio = st.text_area("Bio:", value=user_atual.get('bio'), max_chars=150)
        if st.button("💾 Salvar Perfil", use_container_width=True):
            supabase.table("perfis_usuarios").update({"nickname": n_nick, "foto_perfil": n_foto, "bio": n_bio}).eq("username", user_atual.get('username')).execute()
            st.success("Salvo!")
            st.rerun()

    with sub_aba_convites:
        st.subheader("✉️ Sistema de Convites Compartilhados")
        if user_atual.get('username') == "rafael_oficial":
            st.info("👑 **Vantagem de Desenvolvedor:** Seus convites são **INFINITOS** e ilimitados!")
        else:
            st.metric("Seus Créditos de Convite Restantes:", f"🎫 {user_atual.get('convites_restantes', 0)} de 3")
        
        link_gerado = f"https://silvertokv2.streamlit.app/?ref={user_atual.get('username')}"
        st.markdown("### 🔗 Seu Link de Convite Exclusivo:")
        st.code(link_gerado, language="text")
        st.caption("Envie esse link para seus amigos. Ao entrarem por ele, o sistema pula o código secreto automaticamente!")

    with sub_aba_seguidores:
        amg_add = st.text_input("Seguir usuário (@):").strip()
        if st.button("➕ Seguir") and amg_add:
            chk = supabase.table("perfis_usuarios").select("username").eq("username", amg_add).execute()
            if chk.data:
                la = user_atual.get('lista_amigos', [])
                if not isinstance(la, list): la = []
                if amg_add not in la:
                    la.append(amg_add)
                    supabase.table("perfis_usuarios").update({"lista_amigos": la, "seguindo": user_atual.get('seguindo', 0) + 1}).eq("username", user_atual.get('username')).execute()
                    st.success("Seguindo!")
                    st.rerun()

# --- 7. ABA VISITAR PERFIL ---
elif aba_ativa == "👀 Ver Perfil" and st.session_state.perfil_visitado:
    alvo = st.session_state.perfil_visitado
    try:
        res = supabase.table("perfis_usuarios").select("*").eq("username", alvo).execute()
        if res.data:
            p = res.data[0]
            selo_v, moldura_v = aplicar_moldura_e_selo(p.get('username'), p.get('titulo'), p.get('itens_exclusivos', []), p.get('seguidores', 0))
            
            col_f, col_s = st.columns([1, 2])
            with col_f:
                fv = p.get('foto_perfil', '')
                if not fv or str(fv).strip() in ["0", "None", ""]: fv = 'https://img.icons8.com/colors/150/test-account.png'
                st.markdown(f'<img src="{fv}" style="{moldura_v}" width="120">', unsafe_allow_html=True)
            with col_s:
                st.header(f"{p.get('nickname')}{selo_v}")
                st.write(f"@{p.get('username')} | {p.get('titulo')}\n👥 {p.get('seguidores', 0)} Seguidores")
            
            st.write(f"📝 {p.get('bio', '')}")
            st.write("---")
            
            try:
                live_check = supabase.table("lives_ativas").select("*").eq("streamer_username", alvo).execute()
                if live_check.data:
                    st.error("🔴 ESTE CANAL ESTÁ TRANSMITINDO AO VIVO AGORA!")
                    
                    with st.expander("🎁 Enviar Silver Coins + Mensagem em Voz Alta (Live Pix)", expanded=True):
                        moedas_enviar = st.number_input("Quantidade de Moedas:", min_value=10, value=50, step=10, key="coins_live_pix")
                        msg_enviar = st.text_input("Escrever Mensagem para o Streamer ouvir:", placeholder="Manda um salve!", key="msg_live_pix")
                        
                        if st.button("🪙 Enviar Live Pix", use_container_width=True):
                            saldo_meu = user_atual.get('dinheiro', 0)
                            if saldo_meu >= moedas_enviar:
                                if msg_enviar:
                                    supabase.table("perfis_usuarios").update({"dinheiro": saldo_meu - moedas_enviar}).eq("username", user_atual.get('username')).execute()
                                    supabase.table("live_alertas").insert({"live_id": live_check.data[0]["id"], "enviado_por": user_atual.get('username'), "quantidade_coins": moedas_enviar, "mensagem": msg_enviar, "lido_status": False}).execute()
                                    st.success("🎉 Live Pix enviado!")
                                else: st.warning("Digite uma mensagem.")
                            else: st.error("Saldo de moedas insuficiente na carteira.")
            except: pass
            
            if st.button("Voltar ao Feed"):
                st.session_state.perfil_visitado = None
                st.rerun()
    except: pass

  # --- 8. PAINEL DEV ---
elif aba_ativa == "⚡ Painel Dev" and user_atual.get('username') == "rafael_oficial":
    st.header("Painel Secreto do Desenvolvedor 👑")
    try:
        usuarios_req = supabase.table("perfis_usuarios").select("username, nickname").execute()
        lista_usuarios = [u["username"] for u in usuarios_req.data]
    except: lista_usuarios = []

    if lista_usuarios:
        usuario_alvo = st.selectbox("Selecione o usuário alvo:", lista_usuarios)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.subheader("👥 Seguidores")
            qtd_seguidores = st.number_input("Quantidade", min_value=0, value=1000)
            if st.button("Definir", key="btn_seg"):
                supabase.table("perfis_usuarios").update({"seguidores": qtd_seguidores}).eq("username", usuario_alvo).execute()
                st.rerun()
        with col2:
            st.subheader("💰 Coins")
            qtd_dinheiro = st.number_input("Silver Coins", min_value=0, value=500)
            if st.button("Definir", key="btn_money"):
                supabase.table("perfis_usuarios").update({"dinheiro": qtd_dinheiro}).eq("username", usuario_alvo).execute()
                st.rerun()
        with col3:
            st.subheader("🎖️ Cargos")
            novo_titulo = st.selectbox("Cargo:", ["👑 Desenvolvedor", "⚔️ Vice-Dev", "📢 Divulgadora", "🧪 Tester", "🏅 best friends of the dev", "Usuário"])
            if st.button("Atualizar", key="btn_cargo"):
                supabase.table("perfis_usuarios").update({"titulo": novo_titulo}).eq("username", usuario_alvo).execute()
                st.rerun()
        with col4:
            st.subheader("🔨 Moderação")
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🚫 Banir Usuário", key="btn_banir", use_container_width=True):
                supabase.table("perfis_usuarios").update({"titulo": "❌ BANIDO"}).eq("username", usuario_alvo).execute()
                st.rerun()

        st.write("---")
        st.subheader("🎒 Gerenciador de Inventário (God Mode)")
        item_para_dar = st.text_input("Nome do Item para dar ao usuário:", placeholder="Ex: 🖼️ Moldura de Fogo 🔥")
        if st.button("🎁 Entregar Item para o Usuário", use_container_width=True):
            if item_para_dar:
                busca_user = supabase.table("perfis_usuarios").select("itens_exclusivos").eq("username", usuario_alvo).execute()
                if busca_user.data:
                    inventario_atual = busca_user.data[0].get('itens_exclusivos', [])
                    if not isinstance(inventario_atual, list): inventario_atual = []
                    inventario_atual.append(item_para_dar)
                    supabase.table("perfis_usuarios").update({"itens_exclusivos": inventario_atual}).eq("username", usuario_alvo).execute()
                    st.success(f"🎉 Item injetado!")
                    st.rerun()

        st.write("---")
        st.subheader("⚙️ Ações Globais")
        col_glob1, col_glob2 = st.columns(2)
        with col_glob1:
            valor_bonus = st.number_input("Valor do Bônus Global:", min_value=1, value=100)
            if st.button("💰 Dar Bônus para Todos", use_container_width=True):
                todos = supabase.table("perfis_usuarios").select("username, dinheiro").execute()
                for u in todos.data:
                    novo_saldo = u.get('dinheiro', 0) + valor_bonus
                    supabase.table("perfis_usuarios").update({"dinheiro": novo_saldo}).eq("username", u['username']).execute()
                st.success("Bônus global enviado!")
                st.rerun()
        with col_glob2:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🧹 APAGAR TODOS OS VÍDEOS", use_container_width=True):
                vids = supabase.table("feed_videos").select("id").execute()
                for v in vids.data: supabase.table("feed_videos").delete().eq("id", v['id']).execute()
                st.rerun()
