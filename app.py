#!/usr/bin/env python3
"""
Web wrapper around yt-dlp for DigitalOcean App Platform.

App Platform runs stateless web services with an ephemeral filesystem, so this
does NOT save into a folder like the CLI skill does. Instead it downloads to a
temp dir and streams the file back in the HTTP response, then deletes the temp
dir. Access is gated by a shared secret in the ACCESS_TOKEN env var.

Endpoints:
  GET /                health check
  GET /download        ?url=<video url> [&quality=best|1080p|...] [&format=mp4|webm|mkv] [&audio=1]
                       auth via header  X-Auth-Token: <token>  or  ?token=<token>
"""

import os
import sys
import glob
import shutil
import tempfile
import subprocess

from flask import Flask, request, abort, send_file, jsonify

app = Flask(__name__)

# Set this in the App Platform dashboard (Settings -> App-Level Environment
# Variables) as an encrypted SECRET. Never commit the real value.
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

QUALITIES = {"best", "1080p", "720p", "480p", "360p", "worst"}
FORMATS = {"mp4", "webm", "mkv"}


def _check_auth():
    """Fail closed: a missing server token locks the service, a wrong client
    token is rejected. This keeps a public URL from being a free download proxy."""
    if not ACCESS_TOKEN:
        abort(503, "Service not configured: ACCESS_TOKEN is not set on the server.")
    supplied = request.headers.get("X-Auth-Token") or request.args.get("token")
    if supplied != ACCESS_TOKEN:
        abort(401, "Missing or invalid token.")


def _format_string(quality):
    if quality == "best":
        return "bestvideo+bestaudio/best"
    if quality == "worst":
        return "worstvideo+worstaudio/worst"
    height = quality.replace("p", "")
    return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"


@app.get("/")
def health():
    return jsonify(
        status="ok",
        service="download-youtube",
        configured=bool(ACCESS_TOKEN),
    )


@app.get("/download")
def download():
    _check_auth()

    url = request.args.get("url")
    if not url:
        abort(400, "Missing required 'url' query parameter.")

    quality = request.args.get("quality", "best")
    if quality not in QUALITIES:
        abort(400, f"Invalid quality. Choose one of: {', '.join(sorted(QUALITIES))}.")

    fmt = request.args.get("format", "mp4")
    if fmt not in FORMATS:
        abort(400, f"Invalid format. Choose one of: {', '.join(sorted(FORMATS))}.")

    audio_only = request.args.get("audio", "").lower() in ("1", "true", "yes")

    tmpdir = tempfile.mkdtemp(prefix="dl-")
    # --socket-timeout keeps a stalled connection from hanging indefinitely; the
    # overall subprocess timeout below is the real backstop against App Platform's
    # gateway cutting us off with an opaque 502.
    cmd = ["yt-dlp", "--socket-timeout", "20", "--no-warnings"]
    if audio_only:
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
    else:
        cmd += ["-f", _format_string(quality), "--merge-output-format", fmt]
    cmd += [
        "-o", os.path.join(tmpdir, "%(title).80s [%(id)s].%(ext)s"),
        "--no-playlist",
        url,
    ]

    try:
        # Fail before App Platform's HTTP gateway (~60s) does, so the caller gets
        # a clean app-level error instead of an opaque gateway 502/504.
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=45)
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmpdir, ignore_errors=True)
        print(f"yt-dlp timed out (>45s) for {url}", file=sys.stderr, flush=True)
        abort(504, "Download timed out after 45s — the source is slow or is "
                   "blocking this server (datacenter IPs are often challenged).")
    except subprocess.CalledProcessError as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        # yt-dlp's stderr usually explains the real cause (geo-block, "sign in to
        # confirm you're not a bot" from datacenter IPs, private video, etc.).
        detail = (e.stderr or e.stdout or "").strip()[-800:]
        print(f"yt-dlp failed for {url}: {detail}", file=sys.stderr, flush=True)
        abort(502, f"yt-dlp failed: {detail}")

    files = [f for f in glob.glob(os.path.join(tmpdir, "*")) if os.path.isfile(f)]
    if not files:
        shutil.rmtree(tmpdir, ignore_errors=True)
        abort(502, "Download produced no file.")

    # The merged output is the largest file; partial streams (if any) are smaller.
    path = max(files, key=os.path.getsize)
    resp = send_file(path, as_attachment=True, download_name=os.path.basename(path))
    # Remove the temp dir only after the response has been fully streamed.
    resp.call_on_close(lambda: shutil.rmtree(tmpdir, ignore_errors=True))
    return resp


if __name__ == "__main__":
    # Local dev only; in production gunicorn serves the app (see Dockerfile).
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
