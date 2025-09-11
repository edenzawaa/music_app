import os
import requests
from flask import Flask, Response, jsonify, abort
print("🔧 Flask app file loaded.")

print("🔎 Starting app at:", os.getcwd())
print("📁 Root directory contents:", os.listdir("."))
print("📁 Music directory contents:", os.listdir("music") if os.path.exists("music") else "music folder missing")



app = Flask(__name__)

# 🔹 Configuration
MUSIC_DIR = "music"     # local directory

# Ensure music directory exists
os.makedirs(MUSIC_DIR, exist_ok=True)
for root, dirs, files in os.walk("."):
    print("DIR:", root, "FILES:", files)


# Playlist state
playlist = []
current_index = 0

def sync_music():
    global playlist
    playlist = sorted([f for f in os.listdir(MUSIC_DIR) if f.endswith(".mp3")])
    print("🎶 Playlist loaded:", playlist)
    return playlist;

sync_music()

def home():
    return jsonify({"message": "Flask music streamer running", "tracks": len(playlist)})
    

def get_current_file():
    if not playlist or current_index >= len(playlist):
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
    if not playlist:
        return jsonify({"error": "Playlist is empty"}), 404
    current_index = (current_index + 1) % len(playlist)
    return jsonify({"current": playlist[current_index]})

@app.route('/prev', methods=["POST", "GET"])
def prev_track():
    global current_index
    if not playlist:
        return jsonify({"error": "Playlist is empty"}), 404
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
    sync_music()  # initilize playlist 
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

