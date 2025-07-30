import streamlit as st
from gtts import gTTS
import subprocess
import base64
import os

# Caminho do FFmpeg
FFMPEG_PATH = r"C:\Users\Proje\Downloads\ffmpeg-2025-07-28-git-dc8e753f32-essentials_build\bin\ffmpeg.exe"

# Configurações da página
st.set_page_config(page_title="Leitor de Texto Interativo", page_icon="🎙️", layout="centered")

# CSS
st.markdown("""
    <style>
        body, .stApp {
            background-color: #ffffff !important;
            color: #1D3269 !important;
            font-family: 'Poppins', sans-serif;
        }
        h1, h2, h3, h4, h5, h6, p, label {
            color: #1D3269 !important;
        }
        textarea, .stTextArea textarea {
            background-color: #ffffff !important;
            color: #1D3269 !important;
            border: 1px solid #1D3269 !important;
            border-radius: 6px !important;
            padding: 8px !important;
            font-size: 15px !important;
        }
        .stSelectbox > div > div {
            background-color: #ffffff !important;
            border: 1px solid #1D3269 !important;
            border-radius: 6px !important;
            color: #1D3269 !important;
        }
        .stButton > button, .stDownloadButton > button {
            background: #ffffff !important;
            color: #ffffff !important;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            padding: 8px 20px;
            transition: all 0.2s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background: #94bf48 !important;
            color: #fff !important;
            transform: translateY(-2px);
        }
        audio {
            width: 100%;
            margin-top: 15px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ Leitor de Texto do Informa")

# -------------------------
# BLOCO DE CONFIGURAÇÕES DE VOZ
# -------------------------
# -------------------------
# BLOCO DE CONFIGURAÇÕES DE VOZ
# -------------------------
with st.expander("⚙️ Configurações de Voz"):
    st.markdown("Personalize a voz gerada com base nos parâmetros disponíveis do gTTS.")

    idioma = st.selectbox("Idioma da voz (`lang`)", [
        "pt", "pt-br", "en", "es", "fr", "de", "it", "ja"
    ], index=0)

    tld = st.selectbox("Sotaque / domínio (`tld`)", [
        "com.br", "com", "co.uk", "ca", "com.au", "ie", "co.in", "co.za", "pt"
    ], index=0)

    voz_preset = st.selectbox("Preset de estilo de voz", [
        "Padrão", "Masculino teste"])

    # Valores padrão
    velocidade = 1.0
    pitch = 0
    volume = 0

    # Ajustes automáticos por preset
    if voz_preset == "Masculino teste":
        pitch = -4
        velocidade = 0.9
    

    # Controles manuais (ajustáveis mesmo com preset)
    velocidade = st.slider("Velocidade (atempo)", 0.5, 2.0, velocidade, 0.05, key="velocidade")
    pitch = st.slider("Pitch (Tom)", -20, 20, pitch, 1, key="pitch")
    volume = st.slider("Volume (dB)", -10, 10, volume, 1, key="volume")

# -------------------------
# BLOCO DE CONFIGURAÇÃO DE QUANTIDADE
# -------------------------
with st.expander("📦 Quantidade de Blocos"):
    if "num_blocos" not in st.session_state:
        st.session_state.num_blocos = 2

    st.session_state.num_blocos = st.selectbox(
        "Selecione a quantidade de blocos:",
        options=list(range(1, 11)),
        index=st.session_state.num_blocos - 1
    )

num_blocos = st.session_state.num_blocos

# -------------------------
# BLOCOS DE TEXTO VISÍVEIS SEMPRE
# -------------------------
st.subheader("Blocos de texto")

for i in range(num_blocos):
    st.markdown(f"**Bloco {i+1}**")
    texto = st.text_area(f"Digite o texto para leitura (Bloco {i+1}):", key=f"texto_{i}")
    temp_audio = f"temp_audio_{i}.mp3"
    final_audio = f"voz_final_{i}.mp3"

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"🔊 Preview (Bloco {i+1})"):
            if texto.strip():
                tts = gTTS(text=texto, lang=idioma, tld=tld)
                tts.save(temp_audio)

                filters = []
                if pitch != 0:
                    pitch_factor = 2 ** (pitch / 12.0)
                    filters.append(f"asetrate=44100*{pitch_factor}")
                    filters.append("aresample=44100")
                if velocidade != 1.0:
                    filters.append(f"atempo={velocidade}")
                if volume != 0:
                    filters.append(f"volume={volume}dB")

                filter_str = ",".join(filters) if filters else "anull"
                subprocess.run([
                    FFMPEG_PATH, "-y", "-i", temp_audio, "-af", filter_str, "processed.mp3"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                os.replace("processed.mp3", temp_audio)

                with open(temp_audio, "rb") as f:
                    audio_b64 = base64.b64encode(f.read()).decode()
                st.markdown(
                    f"""
                    <audio controls autoplay>
                        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                    </audio>
                    """,
                    unsafe_allow_html=True
                )
    with col2:
        if st.button(f"💾 Baixar (Bloco {i+1})"):
            tts = gTTS(text=texto, lang=idioma, tld=tld)
            tts.save(final_audio)

            filters = []
            if pitch != 0:
                pitch_factor = 2 ** (pitch / 12.0)
                filters.append(f"asetrate=44100*{pitch_factor}")
                filters.append("aresample=44100")
            if velocidade != 1.0:
                filters.append(f"atempo={velocidade}")
            if volume != 0:
                filters.append(f"volume={volume}dB")

            filter_str = ",".join(filters) if filters else "anull"
            subprocess.run([
                FFMPEG_PATH, "-y", "-i", final_audio, "-af", filter_str, "processed.mp3"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            os.replace("processed.mp3", final_audio)

            with open(final_audio, "rb") as f:
                st.download_button("Baixar MP3", data=f, file_name=f"voz_final_{i+1}.mp3", mime="audio/mp3")
