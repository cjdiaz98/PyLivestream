import signal
import argparse
import os
import glob
from itertools import cycle
from .api import stream_file

def get_mp4_files(directory):
    """Validate and retrieve all MP4 files in the given directory."""
    mp4_files = glob.glob(os.path.join(directory, "*.mp4"))
    if not mp4_files:
        raise ValueError(f"No MP4 files found in the directory: {directory}")
    return mp4_files

if __name__ == "__main__":
    """
    LIVE STREAM using FFMPEG -- Looping over multiple input files in a directory.

    This script streams all MP4 files in the given directory sequentially, looping indefinitely.

    NOTE: for audio files,
        use FileGlob2Livestream.py with options `-image myimg.jpg -loop`

    https://www.scivision.dev/youtube-live-ffmpeg-livestream/
    https://support.google.com/youtube/answer/2853702
    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = argparse.ArgumentParser(description="Livestream MP4 files in a directory sequentially, looping indefinitely.")
    p.add_argument(
        "indir",
        help="Directory containing MP4 files to stream, looping sequentially."
    )
    p.add_argument(
        "websites",
        help="Site to stream, e.g. localhost youtube facebook twitch",
        nargs="+",
    )
    p.add_argument("json", help="JSON file with stream parameters such as key")
    p.add_argument("-t", "--timeout", help="Stop streaming after --timeout seconds", type=int)
    P = p.parse_args()

    try:
        # Get all MP4 files in the directory
        mp4_files = get_mp4_files(P.indir)

        # Cycle through MP4 files indefinitely
        for video_file in cycle(mp4_files):
            print(f"Streaming file: {video_file}")
            stream_file(
                ini_file=P.json,
                websites=P.websites,
                assume_yes=True,
                timeout=P.timeout,
                loop=False,  # Looping the directory, not individual files
                video_file=video_file,
            )
    except ValueError as e:
        print(f"Error: {e}")
