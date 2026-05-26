import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v3.6 Fixed", page_icon="🎬", layout="centered")

# --- CONFIGURAÇÕES DE MANUTENÇÃO (MODO PRIVADO) ---
MODO_MANUTENCAO = False  
ID_REAL_DEVELOPER = "04daaa3c-63ef-486c-b33e-54d4e80ee9e9"

# --- CONEXÃO BANCO DE DADOS ---
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
    st.error("Erro crítico: Não foi possível conectar ao banco de dados Supabase.")
    st.stop()

# --- CONFIGURAÇÕES DE SEGURANÇA MÁXIMA ---
CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- BANCO DE DADOS DE SHIMEJIS / MASCOTES ---
SHIMEJIS_DISPONIVEIS = {
    "Nenhum": "",
    "⚔️ Mascote Espadachim": "⚔️",
    "🔮 Mago Ancestral": "🔮",
    "🦊 Raposa de Fogo": "🦊",
    "🤖 Mini Robô": "🤖",
    "🐱 Gatinho Chibi": "🐱"
}

# --- CONFIGURAÇÃO DE COSMÉTICOS ---
COSMETICOS = {
    "bronze": {"nome": "🥉 Bronze Estelar", "preco": 150, "img": "https://cdn-icons-png.flaticon.com/512/5243/5243422.png"},
    "prata": {"nome": "🥈 Prata Lendária", "preco": 300, "img": "https://cdn-icons-png.flaticon.com/512/5243/5243444.png"},
    "caixa_azul": {"nome": "🔷 Balão Azul Moderno", "preco": 100, "img": "https://cdn-icons-png.flaticon.com/512/2460/2460884.png"},
    "caixa_neon": {"nome": "🔮 Balão Neon Cyber", "preco": 250, "img": "https://cdn-icons-png.flaticon.com/512/2037/2037041.png"},
    "banner_otaku": {"nome": "🔥 Mestre Otaku (Anime)", "preco": 400, "img": "https://cdn-icons-png.flaticon.com/512/2206/2206241.png"},
    "banner_hollywood": {"nome": "🎬 Cinéfilo de Carteirinha", "preco": 400, "img": "https://cdn-icons-png.flaticon.com/512/3172/3172554.png"},
    "banner_dorama": {"nome": "🌸 Dorama Lover", "preco": 450, "img": "https://cdn-icons-png.flaticon.com/512/4230/4230633.png"}
}

# --- PERGUNTAS DO QUIZ GEEK ---
PERGUNTAS_QUIZ = {
    "Anime e Animações": [
        {"pergunta": "Qual é o objetivo principal de Luffy em One Piece?", "opcoes": ["Se tornar Hokage", "Encontrar o All Blue", "Ser o Rei dos Piratas", "Derrotar Madara"], "correta": "Ser o Rei dos Piratas"},
        {"pergunta": "Quem é conhecido como o Alquimista de Aço?", "opcoes": ["Roy Mustang", "Edward Elric", "Alphonse Elric", "Saitama"], "correta": "Edward Elric"}
    ],
    "Filmes e Séries / Doramas": [
        {"pergunta": "Em Round 6 (Squid Game), qual é o prêmio final?", "opcoes": ["Um carro de luxo", "45,6 bilhões de wons", "A liberdade eterna", "1 milhão de dólares"], "correta": "45,6 bilhões de wons"},
        {"pergunta": "Qual é a casa de Harry Potter em Hogwarts?", "opcoes": ["Sonserina", "Corvinal", "Lufa-Lufa", "Grifinória"], "correta": "Grifinória"}
    ]
}

# --- FUNÇÕES AUXILIARES ANTIFALHA ---
def verificar_se_eh_dev(user_id):
    return str(user_id) == ID_REAL_DEVELOPER

def obter_selo_texto(username_alvo, user_id_alvo=None, cargo_adicional="Nenhum"):
    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial":
        return " 👑 DEV"
    if cargo_adicional and cargo_adicional != "Nenhum" and cargo_adicional != "Membro Comum":
        return f" 🎖️ {cargo_adicional}"
    return ""

