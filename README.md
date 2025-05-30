# 🎙️ Transcrição de Áudio com Whisper

<div align="center">
  <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Streamlit">
  <br>
  <a href="https://transcricao-de-audio.streamlit.app">Acesse o App Online</a>
  <br><br>
</div>

Aplicativo completo para transcrição automática de arquivos de áudio utilizando o modelo Whisper da OpenAI, disponível tanto online quanto para execução local.

## 🌟 Recursos Principais

- 🎧 **Suporte a múltiplos formatos**: MP3, WAV, M4A, OGG, FLAC
- ⚙️ **Modelos ajustáveis**: Desde Tiny (rápido) até Large (preciso)
- 📈 **Visualização em tempo real**: Barra de progresso e porcentagem
- ⏯️ **Controle total**: Pausar, continuar ou cancelar transcições
- 📥 **Exportação fácil**: Download do texto transcrito em .txt

## 🌐 Versão Web

Acesse instantaneamente sem instalação:  
🔗 [https://transcricao-de-audio.streamlit.app](https://transcricao-de-audio.streamlit.app)

## 💻 Versão Local

### 📋 Pré-requisitos

- Python 3.8 ou superior
- FFmpeg instalado
- 2GB+ de RAM (para modelos pequenos)

### 🛠️ Instalação Passo a Passo

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/transcricao-audio.git
   cd transcricao-audio
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   pip install -r requirements.txt
