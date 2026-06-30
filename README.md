# download-youtube

A small [Claude](https://claude.com/claude-code) skill that downloads a YouTube
video or Short — and also Instagram Reels, TikTok, X, and any other site
[`yt-dlp`](https://github.com/yt-dlp/yt-dlp) supports — or just its audio, into a
local folder.

It's a thin, well-behaved wrapper around `yt-dlp` with sensible quality/format
defaults, robust filenames, and Windows-friendly output.

## Layout

```
.claude/skills/download-youtube/
├── SKILL.md                    # skill definition (triggering + usage)
└── scripts/download_video.py   # the downloader
download-youtube.skill          # packaged, installable bundle
```

## Requirements

- Python 3.8+
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) (the script auto-installs it via
  pip if missing; keep it current — Instagram/YouTube break old versions:
  `python -m pip install --upgrade yt-dlp`)
- [`ffmpeg`](https://ffmpeg.org/) on `PATH` — required to merge separate
  video+audio streams (anything above ~360p). Install with
  `winget install Gyan.FFmpeg` (Windows), `brew install ffmpeg` (macOS), or
  `apt install ffmpeg` (Linux).

## Usage

```bash
# YouTube video or Short → best quality MP4 into ./YouTube downloads
python ".claude/skills/download-youtube/scripts/download_video.py" "URL" -o "YouTube downloads"

# 720p
python ".claude/skills/download-youtube/scripts/download_video.py" "URL" -q 720p -o "YouTube downloads"

# Audio only (MP3)
python ".claude/skills/download-youtube/scripts/download_video.py" "URL" -a -o "YouTube downloads"

# Login-gated Instagram Reel — borrow cookies from your browser
python ".claude/skills/download-youtube/scripts/download_video.py" "REEL_URL" -o "YouTube downloads" -c firefox
```

### Options

| Flag | Description |
|------|-------------|
| `-o, --output` | Output directory |
| `-q, --quality` | `best` (default), `1080p`, `720p`, `480p`, `360p`, `worst` |
| `-f, --format` | `mp4` (default), `webm`, `mkv` |
| `-a, --audio-only` | Download audio only as MP3 |
| `-c, --cookies-from-browser` | Pull cookies from `chrome`/`firefox`/`edge` for logged-in content |

## Install as a Claude skill

Drop the `download-youtube.skill` bundle into Claude via **Settings → Capabilities
→ Skills**, or copy `.claude/skills/download-youtube/` into your project's or
user's `.claude/skills/` directory.

## Notes

- Files are named `<title (≤80 chars)> [<id>].<ext>` so videos with empty or
  duplicate titles never collide or end up unnamed.
- Playlists are skipped by default; single video only.
- **Instagram:** public Reels usually download anonymously, but Instagram
  rate-limits and may require a login — re-run with `-c firefox`. On Windows,
  `-c chrome` typically fails because modern Chrome encrypts its cookie store;
  prefer Firefox/Edge or a `cookies.txt` export.

Adapted from
[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
(`video-downloader`), extended for Reels and other platforms.

## Disclaimer

For downloading content you own or are authorized to download. Respect the terms
of service of the source platforms and applicable copyright law.
