import requests
from vidgen.Kling.KlingAuth import get_api_token

def submit_video_idea(video_idea: str) -> str:
    """
    Submit a video idea to the Kling API and return the task ID.

    :param video_idea: A text description of the video to generate
    :return: The task ID for the submitted video idea
    """
    # API settings
    API_KEY = get_api_token()  # Replace with your token retrieval logic
    API_URL = "https://api.klingai.com/v1/videos/text2video"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model_name": "kling-v1",  # Replace with your model version
        "duration": 5,            # Video duration in seconds
        "mode": "std",            # Standard mode ("pro" for high-quality mode)
        "prompt": video_idea      # The provided video idea
    }
    
    try:
        # Make the POST request
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("data", {}).get("task_id")
            if task_id:
                return task_id
            else:
                raise ValueError("Task ID not found in the API response.")
        else:
            raise Exception(f"API Error: {response.status_code}, {response.text}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while submitting the video idea: {str(e)}")

# Example Usage
if __name__ == "__main__":
    idea = "A cat is playing with a ball of yarn."
    try:
        task_id = submit_video_idea(idea)
        print(f"Task ID: {task_id}")
    except Exception as e:
        print(f"Failed to submit video idea: {e}")
