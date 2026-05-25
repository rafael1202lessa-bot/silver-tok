import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok & Chat", layout="wide")

# --- CONFIGURAÇÕES DE MANUTENÇÃO (MODO PRIVADO) ---
MODO_MANUTENCAO = True  # Altere para False quando o app for lançado oficialmente!
ID_REAL_DEVELOPER = "04daaa3c-63ef-486c-b33e-54d4e80ee9e9"

# --- CONEXÃO BANCO DE DADOS (SUPABASE) ---
# Adicione suas chaves reais aqui dentro das aspas abaixo:
SUPABASE_URL = "https://ldjtqgeyorkzbvuixxxx.supabase.co"  
SUPABASE_KEY = "sb_publishable_ZWy9Hp6kQxxxx..."         

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

# 🚧 TRAVA ISOLADA DE MANUTENÇÃO (Roda no início para barrar o público)
if MODO_MANUTENCAO:
    id_verificacao = st.session_state.get("usuario_logado", {}).get("id") if st.session_state.get("usuario_logado") else None
    if str(id_verificacao) != ID_REAL_DEVELOPER:
        st.markdown("<h1 style='text-align: center;'>🚧 Silver Tok & Chat 🚧</h1>", unsafe_allow_html=True)
        st.error("O aplicativo está em manutenção para a implementação de novas funções! Voltamos em breve para a Grande Estreia. 🎬🚀")
        st.info("Acompanhe as novidades no nosso grupo oficial.")
        st.stop()

def obter_selo_texto(username_alvo, user_id_alvo):
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

def obter_status_online(timestamp_str):
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
        
        # Atualiza atividade em tempo real
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
        
        with aba_feed:
            st.subheader("📺 Feed Recentes")
            st.info("Espaço reservado para carregar seus vídeos do banco de dados.")
            # Insira o código original do seu feed aqui mais tarde
            
        with aba_loja:
            st.subheader("🛒 Loja de Cosméticos Premium")
            st.info("Espaço reservado para o sistema de compra de Banners e Tags.")
            # Insira o código original da sua loja aqui mais tarde
            
        with aba_chat:
            st.subheader("💬 Salas de Bate-papo Ativas")
            st.info("Espaço reservado para o envio de mensagens, imagens e áudios.")
            # Insira o código original do seu chat aqui mais tarde
            
        with aba_comunidade:
            st.header("🗳️ Central da Comunidade")
            st.caption("Deixe sua ideia para o app ou vote nas próximas atualizações!")
            
            col_sug, col_vot = st.columns(2)
            
            with col_sug:
                st.subheader("💡 Caixa de Sugestões")
                sugestao_texto = st.text_area("O que você gostaria de ver no Silver Tok & Chat?", placeholder="Digite aqui...", key="txt_sugestao")
                if st.button("Enviar Sugestão 🚀", use_container_width=True):
                    if sugestao_texto.strip():
                        try:
                            supabase.table("feedback_usuarios").insert({"id_usuario": u_id, "username": u_name, "tipo": "sugestao", "conteudo": sugestao_texto.strip()}).execute()
                            st.toast("Sugestão enviada com sucesso! 🙏")
                        except:
                            st.error("Erro ao salvar no banco.")
                    else:
                        st.warning("Escreva algo antes de enviar.")
                        
            with col_vot:
                st.subheader("📊 Votação de Estreia")
                opcoes_enquete = ["🎵 Sistema de Áudio nos Vídeos", "👥 Sistema de Seguir Amigos", "🎮 Mini-jogos no Chat", "🎨 Mais Temas"]
                voto_escolhido = st.radio("Escolha uma opção:", opcoes_enquete, key="radio_votacao")
                if st.button("Confirmar Voto 🗳️", use_container_width=True):
                    try:
                        ja_votou = supabase.table("feedback_usuarios").select("*").eq("id_usuario", u_id).eq("tipo", "voto").execute()
                        if ja_votou.data:
                            st.warning("Você já deixou o seu voto!")
                        else:
                            supabase.table("feedback_usuarios").insert({"id_usuario": u_id, "username": u_name, "tipo": "voto", "conteudo": voto_escolhido}).execute()
                            st.toast("Voto registrado com sucesso! 📊")
                    except:
                        st.error("Erro ao registrar voto.")

    except Exception as e:
        st.error(f"Erro na renderização do aplicativo: {e}")
        
