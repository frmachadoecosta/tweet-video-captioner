# X Post to Video

A small Streamlit app that downloads an X post's video, adds the post caption as a title, and lets you download the result.

## Run locally

Requires Python 3.11 and FFmpeg.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Open <http://localhost:8501>, paste an X post URL, and enter an X API bearer token with access to the post.

## Run with Docker Compose

Install Docker Engine with the Compose plugin on the home server. Give the server a reserved LAN address, copy `.env.example` to `.env`, and set `LAN_IP` to that address.

```sh
cp .env.example .env
# Edit .env and set LAN_IP to the server's reserved LAN address.
docker compose up -d --build
```

Open `http://<LAN_IP>:8501` from a device on the same network. Compose binds the port only to the configured LAN address. Do not forward port 8501 from your router. Configure the host firewall to permit port 8501 only from your trusted home network.

To update the app after pulling changes:

```sh
docker compose up -d --build
```

The downloaded JSON, source videos, and processed videos are stored in the persistent `app-cache` Docker volume. Remove that volume with `docker compose down --volumes` only if you want to delete the cached files.

## Configuration and privacy

- The bearer token can be entered in the app or provided as `BEARER_TOKEN` in the container environment.
- Do not commit `.env`, API tokens, or downloaded content. `.gitignore` excludes credentials, caches, local environments, and `assets/`.
- The app uses an installed system font by default. Set `VIDEO_FONT_PATH` to use a specific TrueType font. Docker installs DejaVu Sans Bold.
- Your browser sends the post URL and token to the Streamlit server. The server uses them to request the X API and download the video's media URL.

## Project layout

```text
streamlit_app.py       Streamlit user interface
src/tweet_to_video.py  X API, media download, and video processing
src/manipulate_video.py Caption header rendering
Dockerfile             Container image
compose.yaml           LAN-bound home-server deployment
requirements.txt       Pinned direct Python dependencies
```
