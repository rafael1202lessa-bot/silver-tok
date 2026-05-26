import streamlit as st
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2", page_icon="🚀", layout="wide")

# --- CONEXÃO COM SUPABASE (DIRETO NO CÓDIGO) ---
url = "https://ldjtqgeyorkzbvuichjj.supabase.co"
key = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Erro crítico na inicialização do Supabase: {str(e)}")
    st.stop()

# --- ESTADO DE DESENVOLVIMENTO (BLOQUEIO BETA) ---
# Mude para False quando quiser liberar o aplicativo para todo mundo!
ESTADO_DESENVOLVIMENTO = True 

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

# 🚨 VERIFICAÇÃO DE BLOQUEIO DE DESENVOLVIMENTO 🚨
if ESTADO_DESENVOLVIMENTO:
    # Só permite a entrada se o título for Desenvolvedor ou Tester
    if user_atual["titulo"] not in ["👑 Desenvolvedor", "🧪 Tester"]:
        st.title("🚧 Aplicativo em Manutenção")
        st.warning(f"Olá {user_atual['nickname']}, o Silver Tok v2 está atualmente em desenvolvimento exclusivo para a equipe de testes.")
        st.info("Acesso negado para a sua conta no momento. Tente novamente mais tarde!")
        
        if st.button("Sair da Conta"):
            st.session_state.logado = False
            st.session_state.user_data = None
            st.rerun()
        st.stop() # Interrompe o código aqui para o usuário comum não ver o app

# --- SE PASSOU NO TESTE OU NÃO ESTÁ EM MANUTENÇÃO, CARREGA O APP ---
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
abas = ["📱 Silver Tok (Feed/Shorts)", "🎥 Gravar Vídeo", "💬 Chat & Amigos", "📺 Stream (Filmes/Animes)", "👤 Meu Perfil"]

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
    st.header("Painel Secreto do Desenvolvedor 👑 (God Mode)")
    
    try:
        usuarios_req = supabase.table("perfis_usuarios").select("username, nickname").execute()
        lista_usuarios = [u["username"] for u in usuarios_req.data]
    except Exception as e:
        st.error("Erro ao carregar lista de usuários.")
        lista_usuarios = []

    if lista_usuarios:
        usuario_alvo = st.selectbox("Selecione o usuário para aplicar o comando:", lista_usuarios)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("👥 Modificar Seguidores")
            qtd_seguidores = st.number_input("Quantidade de Seguidores", min_value=0, value=1000, step=50)
            if st.button("Definir Seguidores", use_container_width=True):
                status_verificado = qtd_seguidores >= 1000
                supabase.table("perfis_usuarios").update({
                    "seguidores": qtd_seguidores,
                    "verificado": status_verificado
                }).eq("username", usuario_alvo).execute()
                st.success(f"Seguidores de {usuario_alvo} atualizados para {qtd_seguidores}!")
                st.rerun()

        with col2:
            st.subheader("💰 Modificar Dinheiro")
            qtd_dinheiro = st.number_input("Quantidade de Dinheiro ($)", min_value=0, value=500, step=10)
            if st.button("Definir Saldo", use_container_width=True):
                supabase.table("perfis_usuarios").update({"dinheiro": qtd_dinheiro}).eq("username", usuario_alvo).execute()
                st.success(f"Saldo de {usuario_alvo} alterado para ${qtd_dinheiro}!")
                st.rerun()

        with col3:
            st.subheader("🎖️ Atribuir Títulos")
            novo_titulo = st.selectbox("Escolha o Cargo/Título:", ["👑 Desenvolvedor", "⚔️ Vice-Dev", "📢 Divulgadora", "🧪 Tester", "Best friends of the dev", "Usuário"])
            if st.button("Atualizar Cargo", use_container_width=True):
                supabase.table("perfis_usuarios").update({"titulo": novo_titulo}).eq("username", usuario_alvo).execute()
                st.success(f"Cargo de {usuario_alvo} alterado para: {novo_titulo}!")
                st.rerun()
        
        st.write("---")
        st.subheader("🚫 Zona de Punição")
        if st.button("💥 Banir Usuário (Excluir Conta)", type="primary", use_container_width=True):
            if usuario_alvo == "rafael_oficial":
                st.error("Você não pode banir a sua própria conta de desenvolvedor!")
            else:
                supabase.table("perfis_usuarios").delete().eq("username", usuario_alvo).execute()
                st.success(f"O usuário {usuario_alvo} foi banido com sucesso do Silver Tok!")
                st.rerun()
    else:
        st.warning("Nenhum usuário cadastrado no banco de dados ainda.")
