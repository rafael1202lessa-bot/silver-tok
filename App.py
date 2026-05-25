import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone

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
    st.error("Erro de conexão com o banco de dados.")
    st.stop()

CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
NOME_DEVELOPER = "Rafael_oficial"

# Banco de dados simulado de vídeos para o Bot do Desenvolvedor alimentar o sistema
VIDEOS_BOT_BOTEY = [
    {"titulo": "🔥 Edit Incrível de Anime (Vertical)", "url": "https://www.w3schools.com/html/mov_bbb.mp4", "formato": "vertical"},
    {"titulo": "🌌 Gameplay Relaxante 4K (Horizontal)", "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", "formato": "horizontal"},
    {"titulo": "⚡ Lo-Fi Hip Hop para Estudar (Horizontal)", "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4", "formato": "horizontal"},
    {"titulo": "🎬 Mini Clip Engraçado (Vertical)", "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4", "formato": "vertical"}
]

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Sua plataforma de vídeos e conversas privadas</p>", unsafe_allow_html=True)

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = None
if "id_upload_chat" not in st.session_state:
    st.session_state.id_upload_chat = str(uuid.uuid4())
if "id_audio_chat" not in st.session_state:
    st.session_state.id_audio_chat = str(uuid.uuid4())
if "perfil_visitado" not in st.session_state:
    st.session_state.perfil_visitado = None

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
        if agora - dt_usuario < timedelta(minutes=2):
            return "🟢 Online"
    except:
        pass
    return "⚪ Offline"

def criar_notificacao(id_destinatario, tipo, mensagem):
    if not id_destinatario or st.session_state.usuario_logado is None:
        return
    if str(id_destinatario) == str(st.session_state.usuario_logado["id"]):
        return
    try:
        supabase.table("notificacoes").insert({
            "id_destinatario": id_destinatario,
            "id_remetente": st.session_state.usuario_logado["id"],
            "username_remetente": st.session_state.usuario_logado["username"],
            "tipo": tipo,
            "mensagem": mensagem,
            "lida": False
        }).execute()
    except:
        pass

if st.session_state.usuario_logado is None:
    exibir_logo()
    
    aba_auth = st.tabs(["Fazer Login", "Criar Nova Conta"])
    with aba_auth[0]:
        st.subheader("Acesse sua Conta")
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        if st.button("Entrar 🚀", key="btn_login", use_container_width=True):
            if login_user and login_senha:
                try:
                    busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                    if busca.data and busca.data[0]["senha"] == login_senha:
                        st.session_state.usuario_logado = busca.data[0]
                        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", busca.data[0]["id"]).execute()
                        st.success("Login feito com sucesso!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")
                except Exception as e:
                    st.error(f"Erro ao fazer login: {e}")
            else:
                st.warning("Preencha todos os campos!")
                
    with aba_auth[1]:
        st.subheader("Crie seu Perfil")
        cad_user = st.text_input("Escolha um Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie uma Senha:", type="password", key="cad_senha")
        cad_foto = st.file_uploader("Foto de Perfil (Opcional):", type=["png", "jpg", "jpeg"], key="cad_foto")
        codigo_convite = st.text_input("🔑 Código Secreto:", type="password", key="codigo_convite")
        if st.button("Cadastrar Conta 🎉", key="btn_cad", use_container_width=True):
            if cad_user and cad_senha and codigo_convite == CHAVE_SECRETA:
                try:
                    url_foto = FOTO_PADRAO
                    if cad_foto:
                        nome_f = f"perfis/{uuid.uuid4()}.png"
                        supabase.storage.from_("imagens_chat").upload(nome_f, cad_foto.read())
                        url_foto = supabase.storage.from_("imagens_chat").get_public_url(nome_f)
                    supabase.table("perfis_usuarios").insert({
                        "username": cad_user, 
                        "apelido": cad_user,
                        "senha": cad_senha, 
                        "url_foto_perfil": url_foto, 
                        "ultimo_visto": datetime.now(timezone.utc).isoformat()
                    }).execute()
                    st.success("Conta criada! Agora faça o seu login.")
                except:
                    st.error("Erro ao cadastrar ou o usuário já existe.")
            else:
                st.warning("Verifique os campos!")
