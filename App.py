import streamlit as st
from supabase import create_client, Client
import uuid
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2.6", page_icon="🎬", layout="centered")

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

# --- CONFIGURAÇÕES GERAIS DE SEGURANÇA ---
CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
NOME_DEVELOPER = "Rafael_oficial"
COMANDO_BOT_SECRETO = "/gerar_conteudo_bot"

VIDEOS_BOT_BOTEY = [
    {"titulo": "🔥 Edit Incrível de Anime (Vertical)", "url": "https://www.w3schools.com/html/mov_bbb.mp4", "formato": "vertical"},
    {"titulo": "🌌 Gameplay Relaxante 4K (Horizontal)", "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", "formato": "horizontal"},
    {"titulo": "⚡ Lo-Fi Hip Hop para Estudar (Horizontal)", "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4", "formato": "horizontal"},
    {"titulo": "🎬 Mini Clip Engraçado (Vertical)", "url": "https://commondatachannel.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4", "formato": "vertical"}
]

# --- FUNÇÕES AUXILIARES (Definidas no topo para evitar erros de escopo) ---
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

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Sua plataforma de vídeos e conversas privadas</p>", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
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

# --- FLUXO DE AUTENTICAÇÃO ---
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
                        try:
                            supabase.table("perfis_usuarios").update({"ultimo_visto": datetime.now(timezone.utc).isoformat()}).eq("id", busca.data[0]["id"]).execute()
                        except: pass
                        st.success("Login efetuado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")
                except Exception as e:
                    st.error(f"Erro ao autenticar: {e}")
            else:
                st.warning("Por favor, preencha todos os campos!")
                
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
                    st.success("Conta criada com sucesso! Faça login na aba ao lado.")
                except:
                    st.error("Erro ao cadastrar. O nome de usuário já pode estar em uso.")
            else:
                st.warning("Verifique as credenciais ou o código de convite.")
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

    # --- PAINEL LATERAL (SIDEBAR) ---
    st.sidebar.image(user_atual.get("url_foto_perfil") or FOTO_PADRAO, width=90)
    nome_exibicao = user_atual.get("apelido") or user_atual["username"]
    
    if user_atual["username"] == NOME_DEVELOPER:
        st.sidebar.write(f"**{nome_exibicao}** 👑`DEV`")
        st.sidebar.caption(f"@{user_atual['username']}")
    elif total_seg >= 1000:
        st.sidebar.write(f"**{nome_exibicao}** ✔️")
        st.sidebar.caption(f"@{user_atual['username']}")
    else:
        st.sidebar.write(f"**{nome_exibicao}**")
        st.sidebar.caption(f"@{user_atual['username']}")
    
    st.sidebar.write(f"👥 **{total_seg}** seguidores")
    st.sidebar.write("🟢 Status: **Online**")
    
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
                except: st.error("Erro no envio da imagem de perfil.")
            
            if dados_atualizar:
                try:
                    supabase.table("perfis_usuarios").update(dados_atualizar).eq("id", user_atual["id"]).execute()
                    for k, v in dados_atualizar.items(): st.session_state.usuario_logado[k] = v
                    st.success("Perfil updated!")
                    st.rerun()
                except: st.error("Erro ao salvar dados.")

    if user_atual["username"] == NOME_DEVELOPER:
        with st.sidebar.expander("🤖 Comandos do Desenvolvedor", expanded=True):
            st.write("**Código Secreto:**")
            st.code(COMANDO_BOT_SECRETO, language="text")
            comando_exec = st.text_input("Digitar o comando especial aqui:", placeholder="Cole o código acima...")
            
            if st.button("Executar Comando ⚡", use_container_width=True):
                if comando_exec.strip() == COMANDO_BOT_SECRETO:
                    with st.spinner("Injetando publicações do bot..."):
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
                                    "tipo_formato": v_item["formato"]
                                }).execute()
                                sucesso_envios += 1
                            except: pass
                        if sucesso_envios > 0:
                            st.success(f"O Bot publicou {sucesso_envios} mídias.")
                            st.rerun()
                else: st.warning("Comando inválido!")

    if st.sidebar.button("Sair da Conta 🚪", use_container_width=True):
        st.session_state.usuario_logado = None
        st.session_state.sala_ativa = None
        st.session_state.perfil_visitado = None
        st.rerun()

    # --- NAVEGAÇÃO PRINCIPAL ---
    aba_feed, aba_chat, aba_status, aba_notif = st.tabs([
        "📺 Silver Tok (Feed)", "💬 Chat-Exv", "✨ Status", f"🔔 Notificações ({total_notif})"
    ])
    
    # === 📺 ABA SILVER TOK (FEED) ===
    with aba_feed:
        if st.session_state.perfil_visitado is not None:
            autor_vis = st.session_state.perfil_visitado
            if st.button("⬅️ Voltar para o Feed Global", use_container_width=True):
                st.session_state.perfil_visitado = None
                st.rerun()
                
            st.markdown("---")
            try:
                dados_perf = supabase.table("perfis_usuarios").select("*").eq("username", autor_vis).execute()
                if dados_perf.data:
                    p_info = dados_perf.data[0]
                    id_autor_vis = p_info["id"]
                    img_autor_vis = p_info.get("url_foto_perfil") or FOTO_PADRAO
                    status_autor = obter_status_emoji(p_info.get("ultimo_visto"))
                    apelido_autor = p_info.get("apelido") or p_info["username"]
                    
                    qtd_seg_v = 0
                    try:
                        c_seg_v = supabase.table("seguidores").select("*", count="exact").eq("id_seguido", id_autor_vis).execute()
                        qtd_seg_v = c_seg_v.count if (hasattr(c_seg_v, "count") and c_seg_v.count is not None) else len(c_seg_v.data)
                    except: pass
                    
                    col_p1, col_p2 = st.columns([1, 3])
                    with col_p1: st.image(img_autor_vis, width=100)
                    with col_p2:
                        selo_v = " 👑`DEV`" if autor_vis == NOME_DEVELOPER else (" ✔️" if qtd_seg_v >= 1000 else "")
                        st.subheader(f"{apelido_autor}{selo_v}")
                        st.caption(f"@{autor_vis}")
                        st.write(f"Status: **{status_autor}** | 👥 **{qtd_seg_v}** seguidores")
                        
                        if autor_vis != user_atual["username"]:
                            try:
                                ja_segue_v = supabase.table("seguidores").select("*").eq("id_seguidor", user_atual["id"]).eq("id_seguido", id_autor_vis).execute()
                                if ja_segue_v.data:
                                    if st.button("Seguindo ✓", use_container_width=True):
                                        supabase.table("seguidores").delete().eq("id_seguidor", user_atual["id"]).eq("id_seguido", id_autor_vis).execute()
                                        st.rerun()
                                else:
                                    if st.button("Seguir Perfil ➕", use_container_width=True, type="primary"):
                                        supabase.table("seguidores").insert({"id_seguidor": user_atual["id"], "id_seguido": id_autor_vis}).execute()
                                        criar_notificacao(id_autor_vis, "seguidor", f"@{user_atual['username']} começou a seguir o seu perfil!")
                                        st.rerun()
                            except: pass
                else: st.error("Perfil não encontrado.")
            except Exception as e: st.error(f"Erro ao abrir perfil: {e}")
        else:
            exibir_logo()
            termo_pesquisa = st.text_input("Buscar posts por legenda:", placeholder="Ex: Bleach, Naruto, edit...").strip()

            with st.expander("➕ Publicar Novo Conteúdo"):
                tipo_pub = st.radio("Escolha o método de envio:", ["Enviar Arquivo de Vídeo", "Inserir Link (YouTube)", "Postar Foto 📸"])
                formato_sel = st.selectbox("Formato de Exibição do Feed:", ["mini vídeo (Vertical / Shorts)", "vídeo longo (Horizontal / Padrão)"])
                formato_db = "vertical" if "mini" in formato_sel else "horizontal"
                titulo_v = st.text_input("Legenda da Publicação:")
                
                if tipo_pub == "Inserir Link (YouTube)":
                    link_yt = st.text_input("Link do YouTube:")
                    if st.button("Publicar Link 🚀", use_container_width=True) and titulo_v.strip() and link_yt.strip():
                        supabase.table("feed_videos").insert({
                            "titulo": titulo_v.strip(), "url_video": link_yt.strip(),
                            "username_autor": user_atual["username"], "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": formato_db
                        }).execute()
                        st.success("Publicado com sucesso!"); st.rerun()
                        
                elif tipo_pub == "Enviar Arquivo de Vídeo":
                    file_v = st.file_uploader("Escolha o vídeo mp4:", type=["mp4", "mov"])
                    if st.button("Fazer Upload de Vídeo 🎥", use_container_width=True) and file_v and titulo_v.strip():
                        nome_video_bucket = f"videos/{uuid.uuid4()}.mp4"
                        supabase.storage.from_("videos_feed").upload(nome_video_bucket, file_v.read())
                        url_video_final = supabase.storage.from_("videos_feed").get_public_url(nome_video_bucket)
                        supabase.table("feed_videos").insert({
                            "titulo": titulo_v.strip(), "url_video": url_video_final,
                            "username_autor": user_atual["username"], "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": formato_db
                        }).execute()
                        st.success("Vídeo processado e publicado!"); st.rerun()

                elif tipo_pub == "Postar Foto 📸":
                    file_img = st.file_uploader("Escolha a imagem:", type=["png","jpg","jpeg"])
                    if st.button("Postar Foto no Feed 🖼️", use_container_width=True) and file_img and titulo_v.strip():
                        nome_img_bucket = f"fotos_feed/{uuid.uuid4()}.png"
                        supabase.storage.from_("imagens_chat").upload(nome_img_bucket, file_img.read())
                        url_img_final = supabase.storage.from_("imagens_chat").get_public_url(nome_img_bucket)
                        supabase.table("feed_videos").insert({
                            "titulo": titulo_v.strip(), "url_video": url_img_final,
                            "username_autor": user_atual["username"], "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": "horizontal"
                        }).execute()
                        st.success("Foto publicada!"); st.rerun()

            aba_formato_mini, aba_formato_longo = st.tabs(["📱 Mini Vídeos (Verticais)", "🖥️ Vídeos Longos (Horizontais)"])

            def renderizar_lista_filtrada(lista_posts, identificador_formato):
                for idx, v in enumerate(lista_posts):
                    if str(v.get("titulo", "")).startswith("[STATUS]"): continue
                    autor = v.get('username_autor', 'Membro')
                    img_autor = v.get('avatar_autor') or FOTO_PADRAO
                    video_url = v["url_video"]
                    likes = v.get("curtidas", 0)
                    id_post = v.get("id")
                    chave_comp = f"feed_{identificador_formato}_{idx}_{id_post}"

                    st.markdown("---")
                    col_f1, col_f2 = st.columns([1, 5])
                    with col_f1: 
                        st.image(img_autor, width=50)
                        if st.button("👤", key=f"btn_perfil_f_{chave_comp}"):
                            st.session_state.perfil_visitado = autor
                            st.rerun()
                    with col_f2:
                        st.markdown(f"**{autor}**")
                        st.caption(v["titulo"])

                    if identificador_formato == "vertical":
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: center; background-color: #000; border-radius: 12px; padding: 5px; margin-bottom: 10px;">
                                <video width="290" height="515" controls style="border-radius: 8px;">
                                    <source src="{video_url}" type="video/mp4">
                                </video>
                            </div>
                            """, unsafe_allow_html=True
                        )
                    else:
                        if video_url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) or "/fotos_feed/" in video_url: 
                            st.image(video_url, use_container_width=True)
                        else: 
                            st.video(video_url)

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button(f"❤️ {likes} Curtidas", key=f"btn_like_{chave_comp}"):
                            supabase.table("feed_videos").update({"curtidas": likes + 1}).eq("id", id_post).execute()
                            if v.get("id_autor"):
                                criar_notificacao(v["id_autor"], "curtida", f"@{user_atual['username']} curtiu sua publicação!")
                            st.rerun()
                    with col_b2:
                        if autor == user_atual["username"] and st.button("Remover Post 🗑️", key=f"btn_deletar_{chave_comp}"):
                            supabase.table("feed_videos").delete().eq("id", id_post).execute()
                            st.rerun()

                    # === SECÇÃO DE COMENTÁRIOS INTEGRADA ===
                    with st.expander(f"💬 Comentários para este post"):
                        with st.form(key=f"form_coment_{chave_comp}", clear_on_submit=True):
                            novo_coment = st.text_input("Escreve um comentário:", placeholder="Diz o que achas...")
                            enviar_c = st.form_submit_button("Comentar ✉️")
                            
                            if enviar_c and novo_coment.strip():
                                try:
                                    supabase.table("comentarios_feed").insert({
                                        "id_video": id_post,
                                        "id_autor": user_atual["id"],
                                        "username_autor": user_atual["username"],
                                        "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                        "comentario": novo_coment.strip()
                                    }).execute()
                                    if v.get("id_autor"):
                                        criar_notificacao(v["id_autor"], "comentario", f"@{user_atual['username']} comentou no teu post!")
                                    st.success("Comentário enviado!")
                                    st.rerun()
                                except Exception as e:
                                    st.error("Erro ao enviar comentário. Certifica-te de rodar o SQL corrigido no painel.")

                        try:
                            lista_c = supabase.table("comentarios_feed").select("*").eq("id_video", id_post).order("criado_em", descending=True).execute()
                            if lista_c.data:
                                for c in lista_c.data:
                                    col_c1, col_c2 = st.columns([1, 8])
                                    with col_c1:
                                        st.image(c.get("avatar_autor") or FOTO_PADRAO, width=35)
                                    with col_c2:
                                        st.markdown(f"**{c['username_autor']}**: {c['comentario']}")
                                        st.caption(f"Enviado em: {c['criado_em'][:16].replace('T', ' ')}")
                            else:
                                st.caption("Nenhum comentário por aqui ainda. Sê o primeiro!")
                        except:
                            st.caption("A carregar comentários...")

            try:
                query_feed = supabase.table("feed_videos").select("*")
                if termo_pesquisa: query_feed = query_feed.ilike("titulo", f"%{termo_pesquisa}%")
                dados = query_feed.execute()
                if dados.data:
                    with aba_formato_mini:
                        v_verts = [p for p in dados.data if p.get("tipo_formato") == "vertical"]
                        if v_verts: renderizar_lista_filtrada(reversed(v_verts), "vertical")
                        else: st.info("Nenhum mini vídeo vertical disponível.")
                    with aba_formato_longo:
                        v_horiz = [p for p in dados.data if p.get("tipo_formato") != "vertical"]
                        if v_horiz: renderizar_lista_filtrada(reversed(v_horiz), "horizontal")
                        else: st.info("Nenhum vídeo longo ou foto disponível.")
            except Exception as e: st.error(f"Erro ao ler feed: {e}")


    # === 💬 ABA CHAT-EXV ===
    with aba_chat:
        if st.session_state.sala_ativa is not None:
            st.subheader(f"💬 Conversa Ativa: {st.session_state.sala_ativa}")
            if st.button("⬅️ Fechar Chat e Sair da Sala", use_container_width=True): 
                st.session_state.sala_ativa = None
                st.rerun()
                
            txt_m = st.text_input("Escreva sua mensagem aqui...", key="txt_msg_chat")
            col_u1, col_u2 = st.columns(2)
            with col_u1: up_img = st.file_uploader("Enviar Foto 📸", type=["png","jpg","jpeg"], key=st.session_state.id_upload_chat)
            with col_u2: up_aud = st.audio_input("Enviar Mensagem de Voz 🎙️", key=st.session_state.id_audio_chat)
            
            if st.button("Enviar Mensagem ✉️", use_container_width=True) and (txt_m.strip() or up_img or up_aud):
                url_img = None
                if up_img:
                    nome_f = f"chat/{uuid.uuid4()}.png"
                    supabase.storage.from_("imagens_chat").upload(nome_f, up_img.read())
                    url_img = supabase.storage.from_("imagens_chat").get_public_url(nome_f)
                elif up_aud:
                    nome_a = f"audios/{uuid.uuid4()}.wav"
                    supabase.storage.from_("imagens_chat").upload(nome_a, up_aud.read())
                    url_img = supabase.storage.from_("imagens_chat").get_public_url(nome_a)
                
                try:
                    supabase.table("bate-papo_profissional").insert({
                        "id_usuario": user_atual["id"], "username": user_atual["username"],
                        "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                        "mensagem": txt_m.strip() if txt_m.strip() else None, "url_imagem_enviada": url_img,
                        "codigo_sala": st.session_state.sala_ativa
                    }).execute()
                except Exception as e:
                    st.error("Erro ao enviar mensagem.")
                
                st.session_state.id_upload_chat = str(uuid.uuid4())
                st.session_state.id_audio_chat = str(uuid.uuid4())
                st.rerun()

            st.markdown("---")
            try:
                res = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", st.session_state.sala_ativa).execute()
                if res.data:
                    for m in reversed(res.data[-40:]):
                        col_m1, col_m2 = st.columns([1, 6])
                        with col_m1:
                            st.image(m.get("url_foto_perfil") or FOTO_PADRAO, width=40)
                        with col_m2:
                            st.markdown(f"**{m['username']}:** {m.get('mensagem') or ''}")
                            if m.get("url_imagem_enviada"):
                                if m["url_imagem_enviada"].lower().endswith(('.wav', '.mp3')): 
                                    st.audio(m["url_imagem_enviada"])
                                else: 
                                    st.image(m["url_imagem_enviada"], width=230)
                else: st.info("Nenhuma mensagem nesta sala.")
            except: pass
        else:
            st.title("🎛️ Painel Chat-Exv")
            m_tabs = st.tabs(["💬 Privado", "👨‍👩‍👦 Novo Grupo", "🔑 Entrar", "👥 Amigos", "➕ Adicionar"])
            
            with m_tabs[0]:
                st.subheader("Canais Privados")
                alvo_chat = st.text_input("Username do amigo para chat privado:", placeholder="Ex: Rafael_oficial").strip()
                if st.button("Abrir Conversa Direta 🚀", use_container_width=True) and alvo_chat:
                    lista_nomes = sorted([user_atual['username'].upper(), alvo_chat.upper()])
                    st.session_state.sala_ativa = f"CHAT-{lista_nomes[0]}-{lista_nomes[1]}"
                    st.rerun()
                    
            with m_tabs[1]:
                st.subheader("Criar uma Nova Sala / Grupo")
                nome_novo_grupo = st.text_input("Nome do Grupo:", placeholder="Ex: ANIME-CLUB").strip()
                if st.button("Criar e Entrar no Grupo 🚀", use_container_width=True) and nome_novo_grupo:
                    st.session_state.sala_ativa = nome_novo_grupo.upper()
                    st.rerun()
                    
            with m_tabs[2]:
                st.subheader("Entrar em Código Existente")
                cod_d = st.text_input("Insira o código da sala:").strip().upper()
                if st.button("Conectar à Sala 🚪", use_container_width=True) and cod_d:
                    st.session_state.sala_ativa = cod_d
                    st.rerun()
                    
            with m_tabs[3]:
                st.subheader("Membros da Comunidade")
                try:
                    todos_usuarios = supabase.table("perfis_usuarios").select("username", "ultimo_visto", "url_foto_perfil").execute()
                    if todos_usuarios.data:
                        for u in todos_usuarios.data:
                            if u["username"] != user_atual["username"]:
                                status_u = obter_status_emoji(u.get("ultimo_visto"))
                                col_u1, col_u2, col_u3 = st.columns([1, 3, 2])
                                with col_u1: st.image(u.get("url_foto_perfil") or FOTO_PADRAO, width=40)
                                with col_u2: st.write(f"**{u['username']}**\n{status_u}")
                                with col_u3:
                                    if st.button("Conversar 💬", key=f"chat_list_{u['username']}"):
                                        lista_nomes = sorted([user_atual['username'].upper(), u['username'].upper()])
                                        st.session_state.sala_ativa = f"CHAT-{lista_nomes[0]}-{lista_nomes[1]}"
                                        st.rerun()
                except: pass
                    
            with m_tabs[4]:
                st.subheader("Pesquisar Usuários")
                procura_user = st.text_input("Escreva o username exato:").strip()
                if st.button("Pesquisar Perfil 🔍", use_container_width=True) and procura_user:
                    st.session_state.perfil_visitado = procura_user
                    st.rerun()


    # === ✨ ABA STATUS ===
    with aba_status:
        st.header("✨ Status Recentes")
        with st.expander("➕ Postar um Status Temporário"):
            t_status = st.text_input("O que está a acontecer no teu dia?:")
            f_status = st.file_uploader("Adicionar Foto ao Status:", type=["png","jpg","jpeg"])
            if st.button("Postar Status 🚀", use_container_width=True) and (t_status.strip() or f_status):
                url_st = ""
                if f_status:
                    try:
                        n_b = f"status/{uuid.uuid4()}.png"
                        supabase.storage.from_("imagens_chat").upload(n_b, f_status.read())
                        url_st = supabase.storage.from_("imagens_chat").get_public_url(n_b)
                    except: pass
                supabase.table("feed_videos").insert({
                    "titulo": f"[STATUS] {t_status.strip()}", "url_video": url_st,
                    "username_autor": user_atual["username"], "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                    "curtidas": 0, "id_autor": user_atual["id"], "tipo_formato": "horizontal"
                }).execute()
                st.success("Status publicado!"); st.rerun()

        try:
            todos = supabase.table("feed_videos").select("*").execute()
            if todos.data:
                stats = [p for p in todos.data if str(p.get("titulo","")).startswith("[STATUS]")]
                if stats:
                    for s in reversed(stats):
                        st.markdown(f"**{s['username_autor']}:** {s['titulo'].replace('[STATUS]','')}")
                        if s["url_video"]: st.image(s["url_video"], width=250)
                        st.markdown("---")
                else: st.info("Nenhum status ativo.")
        except: pass


    # === 🔔 ABA NOTIFICAÇÕES ===
    with aba_notif:
        st.header("🔔 Interações Recentes")
        try:
            res_notif = supabase.table("notificacoes").select("*").eq("id_destinatario", user_atual["id"]).execute()
            if res_notif.data:
                if st.button("Marcar todas como lidas ✓", use_container_width=True):
                    supabase.table("notificacoes").update({"lida": True}).eq("id_destinatario", user_atual["id"]).execute()
                    st.rerun()
                for n in reversed(res_notif.data):
                    cor_marcador = "🔴 [NOVA]" if not n['lida'] else "⚪"
                    st.write(f"{cor_marcador} {n['mensagem']}")
            else:
                st.info("Não tens nenhuma notificação recente.")
        except Exception as e:
            st.info("A aguardar criação da tabela 'notificacoes' no Supabase...")
                 
