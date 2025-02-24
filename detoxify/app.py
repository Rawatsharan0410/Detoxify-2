from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Replace with your YouTube API Key
YOUTUBE_API_KEY = "AIzaSyAp26FH_S26dcbWL3uyy3QAXtXAVmiuTL4"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# List of distracting keywords
DISTRACTING_KEYWORDS = [
    "funny", "prank", "comedy", "gaming", "entertainment", "movie", "music", 
    "cartoon", "asmr", "reaction", "tiktok", "memes", "dance", "vlog"
]

# User-blocked channels list
blocked_channels = []

def is_productive(title, description):
    """Checks if the video is productive based on keywords."""
    content = f"{title.lower()} {description.lower()}"
    
    # Block videos containing distracting keywords
    for keyword in DISTRACTING_KEYWORDS:
        if keyword in content:
            return False
    return True

def get_youtube_videos(query, max_results=10):
    params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video"
    }
    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    data = response.json()

    videos = []
    for item in data.get("items", []):
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        channel = item["snippet"]["channelTitle"]

        # Block videos from user-blocked channels
        if channel in blocked_channels:
            continue

        # Apply keyword filtering
        if not is_productive(title, description):
            continue  

        # Assign a usefulness score (higher = better)
        score = 10 - sum(keyword in title.lower() for keyword in DISTRACTING_KEYWORDS)

        video_info = {
            "title": title,
            "video_id": item["id"]["videoId"],
            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
            "channel": channel,
            "score": score
        }
        videos.append(video_info)

    # Sort videos by usefulness score (higher first)
    videos.sort(key=lambda x: x["score"], reverse=True)
    return videos

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query")
    videos = get_youtube_videos(query)
    return jsonify(videos)

@app.route("/block_channel", methods=["POST"])
def block_channel():
    """Allow users to block specific YouTube channels."""
    data = request.get_json()
    channel = data.get("channel")
    if channel and channel not in blocked_channels:
        blocked_channels.append(channel)
    return jsonify({"blocked_channels": blocked_channels})

if __name__ == "__main__":
    app.run(debug=True)
