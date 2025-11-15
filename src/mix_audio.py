#!/usr/bin/env python3
import subprocess

root_dir = "separated/htdemucs/ana/"
input_files = [f"{root_dir}drums.wav", f"{root_dir}bass.wav"]
output_file = f"{root_dir}mixed_audio.wav"

cmd = ["ffmpeg", "-y"]
for file in input_files:
    cmd.extend(["-i", file])

cmd.extend(["-filter_complex", f"amix=inputs={len(input_files)}:duration=longest", output_file])

subprocess.run(cmd)
print(f"✅ Done: {output_file}")