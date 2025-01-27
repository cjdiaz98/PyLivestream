import requests
from KlingAuth import get_api_token

def generate_video_from_image(image_url, prompt= "", duration=5, mode="std", model_name="kling-v1"):
    """
    Generates a video from an image using the KlingAI API.

    Args:
        image_url (str): The URL of the image to use for video generation.
        duration (int): Duration of the video in seconds (default is 5).
        mode (str): Mode of video generation, either "std" (standard) or "pro" (high-quality).
        model_name (str): The model name to use for video generation, e.g., "kling-v1" or "kling-v1-5".

    Returns:
        dict: Response data from the API if successful, or an error message if failed.
    """
    # Get API token
    API_KEY = get_api_token()
    API_URL = "https://api.klingai.com/v1/videos/image2video"

    # Setup headers and payload
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model_name": model_name,
        "image": image_url,
        "duration": duration,
        "mode": mode
    }
    if prompt and prompt != "":
        payload["prompt"] = prompt

    # Make the API request
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("data", {}).get("task_id", {})
            print(f"Video task created successfully! Task ID: {task_id}")
            return data
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return {"error": response.text, "status_code": response.status_code}
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    image_url = "https://cdn.britannica.com/20/194520-050-DCAE62F1/New-World-Sylvilagus-cottontail-rabbits.jpg"
    result = generate_video_from_image(image_url, duration=5, mode="std", model_name="kling-v1")
    print(result)
