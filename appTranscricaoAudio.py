import streamlit as st
import whisper
import os
from datetime import datetime
import time
import threading
from queue import Queue

# Configuração da página
st.set_page_config(
    page_title="Conversor de Áudio para Texto",
    page_icon="🎙️",
    layout="wide"
)

# Variáveis globais para controle da transcrição
if 'transcription_active' not in st.session_state:
    st.session_state.transcription_active = False
if 'transcription_paused' not in st.session_state:
    st.session_state.transcription_paused = False
if 'transcription_cancelled' not in st.session_state:
    st.session_state.transcription_cancelled = False
if 'transcription_result' not in st.session_state:
    st.session_state.transcription_result = None
if 'progress' not in st.session_state:
    st.session_state.progress = 0

# Título e descrição
st.title("🎙️ Conversor de Áudio para Texto com Controle")
st.markdown("""
Este aplicativo utiliza o modelo Whisper da OpenAI para transcrever arquivos de áudio em texto.
Você pode pausar, continuar ou cancelar a transcrição durante o processo.
""")

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    
    # Seleção do modelo
    model_options = {
        "tiny": "Tiny (mais rápido, menos preciso)",
        "base": "Base",
        "small": "Small",
        "medium": "Medium (melhor equilíbrio)",
        "large": "Large (mais lento, mais preciso)"
    }
    selected_model = st.selectbox(
        "Selecione o modelo Whisper:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=3  # Default para medium
    )
    
    st.markdown("---")
    st.markdown("""
    **Controles:**
    - Inicie a transcrição com o botão principal
    - Use os botões para pausar/continuar durante o processo
    - Você pode cancelar a qualquer momento
    """)

# Função de transcrição em thread separada
def transcribe_audio_thread(audio_path, model_size, progress_queue):
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path)
        progress_queue.put(100)
        st.session_state.transcription_result = result["text"]
    except Exception as e:
        progress_queue.put(-1)
        st.session_state.transcription_result = f"Erro: {str(e)}"
    finally:
        st.session_state.transcription_active = False

# Função para monitorar progresso
def monitor_progress(progress_queue, progress_bar, progress_text):
    while st.session_state.transcription_active:
        while not progress_queue.empty():
            progress = progress_queue.get()
            if progress == -1:
                return
            st.session_state.progress = progress
            progress_bar.progress(progress)
            progress_text.text(f"Progresso: {progress}%")
        
        time.sleep(0.1)
        
        if st.session_state.transcription_cancelled:
            progress_text.text("Transcrição cancelada!")
            time.sleep(2)
            break
            
        while st.session_state.transcription_paused:
            progress_text.text(f"Progresso: {st.session_state.progress}% (Pausado)")
            time.sleep(0.5)
            if st.session_state.transcription_cancelled:
                break

# Área de upload de arquivo
uploaded_file = st.file_uploader(
    "Carregue seu arquivo de áudio:",
    type=["mp3", "wav", "m4a", "ogg", "flac"],
    help="Formatos suportados: MP3, WAV, M4A, OGG, FLAC"
)

# Processamento quando um arquivo é carregado
if uploaded_file is not None:
    # Mostrar informações do arquivo
    col1, col2 = st.columns(2)
    with col1:
        st.audio(uploaded_file)
    with col2:
        file_details = {
            "Nome do arquivo": uploaded_file.name,
            "Tipo de arquivo": uploaded_file.type,
            "Tamanho do arquivo": f"{uploaded_file.size / (1024*1024):.2f} MB"
        }
        st.json(file_details)
    
    # Área de controle de transcrição
    if not st.session_state.transcription_active:
        if st.button("Iniciar Transcrição", type="primary"):
            # Salvar arquivo temporariamente
            temp_file = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Resetar estados
            st.session_state.transcription_active = True
            st.session_state.transcription_paused = False
            st.session_state.transcription_cancelled = False
            st.session_state.progress = 0
            st.session_state.temp_file = temp_file
            
            # Criar elementos de progresso
            progress_bar = st.progress(0)
            progress_text = st.empty()
            progress_text.text("Progresso: 0% - Preparando...")
            
            # Criar queue para progresso
            progress_queue = Queue()
            
            # Iniciar thread de transcrição
            thread = threading.Thread(
                target=transcribe_audio_thread,
                args=(temp_file, selected_model, progress_queue)
            )
            thread.start()
            
            # Monitorar progresso na thread principal
            monitor_progress(progress_queue, progress_bar, progress_text)
            
            # Limpar elementos após conclusão
            progress_bar.empty()
            progress_text.empty()
            
            # Mostrar resultado se disponível
            if st.session_state.transcription_result and not st.session_state.transcription_cancelled:
                st.subheader("Resultado da Transcrição:")
                st.text_area("Texto transcrito:", st.session_state.transcription_result, height=300)
                
                # Botão para download
                st.download_button(
                    label="Baixar Transcrição",
                    data=st.session_state.transcription_result,
                    file_name=f"transcricao_{os.path.splitext(uploaded_file.name)[0]}.txt",
                    mime="text/plain"
                )
            
            # Limpar arquivo temporário
            try:
                os.remove(st.session_state.temp_file)
            except:
                pass
    
    # Controles durante a transcrição
    if st.session_state.transcription_active:
        col_pause, col_cancel = st.columns(2)
        with col_pause:
            if st.session_state.transcription_paused:
                if st.button("Continuar Transcrição"):
                    st.session_state.transcription_paused = False
                    st.rerun()
            else:
                if st.button("Pausar Transcrição"):
                    st.session_state.transcription_paused = True
                    st.rerun()
        with col_cancel:
            if st.button("Cancelar Transcrição", type="secondary"):
                st.session_state.transcription_cancelled = True
                st.session_state.transcription_active = False
                st.rerun()
else:
    st.info("Por favor, carregue um arquivo de áudio para começar.")

# Rodapé
st.markdown("---")
st.caption("Aplicativo desenvolvido por Rafael Oliveira, com Whisper da OpenAI e Streamlit | Controles de transcrição implementados")