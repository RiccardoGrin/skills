# Installation Guide

Read this file only when Phase 0 checks report a missing dependency.

## OPENAI_API_KEY

The only thing the user must provide manually.

Ask the user to do one of:
- Export as env var: `export OPENAI_API_KEY=sk-...`
- Add to a `.env` file in the project root: `OPENAI_API_KEY=sk-...`

Do NOT proceed without a valid key.

## yt-dlp

Pure Python package — install with pip:

```bash
pip install yt-dlp
```

No system dependencies. Works on all platforms.

## ffmpeg

Required by yt-dlp for audio extraction. Try each method in order until one works.

### Windows

1. `winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements`
2. If no winget: `choco install ffmpeg -y`
3. If no choco: use the pip fallback below

### macOS

1. `brew install ffmpeg`
2. If no brew: use the pip fallback below

### Linux

1. `sudo apt-get install -y ffmpeg` (Debian/Ubuntu)
2. `sudo dnf install -y ffmpeg` (Fedora/RHEL)
3. If no sudo or no package manager: use the pip fallback below

### Universal pip fallback (all platforms)

Works without admin privileges or a system package manager:

```bash
pip install imageio-ffmpeg
```

This bundles a static ffmpeg binary. Find its path with:

```bash
python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
```

Add the directory containing the binary to PATH for the session, or copy/symlink it somewhere on PATH.

### Verify

After any installation method:

```bash
ffmpeg -version 2>/dev/null | head -1
```

## Python dependencies

Install the skill's requirements (openai, yt-dlp):

```bash
pip install -r <skill-dir>/scripts/requirements.txt
```
