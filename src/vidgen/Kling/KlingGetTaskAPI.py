import json
from typing import Optional, Dict, Any, List
from enum import Enum
from vidgen.Kling.KlingAuth import get_api_token
import requests

# Define the classes as provided
class Error:
    def __init__(self, code: Optional[int], message: Optional[str]) -> None:
        self.code = code
        self.message = message


class Usage:
    def __init__(self, consume: float, frozen: float, type: str) -> None:
        self.consume = consume
        self.frozen = frozen
        self.type = type


class Meta:
    def __init__(self, created_at: Optional[str], ended_at: Optional[str], is_using_private_pool: bool, 
                 started_at: Optional[str], usage: Usage) -> None:
        self.created_at = created_at
        self.ended_at = ended_at
        self.is_using_private_pool = is_using_private_pool
        self.started_at = started_at
        self.usage = usage


class Status(Enum):
    COMPLETED = "Completed"
    FAILED = "Failed"
    PENDING = "Pending"
    PROCESSING = "Processing"
    STAGED = "Staged"

class TaskStatusResult:
    """
    Represents the result of a task status query.
    """
    def __init__(self, url: str, request_id: str, task_id: str, duration: Optional[float]):
        self.url = url
        self.request_id = request_id
        self.task_id = task_id
        self.duration = duration

    def __repr__(self):
        return (f"TaskStatusResult("
                f"url='{self.url}', "
                f"request_id='{self.request_id}', "
                f"task_id='{self.task_id}', "
                f"duration={self.duration})")
                
class Data:
    def __init__(self, detail: None, error: Error, input: Dict[str, Any], logs: List[Dict[str, Any]], 
                 meta: Meta, model: str, output: Dict[str, Any], status: Status, task_id: str, task_type: str) -> None:
        self.detail = detail
        self.error = error
        self.input = input
        self.logs = logs
        self.meta = meta
        self.model = model
        self.output = output
        self.status = status
        self.task_id = task_id
        self.task_type = task_type

class GetTaskModel:
    def __init__(self, code: int, data: Data, message: str) -> None:
        self.code = code
        self.data = data
        self.message = message

def send_get_image2vid_task_request(task_id: str) -> Optional[TaskStatusResult]:
    image2vid_task_retrieve = f"https://api.klingai.com/v1/videos/image2video/{task_id}"
    return send_get_task_request(image2vid_task_retrieve)

def send_get_text2vid_task_request(task_id: str) -> Optional[TaskStatusResult]:
    text2vid_task_retrieve = f"https://api.klingai.com/v1/videos/text2video/{task_id}"
    return send_get_task_request(text2vid_task_retrieve)

def send_get_task_request(url) -> Optional[TaskStatusResult]:
    # Create the payload
    api_key = get_api_token()
    # Set headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }

    # Send the POST request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Task retrieved successfully!")
        print("Response:", response.json())
        return parse_task_status(response.json())
    else:
        print("Failed to get task. Status Code:", response.status_code)
        print("Error:", response.text)
        return None

def parse_task_status(response: dict) -> TaskStatusResult:
    """
    Parse the task status response into a TaskStatusResult instance.

    :param response: The response dictionary from the API.
    :return: A TaskStatusResult instance.
    """
    try:
        request_id = response.get("request_id", "")
        task_data = response.get("data", {})
        task_id = task_data.get("task_id", "")
        task_result = task_data.get("task_result", {})
        videos = task_result.get("videos", [])
        
        # Extract the first video details if available
        if videos and isinstance(videos, list):
            video = videos[0]
            url = video.get("url", "")
            duration = float(video.get("duration", 0))
        else:
            url = ""
            duration = None

        return TaskStatusResult(
            url=url,
            request_id=request_id,
            task_id=task_id,
            duration=duration
        )
    except Exception as e:
        raise ValueError(f"Failed to parse task status response: {e}")

api_response = '''
{
    "code": 200,
    "data": {
        "task_id": "b3efc0ab-3fdb-4b88-b20a-94eef777e125",
        "model": "kling",
        "task_type": "video_generation",
        "status": "completed",
        "config": {
            "service_mode": "private",
            "webhook_config": {
                "endpoint": "",
                "secret": ""
            }
        },
        "input": {},
        "output": {
            "type": "m2v_txt2video_hq",
            "status": 99,
            "works": [
                {
                    "status": 99,
                    "type": "m2v_txt2video_hq",
                    "cover": {
                        "resource": "https://xxx.png",
                        "resource_without_watermark": "",
                        "height": 1440,
                        "width": 1440,
                        "duration": 0
                    },
                    "video": {
                        "resource": "https://xxx.mp4",
                        "resource_without_watermark": "https://storage.goapi.ai/xxx.mp4",
                        "height": 1440,
                        "width": 1440,
                        "duration": 5100
                    }
                }
            ]
        },
        "meta": {},
        "detail": null,
        "logs": [],
        "error": {
            "code": 0,
            "raw_message": "",
            "message": "",
            "detail": null
        }
    },
    "message": "success"
}
'''

if __name__ == "__main__":
    # Parse and use the response
    # api_model = parse_api_response(api_response)
    # print(f"Task Status: {api_model.data.status}")
    # print(f"Video URL: {api_model.data.output['works'][0]['video']['resource']}")

    print(send_get_image2vid_task_request("CjilnGeIgjUAAAAAAErEWA"))
    # send_get_text2vid_task_request("CmJxEWeIgnwAAAAAAEuqyA")