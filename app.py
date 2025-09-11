import os
from flask import Flask, Response, jsonify, abort

app = Flask(__name__)

# 📁 Local folder containing your MP3s (commit this folder to your repo)
MUSIC_DIR = "music"

# Ensure the folder exists
os.makedirs(MUSIC_DIR, exist_ok=True)

# Playlist state
playlist = []
current_index = 0


def load_playlist():
    """Scan the local music folder for MP3 files."""
    global playlist
    playlist = sorted([f for f in os.listdir(MUSIC_DIR) if f.lower().endswith(".mp3")])
    print("🎶 Playlist loaded:", playlist)


def get_current_file():
    """Get the full path of the current MP3 file."""
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
            while chunk := f.read(4096):
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


@app.route('/debug/files')
def debug_files():
    """Optional: list all files in the container for debugging."""
    files = []
    for root, dirs, filenames in os.walk("."):
        for name in filenames:
            files.append(os.path.join(root, name))
    return jsonify(files)


if __name__ == '__main__':
    print("🚀 Starting app, loading local playlist...")
    load_playlist()  # Only scan local files, no downloads
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
