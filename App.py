import streamlit as st
from supabase import create_client, Client
import random

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2", page_icon="🚀", layout="centered")

# --- CONEXÃO COM SUPABASE ---
url = "https://ldjtqgeyorkzbvuichjj.supabase.co"
key = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Erro crítico: {str(e)}")
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

CODIGO_CORRETO = "ChatPrivado2026"

TITULOS = {
    "rafael_oficial": "👑 Desenvolvedor",
    "rafael_secundario": "⚔️ Vice-Dev",
    "amiga_divulgadora": "📢 Divulgadora",
}

# --- FUNÇÕES DE AUTENTICAÇÃO (RECUPERADAS!) ---
def criar_conta(username, password, nickname, codigo):
    if codigo != CODIGO_CORRETO:
        return "Código de convite inválido!"
    try:
        existe = supabase.table("perfis_usuarios").select("*").eq("username", username).execute()
        if existe.data:
            return "Este nome de usuário já está em uso."
        
        titulo = TITULOS.get(username, "Usuário")
        novo_usuario = {
            "username": username,
            "senha": password,
            "nickname": nickname,
            "titulo": titulo,
            "seguidores": 0,
            "seguindo": 0,
            "dinheiro": 0,
            "verificado": False,
            "foto_perfil": "https://cdn-icons-png.flaticon.com/512/149/149071.png",
            "bio": "Olá! Estou usando o Silver Tok.",
            "itens_exclusivos": []
        }
        supabase.table("perfis_usuarios").insert(novo_usuario).execute()
        return "Sucesso"
    except Exception as e:
        return f"Erro ao criar conta: {str(e)}"

# --- TELA DE LOGIN / CADASTRO (RECUPERADA!) ---
if not st.session_state.logado:
    st.title("Welcome to Silver Tok v2 🚀")
    aba_login, aba_cadastro = st.tabs(["🔐 Entrar", "📝 Criar Conta"])
    
    with aba_login:
        user_in = st.text_input("Usuário", key="login_user").strip()
        pass_in = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar", use_container_width=True):
            resultado = supabase.table("perfis_usuarios").select("*").eq("username", user_in).eq("senha", pass_in).execute()
            if resultado.data:
                st.session_state.logado = True
                st.session_state.user_data = resultado.data[0]
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
                
    with aba_cadastro:
        new_user = st.text_input("Escolha seu Usuário", key="cad_user").strip()
        new_nick = st.text_input("Nome de Exibição (Nickname)", key="cad_nick")
        new_pass = st.text_input("Escolha sua Senha", type="password", key="cad_pass")
        convite = st.text_input("Código de Convite Secreto", type="password", key="cad_code")
        
        if st.button("Cadastrar Nova Conta", use_container_width=True):
            if not new_user or not new_pass or not new_nick:
                st.warning("Preencha todos os campos!")
            else:
                status = criar_conta(new_user, new_pass, new_nick, convite)
                if status == "Sucesso":
                    st.success("Conta criada! Faça login ao lado.")
                else:
                    st.error(status)
    st.stop()

# Atualiza os dados do usuário logado em tempo real
def atualizar_sessao():
    res = supabase.table("perfis_usuarios").select("*").eq("username", st.session_state.user_data['username']).execute()
    if res.data:
        st.session_state.user_data = res.data[0]

atualizar_sessao()
user_atual = st.session_state.user_data

# BLOQUEIO DE MANUTENÇÃO
if ESTADO_DESENVOLVIMENTO and user_atual["titulo"] not in ["👑 Desenvolvedor", "🧪 Tester"]:
    st.title("🚧 Aplicativo em Manutenção")
    st.warning(f"Olá {user_atual['nickname']}, o Silver Tok v2 está em desenvolvimento.")
    if st.button("Sair da Conta"):
        st.session_state.logado = False
        st.rerun()
    st.stop()

# --- SIDEBAR ---
st.sidebar.image(user_atual.get('foto_perfil', ''), width=100)
st.sidebar.title(f"@{user_atual['username']}")
if st.sidebar.button("Sair da Conta"):
    st.session_state.logado = False
    st.rerun()

