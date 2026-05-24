import streamlit as st
from supabase import create_client, Client
import uuid

# Configuração da tela para parecer um celular
st.set_page_config(page_title="Mini TikTok", page_icon="📱", layout="centered")

# --- CONEXÃO COM O BANCO ---
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Erro ao conectar ao banco de dados.")

st.title("📱 Meu Clone do TikTok")

# --- ABAS: ASSISTIR VS POSTAR ---
abas = st.tabs(["🔥 Feed de Vídeos", "📤 Postar Novo Vídeo"])

# 1️⃣ ABA DO FEED (ASSISTIR)
with abas[0]:
    try:
        # Busca os vídeos mais recentes no banco
        dados = supabase.table("feed_videos").select("*").order("created_at", desc=True).execute()
        
        if dados.data:
            for video in dados.data:
                st.markdown(f"### 👤 Postado por Usuário")
                
                # Exibe o player de vídeo do Streamlit
                st.video(video["url_video"])
                
                st.write(f"📝 **Legenda:** {video['titulo']}")
                
                # Sistema de curtidas simples
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"❤️ {video['curtidas']}", key=f"like_{video['id']}"):
                        nova_curtida = video['curtidas'] + 1
                        supabase.table("feed_videos").update({"curtidas": nova_curtida}).eq("id", video['id']).execute()
                        st.rerun()
                
                st.markdown("---")
        else:
            st.info("Nenhum vídeo no feed ainda. Seja o primeiro a postar na outra aba!")
    except Exception as e:
        st.write("Crie a tabela 'feed_videos' no Supabase para ver o feed.")

# 2️⃣ ABA DE UPLOAD (POSTAR)
with abas[1]:
    st.subheader("Envie um vídeo curto (.mp4)")
    legenda = st.text_input("Digite uma legenda marcante:")
    arquivo_video = st.file_uploader("Escolha o arquivo de vídeo:", type=["mp4", "mov"])
    
    if st.button("Publicar Vídeo 🚀"):
        if arquivo_video and legenda:
            try:
                # 1. Envia o arquivo de vídeo para o Storage do Supabase
                nome_arquivo = f"feed/{uuid.uuid4()}.mp4"
                supabase.storage.from_("videos_tiktok").upload(nome_arquivo, arquivo_video.read(), file_options={"content-type": "video/mp4"})
                
                # 2. Pega o link público do vídeo que foi enviado
                url_publica = supabase.storage.from_("videos_tiktok").get_public_url(nome_arquivo)
                
                # 3. Salva o link e a legenda na tabela do banco dados
                supabase.table("feed_videos").insert({
                    "titulo": legenda,
                    "url_video": url_publica,
                    "curtidas": 0
                }).execute()
                
                st.success("Vídeo publicado com sucesso! Vá para a aba do Feed para assistir.")
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")
        else:
            st.warning("Por favor, selecione um vídeo e digite uma legenda!")
      
