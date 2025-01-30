import subprocess
import sys
import time
import os
import signal

# Paths to your files/executables
NGINX_EXE = r"C:/nginx/nginx.exe"  # or just 'nginx' if on Linux and in $PATH
NGINX_CONF = "C:/nginx/conf/nginx.conf"
PLACEHOLDER_MP4 = r"C:/git/PyLivestream/videos/whitenoise.mp4"

def start_nginx(conf_path):
    """
    Start Nginx with the given config file.
    Returns the subprocess.Popen handle.
    """
    cmd = [NGINX_EXE, "-c", conf_path]
    print(f"Starting Nginx with command: {' '.join(cmd)}")
    return subprocess.Popen(cmd)

def start_placeholder_stream(mp4_file, rtmp_url):
    """
    Continuously loop an MP4 file, re-encoding or copying to the RTMP server.
    Returns Popen handle for FFmpeg.
    """
    # The -stream_loop -1 parameter repeats the input infinitely (FFmpeg >= 3.4).
    # On older FFmpeg, you'd have to do something more manual.
    
    cmd = [
        "ffmpeg",
        "-re",                 # Read input in real-time
        "-stream_loop", "-1",  # Loop this file indefinitely
        "-i", mp4_file,
        "-c:v", "libx264",     # Possibly re-encode to standard h.264
        "-preset", "veryfast",
        "-c:a", "aac",
        "-f", "flv",
        rtmp_url
    ]
    
    print(f"Starting placeholder stream: {' '.join(cmd)}")
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def main():
    # 1. Launch Nginx-RTMP
    nginx_proc = start_nginx(NGINX_CONF)
    # Give Nginx a moment to start
    time.sleep(2)
    
    # 2. Launch placeholder
    placeholder_url = "rtmp://localhost/live/placeholder"
    placeholder_proc = start_placeholder_stream(PLACEHOLDER_MP4, placeholder_url)
    
    print("Local RTMP server is running on rtmp://localhost/live/<yourkey>")
    print("Placeholder is streaming on rtmp://localhost/live/placeholder.")
    print("Press Ctrl+C to stop everything.")
    
    try:
        # Keep running until user hits Ctrl+C or something else kills the script
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")

    # Clean up
    placeholder_proc.terminate()
    placeholder_proc.wait()
    
    # Gracefully stop Nginx
    if os.name == 'nt':
        # On Windows, we might need to kill the process or use taskkill
        nginx_proc.terminate()
    else:
        # On Linux/Mac, we can send TERM signal
        os.kill(nginx_proc.pid, signal.SIGTERM)
    
    nginx_proc.wait()
    print("All processes stopped.")

if __name__ == "__main__":
    main()
