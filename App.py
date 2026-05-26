import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v3.7 Ultra Master", page_icon="🎬", layout="centered")

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

# --- BANCO DE DADOS LOCAL DE SHIMEJIS / MASCOTES ---
SHIMEJIS_DISPONIVEIS = {
    "Nenhum": "",
    "Mascote Espadachim (Livro)": "⚔️",
    "Mago Ancestral (Livro)": "🔮",
    "Raposa de Fogo": "🦊",
    "Mini Robô": "🤖",
    "Gatinho Chibi": "🐱"
}

# --- CONFIGURAÇÃO DE COSMÉTICOS ---
COSMETICOS = {
    "bronze": {"nome": "🥉 Bronze Estelar", "preco": 150, "img": "https://cdn-icons-png.flaticon.com/512/5243/5243422.png"},
    "prata": {"nome": "🥈 Prata Lendária", "preco": 300, "img": "https://cdn-icons-png.flaticon.com/512/5243/5243444.png"},
    "caixa_azul": {"nome": "🔷 Balão Azul Moderno", "preco": 100, "img": "https://cdn-icons-png.flaticon.com/512/2460/2460884.png"},
    "caixa_neon": {"nome": "🔮 Balão Neon Cyber", "preco": 250, "img": "https://cdn-icons-png.flaticon.com/512/2037/2037041.png"},
    "banner_otaku": {"nome": "🔥 Mestre Otaku (Anime)", "preco": 400, "img": "https://cdn-icons-png.flaticon.com/512/2206/2206241.png"},
    "banner_hollywood": {"nome": "🎬 Cinéfilo de Carteirinha", "preco": 400, "img": "https://cdn-icons-png.flaticon.com/512/3172/3172554.png"},
    "banner_dorama": {"nome": "🌸 Dorama Lover", "preco": 450, "img": "https://cdn-icons-png.flaticon.com/512/4230/4230633.png"},
    "banner_kpop": {"nome": "🌸 Banner K-Popper Oficial", "preco": 0, "img": "https://cdn-icons-png.flaticon.com/512/2991/2991610.png"}
}

VIDEOS_BOT_BOTEY = [
    {"id": "bot_1", "titulo": "⚡ Edit Suprema de Naruto!", "url_video": "https://www.w3schools.com/html/mov_bbb.mp4", "username_autor": "🤖 Bot_Animes", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4213/4213732.png", "curtidas": 142, "tipo_formato": "vertical"},
    {"id": "bot_2", "titulo": "🌌 Relaxing Cinematic View 4K", "url_video": "https://media.w3.org/2010/05/sintel/trailer_hd.mp4", "username_autor": "🤖 Bot_Natureza", "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4213/4213732.png", "curtidas": 98, "tipo_formato": "horizontal"}
]

# --- REGRAS DO SISTEMA ---
REGRAS_SISTEMA = [
    "🚫 Estritamente proibido postar conteúdos +18 ou sexualmente explícitos.",
    "❌ Proibido qualquer tipo de discurso de ódio, racismo, bullying ou discriminação.",
    "⚠️ Não exponha informações pessoais ou de saúde de terceiros publicamente.",
    "🔨 O descumprimento de qualquer regra resultará em banimento imediato e permanente por parte da administração."
]

# --- PERGUNTAS DO QUIZ GEEK ---
PERGUNTAS_QUIZ = {
    "Anime e Animações": [
        {"pergunta": "Qual é o objetivo principal de Luffy em One Piece?", "opcoes": ["Se tornar Hokage", "Encontrar o All Blue", "Ser o Rei dos Piratas", "Derrotar Madara"], "correta": "Ser o Rei dos Piratas"},
        {"pergunta": "Quem é conhecido como o Alquimista de Aço?", "opcoes": ["Roy Mustang", "Edward Elric", "Alphonse Elric", "Saitama"], "correta": "Edward Elric"}
    ],
    "Filmes e Séries / Doramas": [
        {"pergunta": "Em Round 6 (Squid Game), qual é o prêmio final?", "opcoes": ["Um carro de luxo", "45,6 bilhões de wons", "A liberdade eterna", "1 milhão de dólares"], "correta": "45,6 bilhões de wons"},
        {"pergunta": "Qual é a casa de Harry Potter em Hogwarts?", "opcoes": ["Sonserina", "Corvinal", "Lufa-Lufa", "Grifinória"], "correta": "Grifinória"}
    ],
    "Conteúdo Geral": [
        {"pergunta": "Qual empresa desenvolveu o Streamlit?", "opcoes": ["Google", "Snowflake", "Meta", "Microsoft"], "correta": "Snowflake"},
        {"pergunta": "Quantos minutos tem um tempo regulamentar de futebol?", "opcoes": ["40 minutos", "45 minutos", "50 minutos", "60 minutos"], "correta": "45 minutos"}
    ]
}

# --- FUNÇÕES AUXILIARES ANTIFALHA ---
def obter_status_emoji(timestamp_str):
    if not timestamp_str:
        return "⚪ Offline"
    try:
        if "T" in timestamp_str:
            timestamp_str = timestamp_str.split("+")[0]
            dt_usuario = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)
        else:
            dt_usuario = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
        agora = datetime.now(timezone.utc)
        if agora - dt_usuario < timedelta(minutes=3):
            return "🟢 Online"
    except: pass
    return "⚪ Offline"

def verificar_se_eh_dev(user_id):
    return str(user_id) == ID_REAL_DEVELOPER

def obter_selo_texto(username_alvo, user_id_alvo=None, cargo_adicional="Nenhum"):
    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial":
        return " 👑 DEV"
    if cargo_adicional and cargo_adicional != "Nenhum":
        return f" 🎖️ {cargo_adicional}"
    try:
        dados = supabase.table("perfis_usuarios").select("id").eq("username", username_alvo).execute()
        if dados.data:
            id_u = dados.data[0].get("id")
            if id_u:
                res_seg = supabase.table("seguidores").select("*").eq("id_seguido", id_u).execute()
                total = len(res_seg.data) if res_seg.data else 0
                if total >= 1000:
                    return " ✔️"
    except: pass
    return ""