# --- MENU PRINCIPAL ---
abas = ["📱 Feed", "🎥 Gravar/Postar", "👤 Meu Perfil"]
if st.session_state.perfil_visitado:
    abas.append("👀 Ver Perfil")
if user_atual['username'] == "rafael_oficial":
    abas.append("⚡ Painel Dev")

aba_ativa = st.radio("Menu", abas, horizontal=True)
st.write("---")

# --- 1. ABA FEED ---
if aba_ativa == "📱 Feed":
    st.title("📱 Silver Tok")
    termo = st.text_input("🔍 Pesquisar...", "").strip().lower()
    
    try:
        req = supabase.table("feed_videos").select("*").order("id", desc=True).execute()
        videos = req.data
    except:
        videos = []

    for vid in videos:
        if not termo or termo in vid.get('legenda', '').lower() or termo in vid.get('username', '').lower():
            with st.container():
                # Cabeçalho do Post (Foto + Nome)
                autor_req = supabase.table("perfis_usuarios").select("foto_perfil").eq("username", vid['username']).execute()
                foto_autor = autor_req.data[0]['foto_perfil'] if autor_req.data else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                
                col_foto, col_nome = st.columns([1, 5])
                with col_foto:
                    st.image(foto_autor, width=50)
                with col_nome:
                    if st.button(f"**{vid['nickname']}** (@{vid['username']})", key=f"u_{vid['id']}"):
                        st.session_state.perfil_visitado = vid['username']
                        st.rerun()
                
                if vid.get('legenda'): st.write(vid['legenda'])
                st.video(vid['url_video'])
                
                # Interações
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button(f"❤️ {vid['curtidas']}", key=f"l_{vid['id']}", use_container_width=True):
                        supabase.table("feed_videos").update({"curtidas": vid['curtidas'] + 1}).eq("id", id_post).execute()
                        st.rerun()
                with c2:
                    if st.button("🔗 Copiar", key=f"s_{vid['id']}", use_container_width=True):
                        st.success("Link Copiado!")
                with c3:
                    abrir_comentarios = st.checkbox("💬 Comentários", key=f"tab_c_{id_post}")
                
                if abrir_comentarios:
                    st.write("**@pedro_dev:** Esse vídeo ficou brabo! 🔥")
                    st.text_input("Escreva um comentário...", key=f"inp_c_{id_post}")
                
                if user_atual['username'] == vid['username'] or user_atual['username'] == "rafael_oficial":
                    if st.button(f"🗑️ Apagar Vídeo", key=f"d_{vid['id']}", use_container_width=True):
                        supabase.table("feed_videos").delete().eq("id", vid['id']).execute()
                        st.rerun()
                st.write("---")

# --- 2. ABA GRAVAR/POSTAR ---
elif aba_ativa == "🎥 Gravar/Postar":
    st.title("🎥 Câmera Silver Tok")
    aba_cam, aba_link = st.tabs(["📸 Gravar com a Câmera", "🔗 Postar por Link"])
    
    with aba_cam:
        imagem_capturada = st.camera_input("Tirar foto/registro para o Feed")
        if imagem_capturada:
            st.success("Captura realizada com sucesso!")
            
    with aba_link:
        legenda = st.text_input("Legenda do post:")
        url_do_video = st.text_input("Link do vídeo (.mp4):")
        if st.button("Publicar Vídeo", use_container_width=True):
            supabase.table("feed_videos").insert({
                "username": user_atual['username'], "nickname": user_atual['nickname'],
                "legenda": legenda, "url_video": url_do_video, "curtidas": 0
            }).execute()
            st.success("Publicado no Feed!")

