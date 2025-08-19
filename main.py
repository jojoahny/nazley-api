from flask import Flask, request, jsonify
import yt_dlp
import os
import re

app = Flask(__name__)

def sanitize_filename(title):
    """Remove unsafe chars (emojis, slashes, etc.) and limit length"""
    return re.sub(r'[^a-zA-Z0-9_\- ]', '', title)[:80] or "video"

def download_video(url, output_path="downloads", format_str="best[ext=mp4]"):
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        'outtmpl': f'{output_path}/%(title).80s.%(ext)s',
        'format': format_str,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)  
        info['title'] = sanitize_filename(info.get('title', 'video'))
        return {
            "title": info['title'],
            "ext": info.get("ext", "mp4"),
            "url": url
        }

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "Video Downloader API is running 🚀"})

@app.route("/download", methods=["POST"])
def download():
    data = request.json
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url'"}), 400

    url = data["url"]
    try:
        result = download_video(url)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
