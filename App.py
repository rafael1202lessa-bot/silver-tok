import streamlit as st
from supabase import create_client, Client
import uuid
import datetime

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

def exibir_logo():
    st.markdown("<h1 style='text-align: center;'>🎬 Silver Tok & Chat 🔐</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Sua plataforma de vídeos e conversas privadas</p>", unsafe_allow_html=True)

# Inicialização do estado da sessão
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
                    supabase.table("perfis_usuarios").insert({"username": cad_user, "senha": cad_senha, "url_foto_perfil": url_foto}).execute()
                    st.success("Conta criada! Agora faça o seu login.")
                except:
                    st.error("Erro ao cadastrar ou o usuário já existe.")
            else:
                st.warning("Verifique os campos!")
else:
    user_atual = st.session_state.usuario_logado
    total_seg = 0
    try:
        res_seg = supabase.table("seguidores").select("*", count="exact").eq("id_seguido", user_atual["id"]).execute()
        total_seg = res_seg.count if (hasattr(res_seg, "count") and res_seg.count is not None) else len(res_seg.data)
    except:
        pass

    st.sidebar.image(user_atual.get("url_foto_perfil") or FOTO_PADRAO, width=90)
    if user_atual["username"] == NOME_DEVELOPER:
        st.sidebar.write(f"Usuário: **{user_atual['username']}** 👑`DEV`")
    elif total_seg >= 1000:
        st.sidebar.write(f"Usuário: **{user_atual['username']}** ✔️")
    else:
        st.sidebar.write(f"Usuário: **{user_atual['username']}**")
    st.sidebar.write(f"👥 **{total_seg}** seguidores")
    
    if st.sidebar.button("Sair 🚪", use_container_width=True):
        st.session_state.usuario_logado = None
        st.session_state.sala_ativa = None
        st.session_state.perfil_visitado = None
        st.rerun()

    aba_feed, aba_chat = st.tabs(["📺 Silver Tok (Feed)", "💬 Chat-Exv"])
    
    with aba_feed:
        if st.session_state.perfil_visitado is not None:
            autor_vis = st.session_state.perfil_visitado
            if st.button("⬅️ Voltar para o Feed", use_container_width=True):
                st.session_state.perfil_visitado = None
                st.rerun()
                
            st.markdown("---")
            try:
                dados_perf = supabase.table("perfis_usuarios").select("*").eq("username", autor_vis).execute()
                if dados_perf.data:
                    p_info = dados_perf.data[0]
                    id_autor_vis = p_info["id"]
                    img_autor_vis = p_info.get("url_foto_perfil") or FOTO_PADRAO
                    
                    c_seg_v = supabase.table("seguidores").select("*", count="exact").eq("id_seguido", id_autor_vis).execute()
                    qtd_seg_v = c_seg_v.count if (hasattr(c_seg_v, "count") and c_seg_v.count is not None) else len(c_seg_v.data)
                    
                    col_p1, col_p2 = st.columns([1, 3])
                    with col_p1:
                        st.image(img_autor_vis, width=100)
                    with col_p2:
                        selo_v = ""
                        if autor_vis == NOME_DEVELOPER:
                            selo_v = " 👑`DEV`"
                        elif qtd_seg_v >= 1000:
                            selo_v = " ✔️"
                        st.subheader(f"@{autor_vis}{selo_v}")
                        st.write(f"👥 **{qtd_seg_v}** seguidores")
                        
                        if autor_vis != user_atual["username"]:
                            ja_segue_v = supabase.table("seguidores").select("*").eq("id_seguidor", user_atual["id"]).eq("id_seguido", id_autor_vis).execute()
                            if ja_segue_v.data:
                                if st.button("Seguindo ✓", key="btn_unfol_perfil", use_container_width=True):
                                    supabase.table("seguidores").delete().eq("id_seguidor", user_atual["id"]).eq("id_seguido", id_autor_vis).execute()
                                    st.rerun()
                            else:
                                if st.button("Seguir ➕", key="btn_fol_perfil", use_container_width=True, type="primary"):
                                    supabase.table("seguidores").insert({"id_seguidor": user_atual["id"], "id_seguido": id_autor_vis}).execute()
                                    st.rerun()
                                    
                    st.markdown("### 🎬 Publicações")
                    v_dados = supabase.table("feed_videos").select("*").eq("username_autor", autor_vis).execute()
                    if v_dados.data:
                        for idx_v, vid in enumerate(reversed(v_dados.data)):
                            st.caption(vid["titulo"])
                            url_midia = vid["url_video"]
                            if url_midia.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                                st.image(url_midia, use_container_width=True)
                            else:
                                st.video(url_midia)
                            st.markdown(f"❤️ {vid.get('curtidas', 0)} Curtidas")
                            st.markdown("---")
                    else:
                        st.info("Este usuário ainda não publicou nada.")
                else:
                    st.error("Perfil não encontrado.")
            except Exception as err_p:
                st.error(f"Erro ao carregar perfil: {err_p}")
                
        else:
            exibir_logo()
            
            sub_aba_feed, sub_aba_alta = st.tabs(["⏱️ Recentes", "🔥 Em Alta (Mais Curtidos)"])
            termo_pesquisa = st.text_input("Buscar posts por legenda:", placeholder="Ex: Bleach, Naruto, edit...", key="busca_feed").strip()

            with st.expander("➕ Publicar Novo Conteúdo"):
                tipo_pub = st.radio("Escolha o método de envio:", ["Enviar Arquivo de Vídeo (Do Aparelho)", "Inserir Link (YouTube)", "Postar Foto 📸"])
                titulo_v = st.text_input("Legenda do Post:", placeholder="Ex: Edit de Bleach! 🔥", key="legenda_video")
                
                if tipo_pub == "Inserir Link (YouTube)":
                    url_v = st.text_input("Link do Vídeo (YouTube ou MP4 direto):", placeholder="https://www.youtube.com/watch?v=...")
                    if st.button("Publicar Link 🚀", use_container_width=True):
                        if url_v.strip() and titulo_v.strip():
                            link_final = url_v.strip()
                            if "youtube.com/shorts/" in link_final:
                                link_final = link_final.replace("youtube.com/shorts/", "youtube.com/watch?v=")
                            elif "youtu.be/" in link_final and "shorts" in link_final:
                                link_final = link_final.replace("youtu.be/", "youtube.com/watch?v=")
                            try:
                                supabase.table("feed_videos").insert({
                                    "titulo": titulo_v.strip(),
                                    "url_video": link_final,
                                    "username_autor": user_atual["username"],
                                    "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                    "curtidas": 0
                                }).execute()
                                st.success("Postado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar no feed: {e}")
                        else:
                            st.warning("Preencha todos os campos!")
                            
                elif tipo_pub == "Enviar Arquivo de Vídeo (Do Aparelho)":
                    file_v = st.file_uploader("Escolha o vídeo do seu dispositivo:", type=["mp4", "mov", "avi", "mkv"])
                    if st.button("Fazer Upload e Publicar 🎥", use_container_width=True):
                        if file_v and titulo_v.strip():
                            try:
                                with st.spinner("Enviando vídeo..."):
                                    nome_video_bucket = f"videos/{uuid.uuid4()}.mp4"
                                    supabase.storage.from_("videos_feed").upload(nome_video_bucket, file_v.read())
                                    url_video_final = supabase.storage.from_("videos_feed").get_public_url(nome_video_bucket)
                                    
                                    supabase.table("feed_videos").insert({
                                        "titulo": titulo_v.strip(),
                                        "url_video": url_video_final,
                                        "username_autor": user_atual["username"],
                                        "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                        "curtidas": 0
                                    }).execute()
                                    
                                st.success("Vídeo enviado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao fazer upload do vídeo: {e}")
                        else:
                            st.warning("Selecione um arquivo de vídeo!")

                elif tipo_pub == "Postar Foto 📸":
                    file_img = st.file_uploader("Escolha uma foto da galeria:", type=["png", "jpg", "jpeg", "webp"])
                    if st.button("Publicar Foto 🖼️", use_container_width=True):
                        if file_img and titulo_v.strip():
                            try:
                                with st.spinner("Enviando foto..."):
                                    nome_foto_bucket = f"fotos_feed/{uuid.uuid4()}.png"
                                    supabase.storage.from_("imagens_chat").upload(nome_foto_bucket, file_img.read())
                                    url_foto_final = supabase.storage.from_("imagens_chat").get_public_url(nome_foto_bucket)
                                    
                                    supabase.table("feed_videos").insert({
                                        "titulo": titulo_v.strip(),
                                        "url_video": url_foto_final,
                                        "username_autor": user_atual["username"],
                                        "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                        "curtidas": 0
                                    }).execute()
                                    
                                st.success("Foto postada com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao fazer upload da foto: {e}")
                        else:
                            st.warning("Selecione uma foto e digite uma legenda!")

            def renderizar_posts(lista_posts, identificador_aba):
                for idx, v in enumerate(lista_posts):
                    autor = v.get('username_autor', 'Membro')
                    img_autor = v.get('avatar_autor') or FOTO_PADRAO
                    video_url = v["url_video"]
                    
                    if "shorts/" in video_url:
                        video_url = video_url.replace("shorts/", "watch?v=")

                    id_unico_video = v.get("id") or hash(video_url)
                    chave_componente = f"vid_{id_unico_video}_{idx}_{identificador_aba}"

                    selo_verificado = ""
                    id_autor = None
                    try:
                        b_autor = supabase.table("perfis_usuarios").select("id").eq("username", autor).execute()
                        if b_autor.data:
                            id_autor = b_autor.data[0]["id"]
                            c_seg = supabase.table("seguidores").select("*", count="exact").eq("id_seguido", id_autor).execute()
                            qtd_seg_autor = c_seg.count if (hasattr(c_seg, "count") and c_seg.count is not None) else len(c_seg.data)
                            if autor == NOME_DEVELOPER:
                                selo_verificado = " 👑`DEV`"
                            elif qtd_seg_autor >= 1000:
                                selo_verificado = " ✔️"
                    except:
                        pass

                    col_foto, col_nome, col_perfil_btn, col_seguir_btn = st.columns([1, 3, 2, 2])
                    with col_foto:
                        st.image(img_autor, width=45)
                    with col_nome:
                        st.markdown(f"**@{autor}**{selo_verificado}")
                    with col_perfil_btn:
                        if st.button("Ver Perfil 👤", key=f"go_perf_{chave_componente}", use_container_width=True):
                            st.session_state.perfil_visitado = autor
                            st.rerun()
                    with col_seguir_btn:
                        if autor != user_atual["username"] and id_autor is not None:
                            try:
                                ja_segue = supabase.table("seguidores").select("*").eq("id_seguidor", user_atual["id"]).eq("id_seguido", id_autor).execute()
                                if ja_segue.data:
                                    if st.button("Seguindo", key=f"unfol_{chave_componente}", use_container_width=True):
                                        supabase.table("seguidores").delete().eq("id_seguidor", user_atual["id"]).eq("id_seguido", id_autor).execute()
                                        st.rerun()
                                else:
                                    if st.button("Seguir ➕", key=f"fol_{chave_componente}", use_container_width=True, type="primary"):
                                        supabase.table("seguidores").insert({"id_seguidor": user_atual["id"], "id_seguido": id_autor}).execute()
                                        st.rerun()
                            except:
                                pass

                    st.caption(v["titulo"])
                    
                    if video_url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                        st.image(video_url, use_container_width=True)
                    else:
                        st.video(video_url)
                    
                    col_lk, col_del = st.columns([1, 1])
                    likes = v.get("curtidas", 0)
                    with col_lk:
                        if st.button(f"❤️ {likes} Curtidas", key=f"lk_{chave_componente}"):
                            try:
                                supabase.table("feed_videos").update({"curtidas": likes + 1}).eq("url_video", video_url).execute()
                            except:
                                if "id" in v:
                                    supabase.table("feed_videos").update({"curtidas": likes + 1}).eq("id", v["id"]).execute()
                            st.rerun()
                    with col_del:
                        if autor == user_atual["username"]:
                            if st.button("Excluir Post 🗑️", key=f"del_{chave_componente}"):
                                try:
                                    supabase.table("feed_videos").delete().eq("url_video", video_url).execute()
                                except:
                                    if "id" in v:
                                        supabase.table("feed_videos").delete().eq("id", v["id"]).execute()
                                st.success("Removido com sucesso!")
                                st.rerun()

                    total_coment = 0
                    lista_comentarios = []
                    try:
                        res_c = supabase.table("comentarios_videos").select("*").eq("id_video", str(video_url)).execute()
                        if res_c.data:
                            lista_comentarios = res_c.data
                            total_coment = len(res_c.data)
                    except:
                        pass

                    with st.expander(f"💬 Comentários ({total_coment})"):
                        novo_coment = st.text_input("Escreva um comentário...", key=f"in_cm_{chave_componente}", placeholder="O que você achou?")
                        if st.button("Comentar 🚀", key=f"btn_cm_{chave_componente}"):
                            if novo_coment.strip():
                                try:
                                    supabase.table("comentarios_videos").insert({
                                        "id_video": str(video_url),
                                        "username_autor": user_atual["username"],
                                        "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                        "comentario": novo_coment.strip()
                                    }).execute()
                                    st.success("Comentário publicado!")
                                    st.rerun()
                                except Exception as err:
                                    st.error(f"Erro de envio.")

                        st.markdown("---")
                        if lista_comentarios:
                            for idx_c, c in enumerate(reversed(lista_comentarios)):
                                autor_c = c['username_autor']
                                selo_comentario = ""
                                try:
                                    b_aut_c = supabase.table("perfis_usuarios").select("id").eq("username", autor_c).execute()
                                    if b_aut_c.data:
                                        id_aut_c = b_aut_c.data[0]["id"]
                                        c_seg_c = supabase.table("seguidores").select("*", count="exact").eq("id_seguido", id_aut_c).execute()
                                        qtd_seg_c = c_seg_c.count if (hasattr(c_seg_c, "count") and c_seg_c.count is not None) else len(c_seg_c.data)
                                        if autor_c == NOME_DEVELOPER:
                                            selo_comentario = " 👑`DEV`"
                                        elif qtd_seg_c >= 1000:
                                            selo_comentario = " ✔️"
                                except:
                                    pass

                                c_col1, c_col2 = st.columns([1, 6])
                                with c_col1:
                                    st.image(c.get("avatar_autor") or FOTO_PADRAO, width=30)
                                with c_col2:
                                    st.markdown(f"**@{autor_c}**{selo_comentario}")
                                    st.write(c["comentario"])
                                st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
                        else:
                            st.caption("Nenhum comentário ainda.")
                    st.markdown("---")

            try:
                query_feed = supabase.table("feed_videos").select("*")
                if termo_pesquisa:
                    query_feed = query_feed.ilike("titulo", f"%{termo_pesquisa}%")
                dados = query_feed.execute()
                
                with sub_aba_feed:
                    if dados.data:
                        renderizar_posts(reversed(dados.data), "recentes")
                    else:
                        st.info("Nenhum post encontrado.")
                        
                with sub_aba_alta:
                    if dados.data:
                        posts_ordenados = sorted(dados.data, key=lambda k: k.get('curtidas', 0), reverse=True)
                        renderizar_posts(posts_ordenados, "alta")
                    else:
                        st.info("Nenhum post popular ainda.")
            except Exception as e:
                st.error(f"Erro ao carregar o feed: {e}")

    with aba_chat:
        if st.session_state.sala_ativa is not None:
            st.title("💬 Sala Ativa")
            st.code(f"Código da Sala: {st.session_state.sala_ativa}")
            if st.button("⬅️ Voltar ao Menu", use_container_width=True):
                st.session_state.sala_ativa = None
                st.rerun()
                
            txt_m = st.text_input("Mensagem de texto:", key="txt_msg_input")
            
            col_midia1, col_midia2 = st.columns(2)
            with col_midia1:
                upload_img = st.file_uploader("Enviar Imagem 📸", type=["png", "jpg", "jpeg", "gif"], key=st.session_state.id_upload_chat)
            with col_midia2:
                gravar_audio = st.audio_input("Gravar Mensagem de Voz 🎙️", key=st.session_state.id_audio_chat)
                
            if st.button("Enviar Conteúdo ✉️", use_container_width=True):
                if txt_m.strip() or upload_img or gravar_audio:
                    try:
                        url_img = None
                        
                        if upload_img:
                            nome_f = f"chat/{uuid.uuid4()}.png"
                            supabase.storage.from_("imagens_chat").upload(nome_f, upload_img.read())
                            url_img = supabase.storage.from_("imagens_chat").get_public_url(nome_f)
                            
                        if gravar_audio and not url_img:
                            nome_a = f"audios/{uuid.uuid4()}.wav"
                            supabase.storage.from_("imagens_chat").upload(nome_a, gravar_audio.read())
                            url_img = supabase.storage.from_("imagens_chat").get_public_url(nome_a)
                            
                        supabase.table("bate-papo_profissional").insert({
                            "id_usuario": user_atual["id"], 
                            "username": user_atual["username"], 
                            "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO, 
                            "mensagem": txt_m.strip() if txt_m.strip() else None, 
                            "url_imagem_enviada": url_img,
                            "codigo_sala": st.session_state.sala_ativa
                        }).execute()
                        
                        st.session_state.id_upload_chat = str(uuid.uuid4())
                        st.session_state.id_audio_chat = str(uuid.uuid4())
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao enviar mensagem: {e}")
                        
            try:
                res = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", st.session_state.sala_ativa).execute()
                if res.data:
                    for m in reversed(res.data[-40:]):
                        c1, c2 = st.columns([1, 6])
                        with c1:
                            st.image(m.get("url_foto_perfil") or FOTO_PADRAO, width=40)
                        with c2:
                            st.markdown(f"**{m['username']}**")
                            if m.get("mensagem"):
                                st.write(m["mensagem"])
                            if m.get("url_imagem_enviada"):
                                url_midia_c = m["url_imagem_enviada"]
                                if url_midia_c.lower().endswith(('.wav', '.mp3', '.ogg')):
                                    st.audio(url_midia_c)
                                else:
                                    st.image(url_midia_c, use_container_width=True)
                        st.markdown("---")
            except:
                st.write("Sem mensagens nesta sala ainda.")
        else:
            st.title("🎛️ Painel Chat-Exv")
            m_tabs = st.tabs(["💬 Privado", "👨‍👩‍👦 Novo Grupo", "🔑 Entrar", "👥 Amigos", "➕ Adicionar"])
            
            with m_tabs[0]:
                try:
                    amg = supabase.table("lista_amigos").select("*").or_(f"id_usuario_envio.eq.{user_atual['id']},id_usuario_recebe.eq.{user_atual['id']}").eq("status", "aceito").execute()
                    nomes = []
                    m_ids = {}
                    if amg.data:
                        for a in amg.data:
                            o_id = a["id_usuario_recebe"] if str(a["id_usuario_envio"]) == str(user_atual["id"]) else a["id_usuario_envio"]
                            du = supabase.table("perfis_usuarios").select("username").eq("id", o_id).execute()
                            if du.data:
                                n = du.data[0]["username"]
                                nomes.append(n)
                                m_ids[n] = o_id
                    if nomes:
                        alvo = st.selectbox("Escolha um amigo:", nomes)
                        if st.button("Abrir Conversa Particular 🚀", use_container_width=True):
                            ids = sorted([str(user_atual["id"]), str(m_ids[alvo])])
                            st.session_state.sala_ativa = f"PRIVADO-{ids[0][:8]}-{ids[1][:8]}"
                            st.rerun()
                    else:
                        st.info("Sem amigos aceitos por enquanto.")
                except Exception as e:
                    st.caption("Aba de amigos privados pronta.")
                    
            with m_tabs[1]:
                n_grp = st.text_input("Nome do Grupo:")
                if st.button("Criar Grupo 🎉", use_container_width=True) and n_grp:
                    try:
                        cod = f"GRUPO-{str(uuid.uuid4())[:8].upper()}"
                        supabase.table("salas-chat").insert({"codigo_sala": cod, "nome_sala": n_grp, "tipo": "grupo"}).execute()
                        st.success(f"Grupo criado! Código: {cod}")
                        st.session_state.sala_ativa = cod
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar grupo: {e}")
                        
            with m_tabs[2]:
                cod_d = st.text_input("Digite o Código da Sala:").strip().upper()
                if st.button("Entrar na Sala 🚪", use_container_width=True) and cod_d:
                    st.session_state.sala_ativa = cod_d
                    st.rerun()
                    
            with m_tabs[3]:
                try:
                    peds = supabase.table("lista_amigos").select("*").eq("id_usuario_recebe", user_atual["id"]).eq("status", "pendente").execute()
                    if peds.data:
                        for p in peds.data:
                            dr = supabase.table("perfis_usuarios").select("username").eq("id", p["id_usuario_envio"]).execute()
                            if dr.data:
                                st.write(f"Pedido de amizade de: **{dr.data[0]['username']}**")
                                if st.button("Aceitar", key=f"ac_{p['id']}"):
                                    supabase.table("lista_amigos").update({"status": "aceito"}).eq("id", p["id"]).execute()
                                    st.rerun()
                    
                    conf = supabase.table("lista_amigos").select("*").or_(f"id_usuario_envio.eq.{user_atual['id']},id_usuario_recebe.eq.{user_atual['id']}").eq("status", "aceito").execute()
                    if conf.data:
                        for c in conf.data:
                            o_id = c["id_usuario_recebe"] if str(c["id_usuario_envio"]) == str(user_atual["id"]) else c["id_usuario_envio"]
                            du = supabase.table("perfis_usuarios").select("username").eq("id", o_id).execute()
                            if du.data:
                                st.write(f"🟢 {du.data[0]['username']}")
                    else:
                        st.caption("Nenhum amigo na lista.")
                except:
                    st.caption("Nenhum amigo pendente.")
                    
            with m_tabs[4]:
                b_amg = st.text_input("Nome do Usuário para adicionar:").strip()
                if st.button("Enviar Pedido de Amizade ➕", use_container_width=True) and b_amg:
                    try:
                        alvo = supabase.table("perfis_usuarios").select("*").eq("username", b_amg).execute()
                        if alvo.data:
                            if str(alvo.data[0]["id"]) == str(user_atual["id"]):
                                st.error("Você não pode adicionar a si mesmo!")
                            else:
                                supabase.table("lista_amigos").insert({"id_usuario_envio": user_atual["id"], "id_usuario_recebe": alvo.data[0]["id"], "status": "pendente"}).execute()
                                st.success("Pedido enviado com sucesso!")
                        else:
                            st.error("Usuário não encontrado.")
                    except:
                        st.error("Erro ao processar pedido de amizade.")
                  
