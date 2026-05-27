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
    st.error(f"Erro crítico na inicialização do Supabase: {str(e)}")
    st.stop()

# --- ESTADO DE DESENVOLVIMENTO ---
ESTADO_DESENVOLVIMENTO = True 

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "perfil_visitado" not in st.session_state:
    st.session_state.perfil_visitado = None

CODIGO_CORRETO = "ChatPrivado2026"

# --- TELA DE LOGIN / CADASTRO ---
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
                st.error("Incorreto.")
    st.stop()

user_atual = st.session_state.user_data

# BLOQUEIO DE MANUTENÇÃO
if ESTADO_DESENVOLVIMENTO and user_atual["titulo"] not in ["👑 Desenvolvedor", "🧪 Tester"]:
    st.title("🚧 Aplicativo em Manutenção")
    st.stop()

# --- SIDEBAR COM SEU PERFIL ---
st.sidebar.title(f"@{user_atual['username']}")
st.sidebar.write(f" Carteira: ${user_atual['dinheiro']}")
if st.sidebar.button("Sair da Conta"):
    st.session_state.logado = False
    st.rerun()

# --- MENU PRINCIPAL ---
abas = ["📱 Feed", "🎥 Gravar/Postar", "💬 Chat", "👤 Meu Perfil"]
if st.session_state.perfil_visitado:
    abas.append("👀 Ver Perfil")

aba_ativa = st.radio("Menu", abas, horizontal=True)
st.write("---")

# --- 1. ABA FEED ---
if aba_ativa == "📱 Feed":
    st.title("📱 Silver Tok Feed")
    
    termo_pesquisa = st.text_input("🔍 Pesquisar vídeos por legenda ou usuário:", "").strip().lower()
    st.write("---")
    
    try:
        req = supabase.table("feed_videos").select("*").order("id", desc=True).execute()
        videos = req.data
    except:
        videos = []

    if not videos:
        st.info("Nenhum vídeo no feed.")
    else:
        videos_filtrados = []
        for vid in videos:
            legenda = vid.get('legenda', '').lower()
            username = vid.get('username', '').lower()
            nickname = vid.get('nickname', '').lower()
            
            if not termo_pesquisa or (termo_pesquisa in legenda or termo_pesquisa in username or termo_pesquisa in nickname):
                videos_filtrados.append(vid)

        if not videos_filtrados:
            st.warning(f"Nenhum vídeo encontrado para '{termo_pesquisa}'.")
        else:
            for vid in videos_filtrados:
                username_post = vid.get('username', 'anonimo')
                nickname_post = vid.get('nickname', 'Usuário')
                legenda_post = vid.get('legenda', '')
                url_video_post = vid.get('url_video', '')
                curtidas_post = vid.get('curtidas', 0)
                id_post = vid.get('id')

                with st.container():
                    if st.button(f"👤 {nickname_post} (@{username_post})", key=f"user_{id_post}"):
                        st.session_state.perfil_visitado = username_post
                        st.info(f"Carregando perfil... Clique na aba '👀 Ver Perfil' no topo!")
                    
                    if legenda_post:
                        st.write(f" {legenda_post}")
                    
                    if url_video_post:
                        st.video(url_video_post)
                    
                    # --- BOTÕES DE INTERAÇÃO ---
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button(f"❤️ {curtidas_post}", key=f"l_{id_post}", use_container_width=True):
                            supabase.table("feed_videos").update({"curtidas": curtidas_post + 1}).eq("id", id_post).execute()
                            st.rerun()
                    with c2:
                        if st.button("🔗 Copiar", key=f"s_{id_post}", use_container_width=True):
                            st.success("Link Copiado!")
                    with c3:
                        abrir_comentarios = st.checkbox("💬 Comentários", key=f"tab_c_{id_post}")
                    
                    if abrir_comentarios:
                        st.write("**@rafael_oficial:** Esse vídeo ficou brabo! 🔥")
                        st.text_input("Escreva um comentário...", key=f"inp_c_{id_post}")
                    
                    # --- 🗑️ NOVIDADE: FUNÇÃO DE DELETAR VÍDEO SEGURA ---
                    # Só mostra o botão se quem está vendo for o dono do post OU se for você (rafael_oficial)
                    if user_atual['username'] == username_post or user_atual['username'] == "rafael_oficial":
                        st.write("") # Apenas um espacinho visual
                        if st.button(f"🗑️ Apagar meu vídeo", key=f"del_{id_post}", use_container_width=True):
                            try:
                                supabase.table("feed_videos").delete().eq("id", id_post).execute()
                                st.success("Vídeo removido com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao deletar: {str(e)}")
                    
                    st.write("================")

# --- 2. ABA GRAVAR VÍDEO ---
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
            novo_post = {
                "username": user_atual['username'],
                "nickname": user_atual['nickname'],
                "legenda": legenda,
                "url_video": url_do_video,
                "curtidas": 0
            }
            supabase.table("feed_videos").insert(novo_post).execute()
            st.success("Publicado no Feed!")

# --- 3. ABA VISITAR PERFIL ALHEIO ---
elif aba_ativa == "👀 Ver Perfil" and st.session_state.perfil_visitado:
    alvo = st.session_state.perfil_visitado
    st.title(f"👤 Perfil de @{alvo}")
    perfil_req = supabase.table("perfis_usuarios").select("*").eq("username", alvo).execute()
    
    if perfil_req.data:
        p_dados = perfil_req.data[0]
        st.write(f"**Nome:** {p_dados.get('nickname')}")
        st.write(f"**Cargo:** {p_dados.get('titulo', 'Usuário')}")
        st.write(f"**Seguidores:** {p_dados.get('seguidores', 0)} 👥")
        
        st.write("---")
        st.subheader("🎥 Vídeos Publicados por este usuário")
        vids_req = supabase.table("feed_videos").select("*").eq("username", alvo).execute()
        for v in vids_req.data:
            st.write(f"💬 {v.get('legenda')}")
            st.video(v.get('url_video'))
            st.write("---")
    
    if st.button("Fechar Perfil e Voltar"):
        st.session_state.perfil_visitado = None
        st.rerun()

elif aba_ativa == "💬 Chat":
    st.title("💬 Mensagens Privadas")
    st.info("Preparando servidores para a função de Live e Chat!")

elif aba_ativa == "👤 Meu Perfil":
    st.title("👤 Seu Perfil")
    st.json(user_atual)
    
