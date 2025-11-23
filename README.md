# pytube-downloader

A Python project for downloading YouTube videos using pytube.

## Setup

This project uses `uv` for dependency management. Make sure you have `uv` installed on your system.

### Installation

1. Clone the repository
2. Create and activate virtual environment:
    ```bash
    # Create virtual environment
    uv venv
    
    # Activate virtual environment (Fish shell)
    source .venv/bin/activate.fish
    
    # Activate virtual environment (Bash/Zsh)
    source .venv/bin/activate
    ```
3. Install dependencies:
    ```bash
    uv sync
    ```

## Usage

To download a video and process audio:

```bash
# Download video in MP4 format
uv run cli.py "video" --format mp4

# Process audio with demucs
demucs dil2.mp3
```

## Example

```bash
# pytube-downloader
uv run cli.py "video" --format mp4
demucs dil2.mp3
```