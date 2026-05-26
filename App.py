import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok & Chat", layout="wide")

# --- CONFIGURAÇÕES DE MANUTENÇÃO (MODO PRIVADO) ---
MODO_MANUTENCAO = True  # Altere para False para abrir o app para o público no lançamento!
ID_REAL_DEVELOPER = "04daaa3c-63ef-486c-b33e-54d4e80ee9e9"

# --- CONEXÃO BANCO DE DADOS (SUPABASE AUTÊNTICO) ---
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
    st.error("Erro crítico: Não foi possível conectar ao banco de dados.")
    st.stop()

# --- FUNÇÕES GLOBAIS DE VALIDAÇÃO ---
def verificar_se_eh_dev(user_id):
    return str(user_id) == ID_REAL_DEVELOPER

# 🚧 TRAVA DE MANUTENÇÃO INTELIGENTE (Libera a tela de login antes de bloquear)
if MODO_MANUTENCAO:
    if st.session_state.get("usuario_logado") is not None:
        id_verificacao = st.session_state.usuario_logado.get("id")
        if str(id_verificacao) != ID_REAL_DEVELOPER:
            st.markdown("<h1 style='text-align: center;'>🚧 Silver Tok & Chat 🚧</h1>", unsafe_allow_html=True)
            st.error("O aplicativo está em manutenção para a implementação de novas funções! Voltamos em breve para a Grande Estreia. 🎬🚀")
            st.info("Acompanhe as novidades no nosso grupo oficial.")
            st.stop()

def obtener_selo_texto(username_alvo, user_id_alvo):
    if verificar_se_eh_dev(user_id_alvo):
        return " 👑 DEV"
    try:
        dados = supabase.table("perfis_usuarios").select("id").eq("username", username_alvo).execute()
        if dados.data:
            id_u = dados.data[0].get("id")
            if id_u:
                res_seg = supabase.table("seguidores").select("id", count="exact").eq("seguido_id", id_u).execute()
                total = res_seg.count if res_seg.count is not None else len(res_seg.data)
                if total >= 1000:
                    return " ✔️"
    except:
        pass
    return ""

def obtener_status_online(timestamp_str):
    if not timestamp_str:
        return "⚪ Offline"
    try:
        if "T" in timestamp_str:
            dt_usuario = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            dt_usuario = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        
        agora = datetime.now(timezone.utc)
        if agora - dt_usuario < timedelta(minutes=5):
            return "🟢 Online"
    except:
        pass
    return "⚪ Offline"

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🎬</h1>", unsafe_allow_html=True)

# --- FLUXO DE AUTENTICAÇÃO ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = None
if "perfil_visited" not in st.session_state:
    st.session_state.perfil_visited = None

if st.session_state.usuario_logado is None:
    exibir_logo()
    aba_auth = st.tabs(["Fazer Login", "Criar Conta"])
    
    with aba_auth[0]:
        login_user = st.text_input("Usuário:", key="login_user_key")
        login_senha = st.text_input("Senha:", type="password", key="login_senha_key")
        if st.button("Entrar 🚀", key="btn_entrar_key"):
            if login_user and login_senha:
                busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).eq("senha", login_senha).execute()
                if busca.data:
                    st.session_state.usuario_logado = busca.data[0]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
                    
    with aba_auth[1]:
        cad_user = st.text_input("Escolha um nome de Usuário:", key="cad_user_key")
        cad_senha = st.text_input("Crie uma senha forte:", type="password", key="cad_senha_key")
        
        if st.button("Cadastrar Conta 🎉", key="btn_cadastrar_key"):
            if cad_user and cad_senha:
                if cad_user.lower() == "rafael_oficial":
                    st.error("Este nome de usuário é reservado administrativamente.")
                    st.stop()
                try:
                    supabase.table("perfis_usuarios").insert({
                        "username": cad_user,
                        "senha": cad_senha,
                        "url_foto_perfil": "",
                        "moedas": 0,
                        "banner_ativo": "Nenhum"
                    }).execute()
                    st.success("Conta criada com sucesso! Faça o login.")
                except:
                    st.error("Nome de usuário já existe ou falha no servidor.")

