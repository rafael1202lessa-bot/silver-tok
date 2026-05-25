    # === 💬 ABA CHAT-EXV CORRIGIDA (MÍDIAS E COMENTÁRIOS VOLTARAM) ===
    with aba_chat:
        sala_atual = st.session_state.sala_ativa

        if sala_atual:
            st.subheader(f"Sala: {sala_atual}")
            if st.button("⬅️ Sair da Sala"):
                st.session_state.sala_ativa = None
                st.rerun()

            # --- SEÇÃO DE ENVIAR FOTO / ARQUIVO ---
            with st.expander("📸 Enviar Foto ou Mídia"):
                arquivo_chat = st.file_uploader("Escolha uma imagem (PNG/JPG):", type=["png", "jpg", "jpeg", "gif"])
                if st.button("Enviar Foto 🚀") and arquivo_chat:
                    try:
                        nome_da_foto = f"chat/imagens/{uuid.uuid4()}_{arquivo_chat.name}"
                        # Faz o upload para o bucket seguro
                        supabase.storage.from_("imagens_chat").upload(nome_da_foto, arquivo_chat.read())
                        url_da_foto = supabase.storage.from_("imagens_chat").get_public_url(nome_da_foto)
                        
                        # Salva a URL como mensagem no banco
                        supabase.table("bate-papo_profissional").insert({
                            "username": u_name,
                            "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "mensagem": url_da_foto, 
                            "codigo_sala": sala_atual
                        }).execute()
                        st.success("Foto enviada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao enviar foto: {e}")

            # --- SEÇÃO DE ENVIAR ÁUDIO ---
            st.markdown("### 🎙️ Áudio")
            if "b64_audio_data" not in st.session_state:
                st.session_state.b64_audio_data = ""
                
            audio_base64 = st.text_input("Dados do Gravador", type="password", value=st.session_state.b64_audio_data, label_visibility="collapsed", key="audio_b64_injector")
            
            if st.button("Clique aqui se o áudio não subir automático ⚡", use_container_width=True, key="btn_hidden_upload") or (audio_base64 and audio_base64 != st.session_state.b64_audio_data):
                if audio_base64:
                    try:
                        dados_audio = base64.b64decode(audio_base64)
                        nome_arquivo = f"chat/audios/{uuid.uuid4()}.wav"
                        supabase.storage.from_("audios_chat").upload(nome_arquivo, dados_audio)
                        url_publica_audio = supabase.storage.from_("audios_chat").get_public_url(nome_arquivo)
                        
                        supabase.table("bate-papo_profissional").insert({
                            "username": u_name,
                            "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "mensagem": url_publica_audio, 
                            "codigo_sala": sala_atual
                        }).execute()
                        st.session_state.b64_audio_data = ""
                        st.rerun()
                    except: pass

            # Script do Gravador HTML
            gravador_html = """
            <div style="display: flex; gap: 10px; justify-content: center; padding: 5px 0;">
                <button id="startBtn" style="background-color: #24a0ed; color: white; border: none; padding: 12px 20px; border-radius: 25px; font-weight: bold; width: 45%; cursor: pointer; font-size: 14px;">🎙️ Gravar</button>
                <button id="stopBtn" style="background-color: #ff4b4b; color: white; border: none; padding: 12px 20px; border-radius: 25px; font-weight: bold; width: 45%; cursor: pointer; display: none; font-size: 14px;">⏹️ Enviar</button>
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
                        statusLabel.innerText = "Processando áudio...";
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const reader = new FileReader(); reader.readAsDataURL(audioBlob);
                        reader.onloadend = () => {
                            const base64String = reader.result.split(',')[1];
                            const inputs = window.parent.document.querySelectorAll('input[type="password"]');
                            if(inputs.length > 0) {
                                let targetInput = inputs[0]; targetInput.value = base64String;
                                targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                                setTimeout(() => {
                                    const botoes = window.parent.document.querySelectorAll('button');
                                    for (let btn of botoes) { if (btn.innerText.includes("Clique aqui se o áudio")) { btn.click(); break; } }
                                }, 400);
                            }
                        };
                    };
                    mediaRecorder.start(); startBtn.style.display = 'none'; stopBtn.style.display = 'inline-block'; statusLabel.innerText = "🔴 Gravando...";
                } catch(err) { statusLabel.innerText = "Permissão de microfone negada."; }
            };
            stopBtn.onclick = () => { mediaRecorder.stop(); startBtn.style.display = 'inline-block'; stopBtn.style.display = 'none'; statusLabel.innerText = "Enviando..."; };
            </script>
            """
            st.components.v1.html(gravador_html, height=85)
            st.markdown("---")

            # --- INPUT DE TEXTO TRADICIONAL ---
            m_txt = st.text_input("Mensagem de Texto:", key="input_texto_chat_direto", placeholder="Digite sua mensagem aqui...")
            if st.button("Enviar Mensagem ✉️", use_container_width=True):
                if m_txt.strip():
                    try:
                        supabase.table("bate-papo_profissional").insert({
                            "username": u_name,
                            "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "mensagem": m_txt.strip(), 
                            "codigo_sala": sala_atual
                        }).execute()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar mensagem: {e}")

            # --- EXIBIÇÃO DAS MENSAGENS (OS COMENTÁRIOS VOLTARAM AQUI) ---
            try:
                m_dados = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", sala_atual).execute()
                if m_dados.data:
                    # Ordena do mais recente para o mais antigo se necessário, ou mantém histórico
                    for m in reversed(m_dados.data[-40:]):
                        col_m1, col_m2 = st.columns([1, 6])
                        m_user = m.get('username', 'Membro')
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
                                
                            renderizar_caixa_mensagem(m_user, m.get('mensagem', ''), s_msg, txt_caixa, eh_admin=verificar_se_eh_dev(uid_remetente))
                else:
                    st.info("Nenhuma mensagem enviada nesta sala ainda. Seja o primeiro!")
            except Exception as e: 
                st.error(f"Erro ao carregar o histórico de mensagens: {e}")
        else:
            st.title("🎛️ Painel Chat-Exv")
            t_chat = st.tabs(["💬 Privado", "🔑 Entrar", "👥 Grupos", "👥 Membros", "➕ Adicionar"])
            
            with t_chat[0]:
                alvo = st.text_input("Username do amigo para iniciar privado:").strip()
                if st.button("Iniciar Chat Privado") and alvo:
                    lista = sorted([u_name.upper(), alvo.upper()])
                    st.session_state.sala_ativa = f"PRIV-{lista[0]}-{lista[1]}"
                    st.rerun()
            
            with t_chat[1]:
                st.subheader("Entrar em uma Sala Existente")
                cod_entrar = st.text_input("Insira o código do chat:", placeholder="Ex: GRUPO-VIP")
                if st.button("Entrar na Sala 🚪") and cod_entrar:
                    st.session_state.sala_ativa = cod_entrar.strip().upper()
                    st.rerun()
            
            with t_chat[2]:
                g_nome = st.text_input("Nome do Grupo para Criar:").strip().upper()
                if st.button("Criar Grupo 🔐") and g_nome:
                    st.session_state.sala_ativa = g_nome
                    st.rerun()

            with t_chat[3]:
                st.subheader("Membros da Comunidade")
                try:
                    u_todos = supabase.table("perfis_usuarios").select("*").execute()
                    if u_todos.data:
                        for u in u_todos.data:
                            m_username = u.get("username", "")
                            if m_username and m_username != u_name:
                                col_u1, col_u2, col_u3 = st.columns([1, 4, 2])
                                with col_u1:
                                    renderizar_foto_com_banner(u.get("url_foto_perfil") or FOTO_PADRAO, m_username, u.get("id"), tamanho=50, banner_equipado=u.get("banner_ativo", "Nenhum"))
                                with col_u2:
                                    s_u = obter_selo_texto(m_username, u.get("id"))
                                    st.markdown(f"**{m_username}** {s_u}")
                                    st.caption(obter_status_emoji(u.get("ultimo_visto")))
                                with col_u3:
                                    if st.button("Chat 💬", key=f"u_ch_{m_username}"):
                                        lista = sorted([u_name.upper(), m_username.upper()])
                                        st.session_state.sala_ativa = f"PRIV-{lista[0]}-{lista[1]}"
                                        st.rerun()
                except: pass

            with t_chat[4]:
                st.subheader("Adicionar Novos Amigos")
                st.caption("Busque e siga usuários para adicioná-los à sua lista do chat.")
                busca_amigo = st.text_input("Digitar Username do Usuário:", key="busca_amigo_input")
                if st.button("Buscar e Seguir ➕"):
                    if busca_amigo.strip():
                        try:
                            verif = supabase.table("perfis_usuarios").select("id").eq("username", busca_amigo.strip()).execute()
                            if verif.data:
                                am_id = verif.data[0]["id"]
                                supabase.table("seguidores").insert({"id_seguidor": u_id, "id_seguido": am_id}).execute()
                                st.success(f"Você agora está seguindo {busca_amigo.strip()}!")
                        except: st.error("Você já segue este usuário ou ocorreu uma falha.")
                            
