from flask import Blueprint, request, jsonify
from app.services.summarizer import Summarizer

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def helloworld():
    return "PodFast API: YouTube Podcast Summarizer API. Use /api/summarize to summarize a podcast."


@main_bp.route("/api/summarize", methods=["POST"])
def summarize_podcast():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Please provide a YouTube URL in the request body."}), 400

    url = data["url"]
    summarizer = Summarizer()

    try:
        result = summarizer.get_summary(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500