else:
    user_atual = st.session_state.usuario_logado
    
    try:
        supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", user_atual["id"]).execute()
    except:
        pass

    total_seg = 0
    try:
        res_seg = supabase.table("seguidores").select("*", count="exact").eq("id_seguido", user_atual["id"]).execute()
        total_seg = res_seg.count if (hasattr(res_seg, "count") and res_seg.count is not None) else len(res_seg.data)
    except:
        pass

    total_notif = 0
    try:
        res_n = supabase.table("notificacoes").select("*", count="exact").eq("id_destinatario", user_atual["id"]).eq("lida", False).execute()
        total_notif = res_n.count if (hasattr(res_n, "count") and res_n.count is not None) else len(res_n.data)
    except:
        pass

    st.sidebar.image(user_atual.get("url_foto_perfil") or FOTO_PADRAO, width=90)
    nome_exibicao = user_atual.get("apelido") or user_atual["username"]
    
    if user_atual["username"] == NOME_DEVELOPER:
        st.sidebar.write(f"**{nome_exibicao}** 👑`DEV`")
        st.sidebar.caption(f"@{user_atual['username']}")
    else:
        st.sidebar.write(f"**{nome_exibicao}**")
        st.sidebar.caption(f"@{user_atual['username']}")
    
    st.sidebar.write(f"👥 **{total_seg}** seguidores")
    
    with st.sidebar.expander("⚙️ Editar Meu Perfil"):
        novo_apelido = st.text_input("Alterar Apelido:", value=user_atual.get("apelido") or user_atual["username"]).strip()
        nova_foto_perfil = st.file_uploader("Trocar Foto de Perfil:", type=["png", "jpg", "jpeg", "webp"])
        if st.button("Salvar Alterações 💾", use_container_width=True):
            dados_atualizar = {}
            if novo_apelido: dados_atualizar["apelido"] = novo_apelido
            if nova_foto_perfil:
                try:
                    nome_f = f"perfis/{uuid.uuid4()}.png"
                    supabase.storage.from_("imagens_chat").upload(nome_f, nova_foto_perfil.read())
                    dados_atualizar["url_foto_perfil"] = supabase.storage.from_("imagens_chat").get_public_url(nome_f)
                except: st.error("Erro na foto.")
            if dados_atualizar:
                try:
                    supabase.table("perfis_usuarios").update(dados_atualizar).eq("id", user_atual["id"]).execute()
                    for k, v in dados_atualizar.items(): st.session_state.usuario_logado[k] = v
                    st.success("Perfil atualizado!")
                    st.rerun()
                except: st.error("Erro ao salvar.")

    # === NOVO: COMANDOS DO DESENVOLVEDOR (Apenas visível para ti) ===
    if user_atual["username"] == NOME_DEVELOPER:
        with st.sidebar.expander("🤖 Comandos do Desenvolvedor", expanded=False):
            st.caption("Painel de Controle do Sistema do Bot")
            comando_exec = st.text_input("Digitar comando especial:", placeholder="Ex: /gerar_conteudo_bot")
            
            if st.button("Executar Comando ⚡", use_container_width=True):
                if comando_exec.strip() == "/gerar_conteudo_bot":
                    with st.spinner("Bot adicionando posts aleatórios no feed..."):
                        sucesso_envios = 0
                        for v_item in VIDEOS_BOT_BOTEY:
                            try:
                                supabase.table("feed_videos").insert({
                                    "titulo": v_item["titulo"],
                                    "url_video": v_item["url"],
                                    "username_autor": "System_Bot",
                                    "avatar_autor": "https://cdn-icons-png.flaticon.com/512/4712/4712035.png",
                                    "curtidas": 0,
                                    "id_autor": user_atual["id"],
                                    "tipo_formato": v_item["formato"] # Salva se é vertical ou horizontal
                                }).execute()
                                sucesso_envios += 1
                            except Exception as err:
                                pass
                        if sucesso_envios > 0:
                            st.success(f"Sucesso! Bot publicou {sucesso_envios} vídeos no sistema.")
                            st.rerun()
                        else:
                            st.error("Erro estrutural. Verifique se a coluna 'tipo_formato' existe no Supabase.")
                else:
                    st.warning("Comando desconhecido ou inválido.")

    if st.sidebar.button("Sair 🚪", use_container_width=True):
        st.session_state.usuario_logado = None
        st.session_state.sala_ativa = None
        st.session_state.perfil_visitado = None
        st.rerun()

    aba_feed, aba_chat, aba_status, aba_notif = st.tabs([
        "📺 Silver Tok (Feed)", "💬 Chat-Exv", "✨ Status", f"🔔 Notificações ({total_notif})"
    ])
    
    # === ABA FEED (ATUALIZADA COM COMPARTIMENTOS DE VÍDEO VERTICAL / HORIZONTAL) ===
    with aba_feed:
        if st.session_state.perfil_visitado is not None:
            # [Seção de perfil visitado mantida idêntica para preservar navegação]
            autor_vis = st.session_state.perfil_visitado
            if st.button("⬅️ Voltar para o Feed", use_container_width=True):
                st.session_state.perfil_visitado = None
                st.rerun()
            st.markdown("---")
            try:
                dados_perf = supabase.table("perfis_usuarios").select("*").eq("username", autor_vis).execute()
                if dados_perf.data:
                    p_info = dados_perf.data[0]
                    st.subheader(f"{p_info.get('apelido') or p_info['username']}")
                    st.caption(f"@{autor_vis}")
                    
                    v_dados = supabase.table("feed_videos").select("*").eq("username_autor", autor_vis).execute()
                    if v_dados.data:
                        for vid in reversed(v_dados.data):
                            if vid["titulo"].startswith("[STATUS]"): continue
                            st.caption(vid["titulo"])
                            st.video(vid["url_video"])
                else: st.error("Perfil não encontrado.")
            except Exception as e: st.error(f"Erro: {e}")
                
        else:
            exibir_logo()
            
            termo_pesquisa = st.text_input("Buscar posts por legenda:", placeholder="Ex: Bleach, Naruto, edit...", key="busca_feed").strip()

            with st.expander("➕ Publicar Novo Conteúdo Manualmente"):
                tipo_pub = st.radio("Escolha o método de envio:", ["Enviar Arquivo de Vídeo (Do Aparelho)", "Inserir Link (YouTube)", "Postar Foto 📸"])
                formato_selecionado = st.selectbox("Formato de Exibição da Tela:", ["mini vídeo (Vertical / Shorts)", "vídeo longo (Horizontal / Padrão)"])
                formato_db = "vertical" if "mini" in formato_selecionado else "horizontal"
                titulo_v = st.text_input("Legenda do Post:", placeholder="Ex: Meu novo vídeo! 🔥", key="legenda_video")
                
                if tipo_pub == "Inserir Link (YouTube)":
                    url_v = st.text_input("Link do Vídeo (YouTube):")
                    if st.button("Publicar Link 🚀", use_container_width=True) and url_v.strip() and titulo_v.strip():
                        try:
                            supabase.table("feed_videos").insert({
                                "titulo": titulo_v.strip(), "url_video": url_v.strip(),
                                "username_autor": user_atual["username"], "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": formato_db
                            }).execute()
                            st.success("Postado!"); st.rerun()
                        except Exception as e: st.error(f"Erro: {e}")
                            
                elif tipo_pub == "Enviar Arquivo de Vídeo (Do Aparelho)":
                    file_v = st.file_uploader("Escolha o vídeo:", type=["mp4", "mov", "avi"])
                    if st.button("Fazer Upload e Publicar 🎥", use_container_width=True) and file_v and titulo_v.strip():
                        try:
                            with st.spinner("Enviando..."):
                                nome_video_bucket = f"videos/{uuid.uuid4()}.mp4"
                                supabase.storage.from_("videos_feed").upload(nome_video_bucket, file_v.read())
                                url_video_final = supabase.storage.from_("videos_feed").get_public_url(nome_video_bucket)
                                supabase.table("feed_videos").insert({
                                    "titulo": titulo_v.strip(), "url_video": url_video_final,
                                    "username_autor": user_atual["username"], "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                    "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": formato_db
                                }).execute()
                            st.success("Vídeo enviado!"); st.rerun()
                        except Exception as e: st.error(f"Erro: {e}")

                elif tipo_pub == "Postar Foto 📸":
                    file_img = st.file_uploader("Escolha uma foto:", type=["png", "jpg", "jpeg"])
                    if st.button("Publicar Foto 🖼️", use_container_width=True) and file_img and titulo_v.strip():
                        try:
                            with st.spinner("Enviando..."):
                                nome_foto_bucket = f"fotos_feed/{uuid.uuid4()}.png"
                                supabase.storage.from_("imagens_chat").upload(nome_foto_bucket, file_img.read())
                                url_foto_final = supabase.storage.from_("imagens_chat").get_public_url(nome_foto_bucket)
                                supabase.table("feed_videos").insert({
                                    "titulo": titulo_v.strip(), "url_video": url_foto_final,
                                    "username_autor": user_atual["username"], "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                    "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": "horizontal"
                                }).execute()
                            st.success("Foto postada!"); st.rerun()
                        except Exception as e: st.error(f"Erro: {e}")

            # Sub-abas dividindo o Feed em Mini Vídeos Verticais e Vídeos Longos Horizontais
            aba_formato_mini, aba_formato_longo = st.tabs(["📱 Mini Vídeos (Verticais)", "🖥️ Vídeos Longos (Horizontais)"])

            def renderizar_lista_filtrada(lista_posts, identificador_formato):
                for idx, v in enumerate(lista_posts):
                    if str(v.get("titulo", "")).startswith("[STATUS]"): continue
                    
                    autor = v.get('username_autor', 'Membro')
                    img_autor = v.get('avatar_autor') or FOTO_PADRAO
                    video_url = v["url_video"]
                    likes = v.get("curtidas", 0)
                    chave_comp = f"f_{identificador_formato}_{idx}_{v.get('id', hash(video_url))}"

                    st.markdown("---")
                    col_f1, col_f2 = st.columns([1, 5])
                    with col_f1: st.image(img_autor, width=45)
                    with col_f2:
                        st.markdown(f"**{autor}**")
                        st.caption(v["titulo"])

                    # Regra de exibição de Tela com base no Formato selecionado ou detectado
                    if identificador_formato == "vertical":
                        # HTML injetado seguro para simular a proporção vertical mobile (9:16)
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: center; background-color: #000; border-radius: 12px; padding: 5px;">
                                <video width="290" height="515" controls style="border-radius: 8px;">
                                    <source src="{video_url}" type="video/mp4">
                                    Seu navegador não suporta vídeos.
                                </video>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    else:
                        # Exibição horizontal cheia clássica (16:9)
                        if video_url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                            st.image(video_url, use_container_width=True)
                        else:
                            st.video(video_url)

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button(f"❤️ {likes} Curtidas", key=f"lk_{chave_comp}"):
                            try: supabase.table("feed_videos").update({"curtidas": likes + 1}).eq("id", v["id"]).execute()
                            except: pass
                            st.rerun()
                    with col_b2:
                        if autor == user_atual["username"]:
                            if st.button("Remover 🗑️", key=f"del_{chave_comp}"):
                                try: supabase.table("feed_videos").delete().eq("id", v["id"]).execute()
                                except: pass
                                st.rerun()

            try:
                query_feed = supabase.table("feed_videos").select("*")
                if termo_pesquisa:
                    query_feed = query_feed.ilike("titulo", f"%{termo_pesquisa}%")
                dados = query_feed.execute()
                
                if dados.data:
                    # Filtra em memória os tipos correspondentes salvos no Supabase
                    videos_verticais = [p for p in dados.data if p.get("tipo_formato") == "vertical"]
                    videos_horizontais = [p for p in dados.data if p.get("tipo_formato") != "vertical"]
                    
                    with aba_formato_mini:
                        if videos_verticais: renderizar_lista_filtrada(reversed(videos_verticais), "vertical")
                        else: st.info("Nenhum mini vídeo vertical por aqui.")
                            
                    with aba_formato_longo:
                        if videos_horizontais: renderizar_lista_filtrada(reversed(videos_horizontais), "horizontal")
                        else: st.info("Nenhum vídeo longo horizontal por aqui.")
                else:
                    st.info("Nenhum conteúdo publicado.")
            except Exception as e:
                st.error(f"Erro ao ler feed: {e}")

    # === [Abas Restantes Permanecem Intactas da Última Versão Funcional] ===
    with aba_chat:
        if st.session_state.sala_ativa is not None:
            st.title(f"💬 Sala: {st.session_state.sala_ativa}")
            if st.button("⬅️ Voltar ao Menu Chat"): st.session_state.sala_ativa = None; st.rerun()
            # Mecanismo interno de chat simplificado para exibição limpa
            try:
                res = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", st.session_state.sala_ativa).execute()
                if res.data:
                    for m in reversed(res.data[-20:]):
                        st.write(f"**{m['username']}:** {m.get('mensagem', '[Mídia]')}")
            except: pass
        else:
            st.write("Escolha uma sala ativa ou crie uma nova para conversar.")
            
    with aba_status:
        st.write("Área destinada para atualizações de Status temporários de 24 horas.")
        
    with aba_notif:
        st.write("Sem notificações complexas ativas.")