# --- 3. ABA MEU PERFIL (ESTILO INSTAGRAM/TIKTOK) ---
elif aba_ativa == "👤 Meu Perfil":
    col_foto, col_stats = st.columns([1, 2])
    with col_foto:
        st.image(user_atual.get('foto_perfil', 'https://cdn-icons-png.flaticon.com/512/149/149071.png'), width=140)
    with col_stats:
        st.header(user_atual['nickname'])
        st.write(f"**@{user_atual['username']}** | {user_atual['titulo']}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Seguidores", user_atual.get('seguidores', 0))
        c2.metric("Seguindo", user_atual.get('seguindo', 0))
        c3.metric("Carteira", f"${user_atual['dinheiro']}")
    
    st.write(f"📝 **Bio:** {user_atual.get('bio', '')}")
    
    expander = st.expander("⚙️ Editar Perfil")
    with expander:
        novo_nick = st.text_input("Mudar Nickname:", value=user_atual['nickname'])
        nova_bio = st.text_area("Mudar Bio:", value=user_atual.get('bio', ''))
        nova_foto = st.text_input("Link da Foto de Perfil:", value=user_atual.get('foto_perfil', ''))
        if st.button("Salvar Alterações"):
            supabase.table("perfis_usuarios").update({
                "nickname": novo_nick, "bio": nova_bio, "foto_perfil": nova_foto
            }).eq("username", user_atual['username']).execute()
            st.success("Perfil atualizado!")
            st.rerun()

    st.write("---")
    st.subheader("🎬 Meus Vídeos")
    meus_vids = supabase.table("feed_videos").select("*").eq("username", user_atual['username']).execute()
    for v in meus_vids.data: st.video(v['url_video'])

# --- 4. ABA VISITAR PERFIL ALHEIO ---
elif aba_ativa == "👀 Ver Perfil" and st.session_state.perfil_visitado:
    alvo = st.session_state.perfil_visitado
    res = supabase.table("perfis_usuarios").select("*").eq("username", alvo).execute()
    if res.data:
        p = res.data[0]
        col_f, col_s = st.columns([1, 2])
        with col_f: st.image(p.get('foto_perfil', 'https://cdn-icons-png.flaticon.com/512/149/149071.png'), width=120)
        with col_s:
            st.header(p['nickname'])
            st.write(f"@{p['username']} | {p['titulo']}")
            st.write(f"👥 {p.get('seguidores', 0)} Seguidores")
        
        st.write(f"📝 {p.get('bio', '')}")
        if st.button("Voltar ao Feed"):
            st.session_state.perfil_visitado = None
            st.rerun()
        st.write("---")
        vids = supabase.table("feed_videos").select("*").eq("username", alvo).execute()
        for v in vids.data: st.video(v['url_video'])

# --- 5. PAINEL DEV (GOD MODE RECUPERADO!) ---
elif aba_ativa == "⚡ Painel Dev" and user_atual['username'] == "rafael_oficial":
    st.header("Painel Secreto do Desenvolvedor 👑")
    try:
        usuarios_req = supabase.table("perfis_usuarios").select("username, nickname").execute()
        lista_usuarios = [u["username"] for u in usuarios_req.data]
    except:
        lista_usuarios = []

    if lista_usuarios:
        usuario_alvo = st.selectbox("Selecione o usuário:", lista_usuarios)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("👥 Seguidores")
            qtd_seguidores = st.number_input("Quantidade", min_value=0, value=1000)
            if st.button("Definir", key="btn_seg"):
                supabase.table("perfis_usuarios").update({"seguidores": qtd_seguidores, "verificado": qtd_seguidores >= 1000}).eq("username", usuario_alvo).execute()
                st.rerun()

        with col2:
            st.subheader("💰 Carteira")
            qtd_dinheiro = st.number_input("Dinheiro ($)", min_value=0, value=500)
            if st.button("Definir", key="btn_money"):
                supabase.table("perfis_usuarios").update({"dinheiro": qtd_dinheiro}).eq("username", usuario_alvo).execute()
                st.rerun()

        with col3:
            st.subheader("🎖️ Cargos")
            novo_titulo = st.selectbox("Cargo:", ["👑 Desenvolvedor", "⚔️ Vice-Dev", "📢 Divulgadora", "🧪 Tester", "Usuário",  "🥇 best friends of the dev" ])
            if st.button("Atualizar", key="btn_cargo"):
                supabase.table("perfis_usuarios").update({"titulo": novo_titulo}).eq("username", usuario_alvo).execute()
                st.rerun()
    
