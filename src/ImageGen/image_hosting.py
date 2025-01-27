import threading
from flask import Flask, send_file, abort
from pyngrok import ngrok
import os

# Specify the directory where your images are stored
IMAGE_DIRECTORY = os.path.join(os.getcwd(), "out")

# Ensure the directory exists
os.makedirs(IMAGE_DIRECTORY, exist_ok=True)

# Check if the directory exists
if not os.path.exists(IMAGE_DIRECTORY):
    raise FileNotFoundError(f"Image directory not found: {IMAGE_DIRECTORY}")

app = Flask(__name__)

@app.route("/<path:image_name>")
def serve_image(image_name):
    # Construct the full path to the image
    image_path = os.path.join(IMAGE_DIRECTORY, image_name)
    
    # Check if the file exists and is a valid file
    if not os.path.exists(image_path) or not os.path.isfile(image_path):
        abort(404, description="Image not found")
    
    # Serve the image file
    return send_file(image_path, mimetype='image/jpeg')

def run_flask():
    """Run the Flask server."""
    app.run(port=5000)

def start_ngrok():
    """Start ngrok and return the public URL."""
    public_url = ngrok.connect(5000)
    print(f"Public URL: {public_url}")
    return public_url

