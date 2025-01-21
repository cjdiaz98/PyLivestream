import os
import subprocess
from io import BytesIO
from dotenv import load_dotenv
# from vidgen.hailuo_example import query_video_generation, fetch_video_result, invoke_video_generation
from flask import Flask, request, jsonify
import threading
import time
import requests
from vidgen.VidgenUtils import VideoGeneration, submit_video_idea, get_placeholder_bytes
from typing import List, Optional

load_dotenv('../../.env')
placeholder_path3 = "C:/git/PyLivestream/videos/whitenoise3.mp4"
# Get Twitch key from environment variable
# twitch_key = os.getenv("TWITCH_STREAM_KEY")
twitch_key = "live_571818441_k0IH7DNEt7ryArk81UknYJQf4nSGmF"
if not twitch_key:
    raise EnvironmentError("TWITCH_STREAM_KEY environment variable is not set.")

# Construct the Twitch RTMP URL
twitch_url = f"rtmp://live.twitch.tv/app/{twitch_key}"

app = Flask(__name__)

# Shared variable between the endpoint and main loop
idea_queue: List[VideoGeneration] = []

def run_flask_app():
    """Run Flask app in a separate thread."""
    app.run(host="0.0.0.0", port=5000, debug=False)

@app.route('/submit-idea', methods=['POST'])
def submit_idea():
    global shared_variable
    data = request.json
    if not data or 'description' not in data:
        return jsonify({"error": "Invalid input, 'description' is required"}), 400

    description = data['description']
    vidgen = submit_video_idea(description)
    idea_queue.append(vidgen)
    # Update the shared variable
    shared_variable["task_id"] = task_id

    return jsonify({"message": "Idea submitted successfully", "task_id": task_id}), 200

def get_next_generated_file() -> str | None:
    if not idea_queue:
        return None
    else:
        top_vid = idea_queue.pop()
        return top_vid.url


def stream_from_url(url, ffmpeg_process):
    """
    Stream bytes from a URL to the ffmpeg process.
    :param url: The URL of the video to stream.
    :param ffmpeg_process: The ffmpeg process to write bytes to.
    """
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:  # Only write non-empty chunks
                    ffmpeg_process.stdin.write(chunk)
    except Exception as e:
        print(f"Error streaming from URL: {e}")

def stream_placeholder(placeholder_bytes, ffmpeg_process):
    """
    Stream placeholder bytes to the ffmpeg process in a loop.
    :param placeholder_bytes: Bytes-like object of the placeholder video.
    :param ffmpeg_process: The ffmpeg process to write bytes to.
    """
    print("stream placeholder")
    placeholder_bytes.seek(0)
    data = placeholder_bytes.read(4096)
    if not data:
        placeholder_bytes.seek(0)
    ffmpeg_process.stdin.write(data)

def start_ffmpeg_process(twitch_url: str):
    """
    Start the ffmpeg process for streaming to Twitch.
    """
    return subprocess.Popen(
        [
            "ffmpeg",
            "-re",
            "-f", "rawvideo",  # Raw video input
            "-pixel_format", "yuv420p",  # Input pixel format
            "-video_size", "1920x1080",  # Resolution
            "-framerate", "30",  # Frame rate
            "-i", "pipe:",  # Read input from stdin (video)
            "-f", "lavfi",  # Use lavfi for audio filter
            "-i", "anullsrc=r=44100:cl=stereo",  # Generate silent audio
            "-vf", "format=yuv420p",  # Output pixel format
            "-c:v", "libx264",  # Encode to H.264
            "-preset", "veryfast",
            "-b:v", "500k",
            "-g", "60",
            "-c:a", "aac",  # Audio codec
            "-ar", "44100",  # Audio sample rate
            "-b:a", "128k",  # Audio bitrate
            "-f", "flv",
            twitch_url,
        ],
        stdin=subprocess.PIPE
    )

# idea_queue.append(VideoGeneration("", task_id="CmJxEWeIgnwAAAAAAEuqyA"))

# if __name__ == "__main__":
#     placeholder_path = "placeholder.mp4"  # Replace with your placeholder video path
#     twitch_url = "rtmp://your-twitch-url-here"  # Replace with your Twitch stream URL

#     # Prepare placeholder bytes
#     placeholder_bytes = get_placeholder_bytes(placeholder_path)

#     # Start the ffmpeg process
#     ffmpeg_process = start_ffmpeg_process(twitch_url)

#     # Stream placeholder bytes in a loop
#     try:
#         stream_placeholder(placeholder_bytes, ffmpeg_process)
#     except BrokenPipeError:
#         print("FFmpeg process ended. Exiting...")
#     finally:
#         ffmpeg_process.stdin.close()
#         ffmpeg_process.wait()

if __name__ == "__main__":
    # task_id = invoke_video_generation()
    placeholder_bytes = get_placeholder_bytes(placeholder_path3)

    # Start ffmpeg process
    ffmpeg_process = start_ffmpeg_process(twitch_url)

    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    current_url = None
    while True:
        vid_url = get_next_generated_file(task_id)
        if vid_url:
            stream_from_url(vid_url, ffmpeg_process)
        else:
            stream_placeholder(placeholder_bytes, ffmpeg_process)
        time.sleep(5)

    # Cleanup
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()
