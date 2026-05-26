import streamlit as st
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2", page_icon="🚀", layout="wide")

# --- CONEXÃO COM SUPABASE ---
# O Streamlit já puxa isso dos Secrets automaticamente
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Erro ao conectar ao banco de dados. Verifique os Secrets.")
    st.stop()

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# --- CÓDIGO CONVITE OBRIGATÓRIO ---
CODIGO_CORRETO = "ChatPrivado2026"

# --- TÍTULOS ESPECIAIS ---
TITULOS = {
    "rafael_oficial": "👑 Desenvolvedor",
    "rafael_secundario": "⚔️ Vice-Dev",
    "amiga_divulgadora": "📢 Divulgadora",
}

# --- FUNÇÕES DE AUTENTICAÇÃO ---
def criar_conta(username, password, nickname, codigo):
    if codigo != CODIGO_CORRETO:
        return "Código de convite inválido! Você precisa do código correto para criar conta."
    
    try:
        # Verifica se o usuário já existe
        existe = supabase.table("perfis_usuarios").select("*").eq("username", username).execute()
        if existe.data:
            return "Este nome de usuário já está em uso."
        
        # Define título inicial baseado no username
        titulo = TITULOS.get(username, "Usuário")
        
        # Insere no banco de dados
        novo_usuario = {
            "username": username,
            "senha": password,
            "nickname": nickname,
            "titulo": titulo,
            "seguidores": 0,
            "dinheiro": 0,
            "verificado": False,
            "itens_exclusivos": []
        }
        supabase.table("perfis_usuarios").insert(novo_usuario).execute()
        return "Sucesso"
    except Exception as e:
        return f"Erro ao criar conta: {str(e)}"

def fazer_login(username, password):
    try:
        resultado = supabase.table("perfis_usuarios").select("*").eq("username", username).eq("senha", password).execute()
        if resultado.data:
            return resultado.data[0]
        return None
    except Exception as e:
        st.error(f"Erro no login: {str(e)}")
        return None

# --- TELA DE LOGIN / CADASTRO ---
if not st.session_state.logado:
    st.title("Welcome to Silver Tok v2 🚀")
    
    aba_login, aba_cadastro = st.tabs(["🔐 Entrar", "📝 Criar Conta"])
    
    with aba_login:
        user_in = st.text_input("Usuário", key="login_user").strip()
        pass_in = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar", use_container_width=True):
            user = fazer_login(user_in, pass_in)
            if user:
                st.session_state.logado = True
                st.session_state.user_data = user
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
                
    with aba_cadastro:
        new_user = st.text_input("Escolha seu Usuário (Ex: rafael_oficial)", key="cad_user").strip()
        new_nick = st.text_input("Nome de Exibição (Nickname)", key="cad_nick")
        new_pass = st.text_input("Escolha sua Senha", type="password", key="cad_pass")
        convite = st.text_input("Código de Convite Secreto", type="password", key="cad_code")
        
        if st.button("Cadastrar Nova Conta", use_container_width=True):
            if not new_user or not new_pass or not new_nick:
                st.warning("Preencha todos os campos!")
            else:
                status = criar_conta(new_user, new_pass, new_nick, convite)
                if status == "Sucesso":
                    st.success("Conta criada com sucesso! Faça login na aba ao lado.")
                else:
                    st.error(status)
    st.stop()

# --- SE O USUÁRIO ESTÁ LOGADO, ENTRA NO APLICATIVO PRINCIPAL ---
user_atual = st.session_state.user_data

# Sidebar com Perfil rápido
st.sidebar.title(f"Olá, {user_atual['nickname']}!")
st.sidebar.write(f"**Cargo:** {user_atual['titulo']}")
st.sidebar.write(f"**Seguidores:** {user_atual['seguidores']} 👥")
st.sidebar.write(f"**Carteira:** ${user_atual['dinheiro']}")

if user_atual['verificado'] or user_atual['seguidores'] >= 1000:
    st.sidebar.write("**Status:** 👑 Verificado")

if st.sidebar.button("Sair da Conta"):
    st.session_state.logado = False
    st.session_state.user_data = None
    st.rerun()

# --- ABAS PRINCIPAIS DO APLICATIVO ---
# Criando a estrutura solicitada
abas = ["📱 Silver Tok (Feed/Shorts)", "🎥 Gravar Vídeo", "💬 Chat & Amigos", "📺 Stream (Filmes/Animes)", "👤 Meu Perfil"]

# Se for a sua conta principal, adiciona o Painel de Comando Dev
if user_atual['username'] == "rafael_oficial":
    abas.append("⚡ Painel Dev (God Mode)")

aba_ativa = st.radio("Navegação", abas, horizontal=True)

st.write("---")

# --- CONTEÚDO DE CADA ABA ---

if aba_ativa == "📱 Silver Tok (Feed/Shorts)":
    st.header("Feed de Vídeos")
    st.info("Aqui ficarão os vídeos normais e os Shorts estilo TikTok.")

elif aba_ativa == "🎥 Gravar Vídeo":
    st.header("Estúdio de Gravação (Estilo TikTok)")
    st.info("Painel vertical otimizado para gravação e upload de corpo inteiro.")

elif aba_ativa == "💬 Chat & Amigos":
    st.header("Central de Mensagens")
    st.info("Área de conversas privadas, em grupo, amigos e seguidores.")

elif aba_ativa == "📺 Stream (Filmes/Animes)":
    st.header("Silver Stream 🍿")
    st.subheader("Bleach (Todos os Episódios Dublados PT-BR)")
    st.info("Área de streaming. Pronta para receber os links dos episódios.")

elif aba_ativa == "👤 Meu Perfil":
    st.header("Seu Perfil")
    st.json(user_atual)

elif aba_ativa == "⚡ Painel Dev (God Mode)":
    st.header("Painel Secreto do Desenvolvedor 👑")
    st.write("Comandos para alterar saldo, seguidores, banir usuários e gerar itens.")
    
