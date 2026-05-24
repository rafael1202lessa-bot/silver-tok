import streamlit as st
from supabase import create_client, Client
import uuid

st.set_page_config(page_title="Silver Tok v2.0", page_icon="🎬", layout="centered")

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
    st.error("Erro de conexão.")
    st.stop()

CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = None
if "id_upload_chat" not in st.session_state:
    st.session_state.id_upload_chat = str(uuid.uuid4())
if "id_upload_video" not in st.session_state:
    st.session_state.id_upload_video = str(uuid.uuid4())

if st.session_state.usuario_logado is None:
    st.title("🎬 Silver Tok & Chat 🔐")
    aba_auth = st.tabs(["Fazer Login", "Criar Nova Conta"])
    with aba_auth[0]:
        st.subheader("Acesse sua Conta")
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        if st.button("Entrar 🚀", key="btn_login", use_container_width=True):
            if login_user and login_senha:
                busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                if busca.data and busca.data[0]["senha"] == login_senha:
                    st.session_state.usuario_logado = busca.data[0]
                    st.success("Login feito!")
                    st.rerun()
                else:
                    st.error("Incorreto.")
            else:
                st.warning("Preencha tudo!")
    with aba_auth[1]:
        st.subheader("Crie seu Perfil")
        cad_user = st.text_input("Escolha Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie Senha:", type="password", key="cad_senha")
        codigo_convite = st.text_input("🔑 Código Secreto:", type="password", key="codigo_convite")
        if st.button("Cadastrar Conta 🎉", key="btn_cad", use_container_width=True):
            if cad_user and cad_senha and codigo_convite == CHAVE_SECRETA:
                try:
                    supabase.table("perfis_usuarios").insert({"username": cad_user, "senha": cad_senha, "url_foto_perfil": FOTO_PADRAO}).execute()
                    st.success("Criado! Faça login.")
                except:
                    st.error("Erro ou usuário já existe.")
            else:
                st.warning("Verifique os campos e o código!")
                else:
    user_atual = st.session_state.usuario_logado
    st.sidebar.image(FOTO_PADRAO, width=90)
    st.sidebar.write(f"Usuário: **{user_atual['username']}**")
    if st.sidebar.button("Sair 🚪", use_container_width=True):
        st.session_state.usuario_logado = None
        st.rerun()

    aba_feed, aba_chat = st.tabs(["📺 Silver Tok (Feed)", "💬 Chat-Exv"])

    with aba_feed:
        st.title("📺 Feed de Edits")
        with st.expander("➕ Publicar Vídeo"):
            titulo_v = st.text_input("Legenda:", placeholder="Edit top!")
            arq_v = st.file_uploader("Vídeo (MP4):", type=["mp4"], key=st.session_state.id_upload_video)
            if st.button("Publicar 🚀", use_container_width=True):
                if arq_v and titulo_v:
                    nome_f = f"videos/{uuid.uuid4()}.mp4"
                    supabase.storage.from_("videos_feed").upload(nome_f, arq_v.read())
                    url_f = supabase.storage.from_("videos_feed").get_public_url(nome_f)
                    supabase.table("feed_videos").insert({"titulo": titulo_v, "url_video": url_f, "username_autor": user_atual["username"], "curtidas": 0}).execute()
                    st.success("Postado!")
                    st.session_state.id_upload_video = str(uuid.uuid4())
                    st.rerun()

        try:
            dados = supabase.table("feed_videos").select("*").execute()
            if dados.data:
                for v in reversed(dados.data):
                    st.markdown(f"**@{v.get('username_autor', 'Membro')}** - {v['titulo']}")
                    st.video(v["url_video"])
                    likes = v.get("curtidas", 0)
                    if st.button(f"❤️ {likes} Curtidas", key=f"lk_{v['id']}"):
                        supabase.table("feed_videos").update({"curtidas": likes + 1}).eq("id", v["id"]).execute()
                        st.rerun()
                    st.markdown("---")
        except:
            st.error("Erro ao carregar o feed.")

    with aba_chat:
        st.title("💬 Chat Geral")
        txt_m = st.text_input("Sua mensagem:", key="msg_geral")
        if st.button("Enviar Msg ✉️", use_container_width=True) and txt_m.strip():
            supabase.table("bate-papo_profissional").insert({"id_usuario": user_atual["id"], "username": user_atual["username"], "mensagem": txt_m.strip(), "codigo_sala": "GERAL"}).execute()
            st.rerun()

        try:
            msgs = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", "GERAL").execute()
            if msgs.data:
                for m in reversed(msgs.data[-30:]):
                    st.markdown(f"**{m['username']}:** {m['mensagem']}")
        except:
            st.error("Erro ao carregar chat.")
            
