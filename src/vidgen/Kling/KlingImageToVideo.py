import requests
from KlingAuth import get_api_token

# Replace with your actual API key and endpoint
API_KEY = get_api_token()
API_URL = "https://api.klingai.com/v1/videos/image2video"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model_name": "kling-v1",  # or "kling-v1-5" if available
    "image": "https://cdn.britannica.com/20/194520-050-DCAE62F1/New-World-Sylvilagus-cottontail-rabbits.jpg",  # Replace with your image URL or Base64 string
    "duration": 5,  # Duration in seconds
    "mode": "std"  # Standard mode (use "pro" for high-quality mode)
}

# Make the POST request to the API
try:
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(data)
        task_id = data.get("data", {}).get("task_id", {})
        # print(f"Video generated successfully! Download it here: {video_url}")
    else:
        print(f"Error: {response.status_code}, {response.text}")
except Exception as e:
    print(f"An error occurred: {str(e)}")