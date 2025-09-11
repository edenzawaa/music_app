import os
import requests
from flask import Flask, Response, jsonify, abort

app = Flask(__name__)

# 🔹 Configuration
GITHUB_USER = "edenzawaa"
GITHUB_REPO = "music_host"
GITHUB_PATH = "clean"   # folder in repo where mp3s are stored
MUSIC_DIR = "music"     # local directory

# Ensure music directory exists
os.makedirs(MUSIC_DIR, exist_ok=True)

# Playlist state
playlist = []
current_index = 0

def sync_music():
    #fetches all song from repo and save in into the music folder
    global playlist
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_PATH}"
    resp = requests.get(url)

    if resp.status_code != 200:
        print("❌ Failed to fetch from GitHub:", resp.text)
        return

    files = resp.json()
    for f in files:
        if f["name"].endswith(".mp3"):
            download_url = f["download_url"]
            local_path = os.path.join(MUSIC_DIR, f["name"])
            if not os.path.exists(local_path):  # skip if already downloaded
                print(f"⬇️ Downloading {f['name']}...")
                song = requests.get(download_url)
                with open(local_path, "wb") as out:
                    out.write(song.content)

    # Build playlist after sync
    playlist = sorted([f for f in os.listdir(MUSIC_DIR) if f.endswith(".mp3")])
    print("Playlist loaded:", playlist)


def get_current_file():
    if not playlist:
        return None
    return os.path.join(MUSIC_DIR, playlist[current_index])


@app.route('/stream')
def stream():
    filepath = get_current_file()
    if not filepath or not os.path.exists(filepath):
        abort(404, description="No track found")

    def generate():
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                yield chunk
    return Response(generate(), mimetype="audio/mpeg")


@app.route('/next', methods=["POST", "GET"])
def next_track():
    global current_index
    if playlist:
        current_index = (current_index + 1) % len(playlist)
    return jsonify({"current": playlist[current_index]})


@app.route('/prev', methods=["POST", "GET"])
def prev_track():
    global current_index
    if playlist:
        current_index = (current_index - 1) % len(playlist)
    return jsonify({"current": playlist[current_index]})


@app.route('/status')
def status():
    return jsonify({
        "playlist": playlist,
        "current": playlist[current_index] if playlist else None,
        "index": current_index
    })
#incase if i want to add a ips display for current song later

if __name__ == '__main__':
    sync_music()  # fetch songs from GitHub on startup
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

