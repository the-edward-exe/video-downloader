#!/usr/bin/env python3
"""
Video Downloader
Downloads videos from YouTube, Instagram Reels, and any other site supported by
yt-dlp, with customizable quality and format options.
"""

import argparse
import sys
import subprocess
import json


def check_yt_dlp():
    """Check if yt-dlp is installed, install if not."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("yt-dlp not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "yt-dlp"], check=True)


def get_video_info(url, cookies_from_browser=None):
    """Get information about the video without downloading."""
    cmd = ["yt-dlp", "--dump-json", "--no-playlist"]
    if cookies_from_browser:
        cmd.extend(["--cookies-from-browser", cookies_from_browser])
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    # Some extractors (e.g. a Reel that resolves to multiple entries) emit one
    # JSON object per line; take the first.
    return json.loads(result.stdout.splitlines()[0])


def download_video(url, output_path="/mnt/user-data/outputs", quality="best", format_type="mp4", audio_only=False, cookies_from_browser=None):
    """
    Download a video from YouTube, Instagram Reels, or any yt-dlp-supported site.

    Args:
        url: Video URL (YouTube, Instagram Reel, TikTok, etc.)
        output_path: Directory to save the video
        quality: Quality setting (best, 1080p, 720p, 480p, 360p, worst)
        format_type: Output format (mp4, webm, mkv, etc.)
        audio_only: Download only audio (mp3)
        cookies_from_browser: Browser name to pull cookies from for logged-in
            content (e.g. "chrome", "firefox", "edge"). Needed for some Reels.
    """
    check_yt_dlp()

    # Build command
    cmd = ["yt-dlp"]

    if cookies_from_browser:
        cmd.extend(["--cookies-from-browser", cookies_from_browser])

    if audio_only:
        cmd.extend([
            "-x",  # Extract audio
            "--audio-format", "mp3",
            "--audio-quality", "0",  # Best quality
        ])
    else:
        # Video quality settings
        if quality == "best":
            format_string = "bestvideo+bestaudio/best"
        elif quality == "worst":
            format_string = "worstvideo+worstaudio/worst"
        else:
            # Specific resolution (e.g., 1080p, 720p)
            height = quality.replace("p", "")
            format_string = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

        cmd.extend([
            "-f", format_string,
            "--merge-output-format", format_type,
        ])

    # Output template. Truncate the title (Reel/TikTok captions can be huge or
    # empty) and append the id so files never collide or end up unnamed.
    cmd.extend([
        "-o", f"{output_path}/%(title).80s [%(id)s].%(ext)s",
        "--no-playlist",  # Don't download playlists by default
    ])

    cmd.append(url)

    print(f"Downloading from: {url}")
    print(f"Quality: {quality}")
    print(f"Format: {'mp3 (audio only)' if audio_only else format_type}")
    print(f"Output: {output_path}\n")

    try:
        # Get video info first
        info = get_video_info(url, cookies_from_browser=cookies_from_browser)
        duration = info.get("duration") or 0  # may be missing/None for Reels
        print(f"Title: {info.get('title') or 'Unknown'}")
        print(f"Duration: {duration // 60}:{duration % 60:02d}")
        print(f"Uploader: {info.get('uploader') or 'Unknown'}\n")

        # Download the video
        subprocess.run(cmd, check=True)
        print(f"\n[OK] Download complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error downloading video: {e}")
        # Surface yt-dlp's own message (captured steps swallow it otherwise).
        # For Instagram this is usually the "use --cookies-from-browser" hint.
        if e.stderr:
            print(e.stderr.strip())
        return False
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download videos from YouTube, Instagram Reels, and other "
                    "yt-dlp-supported sites with customizable quality and format"
    )
    parser.add_argument("url", help="Video URL (YouTube, Instagram Reel, etc.)")
    parser.add_argument(
        "-o", "--output",
        default="/mnt/user-data/outputs",
        help="Output directory (default: /mnt/user-data/outputs)"
    )
    parser.add_argument(
        "-q", "--quality",
        default="best",
        choices=["best", "1080p", "720p", "480p", "360p", "worst"],
        help="Video quality (default: best)"
    )
    parser.add_argument(
        "-f", "--format",
        default="mp4",
        choices=["mp4", "webm", "mkv"],
        help="Video format (default: mp4)"
    )
    parser.add_argument(
        "-a", "--audio-only",
        action="store_true",
        help="Download only audio as MP3"
    )
    parser.add_argument(
        "-c", "--cookies-from-browser",
        default=None,
        help="Pull cookies from this browser for logged-in content, e.g. "
             "chrome, firefox, edge. Needed for some Instagram Reels."
    )

    args = parser.parse_args()

    success = download_video(
        url=args.url,
        output_path=args.output,
        quality=args.quality,
        format_type=args.format,
        audio_only=args.audio_only,
        cookies_from_browser=args.cookies_from_browser
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
