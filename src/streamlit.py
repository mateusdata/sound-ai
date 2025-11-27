import streamlit as st
import subprocess
import requests
import urllib.parse
from pathlib import Path
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Demucs Mixer",
    page_icon="🎧",
    layout="wide"
)

# --- CONFIGURAÇÃO DE DIRETÓRIOS ---
BASE_DIR = Path.cwd()
SRC_DIR = BASE_DIR / "src"
SEPARATED_DIR = BASE_DIR / "separated" / "htdemucs"

SRC_DIR.mkdir(exist_ok=True)
SEPARATED_DIR.mkdir(parents=True, exist_ok=True)

# --- FUNÇÕES ---
def download_audio(video_url, music_name):
    """Baixa áudio do YouTube via API."""
    mp3_path = SRC_DIR / f"{music_name}.mp3"
    
    if mp3_path.exists():
        mp3_path.unlink()

    encoded_url = urllib.parse.quote(video_url, "")
    api_url = f"https://www.clipto.com/api/youtube/mp3?url={encoded_url}&csrfToken=8crUK66l-IsnUGoga9wzUzPRRfb4Inx9MEIw"

    try:
        with st.spinner(f"⬇️ Baixando '{music_name}'..."):
            r = requests.get(api_url, stream=True)
            r.raise_for_status()
            with open(mp3_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        return mp3_path
    except Exception as e:
        st.error(f"Erro no download: {e}")
        return None

def compress_audio(file_path):
    """Comprime o WAV para reduzir tamanho sem perder muito qualidade."""
    compressed_path = file_path.parent / f"{file_path.stem}_compressed.wav"
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(file_path),
        "-c:a", "adpcm_ms",
        str(compressed_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    file_path.unlink()
    compressed_path.rename(file_path)

def process_demucs(mp3_path, music_name):
    """Roda o Demucs, comprime stems e mistura bateria+baixo."""
    
    # 1️⃣ Rodar Demucs
    with st.spinner("🎧 Rodando Demucs (Separando faixas)..."):
        result = subprocess.run(["demucs", str(mp3_path)], capture_output=True, text=True)
        if result.returncode != 0:
            st.error("Erro ao rodar Demucs:")
            st.code(result.stderr)
            return False

    # 2️⃣ Localizar pasta de saída
    target_dir = SEPARATED_DIR / music_name
    if not target_dir.exists():
        st.error(f"❌ Pasta de saída não encontrada: {target_dir}")
        return False

    # 3️⃣ Comprimir os 4 stems
    stems = ["vocals.wav", "drums.wav", "bass.wav", "other.wav"]
    for stem in stems:
        stem_path = target_dir / stem
        if stem_path.exists():
            compress_audio(stem_path)

    # 4️⃣ Misturar Bateria e Baixo
    drums = target_dir / "drums.wav"
    bass = target_dir / "bass.wav"
    output_file = target_dir / "mixed_audio.wav"

    if not drums.exists() or not bass.exists():
        st.warning(f"⚠️ Não foi possível encontrar drums.wav ou bass.wav em {target_dir}")
        return False

    with st.spinner("🎛️ Misturando Bateria e Baixo..."):
        cmd_ffmpeg = [
            "ffmpeg", "-y",
            "-i", str(drums),
            "-i", str(bass),
            "-filter_complex", "amix=inputs=2:duration=longest",
            str(output_file)
        ]
        subprocess.run(cmd_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5️⃣ Apagar MP3 original
    try:
        mp3_path.unlink()
    except Exception as e:
        st.warning(f"Não foi possível apagar o MP3 original: {e}")

    return output_file

# --- SIDEBAR ---
with st.sidebar:
    st.header("Mateus Sonoro 🎧")
    
    input_url = st.text_input("🔗 Link do YouTube", placeholder="https://youtube.com/...")
    input_name = st.text_input("📝 Nome da Música (sem espaços preferencialmente)", placeholder="Ex: Coldplay_Yellow")
    
    btn_processar = st.button("🚀 Baixar e Separar")

    if btn_processar:
        if not input_url or not input_name:
            st.warning("Preencha o Link e o Nome!")
        else:
            clean_name = "".join([c for c in input_name if c.isalnum() or c in (' ', '_', '-')]).strip()
            path_mp3 = download_audio(input_url, clean_name)
            if path_mp3:
                final_mix = process_demucs(path_mp3, clean_name)
                if final_mix:
                    st.success(f"✅ Sucesso! '{clean_name}' processada.")
                    st.rerun()

# --- ÁREA PRINCIPAL ---
st.title("📂 Galeria de Mixes (Bateria + Baixo)")
st.markdown("Lista de arquivos `mixed_audio.wav` encontrados em `separated/htdemucs/`")
st.divider()

found_any = False

if SEPARATED_DIR.exists():
    subfolders = [f for f in SEPARATED_DIR.iterdir() if f.is_dir()]
    subfolders.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    for folder in subfolders:
        mix_file = folder / "mixed_audio.wav"
        if mix_file.exists():
            found_any = True
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"🎵 {folder.name}")
                    st.audio(str(mix_file), format="audio/wav")
                with col2:
                    st.info(f"📁 {folder.name}")
                    with open(mix_file, "rb") as file:
                        st.download_button(
                            label="⬇️ Download WAV",
                            data=file,
                            file_name=f"{folder.name}_drum_bass.wav",
                            mime="audio/wav",
                            key=f"dl_{folder.name}"
                        )
            st.divider()

if not found_any:
    st.info("Nenhuma música processada encontrada ainda. Use a barra lateral para adicionar!")
