import streamlit as st
import subprocess
import requests
import urllib.parse
import sys
import shutil
from pathlib import Path
from tqdm import tqdm

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Drum & Bass Extractor", page_icon="🥁")

# Define os caminhos baseados na estrutura do seu projeto
BASE_DIR = Path.cwd()
SRC_DIR = BASE_DIR / "src"
SEPARATED_DIR = BASE_DIR / "separated"
DEMUCS_OUTPUT_DIR = SEPARATED_DIR / "htdemucs"

# Garante que as pastas existam
SRC_DIR.mkdir(exist_ok=True)

def download_audio(url_youtube, progress_bar):
   
    try:
       
       
        filename = "temp_audio" 
        output_path = SRC_DIR / f"{filename}.mp3"
        
        encoded_url = urllib.parse.quote(url_youtube, "")
       
        api_url = f"https://www.clipto.com/api/youtube/mp3?url={encoded_url}&csrfToken=8crUK66l-IsnUGoga9wzUzPRRfb4Inx9MEIw"
        
        r = requests.get(api_url, stream=True)
        total_size = int(r.headers.get("content-length", 0))
        
       
        if total_size < 10000 and total_size > 0:
             st.error("Erro no download: A API retornou um arquivo inválido. O link pode ser inválido ou o token expirou.")
             return None

        downloaded = 0
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress_bar.progress(min(downloaded / total_size, 1.0))
        
        return output_path
    except Exception as e:
        st.error(f"Erro ao baixar: {e}")
        return None

def run_demucs(input_path):
   
    try:
       
        cmd = ["demucs", str(input_path)]
        
       
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            st.error("Erro no Demucs:")
            st.code(result.stderr)
            return False
        return True
    except Exception as e:
        st.error(f"Erro crítico ao executar Demucs: {e}")
        return False

def mix_tracks(song_folder_name):
   
   
    track_dir = DEMUCS_OUTPUT_DIR / song_folder_name
    
    drums = track_dir / "drums.wav"
    bass = track_dir / "bass.wav"
    output_mixed = track_dir / "drums_and_bass_mix.wav"

    if not drums.exists() or not bass.exists():
        st.error(f"Arquivos separados não encontrados em: {track_dir}")
        return None

    cmd = [
        "ffmpeg", "-y",
        "-i", str(drums),
        "-i", str(bass),
        "-filter_complex", "amix=inputs=2:duration=longest",
        str(output_mixed)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_mixed
    except subprocess.CalledProcessError as e:
        st.error("Erro no FFmpeg ao mixar as faixas.")
        return None

# --- INTERFACE DO STREAMLIT ---

st.title("🎧 Extrator de Baixo e Bateria")
st.markdown("Cole o link do YouTube, a IA separa tudo e te entrega o mix pronto.")

youtube_url = st.text_input("URL do YouTube:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("🚀 Processar Áudio", type="primary"):
    if not youtube_url:
        st.warning("Por favor, insira uma URL.")
    else:
       
        with st.status("Iniciando processamento...", expanded=True) as status:
            
           
            st.write("⬇️ Baixando áudio do YouTube...")
            progress_bar = st.progress(0)
            mp3_path = download_audio(youtube_url, progress_bar)
            
            if mp3_path:
                st.write("✅ Download concluído!")
                
               
                st.write("🧠 A IA (Demucs) está separando as faixas... (Isso pode demorar)")
               
                song_name = mp3_path.stem
                potential_old_folder = DEMUCS_OUTPUT_DIR / song_name
                if potential_old_folder.exists():
                    shutil.rmtree(potential_old_folder)

                success = run_demucs(mp3_path)
                
                if success:
                    st.write("✅ Separação concluída!")
                    
                   
                    st.write("🎛️ Mixando Bateria + Baixo...")
                    final_file = mix_tracks(song_name)
                    
                    if final_file:
                        status.update(label="Processo finalizado com sucesso!", state="complete", expanded=False)
                        
                        st.success("Tudo pronto! Ouça ou baixe abaixo.")
                        
                       
                        st.audio(str(final_file), format="audio/wav")
                        
                       
                        with open(final_file, "rb") as file:
                            st.download_button(
                                label="📥 Baixar Mix (WAV)",
                                data=file,
                                file_name="drums_bass_mix.wav",
                                mime="audio/wav"
                            )
                    else:
                        status.update(label="Erro na mixagem", state="error")
                else:
                    status.update(label="Erro na separação", state="error")
            else:
                status.update(label="Erro no download", state="error")

# Rodapé com info de debug
with st.expander("ℹ️ Informações do Sistema"):
    st.text(f"Diretório Raiz: {BASE_DIR}")
    st.text(f"Diretório Saída Demucs: {DEMUCS_OUTPUT_DIR}")