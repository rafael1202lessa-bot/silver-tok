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

# --- TELA DE LOGIN ---
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

# Atualiza os dados do usuário logado em tempo real
def atualizar_sessao():
    res = supabase.table("perfis_usuarios").select("*").eq("username", st.session_state.user_data['username']).execute()
    if res.data:
        st.session_state.user_data = res.data[0]

atualizar_sessao()
user_atual = st.session_state.user_data

# --- SIDEBAR ---
st.sidebar.image(user_atual.get('foto_perfil', ''), width=100)
st.sidebar.title(f"@{user_atual['username']}")
if st.sidebar.button("Sair da Conta"):
    st.session_state.logado = False
    st.rerun()

# --- MENU PRINCIPAL ---
abas = ["📱 Feed", "🎥 Postar", "👤 Meu Perfil"]
if st.session_state.perfil_visitado:
    abas.append("👀 Ver Perfil")

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
                # Buscamos a foto de quem postou
                autor_req = supabase.table("perfis_usuarios").select("foto_perfil").eq("username", vid['username']).execute()
                foto_autor = autor_req.data[0]['foto_perfil'] if autor_req.data else ""
                
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
                    if st.button(f"❤️ {vid['curtidas']}", key=f"l_{vid['id']}"):
                        supabase.table("feed_videos").update({"curtidas": vid['curtidas'] + 1}).eq("id", vid['id']).execute()
                        st.rerun()
                
                if user_atual['username'] == vid['username'] or user_atual['username'] == "rafael_oficial":
                    if st.button(f"🗑️ Apagar", key=f"d_{vid['id']}"):
                        supabase.table("feed_videos").delete().eq("id", vid['id']).execute()
                        st.rerun()
                st.write("---")

# --- 2. ABA POSTAR ---
elif aba_ativa == "🎥 Postar":
    st.title("🎥 Novo Post")
    legenda = st.text_input("Legenda:")
    url_vid = st.text_input("Link do vídeo (.mp4):")
    if st.button("Publicar"):
        supabase.table("feed_videos").insert({
            "username": user_atual['username'], "nickname": user_atual['nickname'],
            "legenda": legenda, "url_video": url_vid, "curtidas": 0
        }).execute()
        st.success("Postado!")

# --- 3. ABA MEU PERFIL (ESTILO INSTAGRAM) ---
elif aba_ativa == "👤 Meu Perfil":
    # Cabeçalho do Perfil
    col_foto, col_stats = st.columns([1, 2])
    
    with col_foto:
        st.image(user_atual.get('foto_perfil', ''), width=150)
    
    with col_stats:
        st.header(user_atual['nickname'])
        st.write(f"**@{user_atual['username']}** | {user_atual['titulo']}")
        
        # Contadores estilo Social Media
        c1, c2, c3 = st.columns(3)
        c1.metric("Seguidores", user_atual.get('seguidores', 0))
        c2.metric("Seguindo", user_atual.get('seguindo', 0))
        c3.metric("Carteira", f"${user_atual['dinheiro']}")
    
    st.write(f"📝 **Bio:** {user_atual.get('bio', '')}")
    
    # Botão para Editar
    expander = st.expander("⚙️ Editar Perfil")
    with expander:
        novo_nick = st.text_input("Mudar Nickname:", value=user_atual['nickname'])
        nova_bio = st.text_area("Mudar Bio:", value=user_atual.get('bio', ''))
        nova_foto = st.text_input("Link da Foto de Perfil:", value=user_atual.get('foto_perfil', ''))
        
        if st.button("Salvar Alterações"):
            supabase.table("perfis_usuarios").update({
                "nickname": novo_nick,
                "bio": nova_bio,
                "foto_perfil": nova_foto
            }).eq("username", user_atual['username']).execute()
            st.success("Perfil atualizado!")
            st.rerun()

    st.write("---")
    st.subheader("🎬 Meus Vídeos")
    meus_vids = supabase.table("feed_videos").select("*").eq("username", user_atual['username']).execute()
    for v in meus_vids.data:
        st.video(v['url_video'])

# --- 4. VISITAR PERFIL ---
elif aba_ativa == "👀 Ver Perfil" and st.session_state.perfil_visitado:
    alvo = st.session_state.perfil_visitado
    res = supabase.table("perfis_usuarios").select("*").eq("username", alvo).execute()
    if res.data:
        p = res.data[0]
        col_f, col_s = st.columns([1, 2])
        with col_f: st.image(p.get('foto_perfil', ''), width=120)
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
                