def renderizar_foto_com_banner(url_foto, username_alvo, user_id_alvo=None, tamanho=90, banner_equipado="Nenhum", shimeji="Nenhum"):
    if not url_foto:
        url_foto = FOTO_PADRAO
    
    shimeji_html = ""
    if shimeji in SHIMEJIS_DISPONIVEIS and SHIMEJIS_DISPONIVEIS[shimeji] != "":
        valor_shimeji = SHIMEJIS_DISPONIVEIS[shimeji]
        if valor_shimeji.startswith("http"):
            shimeji_html = f'<img src="{valor_shimeji}" style="position: absolute; bottom: -5px; right: -5px; width: {int(tamanho*0.4)}px; height: {int(tamanho*0.4)}px; border-radius: 50%; background: white; padding: 1px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); z-index: 12; object-fit: cover;">'
        else:
            shimeji_html = f'<div style="position: absolute; bottom: -5px; right: -5px; font-size: {int(tamanho*0.35)}px; background: white; border-radius: 50%; padding: 2px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); z-index: 12;">{valor_shimeji}</div>'

    if verificar_se_eh_dev(user_id_alvo) or username_alvo == "Rafael_oficial" or banner_equipado == "👑 Coroa Suprema DEV":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 4px solid #ffd700; box-shadow: 0 0 20px #ffd700;"
        coroa_html = f'<div style="position: absolute; top: -22px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.38)}px; z-index: 10;">👑</div>'
    elif banner_equipado == "🥉 Bronze Estelar":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #cd7f32;"
        coroa_html = ''
    elif banner_equipado == "🥈 Prata Lendária":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #c0c0c0; box-shadow: 0 0 8px #c0c0c0;"
        coroa_html = ''
    elif banner_equipado == "🔥 Mestre Otaku (Anime)":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #ff4500; box-shadow: 0 0 12px #ff4500;"
        coroa_html = f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🦊</div>'
    elif banner_equipado == "🌸 Banner K-Popper Oficial":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #ff69b4; box-shadow: 0 0 12px #ff69b4;"
        coroa_html = f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🎤</div>'
    elif banner_equipado == "🎬 Cinéfilo de Carteirinha":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #1e90ff; box-shadow: 0 0 12px #1e90ff;"
        coroa_html = f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🎥</div>'
    elif banner_equipado == "🌸 Dorama Lover":
        estilo_css = f"border-radius: 50%; object-fit: cover; border: 3px solid #ff69b4; box-shadow: 0 0 12px #ff69b4;"
        coroa_html = f'<div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: {int(tamanho*0.35)}px; z-index: 10;">🌸</div>'
    else:
        estilo_css = "border-radius: 50%; object-fit: cover; border: 1px solid #ccc;"
        coroa_html = ''
        
    html = f"""
    <div style="position: relative; display: inline-block; text-align: center; margin-top: 10px;">
        {coroa_html}
        <img src="{url_foto}" width="{tamanho}" height="{tamanho}" style="{estilo_css}">
        {shimeji_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def renderizar_caixa_mensagem(username, mensagem, selo, estilo_caixa, eh_admin=False):
    if mensagem is None or str(mensagem).lower() == "none":
        return

    if eh_admin or estilo_caixa == "👑 Balão Dourado DEV":
        estilo_css = "background: linear-gradient(135deg, #fff7e6, #ffeaa7); border-left: 5px solid #ffd700; padding: 12px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(255,215,0,0.2);"
    elif estilo_caixa == "🔷 Balão Azul Moderno":
        estilo_css = "background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 10px; border-radius: 8px; margin-bottom: 8px;"
    elif estilo_caixa == "🔮 Balão Neon Cyber":
        estilo_css = "background-color: #1a1a2e; border: 1px solid #e94560; color: #fff; padding: 10px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 0 10px #e94560;"
    else:
        estilo_css = "background-color: #f1f3f4; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #ccc;"
        
    conteudo_final = mensagem
    if str(mensagem).startswith("https://"):
        if any(ext in str(mensagem).lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
            conteudo_final = f'<br><img src="{mensagem}" style="max-width: 100%; border-radius: 8px; margin-top: 5px;">'
        elif any(ext in str(mensagem).lower() for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.webm', '.bin']) or "audio" in str(mensagem).lower():
            conteudo_final = f'<br><audio controls style="max-width: 100%; margin-top: 5px;"><source src="{mensagem}"></audio>'

    st.markdown(f"""
    <div style="{estilo_css}">
        <span style="font-weight: bold; color: {'#d4af37' if (eh_admin or estilo_caixa == '👑 Balão Dourado DEV') else '#333'};">{username}</span> 
        <span style="font-size: 12px; font-weight: bold; color: #d4af37;">{selo}</span>: 
        <span style="color: {'#111' if estilo_caixa != '🔮 Balão Neon Cyber' else '#fff'};">{conteudo_final}</span>
    </div>
    """, unsafe_allow_html=True)

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)

# --- FLUXO DE AUTENTICAÇÃO ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = "GERAL"
if "perfil_visitado" not in st.session_state:
    st.session_state.perfil_visitado = None

if st.session_state.usuario_logado is None:
    exibir_logo()
    aba_auth = st.tabs(["Fazer Login", "Criar Nova Conta"])
    with aba_auth[0]:
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        if st.button("Entrar 🚀", key="btn_login", use_container_width=True):
            if login_user and login_senha:
                busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                if busca.data and busca.data[0].get("senha") == login_senha:
                    if busca.data[0].get("website") == "BANIDO":
                        st.error("Esta conta foi banida permanentemente.")
                    else:
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
                if cad_user.lower() == "rafael_oficial":
                    st.error("Este nome de usuário é reservado do sistema.")
                    st.stop()
                try:
                    supabase.table("perfis_usuarios").insert({
                        "username": cad_user, "apelido": cad_user, "senha": cad_senha, 
                        "url_foto_perfil": FOTO_PADRAO, "ultimo_visto": datetime.now(timezone.utc).isoformat(),
                        "moedas": 0, "banner_ativo": "Nenhum"
                    }).execute()
                    st.success("Conta criada! Faça login.")
                except:
                    st.error("Nome de usuário indisponível.")
else:
    user_atual = st.session_state.usuario_logado
    u_id = str(user_atual.get("id", "")) if user_atual.get("id") else "04daaa3c-63ef-486c-b33e-54d4e80ee9e9"
    u_name = user_atual.get("username", "Membro")
    is_admin = verificar_se_eh_dev(u_id) or u_name == "Rafael_oficial"
    u_cargo = user_atual.get("biografia") if user_atual.get("biografia") else "Nenhum" 
    u_shimeji = user_atual.get("localizacao") if user_atual.get("localizacao") else "Nenhum" 

    if MODO_MANUTENCAO and not is_admin:
        st.markdown("<h1 style='text-align: center;'>🚧 Silver Tok & Chat 🚧</h1>", unsafe_allow_html=True)
        st.error("O aplicativo está em manutenção para a implementação de novas funções! Voltamos em breve para a Grande Estreia. 🎬🚀")
        st.stop()
        
    try:
        atualizar_dados = supabase.table("perfis_usuarios").select("*").eq("id", u_id).execute()
        if atualizar_dados.data:
            st.session_state.usuario_logado = atualizar_dados.data[0]
            user_atual = st.session_state.usuario_logado
    except: pass

    total_notif = 0
    try:
        res_n = supabase.table("notificacoes").select("*").eq("id_destinatario", u_id).eq("lida", False).execute()
        total_notif = len(res_n.data) if res_n.data else 0
    except: pass

    # --- BARRA LATERAL ---
    with st.sidebar:
        banner_v = user_atual.get("banner_ativo", "Nenhum")
        renderizar_foto_com_banner(user_atual.get("url_foto_perfil") or FOTO_PADRAO, u_name, u_id, tamanho=90, banner_equipado=banner_v, shimeji=u_shimeji)
        
        selo_proprio = obter_selo_texto(u_name, u_id, cargo_adicional=u_cargo)
        st.write(f"**{user_atual.get('apelido') or u_name}** {selo_proprio}")
        st.markdown(f"🪙 **Silver Coins:** {user_atual.get('moedas', 0)}")
        
        with st.expander("🦊 Meus Shimejis / Mascotes"):
            escolha_shim = st.selectbox("Escolha seu Acompanhante:", list(SHIMEJIS_DISPONIVEIS.keys()), index=list(SHIMEJIS_DISPONIVEIS.keys()).index(u_shimeji) if u_shimeji in SHIMEJIS_DISPONIVEIS else 0)
            if st.button("Ativar Mascote ✨", use_container_width=True):
                try:
                    supabase.table("perfis_usuarios").update({"localizacao": escolha_shim}).eq("id", u_id).execute()
                    st.toast("Mascote invocado!")
                    st.rerun()
                except: pass

        with st.expander("🎒 Meu Inventário"):
            st.caption("Equipe suas customizações salvas:")
            st.write(f"Ativo no momento: **{user_atual.get('banner_ativo', 'Nenhum')}**")
            
            opcoes_inventario = [
                "Nenhum", "🥉 Bronze Estelar", "🥈 Prata Lendária", 
                "🔷 Balão Azul Moderno", "🔮 Balão Neon Cyber", 
                "🔥 Mestre Otaku (Anime)", "🎬 Cinéfilo de Carteirinha", "🌸 Dorama Lover", "🌸 Banner K-Popper Oficial"
            ]
            
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
                    supabase.table("perfis_usuarios").update({"banner_ativo": escolha_custom}).eq("id", u_id).execute()
                    st.toast("Item equipado com sucesso! 🛡️")
                    st.rerun()
                except: pass

        with st.expander("⚙️ Editar Meu Perfil"):
            novo_apelido = st.text_input("Alterar Apelido:", value=user_atual.get("apelido") or u_name)
            nova_foto = st.text_input("URL da Foto de Perfil:", value=user_atual.get("url_foto_perfil") or FOTO_PADRAO)
            if st.button("Salvar Alterações 💾"):
                try:
                    supabase.table("perfis_usuarios").update({
                        "apelido": novo_apelido.strip(),
                        "url_foto_perfil": nova_foto.strip()
                    }).eq("id", u_id).execute()
                    st.success("Perfil updated!")
                    st.rerun()
                except: st.error("Erro ao salvar dados.")

        st.markdown("---")
        if st.button("Sair da Conta 🚪", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.sala_ativa = "GERAL"
            st.session_state.perfil_visitado = None
            st.rerun()

    # --- LISTAGEM DO FEED TRATADA CONTRA ERROS ---
def renderizar_lista_filtrada(lista_posts):
    if termo_busca:
        lista_posts = [p for p in lista_posts if termo_busca.lower() in str(p.get("titulo", "")).lower()]
        if ordenacao == "🔥 Mais Populares":
            lista_posts = sorted(lista_posts, key=lambda x: x.get("likes", 0), reverse=True)

    for idx, v in enumerate(lista_posts):
            if str(v.get("titulo", "")).startswith("[STATUS]") or str(v.get("titulo", "")).startswith("[ANIMES]") or str(v.get("titulo", "")).startswith("[FILMES]") or str(v.get("titulo", "")).startswith("[SÉRIES / DESENHOS]") or str(v.get("titulo", "")).startswith("[DORAMAS]"): 
                continue
            autor = v.get('username_autor', 'Membro')
            id_autor_post = v.get('id_autor')
            img_autor = v.get('avatar_autor') or FOTO_PADRAO
            video_url = v.get("url_video", "")
            id_post = v.get("id")
            chave_comp = f"feed_{identificador_formato}_{idx}_{id_post}"

            st.markdown("---")
            col_f1, col_f2 = st.columns([1, 5], vertical_alignment="bottom")
            with col_f1: 
                renderizar_foto_com_banner(img_autor, autor, id_autor_post, tamanho=50)
                if st.button("👤", key=f"btn_perfil_f_{chave_comp}"):
                    st.session_state.perfil_visitado = autor
                    st.rerun()
            with col_f2:
                selo_autor = obter_selo_texto(autor, id_autor_post)
                st.markdown(f"**{autor}** {selo_autor}")
                st.caption(v.get("titulo", ""))

            if v.get("tipo_formato") == "vertical":
                st.markdown(f'<div style="display: flex; justify-content: center;"><video width="290" height="515" controls><source src="{video_url}" type="video/mp4"></video></div>', unsafe_allow_html=True)
            else:
                if str(video_url).lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    st.image(video_url, use_container_width=True)
                elif video_url:
                    st.video(video_url)

            col_b1, col_b2 = st.columns([2, 2])
            with col_b1:
                if st.button(f"❤️ {v.get('curtidas', 0)} Curtidas", key=f"like_{chave_comp}"):
                    if "bot_" not in str(id_post):
                        try:
                            supabase.table("feed_videos").update({"curtidas": v.get('curtidas', 0) + 1}).eq("id", id_post).execute()
                        except: pass
                    st.rerun()
            with col_b2:
                if autor == u_name or verificar_se_eh_dev(u_id):
                    if st.button("Remover Post 🗑️", key=f"del_{chave_comp}"):
                        if "bot_" not in str(id_post):
                            try:
                                supabase.table("feed_videos").delete().eq("id", id_post).execute()
                            except: pass
                        st.rerun()

            with st.expander(f"💬 Ver Comentários do Post"):
                cod_discussao = f"POST-{id_post}"
                novo_coment = st.text_input("Escreva um comentário...", key=f"in_coment_{chave_comp}")
                if st.button("Comentar 💬", key=f"btn_coment_{chave_comp}"):
                    if novo_coment.strip():
                        try:
                            supabase.table("bate-papo_profissional").insert({
                                "username": u_name,
                                "id_usuario": str(u_id),
                                "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                "mensagem": novo_coment.strip(),
                                "codigo_sala": cod_discussao
                            }).execute()
                            st.rerun()
                        except: pass

                try:
                    comentarios = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", cod_discussao).execute()
                    if comentarios.data:
                        for c in comentarios.data:
                            c_user = c.get('username')
                            c_msg = c.get('mensagem')
                            if c_msg and str(c_msg).lower() != "none":
                                col_c1, col_c2 = st.columns([1, 6], vertical_alignment="bottom")
                                try:
                                    estilo_c = supabase.table("perfis_usuarios").select("banner_ativo", "id", "url_foto_perfil", "biografia").eq("username", c_user).execute()
                                    txt_caixa_c = estilo_c.data[0].get("banner_ativo", "Nenhum") if estilo_c.data else "Nenhum"
                                    uid_c = estilo_c.data[0].get("id") if estilo_c.data else None
                                    foto_c = estilo_c.data[0].get("url_foto_perfil") or FOTO_PADRAO
                                    cargo_c = estilo_c.data[0].get("biografia") if estilo_c.data else "Nenhum"
                                except:
                                    txt_caixa_c = "Nenhum"
                                    uid_c = None
                                    foto_c = FOTO_PADRAO
                                    cargo_c = "Nenhum"
                                    
                                with col_c1:
                                    renderizar_foto_com_banner(foto_c, c_user, uid_c, tamanho=40, banner_equipado=txt_caixa_c)
                                with col_c2:
                                    selo_c = obter_selo_texto(c_user, uid_c, cargo_adicional=cargo_c)
                                    renderizar_caixa_mensagem(c_user, c_msg, selo_c, txt_caixa_c, eh_admin=verificar_se_eh_dev(uid_c))
                        except Exception as e:
        pass

    # --- NAVEGAÇÃO PRINCIPAL ---
    abas_principais = ["📺 Silver Tok (Feed)", "🛒 Loja", "💬 Chat", "🎮 Entretenimento", "🤓 Área Geek", "❓ Quiz"]

    if is_admin:
        abas_principais.append("👑 Painel Admin Secreto")

    abas = st.tabs(abas_principais)
    

abas = st.tabs(abas_principais)

aba_feed = abas[0]
aba_loja = abas[1]
aba_chat = abas[2]
aba_entretenimento = abas[3]
aba_geek = abas[4]
aba_quiz = abas[5]
aba_admin = abas[6] if len(abas) > 6 else None

# === 📺 ABA 1: FEED COMPLETO ===
with aba_feed:

    if st.session_state.perfil_visited:

        if st.session_state.perfil_visitado:
            autor_vis = st.session_state.perfil_visitado
            if st.button("⬅️ Voltar ao Feed Global"):
                st.session_state.perfil_visitado = None
                st.rerun()
            
            p_dados = supabase.table("perfis_usuarios").select("*").eq("username", autor_vis).execute()
            if p_dados.data:
                p_info = p_dados.data[0]
                vis_id = p_info.get("id", "")
                col_p1, col_p2 = st.columns([1, 3], vertical_alignment="bottom")
                with col_p1:
                    renderizar_foto_com_banner(p_info.get("url_foto_perfil") or FOTO_PADRAO, autor_vis, vis_id, tamanho=80, banner_equipado=p_info.get("banner_ativo", "Nenhum"), shimeji=p_info.get("localizacao", "Nenhum"))
                with col_p2:
                    s_vis = obter_selo_texto(autor_vis, vis_id, cargo_adicional=p_info.get("biografia", "Nenhum"))
                    st.subheader(f"{p_info.get('apelido') or autor_vis} {s_vis}")
                    
                    if autor_vis != u_name and vis_id:
                        try:
                            ja_segue = supabase.table("seguidores").select("*").eq("id_seguidor", u_id).eq("id_seguido", vis_id).execute()
                            if ja_segue.data:
                                if st.button("Seguindo ✓"):
                                    supabase.table("seguidores").delete().eq("id_seguidor", u_id).eq("id_seguido", vis_id).execute()
                                    st.rerun()
                            else:
                                if st.button("Seguir ➕", type="primary"):
                                    supabase.table("seguidores").insert({"id_seguidor": u_id, "id_seguido": vis_id}).execute()
                                    st.rerun()
                        except: pass

                st.write("### Publicações do Usuário")
                try:
                    v_dados = supabase.table("feed_videos").select("*").eq("username_autor", autor_vis).execute()
                    if v_dados.data:
                        renderizar_lista_filtrada(reversed(v_dados.data), "perfil")
                    else:
                        st.info("Nenhuma publicação encontrada.")
                except: st.error("Erro ao carregar publicações deste perfil.")
        else:
            exibir_logo()
            busca_legenda = st.text_input("Buscar posts por legenda:", placeholder="Ex: Bleach, Naruto...")
            ordenar_por = st.radio("Ordenar por:", ["📅 Mais Recentes", "🔥 Mais Populares"], horizontal=True)
            
            aba_midia = st.tabs(["📱 Mini Vídeos", "🖥️ Vídeos Longos / Fotos"])
            
            with aba_midia[0]:
                try:
                    f_dados = supabase.table("feed_videos").select("*").eq("tipo_formato", "vertical").execute()
                    posts_completos = (f_dados.data or []) + [b for b in VIDEOS_BOT_BOTEY if b.get("tipo_formato") == "vertical"]
                    renderizar_lista_filtrada(reversed(posts_completos), "vertical_global", busca_legenda, ordenar_por)
                except: st.error("Erro ao carregar a tabela feed_videos.")

            with aba_midia[1]:
                with st.expander("➕ Publicar Novo Conteúdo"):
                    t_pub = st.text_input("Legenda:", key="leg_nova")
                    f_midia = st.file_uploader("Arquivo de Vídeo ou Imagem:", type=["mp4", "png", "jpg", "jpeg"])
                    fmt = st.selectbox("Formato:", ["Horizontal / Padrão", "Vertical / Shorts"])
                    fmt_db = "vertical" if "Vertical" in fmt else "horizontal"
                    
                    if st.button("Publicar Post 🚀") and f_midia and t_pub:
                        try:
                            bucket = "videos_feed" if fmt_db == "vertical" or f_midia.name.endswith(".mp4") else "imagens_chat"
                            path_b = f"feed/{uuid.uuid4()}_{f_midia.name}"
                            supabase.storage.from_(bucket).upload(path_b, f_midia.read())
                            url_f = supabase.storage.from_(bucket).get_public_url(path_b)
                            
                            supabase.table("feed_videos").insert({
                                "titulo": t_pub, "url_video": url_f, "username_autor": u_name,
                                "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0,
                                "id_autor": str(u_id), "tipo_formato": fmt_db
                            }).execute()
                            st.success("Publicado!")
                            st.rerun()
                        except: st.error("Erro ao tentar subir arquivo para o Storage.")

                try:
                    f_dados = supabase.table("feed_videos").select("*").eq("tipo_formato", "horizontal").execute()
                    posts_completos_h = (f_dados.data or []) + [b for b in VIDEOS_BOT_BOTEY if b.get("tipo_formato") == "horizontal"]
                    renderizar_lista_filtrada(reversed(posts_completos_h), "horizontal_global", busca_legenda, ordenar_por)
                except: pass

    # === 🛒 ABA 2: LOJA ===
    with aba_loja:
        st.header("🛒 Loja de Cosméticos Premium")
        saldo_atual = user_atual.get("moedas", 0)
        st.info(f"Seu saldo actual: 🪙 {saldo_atual} Silver Coins")
        
        col_l1, col_l2 = st.columns(2)
        for idx, (chave, info) in enumerate(COSMETICOS.items()):
            coluna_foco = col_l1 if idx % 2 == 0 else col_l2
            with coluna_foco:
                with st.container(border=True):
                    if info.get("img"):
                        st.image(info["img"], width=60)
                    st.markdown(f"### {info['nome']}")
                    st.write(f"Preço: 🪙 {info['preco']} Silver Coins")
                    
                    if saldo_atual >= info['preco']:
                        if st.button(f"Adquirir Item", key=f"loja_buy_{chave}", use_container_width=True):
                            try:
                                novo_saldo = int(saldo_atual) - int(info['preco'])
                                supabase.table("perfis_usuarios").update({"moedas": novo_saldo}).eq("id", u_id).execute()
                                st.success("Adquirido!")
                                st.rerun()
                            except: pass
                    else:
                        st.button("Coins Insuficientes ❌", key=f"insuf_{chave}", disabled=True, use_container_width=True)

    # === 💬 ABA 3: CHAT-EXV TOTALMENTE EXPANDIDO ===
    with aba_chat:
        st.header("💬 Chat-Exv Core")
        aba_c_interna = st.tabs(["🌐 Sala Ativa", "🔑 Entrar / Criar Sala", "👥 Lista de Amigos", "➕ Adicionar Amigo"])
        sala_atual = st.session_state.sala_ativa
        
        with aba_c_interna[0]:
            st.subheader(f"Sala Atual: `{sala_atual}`")
            if sala_atual != "GERAL":
                if st.button("⬅️ Sair da Sala e voltar para a GERAL"):
                    st.session_state.sala_ativa = "GERAL"
                    st.rerun()
            
            with st.expander("📸 Enviar Foto / Mídia"):
                arquivo_chat = st.file_uploader("Escolha uma imagem para o chat:", type=["png", "jpg", "jpeg", "gif", "webp"])
                if st.button("Enviar Imagem 🚀") and arquivo_chat:
                    try:
                        nome_da_foto = f"chat/imagens/{uuid.uuid4()}_{arquivo_chat.name}"
                        supabase.storage.from_("imagens_chat").upload(nome_da_foto, arquivo_chat.read())
                        url_da_foto = supabase.storage.from_("imagens_chat").get_public_url(nome_da_foto)
                        
                        supabase.table("bate-papo_professional").insert({
                            "username": u_name, "id_usuario": str(u_id),
                            "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "mensagem": url_da_foto, "codigo_sala": sala_atual
                        }).execute()
                        st.rerun()
                    except Exception as e: st.error(f"Falha ao subir imagem: {e}")

            st.markdown("### 🎙️ Gravador de Áudio")
            if "b64_audio_data" not in st.session_state:
                st.session_state.b64_audio_data = ""
                
            audio_base64 = st.text_input("Dados Gravador", type="password", value=st.session_state.b64_audio_data, label_visibility="collapsed", key="audio_injector")
            
            if st.button("Clique aqui se o áudio não subir automático ⚡", use_container_width=True) or (audio_base64 and audio_base64 != st.session_state.b64_audio_data):
                if audio_base64:
                    try:
                        dados_audio = base64.b64decode(audio_base64)
                        nome_arquivo = f"chat/audios/{uuid.uuid4()}.wav"
                        supabase.storage.from_("audios_chat").upload(nome_arquivo, dados_audio)
                        url_publica_audio = supabase.storage.from_("audios_chat").get_public_url(nome_arquivo)
                        
                        supabase.table("bate-papo_professional").insert({
                            "username": u_name, "id_usuario": str(u_id),
                            "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "mensagem": url_publica_audio, "codigo_sala": sala_atual
                        }).execute()
                        st.session_state.b64_audio_data = ""
                        st.rerun()
                    except Exception as e: st.error(f"Erro ao salvar áudio: {e}")

            gravador_html = """
            <div style="display: flex; gap: 10px; justify-content: center; padding: 5px 0;">
                <button id="startBtn" style="background-color: #24a0ed; color: white; border: none; padding: 12px 20px; border-radius: 25px; font-weight: bold; width: 45%; cursor: pointer;">🎙️ Gravar</button>
                <button id="stopBtn" style="background-color: #ff4b4b; color: white; border: none; padding: 12px 20px; border-radius: 25px; font-weight: bold; width: 45%; cursor: pointer; display: none;">⏹️ Enviar</button>
            </div>
            <div id="statusLabel" style="text-align: center; color: #777; font-size: 12px; margin-top: 5px;">Pressione Gravar para falar</div>
            <script>
            let mediaRecorder; let audioChunks = [];
            const startBtn = document.getElementById('startBtn'); const stopBtn = document.getElementById('stopBtn'); const statusLabel = document.getElementById('statusLabel');
            startBtn.onclick = async () => {
                audioChunks = [];
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const reader = new FileReader(); reader.readAsDataURL(audioBlob);
                        reader.onloadend = () => {
                            const base64String = reader.result.split(',')[1];
                            const inputs = window.parent.document.querySelectorAll('input[type="password"]');
                            if(inputs.length > 0) {
                                let targetInput = inputs[0]; targetInput.value = base64String;
                                targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        };
                    };
                    mediaRecorder.start(); startBtn.style.display = 'none'; stopBtn.style.display = 'inline-block'; statusLabel.innerText = "🔴 Gravando...";
                } catch(err) { statusLabel.innerText = "Microfone negado."; }
            };
            stopBtn.onclick = () => { mediaRecorder.stop(); startBtn.style.display = 'inline-block'; stopBtn.style.display = 'none'; statusLabel.innerText = "Enviando..."; };
            </script>
            """
            st.components.v1.html(gravador_html, height=85)
            st.markdown("---")

            m_txt = st.text_input("Mensagem:", key="input_texto_chat_direto", placeholder="Digite sua mensagem...")
            if st.button("Enviar Mensagem ✉️", use_container_width=True) and m_txt.strip():
                try:
                    supabase.table("bate-papo_professional").insert({
                        "username": u_name, "id_usuario": str(u_id),
                        "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                        "mensagem": m_txt.strip(), "codigo_sala": sala_atual
                    }).execute()
                    st.rerun()
                except Exception as e: st.error(f"Erro ao salvar mensagem: {e}")

            try:
                m_dados = supabase.table("bate-papo_professional").select("*").eq("codigo_sala", sala_atual).execute()
                for m in reversed(m_dados.data[-40:]):
                    if "POST-" in str(m.get("codigo_sala")): continue
                    m_user = m.get('username', 'Membro')
                    m_msg = m.get('mensagem', '')
                    
                    col_m1, col_m2 = st.columns([1, 6], vertical_alignment="bottom")
                    with col_m1:
                        renderizar_foto_com_banner(m.get("url_foto_perfil") or FOTO_PADRAO, m_user, tamanho=40)
                    with col_m2:
                        s_msg = obter_selo_texto(m_user)
                        try:
                            estilo_u = supabase.table("perfis_usuarios").select("banner_ativo", "id").eq("username", m_user).execute()
                            txt_caixa = estilo_u.data[0].get("banner_ativo", "Nenhum") if estilo_u.data else "Nenhum"
                            uid_remetente = estilo_u.data[0].get("id") if estilo_u.data else ""
                        except:
                            txt_caixa = "Nenhum"
                            uid_remetente = ""
                        renderizar_caixa_mensagem(m_user, m_msg, s_msg, txt_caixa, eh_admin=verificar_se_eh_dev(uid_remetente))
            except: pass

        with aba_c_interna[1]:
            st.subheader("🔑 Entrar em Chat Privado ou Grupo")
            cod_sala_in = st.text_input("Código Secreto da Sala (Ex: ChatAmigos7, RafaelPrivado):").strip()
            if st.button("Conectar à Sala 🚪", use_container_width=True):
                if cod_sala_in:
                    st.session_state.sala_ativa = cod_sala_in.upper()
                    st.success(f"Conectado à sala {cod_sala_in.upper()}!")
                    st.rerun()

        with aba_c_interna[2]:
            st.subheader("👥 Seus Amigos & Conexões")
            try:
                seg_dados = supabase.table("seguidores").select("*").eq("id_seguidor", u_id).execute()
                if seg_dados.data:
                    for s_item in seg_dados.data:
                        id_amigo = s_item.get("id_seguido")
                        perfil_amigo = supabase.table("perfis_usuarios").select("*").eq("id", id_amigo).execute()
                        if perfil_amigo.data:
                            p_amg = perfil_amigo.data[0]
                            st.write(f"• **{p_amg.get('username')}** - Status: {obter_status_emoji(p_amg.get('ultimo_visto'))}")
                            if st.button(f"Abrir Direct com {p_amg.get('username')}", key=f"dm_{p_amg.get('id')}"):
                                id_sala_combinada = f"DM-{max(u_id, str(id_amigo))}-{min(u_id, str(id_amigo))}"
                                st.session_state.sala_ativa = id_sala_combinada
                                st.rerun()
                else:
                    st.caption("Você ainda não adicionou ou seguiu ninguém.")
            except: pass

        with aba_c_interna[3]:
            st.subheader("➕ Localizar e Adicionar Amigos")
            nome_busca_amigo = st.text_input("Digite o nome exato do usuário:")
            if st.button("Adicionar Conexão 🚀"):
                if nome_busca_amigo:
                    try:
                        alvo_dados = supabase.table("perfis_usuarios").select("*").eq("username", nome_busca_amigo).execute()
                        if alvo_dados.data:
                            id_alvo_amg = alvo_dados.data[0].get("id")
                            supabase.table("seguidores").insert({"id_seguidor": u_id, "id_seguido": id_alvo_amg}).execute()
                            st.success(f"Agora você está seguindo {nome_busca_amigo}!")
                        else:
                            st.error("Usuário não encontrado.")
                    except: st.error("Erro ao processar solicitação.")

    # === 🍿 ABA 4: ÁREA GEEK COMPLETA ===
    with aba_entretenimento:
        st.header("🍿 Catálogo Geek da Comunidade")
        st.write("Indique obras, compartilhe links e veja o que a galera está assistindo!")
        
        with st.expander("🎬 Adicionar Recomendação no Catálogo"):
            nova_obra_titulo = st.text_input("Nome da Obra (Anime/Filme/Série/Dorama):")
            nova_obra_categoria = st.selectbox("Categoria:", ["Animes", "Filmes", "Séries / Desenhos", "Doramas"])
            nova_obra_link = st.text_input("Link/URL do trailer ou imagem (Opcional):")
            
            if st.button("Salvar Indicação ✨"):
                if nova_obra_titulo:
                    try:
                        supabase.table("feed_videos").insert({
                            "titulo": f"[{nova_obra_categoria.upper()}] {nova_obra_titulo}",
                            "url_video": nova_obra_link if nova_obra_link else "https://cdn-icons-png.flaticon.com/512/3172/3172554.png",
                            "username_autor": u_name,
                            "id_autor": str(u_id),
                            "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "curtidas": 0,
                            "tipo_formato": "horizontal"
                        }).execute()
                        st.success("Recomendação adicionada com sucesso!")
                        st.rerun()
                    except: st.error("Erro ao salvar recomendação.")

        abas_geek = st.tabs(["⛩️ Animes", "🎬 Filmes", "📺 Séries / Desenhos", "🌸 Doramas"])
        categorias_chaves = ["ANIMES", "FILMES", "SÉRIES / DESENHOS", "DORAMAS"]
        
        for g_idx, g_aba in enumerate(abas_geek):
            with g_aba:
                st.subheader(f"Indicações de {categorias_chaves[g_idx].capitalize()}")
                try:
                    g_dados = supabase.table("feed_videos").select("*").execute()
                    itens_filtrados = [item for item in (g_dados.data or []) if f"[{categorias_chaves[g_idx]}]" in str(item.get("titulo", ""))]
                    
                    if itens_filtrados:
                        for item in reversed(itens_filtrados):
                            st.info(f"**{item.get('titulo').replace(f'[{categorias_chaves[g_idx]}] ', '')}** (Indicado por {item.get('username_autor')})")
                            if item.get("url_video") and "http" in item.get("url_video"):
                                st.caption(f"Link: {item.get('url_video')}")
                    else:
                        st.caption(f"Nenhum conteúdo adicionado em {categorias_chaves[g_idx].capitalize()} ainda. Comece agora!")
                except: pass

    # === 🧠 ABA 5: SUPER QUIZ PREMIADO ===
    with aba_quiz:
        st.header("🧠 Super Quiz Premiado")
        cat_q = st.selectbox("Escolha o Tema do Desafio:", list(PERGUNTAS_QUIZ.keys()))
        pf = PERGUNTAS_QUIZ[cat_q][0]
        st.write(f"**Pergunta:** {pf['pergunta']}")
        r_usr = st.radio("Escolha uma alternativa:", pf["opcoes"])
        if st.button("Enviar Resposta 🎯"):
            if r_usr == pf["correta"]:
                try:
                    moedas_atuais = int(user_atual.get("moedas", 0))
                    supabase.table("perfis_usuarios").update({"moedas": moedas_atuais + 100}).eq("id", str(u_id)).execute()
                    st.success("Resposta Correta! Você ganhou +100 Silver Coins!")
                except Exception as e: 
                    st.error(f"Erro ao computar premiação no banco.")
            else: st.error("Incorreto, tente de novo!")

    # === ✨ ABA 6: STATUS ===
    with aba_status:
        st.header("✨ Status Momentâneos")
        st_in = st.text_input("O que você está pensando agora?")
        if st.button("Publicar Status") and st_in.strip():
            try:
                supabase.table("feed_videos").insert({
                    "titulo": f"[STATUS] {st_in.strip()}", "url_video": "", "username_autor": u_name, "id_autor": str(u_id), "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "curtidas": 0, "tipo_formato": "horizontal"
                }).execute()
                st.success("Status postado!")
                st.rerun()
            except: pass

    # === 🔔 ABA 7: NOTIFICAÇÕES COMPLETAS ===
    with aba_notif:
        st.header("🔔 Minhas Notificações")
        if st.button("Limpar e Marcar Todas como Lidas 🧹"):
            try:
                supabase.table("notificacoes").update({"lida": True}).eq("id_destinatario", str(u_id)).execute()
                st.success("Notificações limpas!")
                st.rerun()
            except: pass
            
        try:
            res_notif = supabase.table("notificacoes").select("*").eq("id_destinatario", str(u_id)).execute()
            if res_notif.data:
                for n in reversed(res_notif.data):
                    status_lida = "🔹" if not n.get("lida") else "⚪"
                    st.write(f"{status_lida} {n.get('mensagem')} *({n.get('criado_em', '')[:10]})*")
            else: 
                st.info("Sua caixa de notificações está totalmente vazia por enquanto!")
        except: pass

    # === 👑 ABA 8: PAINEL ADMIN SECHETO TOTALMENTE PREENCHIDO ===
    if is_admin:
        with abas[7]:
            st.header("👑 Painel de Gerenciamento Geral (Dev)")
            st.write("Bem-vindo de volta ao comando central, Rafael.")
            
            # 1. NOVO RECURSO: Injetor Geek Próprio do Admin (Envia Animes, Séries, Doramas e Filmes)
            with st.expander("⛩️ Injetor de Conteúdo Geek Oficial"):
                a_n = st.text_input("Nome da Obra Geek:")
                a_c = st.selectbox("Categoria do Item:", ["Animes", "Filmes", "Séries / Desenhos", "Doramas"], key="admin_geek_cat")
                a_l = st.text_input("Link/Trailer (Opcional):", key="admin_geek_link")
                if st.button("Injetar Obra no Catálogo 🚀", use_container_width=True) and a_n:
                    try:
                        supabase.table("feed_videos").insert({
                            "titulo": f"[{a_c.upper()}] {a_n}",
                            "url_video": a_l if a_l else "https://cdn-icons-png.flaticon.com/512/3172/3172554.png",
                            "username_autor": "🤖 Sistema Dev",
                            "id_autor": str(u_id),
                            "avatar_autor": "https://cdn-icons-png.flaticon.com/512/2585/2585164.png",
                            "curtidas": 0,
                            "tipo_formato": "horizontal"
                        }).execute()
                        st.success(f"{a_n} inserido com sucesso nas categorias!")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

            # 2. Painel de Moedas
            st.subheader("🪙 Injetor de Silver Coins")
            alvo_moedas = st.text_input("Nome do Usuário para receber moedas:")
            qtd_moedas = st.number_input("Quantidade de Moedas:", min_value=1, value=500)
            if st.button("Injetar Moedas ⚡"):
                try:
                    perfil_alvo = supabase.table("perfis_usuarios").select("*").eq("username", alvo_moedas).execute()
                    if perfil_alvo.data:
                        total_m = int(perfil_alvo.data[0].get("moedas", 0)) + qtd_moedas
                        supabase.table("perfis_usuarios").update({"moedas": total_m}).eq("username", alvo_moedas).execute()
                        st.success(f"Moedas injetadas com sucesso para {alvo_moedas}!")
                    else: st.error("Usuário não encontrado.")
                except: pass
                
            # 3. Moderação do Chat
            st.subheader("🧹 Limpeza do Bate-Papo")
            sala_limpar = st.text_input("Código da sala para limpar mensagens:", value="GERAL")
            if st.button("Apagar Mensagens da Sala 🔥"):
                try:
                    supabase.table("bate-papo_professional").delete().eq("codigo_sala", sala_limpar).execute()
                    st.success(f"A sala {sala_limpar} foi totalmente limpa!")
                    st.rerun()
                except: st.error("Erro ao limpar mensagens.")
                
            # 4. Atribuição de Cargos Oficiais
            with st.expander("🎖️ Atribuir Cargos Customizados"):
                user_cargo_target = st.text_input("Username do Usuário:").strip()
                cargo_definido = st.selectbox("Selecione o Cargo:", ["Tester", "Best friends of the dev", "Vice-dev", "Divulgadora", "Moderador", "VIP"])
                if st.button("Conceder Cargo Oficial 🎖️", use_container_width=True):
                    try:
                        supabase.table("perfis_usuarios").update({"biografia": cargo_definido}).eq("username", user_cargo_target).execute()
                        st.success(f"Cargo de {cargo_definido} aplicado com sucesso!")
                    except: st.error("Erro ao atualizar cargo.")

            # 5. Banimento Permanente
            with st.expander("🟥 Banimento Definitivo"):
                user_ban_target = st.text_input("Username do Infrator:").strip()
                if st.button("BANIR USUÁRIO PERMANENTEMENTE 🟥", use_container_width=True):
                    if user_ban_target == "Rafael_oficial":
                        st.error("Não é possível banir a conta mestre do desenvolvedor.")
                    else:
                        try:
                            supabase.table("perfis_usuarios").update({"website": "BANIDO"}).eq("username", user_ban_target).execute()
                            st.error(f"O usuário {user_ban_target} foi banido permanentemente do sistema.")
                        except: pass

            # 6. Status Interno do App
            st.subheader("📊 Métricas da Plataforma")
            try:
                total_usuarios = len(supabase.table("perfis_usuarios").select("id").execute().data)
                total_posts = len(supabase.table("feed_videos").select("id").execute().data)
                st.write(f"• Usuários cadastrados: **{total_usuarios}**")
                st.write(f"• Publicações e registros totais: **{total_posts}**")
            except: pass

    try:
        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", u_id).execute()
    except: pass
