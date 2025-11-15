#!/usr/bin/env python3
"""
Script para mixar stems de áudio usando FFmpeg
Uso: python mix_stems.py drums.wav bass.wav -o output.wav
"""

import subprocess
import sys
import os
from pathlib import Path


def mix_audio_files(input_files, output_file):
    """
    Mixa múltiplos arquivos de áudio em um único arquivo usando FFmpeg
    
    Args:
        input_files: Lista de caminhos dos arquivos de entrada
        output_file: Caminho do arquivo de saída
    """
    # Verifica se os arquivos existem
    for file in input_files:
        if not os.path.exists(file):
            print(f"❌ Erro: Arquivo não encontrado: {file}")
            return False
    
    # Monta o comando FFmpeg
    cmd = ["ffmpeg", "-y"]  # -y para sobrescrever sem perguntar
    
    # Adiciona os arquivos de entrada
    for file in input_files:
        cmd.extend(["-i", file])
    
    # Adiciona o filtro de mixagem
    num_inputs = len(input_files)
    cmd.extend([
        "-filter_complex",
        f"amix=inputs={num_inputs}:duration=longest",
        output_file
    ])
    
    print(f"🎵 Mixando {num_inputs} arquivo(s)...")
    print(f"   Entrada: {', '.join([Path(f).name for f in input_files])}")
    print(f"   Saída: {Path(output_file).name}")
    
    try:
        # Executa o comando
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Sucesso! Arquivo salvo: {output_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar FFmpeg:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ Erro: FFmpeg não está instalado!")
        print("   Instale com: sudo apt install ffmpeg")
        return False


def main():
    if len(sys.argv) < 3:
        print("Uso: python mix_stems.py <arquivo1> <arquivo2> [arquivo3...] -o <saída>")
        print("\nExemplos:")
        print("  python mix_stems.py drums.wav bass.wav -o drums_bass.wav")
        print("  python mix_stems.py drums.wav bass.wav other.wav -o instrumental.wav")
        sys.exit(1)
    
    # Separa argumentos
    args = sys.argv[1:]
    
    # Procura o argumento -o
    if "-o" in args:
        o_index = args.index("-o")
        input_files = args[:o_index]
        output_file = args[o_index + 1] if o_index + 1 < len(args) else None
        
        if not output_file:
            print("❌ Erro: Especifique o arquivo de saída após -o")
            sys.exit(1)
    else:
        # Se não especificar -o, usa os 2 primeiros como entrada e último como saída
        input_files = args[:-1]
        output_file = args[-1]
    
    # Verifica se temos pelo menos 2 arquivos para mixar
    if len(input_files) < 2:
        print("❌ Erro: É necessário pelo menos 2 arquivos para mixar")
        sys.exit(1)
    
    # Garante que o diretório de saída existe
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Mixa os arquivos
    success = mix_audio_files(input_files, output_file)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()