def renderizar_foto_com_banner(url_foto, username_alvo, user_id_alvo=None, tamanho=80, banner_equipado="Nenhum", shimeji="Nenhum"):
    if not url_foto:
        url_foto = FOTO_PADRAO
    
    shimeji_html = ""
    if shimeji in SHIMEJIS_DISPONIVEIS and SHIMEJIS_DISPONIVEIS[shimeji] != "":
        shimeji_html = f'<div style="position: absolute; bottom: -8px; right: -8px; font-size: {int(tamanho*0.4)}px; background: #fff; border-radius: 50%; padding: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); z-index: 99;">{SHIMEJIS_DISPONIVEIS[shimeji]}</div>'

    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial" or banner_equipado == "👑 Coroa Suprema DEV":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 4px solid #ffd700; box-shadow: 0 0 15px #ffd700;"
        coroa_html = f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.4)}px; z-index: 10;">👑</div>'
    elif banner_equipado == "🥉 Bronze Estelar":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #cd7f32;"
        coroa_html = ''
    elif banner_equipado == "🥈 Prata Lendária":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #c0c0c0; box-shadow: 0 0 8px #c0c0c0;"
        coroa_html = ''
    elif "Otaku" in str(banner_equipado):
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #ff4500; box-shadow: 0 0 10px #ff4500;"
        coroa_html = f'<div style="position: absolute; top: -18px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🦊</div>'
    elif "🌸" in str(banner_equipado) or "Dorama" in str(banner_equipado):
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #ff69b4; box-shadow: 0 0 10px #ff69b4;"
        coroa_html = f'<div style="position: absolute; top: -18px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🌸</div>'
    else:
        estilo_css = "border-radius: 50%; object-fit: cover; border: 2px solid #ccc;"
        coroa_html = ''
        
    html = f"""
    <div style="position: relative; display: inline-block; text-align: center; margin-top: 15px; margin-bottom: 5px;">
        {coroa_html}
        <img src="{url_foto}" width="{tamanho}" height="{tamanho}" style="{estilo_css}">
        {shimeji_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def renderizar_caixa_mensagem(username, mensagem, selo, estilo_caixa, eh_admin=False):
    if not mensagem or str(mensagem).lower() == "none":
        return

    if eh_admin or estilo_caixa == "👑 Balão Dourado DEV":
        estilo_css = "background: linear-gradient(135deg, #fff7e6, #ffeaa7); border-left: 5px solid #ffd700; padding: 12px; border-radius: 8px; margin-bottom: 8px;"
    elif "Azul" in str(estilo_caixa):
        estilo_css = "background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
    elif "Neon" in str(estilo_caixa):
        estilo_css = "background-color: #1a1a2e; border: 1px solid #e94560; color: #fff; padding: 10px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 0 8px #e94560;"
    else:
        estilo_css = "background-color: #f1f3f4; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #ccc;"
        
    conteudo_final = mensagem
    if str(mensagem).startswith("https://") and any(ext in str(mensagem).lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', 'jpeg']):
        conteudo_final = f'<br><img src="{mensagem}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'
    elif str(mensagem).startswith("https://") and any(ext in str(mensagem).lower() for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.bin']):
        conteudo_final = f'<br><audio controls style="max-width: 100%; margin-top: 5px;"><source src="{mensagem}"></audio>'

    st.markdown(f"""
    <div style="{estilo_css}">
        <span style="font-weight: bold; color: #333;">{username}</span> 
        <span style="font-size: 11px; font-weight: bold; color: #d4af37;">{selo}</span>: 
        <span style="color: {'#111' if 'Neon' not in str(estilo_caixa) else '#fff'};">{conteudo_final}</span>
    </div>
    """, unsafe_allow_html=True)

# --- GERENCIAMENTO DE ESTADO ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = None
if "shimeji_local" not in st.session_state:
    st.session_state.shimeji_local = "Nenhum"
if "catalogo_memoria" not in st.session_state:
    st.session_state.catalogo_memoria = {cat: [] for cat in ["Animes", "Filmes", "Séries e Desenhos", "Doramas", "Livros e Mangás"]}

# --- FLUXO DE LOGIN / CADASTRO ---
if st.session_state.usuario_logado is None:
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)
    aba_auth = st.tabs(["Fazer Login", "Criar Nova Conta"])
    
    with aba_auth[0]:
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        if st.button("Entrar 🚀", key="btn_login", use_container_width=True):
            if login_user and login_senha:
                busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                if busca.data and busca.data[0].get("senha") == login_senha:
                    st.session_state.usuario_logado = busca.data[0]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
                    
    with aba_auth[1]:
        cad_user = st.text_input("Escolha um Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie uma Senha:", type="password", key="cad_senha")
        codigo_convite = st.text_input("🔑 Código Secreto:", type="password", key="codigo_convite")
        if st.button("Cadastrar Conta 🎉", key="btn_cad", use_container_width=True):
            if cad_user and cad_senha and codigo_convite == CHAVE_SECRETA:
                try:
                    supabase.table("perfis_usuarios").insert({
                        "username": cad_user, "apelido": cad_user, "senha": cad_senha, 
                        "url_foto_perfil": FOTO_PADRAO, "moedas": 0, "banner_ativo": "Nenhum", "biografia": "Tester"
                    }).execute()
                    st.success("Conta criada! Faça login.")
                except:
                    st.error("Nome de usuário indisponível.")
else:
    # Sincroniza dados do usuário logado
    user_atual = st.session_state.usuario_logado
    u_id = user_atual.get("id")
    u_name = user_atual.get("username", "Membro")
    is_admin = verificar_se_eh_dev(u_id)
    
    # Puxa o cargo e dados salvos nas colunas alternativas para evitar quebras
    u_cargo = user_atual.get("biografia") if user_atual.get("biografia") else "Tester"
    u_moedas = user_atual.get("moedas") if user_atual.get("moedas") is not None else 0

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown("### 👤 Meu Perfil")
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil"), u_name, u_id, tamanho=90, banner_equipado=user_atual.get("banner_ativo", "Nenhum"), shimeji=st.session_state.shimeji_local)
        
        selo_p = obter_selo_texto(u_name, u_id, cargo_adicional=u_cargo)
        st.write(f"**{user_atual.get('apelido') or u_name}** {selo_p}")
        st.markdown(f"🪙 **Silver Coins:** {u_moedas}")
        st.caption(f"Cargo Atual: `{u_cargo}`")
        
        # --- ATIVADOR DE SHIMEJIS PROPRIOS NATIVO ---
        st.markdown("---")
        st.session_state.shimeji_local = st.selectbox("🦊 Invocar Mascote/Shimeji:", list(SHIMEJIS_DISPONIVEIS.keys()), index=list(SHIMEJIS_DISPONIVEIS.keys()).index(st.session_state.shimeji_local) if st.session_state.shimeji_local in SHIMEJIS_DISPONIVEIS else 0)
        
        # --- INVENTÁRIO ---
        with st.expander("🎒 Meu Inventário"):
            opcoes_inv = ["Nenhum", "🥉 Bronze Estelar", "🥈 Prata Lendária", "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber", "🔥 Mestre Otaku (Anime)", "🌸 Dorama Lover"]
            if is_admin:
                opcoes_inv.append("👑 Coroa Suprema DEV")
                opcoes_inv.append("👑 Balão Dourado DEV")
            
            escolha_c = st.selectbox("Equipar Cosmético:", opcoes_inv)
            if st.button("Equipar 🛡️"):
                try:
                    supabase.table("perfis_usuarios").update({"banner_ativo": escolha_c}).eq("id", u_id).execute()
                    user_atual["banner_ativo"] = escolha_c
                    st.toast("Cosmético atualizado!")
                    st.rerun()
                except: pass

        if st.button("Sair da Conta 🚪", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.sala_ativa = None
            st.rerun()

    # --- NAVEGAÇÃO DOS RECUSOS PRINCIPAIS ---
    abas_menu = ["📺 Silver Tok", "🛒 Loja Premium", "💬 Chat-Exv", "🍿 Área Geek", "🧠 Super Quiz"]
    if is_admin:
        abas_menu.append("👑 Painel Admin")
        
    abas = st.tabs(abas_menu)

    # === 1. FEED SILVER TOK ===
    with abas[0]:
        st.title("Feed de Vídeos da Comunidade")
        try:
            feed_dados = supabase.table("feed_videos").select("*").execute()
            if feed_dados.data:
                for post in reversed(feed_dados.data):
                    with st.container(border=True):
                        st.markdown(f"**@{post.get('username_autor')}** postou:")
                        st.caption(post.get("titulo"))
                        if post.get("url_video"):
                            st.video(post.get("url_video"))
            else:
                st.info("Nenhum vídeo carregado no momento global.")
        except:
            st.warning("Feed offline temporariamente. Use os chats para compartilhar links de mídias!")

    # === 2. LOJA PREMIUM ===
    with abas[1]:
        st.header("🛒 Loja Premium")
        st.write(f"Seu Saldo: 🪙 {u_moedas} Silver Coins")
        col_l1, col_l2 = st.columns(2)
        for idx, (chave, info) in enumerate(COSMETICOS.items()):
            col_fogo = col_l1 if idx % 2 == 0 else col_l2
            with col_fogo:
                with st.container(border=True):
                    st.markdown(f"### {info['nome']}")
                    st.write(f"Preço: 🪙 {info['preco']} Coins")
                    if u_moedas >= info['preco']:
                        if st.button(f"Comprar {info['nome']}", key=f"loj_{chave}"):
                            try:
                                novo_s = int(u_moedas) - int(info['preco'])
                                supabase.table("perfis_usuarios").update({"moedas": novo_s}).eq("id", u_id).execute()
                                st.success("Adquirido com sucesso!")
                                st.rerun()
                            except: pass
                    else:
                        st.caption("Saldo Insuficiente")

    # === 3. CHAT-EXV COM PROTOCOLO DE ID COMPATÍVEL ===
    with abas[2]:
        st.header("💬 Chat-Exv Comunidade")
        
        if st.session_state.sala_ativa is None:
            st.session_state.sala_ativa = "GERAL"
            
        sala = st.session_state.sala_ativa
        st.write(f"Você está na Sala: `{sala}`")
        
        # Mudar sala
        nova_sala_opt = st.text_input("Mudar para outra sala (Digite o nome):", value=sala).upper()
        if st.button("Trocar de Sala 🚪"):
            st.session_state.sala_ativa = nova_sala_opt
            st.rerun()

        # Input de Mensagem
        m_txt = st.text_input("Sua Mensagem:", key="msg_input_field")
        if st.button("Enviar Mensagem ✉️", use_container_width=True) and m_txt.strip():
            try:
                # CORREÇÃO CRÍTICA: Injeta o id_usuario exigido pelo seu banco de dados
                supabase.table("bate-papo_profissional").insert({
                    "username": u_name,
                    "mensagem": m_txt.strip(),
                    "codigo_sala": sala,
                    "id_usuario": u_id,
                    "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO
                }).execute()
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar mensagem: {e}")

        # Envio de Arquivo / Imagem
        with st.expander("📸 Compartilhar Foto / Mídia"):
            arq = st.file_uploader("Escolha imagem:", type=["png", "jpg", "jpeg", "gif"])
            if st.button("Enviar Imagem 🚀") and arq:
                try:
                    path_imagem = f"chat/{uuid.uuid4()}_{arq.name}"
                    supabase.storage.from_("imagens_chat").upload(path_imagem, arq.read())
                    url_p = supabase.storage.from_("imagens_chat").get_public_url(path_imagem)
                    
                    # CORREÇÃO CRÍTICA: Injeta o id_usuario para não dar erro constraint null
                    supabase.table("bate-papo_profissional").insert({
                        "username": u_name,
                        "mensagem": url_p,
                        "codigo_sala": sala,
                        "id_usuario": u_id,
                        "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO
                    }).execute()
                    st.success("Mídia postada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Falha ao subir imagem: {e}")

        st.markdown("---")
        # Mostrar Histórico do Chat
        try:
            mensagens_banco = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", sala).execute()
            if mensagens_banco.data:
                for m in reversed(mensagens_banco.data[-30:]):
                    u_remetente = m.get("username", "Membro")
                    msg_corpo = m.get("mensagem", "")
                    f_remetente = m.get("url_foto_perfil") or FOTO_PADRAO
                    
                    col_m1, col_m2 = st.columns([1, 7])
                    with col_m1:
                        st.markdown(f'<img src="{f_remetente}" width="35" style="border-radius:50%;">', unsafe_allow_html=True)
                    with col_m2:
                        renderizar_caixa_mensagem(u_remetente, msg_corpo, "", "Nenhum", eh_admin=(u_remetente == "Rafael_oficial"))
        except: pass

    # === 4. ÁREA GEEK E LITERÁRIA NATIVA ===
    with abas[3]:
        st.header("🍿 Catálogo Geek da Comunidade")
        
        abas_geek = st.tabs(["⛩️ Animes", "🎬 Filmes", "📺 Séries / Desenhos", "🌸 Doramas", "📖 Livros e Mangás"])
        categorias_lista = ["Animes", "Filmes", "Séries e Desenhos", "Doramas", "Livros e Mangás"]
        
        for id_g, nome_g in enumerate(categorias_lista):
            with abas_geek[id_g]:
                st.subheader(f"Indicações de {nome_g}")
                
                # Permite qualquer usuário adicionar para ficar dinâmico e livre de erros
                with st.expander(f"➕ Adicionar Recomendação em {nome_g}"):
                    nome_obra = st.text_input("Nome da Obra:", key=f"no_{nome_g}")
                    desc_obra = st.text_area("Sua Avaliação / Detalhes:", key=f"de_{nome_g}")
                    if st.button("Salvar no Catálogo ✨", key=f"bt_{nome_g}"):
                        if nome_obra and desc_obra:
                            st.session_state.catalogo_memoria[nome_g].append({"titulo": nome_obra, "detalhes": desc_obra, "autor": u_name})
                            st.toast("Adicionado com sucesso!")
                
                # Lista itens adicionados
                itens_na_categoria = st.session_state.catalogo_memoria[nome_g]
                if itens_na_categoria:
                    for it in reversed(itens_na_categoria):
                        with st.container(border=True):
                            st.markdown(f"### {it['titulo']}")
                            st.write(it['detalhes'])
                            st.caption(f"Enviado por: @{it['autor']}")
                else:
                    st.info(f"Nenhum conteúdo adicionado em {nome_g} ainda. Comece agora!")

    # === 5. SUPER QUIZ (BLINDADO CONTRA ERRO DE PREMIAÇÃO) ===
    with abas[4]:
        st.header("🧠 Desafio Quiz Silver Coins")
        
        cat_escolhida = st.selectbox("Escolha um Tema:", list(PERGUNTAS_QUIZ.keys()))
        pergunta_foco = PERGUNTAS_QUIZ[cat_escolhida][0]
        
        st.write(pergunta_foco["pergunta"])
        resp_user = st.radio("Selecione a certa:", pergunta_foco["opcoes"])
        
        if st.button("Enviar Resposta 🎯"):
            if resp_user == pergunta_foco["correta"]:
                st.success("Correct! +100 Silver Coins ganhas!")
                try:
                    # Tenta atualizar o saldo de forma segura
                    novo_saldo_q = int(u_moedas) + 100
                    supabase.table("perfis_usuarios").update({"moedas": novo_saldo_q}).eq("id", u_id).execute()
                    st.balloons()
                except:
                    st.info("Sucesso! Sua conta receberá os 100 coins assim que o admin processar o lote no painel.")
            else:
                st.error("Resposta Incorreta, tente de novo!")

    # === 6. PAINEL ADMIN DO RAFAEL ===
    if is_admin:
        with abas[5]:
            st.header("👑 Painel Admin Secreto (Rafael)")
            
            st.subheader("Gerenciar Cargos & Coins dos Usuários")
            try:
                usuarios_lista = supabase.table("perfis_usuarios").select("*").execute()
                if usuarios_lista.data:
                    for user_banco in usuarios_lista.data:
                        id_membro = user_banco.get("id")
                        name_membro = user_banco.get("username")
                        moedas_membro = user_banco.get("moedas") if user_banco.get("moedas") is not None else 0
                        cargo_membro = user_banco.get("biografia") if user_banco.get("biografia") else "Tester"
                        
                        with st.container(border=True):
                            st.write(f"**Usuário:** @{name_membro} | Saldo: 🪙 {moedas_membro} | Cargo: `{cargo_membro}`")
                            col_a1, col_a2 = st.columns(2)
                            with col_a1:
                                input_moedas = st.number_input(f"Definir Coins para @{name_membro}", min_value=0, value=int(moedas_membro), key=f"adm_m_{id_membro}")
                            with col_a2:
                                input_cargo = st.selectbox(f"Mudar Cargo de @{name_membro}", ["Tester", "Best Friends of the dev", "Vice-dev", "Membro Comum"], index=0, key=f"adm_c_{id_membro}")
                                
                            if st.button("Salvar Alterações ⚙️", key=f"btn_adm_s_{id_membro}"):
                                supabase.table("perfis_usuarios").update({
                                    "moedas": input_moedas,
                                    "biografia": input_cargo
                                }).eq("id", id_membro).execute()
                                st.success("Atualizado com sucesso!")
                                st.rerun()
            except Exception as e:
                st.write("Aguardando registro de novos membros para carregar lista.")
