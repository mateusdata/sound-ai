import argparse
from pytubefix import YouTube
from pytubefix.cli import on_progress
import moviepy
import os

def baixar_video(url, formato, output_dir="."):
    yt = YouTube(url, on_progress_callback=on_progress)
    stream = yt.streams.get_highest_resolution()
    print(f"📥 Baixando: {yt.title}")

    arquivo = stream.download(output_path=output_dir)

    # Se for vídeo normal (mp4)
    if formato == "mp4":
        print("✔ Download finalizado (MP4).")
        return

    # Converter para áudio
    print(f"🔄 Convertendo para {formato}...")

    audio = moviepy.AudioFileClip(arquivo)
    nome_base = os.path.splitext(arquivo)[0]
    novo_arquivo = f"{nome_base}.{formato}"

    audio.write_audiofile(novo_arquivo)
    audio.close()

    os.remove(arquivo)  # Remove o mp4 temporário
    print(f"🎧 Arquivo convertido: {novo_arquivo}")


def main():
    parser = argparse.ArgumentParser(description="YouTube Downloader CLI")
    parser.add_argument("url", help="URL do vídeo do YouTube")
    parser.add_argument("--format", choices=["mp3", "mp4", "wav"], default="mp4",
                        help="Formato de saída desejado")

    args = parser.parse_args()

    baixar_video(args.url, args.format)


if __name__ == "__main__":
    main()
