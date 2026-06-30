---
name: download-youtube
description: Download a YouTube video or Short (also Instagram Reels, TikTok, X, and any other yt-dlp-supported site) — or just its audio — into a local folder. Use this whenever the user pastes a YouTube/video URL and wants to save, download, grab, archive, or rip it locally, or asks for an MP3/audio extraction from a video. Triggers even if they don't say "yt-dlp" or "download skill" — a video URL plus intent to save it locally is enough.
---

# Download YouTube (and other video) Skill

Downloads videos from YouTube (including Shorts), Instagram Reels, TikTok, X, and
any other site `yt-dlp` supports, with selectable quality and format, via a small
Python wrapper around `yt-dlp`. Use it whenever someone wants a video URL saved to
a folder rather than just watched or summarized.

Source: adapted from ComposioHQ/awesome-claude-skills (`video-downloader`),
extended for Reels and other platforms.

## Requirements

- `python` (3.8+)
- `yt-dlp` (the script auto-installs it via pip if missing; if downloads fail with
  extractor errors, update it: `python -m pip install --upgrade yt-dlp`)
- `ffmpeg` on PATH — needed to merge separate video+audio streams (any quality
  above ~360p comes as two streams). Without it you get two leftover partial files
  instead of one playable MP4. Install with `winget install Gyan.FFmpeg` (Windows),
  `brew install ffmpeg` (macOS), or `apt install ffmpeg` (Linux). On Windows, open a
  fresh shell afterward so the new PATH is picked up.

## Usage

Run from the project root. Save into the project's `YouTube downloads/` folder:

```bash
python ".claude/skills/download-youtube/scripts/download_video.py" "URL" -o "YouTube downloads"
```

### Options

- `-o, --output`   Output directory (use `"YouTube downloads"` for this repo)
- `-q, --quality`  `best` (default), `1080p`, `720p`, `480p`, `360p`, `worst`
- `-f, --format`   `mp4` (default), `webm`, `mkv`
- `-a, --audio-only`  Download audio only as MP3
- `-c, --cookies-from-browser`  Pull cookies from a browser (`chrome`,
  `firefox`, `edge`, …) for logged-in content. Needed for some Reels.

### Examples

```bash
# YouTube video or Short — best quality MP4 into the project folder
python ".claude/skills/download-youtube/scripts/download_video.py" "https://www.youtube.com/watch?v=ID" -o "YouTube downloads"
python ".claude/skills/download-youtube/scripts/download_video.py" "https://www.youtube.com/shorts/ID" -o "YouTube downloads"

# Instagram Reel
python ".claude/skills/download-youtube/scripts/download_video.py" "https://www.instagram.com/reel/REEL_ID/" -o "YouTube downloads"

# Reel that requires a login — borrow cookies from your browser
python ".claude/skills/download-youtube/scripts/download_video.py" "https://www.instagram.com/reel/REEL_ID/" -o "YouTube downloads" -c firefox

# 720p / audio-only MP3
python ".claude/skills/download-youtube/scripts/download_video.py" "URL" -q 720p -o "YouTube downloads"
python ".claude/skills/download-youtube/scripts/download_video.py" "URL" -a -o "YouTube downloads"
```

## Notes

- Works with any site yt-dlp supports (YouTube + Shorts, Instagram Reels, TikTok,
  X, etc.) — just pass the URL. The name says "youtube" but it isn't YouTube-only.
- Filenames are `<title (truncated to 80 chars)> [<id>].<ext>`; the id keeps
  Reels/TikToks with empty or duplicate captions from colliding or ending up
  unnamed. yt-dlp substitutes characters illegal in Windows filenames (e.g. `|`
  becomes the full-width `｜`).
- Playlists are skipped by default (`--no-playlist`); single video only.
- **Instagram caveat:** public Reels usually download anonymously, but Instagram
  rate-limits and may demand a login. If you hit "login required", "rate limited",
  or "empty media response", re-run with `-c firefox` (or your browser) to use your
  session cookies. On Windows, `-c chrome` typically fails ("could not copy Chrome
  cookie database") because modern Chrome encrypts its cookie store — prefer
  Firefox/Edge, or export a cookies.txt file. Private accounts always require auth.
- The upstream default output is `/mnt/user-data/outputs`; for this repo always
  pass `-o "YouTube downloads"`.