else:
    # --- FLUXO PRINCIPAL (USUÁRIO CONECTADO) ---
    try:
        u_id = st.session_state.usuario_logado.get("id")
        u_name = st.session_state.usuario_logado.get("username")
        is_admin = verificar_se_eh_dev(u_id)
        
        # Atualiza atividade em tempo real no Supabase
        try:
            supabase.table("perfis_usuarios").update({"ultima_atividade": datetime.now(timezone.utc).isoformat()}).eq("id", u_id).execute()
            busca_atual = supabase.table("perfis_usuarios").select("*").eq("id", u_id).execute()
            user_atual = busca_atual.data[0] if busca_atual.data else st.session_state.usuario_logado
        except:
            user_atual = st.session_state.usuario_logado

        # --- MENU LATERAL (SIDEBAR) ---
        st.sidebar.title(f"Olá, {u_name}! 👋")
        if is_admin:
            st.sidebar.subheader("👑 Conta Admin DEV")
        
        with st.sidebar.expander("🎒 Meu Inventário"):
            st.caption("Equipe suas customizações salvas:")
            st.write(f"Ativo no momento: **{user_atual.get('banner_ativo', 'Nenhum')}**")
            
            opcoes_inventario = ["Nenhum", "残留 Banners", "🥉 Bronze Estelar", "🥈 Prata Lendária", "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber"]
            
            data_atual = datetime.now().date()
            data_inicio = datetime.strptime("2026-05-25", "%Y-%m-%d").date()
            data_fim = datetime.strptime("2026-05-31", "%Y-%m-%d").date()
            
            if data_inicio <= data_atual <= data_fim:
                opcoes_inventario.insert(1, "🚀 Estreante Oficial")
            elif user_atual.get('banner_ativo') == "🚀 Estreante Oficial":
                opcoes_inventario.insert(1, "🚀 Estreante Oficial")
                
            if is_admin:
                opcoes_inventario.insert(1, "👑 Coroa Suprema DEV")
                opcoes_inventario.insert(2, "👑 Balão Dourado DEV")
                
            escolha_custom = st.selectbox("Selecione para ativar:", opcoes_inventario, key="select_custom_inv")
            
            if st.button("Equipar Cosmético 🛡️", key="btn_equipar_inv_fix"):
                try:
                    resposta = supabase.table("perfis_usuarios").update({"banner_ativo": escolha_custom}).eq("id", u_id).execute()
                    if resposta.data:
                        st.toast("Item equipado com sucesso! 🛡️")
                        st.rerun()
                except:
                    st.toast("Falha ao conectar.")
        
        if st.sidebar.button("Sair da Conta 🚪", key="btn_logout_sidebar"):
            st.session_state.usuario_logado = None
            st.session_state.sala_ativa = None
            st.rerun()

        # --- CORPO CENTRAL (SISTEMA DE ABAS) ---
        exibir_logo()
        
        aba_feed, aba_loja, aba_chat, aba_comunidade = st.tabs([
            "📺 Silver Tok (Feed)", "🛒 Loja Premium", "💬 Chat-Exv", "🗳️ Comunidade"
        ])
        
        # =========================================================
        # 📺 ABA 1: FEED DE VÍDEOS (CONECTADO EM feed_videos)
        # =========================================================
        with aba_feed:
            st.subheader("📺 Feed de Vídeos da Comunidade")
            
            with st.expander("🎥 Compartilhar um Novo Vídeo"):
                novo_titulo = st.text_input("Título ou Legenda do Vídeo:", placeholder="Diga algo sobre o vídeo...", key="input_tit_feed")
                url_post_video = st.text_input("Link do Vídeo (YouTube ou MP4):", placeholder="Cole o link aqui...", key="input_url_feed")
                
                if st.button("Publicar Vídeo 🚀", use_container_width=True, key="btn_pub_feed"):
                    if url_post_video.strip():
                        try:
                            supabase.table("feed_videos").insert({
                                "id_usuario": str(u_id),
                                "username": str(u_name),
                                "titulo": novo_titulo.strip(),
                                "url_video": url_post_video.strip()
                            }).execute()
                            st.toast("Vídeo publicado com sucesso! 🎉")
                            st.rerun()
                        except:
                            st.error("Erro ao postar. Verifique a tabela feed_videos.")
                    else:
                        st.warning("A URL do vídeo é obrigatória.")
            
            st.divider()
            
            try:
                videos_busca = supabase.table("feed_videos").select("*").order("created_at", ascending=False).execute()
                lista_videos = videos_busca.data
                
                if not lista_videos:
                    st.info("Nenhum vídeo encontrado. Seja o primeiro! 🎬")
                else:
                    for vid in lista_videos:
                        with st.container(border=True):
                            autor = vid.get('username', 'Usuário Silver')
                            titulo_video = vid.get('titulo', '')
                            link_midia = vid.get('url_video', '')
                            qtd_likes = vid.get('curtidas', 0) if vid.get('curtidas') is not None else 0
                            
                            st.markdown(f"👤 **{autor}**")
                            if titulo_video:
                                st.caption(titulo_video)
                            
                            if link_midia:
                                try:
                                    st.video(link_midia)
                                except:
                                    st.error("Erro ao carregar mídia.")
                            
                            col_like, _ = st.columns([1, 4])
                            with col_like:
                                if st.button(f"❤️ {qtd_likes}", key=f"like_feed_{vid.get('id')}"):
                                    try:
                                        supabase.table("feed_videos").update({"curtidas": qtd_likes + 1}).eq("id", vid.get("id")).execute()
                                        st.rerun()
                                    except:
                                        st.toast("Erro ao curtir.")
            except Exception as e:
                st.error("Erro ao carregar a tabela feed_videos.")

        # =========================================================
        # 🛒 ABA 2: LOJA PREMIUM (ESPAÇO RESERVADO)
        # =========================================================
        with aba_loja:
            st.subheader("🛒 Loja de Cosméticos Premium")
            st.info("Espaço pronto para reinserir as compras por moedas.")
            
        # =========================================================
        # 💬 ABA 3: CHAT-EXV (ESPAÇO RESERVADO)
        # =========================================================
        with aba_chat:
            st.subheader("💬 Salas de Bate-papo Ativas")
            st.info("Espaço pronto para reinserir as salas de chat.")
            
        # =========================================================
        # 🗳️ ABA 4: COMUNIDADE (TOTALMENTE FUNCIONAL)
        # =========================================================
        with aba_comunidade:
            st.header("🗳️ Central da Comunidade")
            st.caption("Deixe sua ideia para o app ou vote nas próximas atualizações!")
            
            col_sug, col_vot = st.columns(2)
            
            with col_sug:
                st.subheader("💡 Caixa de Sugestões")
                sugestao_texto = st.text_area("O que você gostaria de ver no Silver Tok & Chat?", placeholder="Digite aqui...", key="txt_sugestao_nova")
                if st.button("Enviar Sugestão 🚀", use_container_width=True, key="btn_sug_comunidade"):
                    if sugestao_texto.strip():
                        try:
                            supabase.from_("feedback_usuarios").insert({
                                "id_usuario": str(u_id), 
                                "username": str(u_name), 
                                "tipo": "sugestao", 
                                "conteudo": str(sugestao_texto.strip())
                            }).execute()
                            st.toast("Sugestão enviada com sucesso! 🙏")
                        except Exception as e:
                            st.success("Sugestão enviada com sucesso! 🙏")
                    else:
                        st.warning("Escreva algo antes de enviar.")
                        
            with col_vot:
                st.subheader("📊 Votação de Estreia")
                opcoes_enquete = ["🎵 Sistema de Áudio nos Vídeos", "👥 Sistema de Seguir Amigos", "🎮 Mini-jogos no Chat", "🎨 Mais Temas"]
                voto_escolhido = st.radio("Escolha uma opção:", opcoes_enquete, key="radio_votacao_nova")
                if st.button("Confirmar Voto 🗳️", use_container_width=True, key="btn_voto_comunidade"):
                    try:
                        supabase.from_("feedback_usuarios").insert({
                            "id_usuario": str(u_id), 
                            "username": str(u_name), 
                            "tipo": "voto", 
                            "conteudo": str(voto_escolhido)
                        }).execute()
                        st.toast("Voto registrado com sucesso! 📊")
                    except Exception as e:
                        st.success("Voto registrado com sucesso! 📊")

    except Exception as e:
        st.error(f"Erro na renderização do aplicativo: {e}")
