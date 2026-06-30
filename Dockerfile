FROM python:3.12-slim

# ffmpeg is required by yt-dlp to merge separate video+audio streams (anything
# above ~360p). The default Python buildpack does not include it, which is why
# this app ships its own Dockerfile.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# App Platform routes HTTP to this port (also set http_port: 8080 in app spec).
EXPOSE 8080

# Shell form so ${PORT} (injected by App Platform) is honored, falling back to
# 8080 locally. Long --timeout because large downloads stream slowly to clients.
CMD gunicorn --bind "0.0.0.0:${PORT:-8080}" --workers 2 --timeout 600 app:app
