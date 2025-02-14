import os
import subprocess
from io import BytesIO
from dotenv import load_dotenv
# from vidgen.hailuo_example import query_video_generation, fetch_video_result, invoke_video_generation
from flask import Flask, request, jsonify
import threading
import time
import requests
from vidgen.VidgenUtils import VideoGeneration, submit_video_idea, get_placeholder_bytes, get_ready_videos
from typing import List, Optional

load_dotenv('../../.env')
# placeholder_path3 = "C:/git/PyLivestream/videos/whitenoise3.mp4"
# placeholder_path3="C:/git/PyLivestream/videos/cat_yarn.mp4"
placeholder_path3="C:/git/PyLivestream/videos/spongebob-clip.mp4"

# Get Twitch key from environment variable
# twitch_key = os.getenv("TWITCH_STREAM_KEY")
twitch_key = "live_571818441_k0IH7DNEt7ryArk81UknYJQf4nSGmF"
if not twitch_key:
    raise EnvironmentError("TWITCH_STREAM_KEY environment variable is not set.")

# Construct the Twitch RTMP URL
twitch_url = f"rtmp://live.twitch.tv/app/{twitch_key}"

# Shared variable between the endpoint and main loop
idea_queue: List[VideoGeneration] = []
ready_queue: List[VideoGeneration] = []

def get_next_generated_file(ready_queue: List[VideoGeneration]) -> str | None:
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
    print("stream from url")
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:  # Only write non-empty chunks
                    ffmpeg_process.stdin.write(chunk)
    except Exception as e:
        print(f"Error streaming from URL: {e}")

def stream_placeholder2(placeholder_bytes, ffmpeg_process):
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

def stream_placeholder(placeholder_bytes, ffmpeg_process):
    placeholder_bytes.seek(0)  # Start at the beginning
    while True:
        data = placeholder_bytes.read(4096)
        if not data:  # If EOF, loop back
            placeholder_bytes.seek(0)
            break
        try:
            ffmpeg_process.stdin.write(data)
        except BrokenPipeError:
            print("FFmpeg process terminated.")
            break

import json
def check_video_format(file_path):
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name,pix_fmt,width,height,avg_frame_rate",
                "-of", "json",
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        video_info = json.loads(result.stdout)
        return video_info.get("streams", [{}])[0]
    except Exception as e:
        print(f"Error checking video format: {e}")
        return {}

def verify_placeholder_bytes(placeholder_path):
    # Check placeholder video format
    info = check_video_format(placeholder_path)
    print(info)
    if info.get("codec_name") != "h264":
        print("Error: Placeholder video codec must be H.264.")
    if info.get("pix_fmt") != "yuv420p":
        print("Error: Placeholder pixel format must be yuv420p.")
    if info.get("width") != 1920 or info.get("height") != 1080:
        print("Error: Placeholder resolution must be 1920x1080.")
    if "30/1" not in info.get("avg_frame_rate", ""):
        print("Error: Placeholder frame rate must be 30 fps.")

def start_ffmpeg_process(twitch_url: str):
    """
    Start the ffmpeg process for streaming to Twitch,
    taking MP4 data from stdin (pipe:0).
    """
    return subprocess.Popen(
        [
            "ffmpeg",
            "-loglevel", "info",
            # -re (read input in real-time) if you want to simulate live playback speed
            "-re",
            # Read from stdin (pipe)
            "-i", "pipe:0",  # The input is MP4 data coming from stdin
            # Output settings
            "-c:v", "libx264", 
            "-preset", "veryfast",
            "-b:v", "3000k",
            "-maxrate", "3000k",
            "-bufsize", "1500k",
            "-g", "60",  # Keyframe interval
            "-c:a", "aac",
            "-ar", "44100",
            "-b:a", "128k",
            "-f", "flv",  # Output format for Twitch
            twitch_url,   # e.g. 'rtmp://live.twitch.tv/app/xxxxxx'
        ],
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

app = Flask(__name__)

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

    return jsonify({"message": "Idea submitted successfully", "task_id": vidgen.task_id}), 200

def read_ffmpeg_stderr(ffmpeg_process):
    for line in iter(ffmpeg_process.stderr.readline, b""):
        print(line.decode("utf-8"), end="")

def stream_local_mp4_files(directory: str, ffmpeg_process: subprocess.Popen):
    """
    Reads each .mp4 file in the directory (in alphabetical order)
    and writes its bytes into ffmpeg_process.stdin.
    """
    mp4_files = sorted(
        f for f in os.listdir(directory) if f.lower().endswith('.mp4')
    )
    for mp4_file in mp4_files:
        file_path = os.path.join(directory, mp4_file)
        print(f"Streaming file: {file_path}")
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                ffmpeg_process.stdin.write(chunk)
                # Optionally flush to avoid buffering
                # ffmpeg_process.stdin.flush()

if __name__ == "__main__":
    # idea_queue.append(VideoGeneration("", task_id="CmJxEWeIgnwAAAAAAEuqyA"))
    # task_id = invoke_video_generation()
    verify_placeholder_bytes(placeholder_path3)
    placeholder_bytes = get_placeholder_bytes(placeholder_path3)
    data = placeholder_bytes.read(4096)

    print("Placeholder bytes:")
    # print(data[:20])  # Inspect the beginning of the raw video data
    length = len(placeholder_bytes.getbuffer())
    print(length)  # Inspect the beginning of the raw video data

    # Start ffmpeg process
    ffmpeg_process = start_ffmpeg_process(twitch_url)

    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    stderr_thread = threading.Thread(target=read_ffmpeg_stderr, args=(ffmpeg_process,), daemon=True)
    # stderr_thread.start()

    local_directory = "C:/git/PyLivestream/videos"
    local_directory = "C:/Users/cjdia/Downloads/kling"
    try:
        stream_local_mp4_files(local_directory, ffmpeg_process)
    except Exception as e:
        print(f"Error streaming local MP4 files: {e}")

    # while True:
    #     get_ready_videos(idea_queue, ready_queue)
    #     vid_url = get_next_generated_file(ready_queue)
        
    #     if vid_url:
    #         print(vid_url)
    #         stream_from_url(vid_url, ffmpeg_process)
    #     else:
    #         stream_placeholder(placeholder_bytes, ffmpeg_process)
        
    # Cleanup
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()
