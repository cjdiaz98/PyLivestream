from typing import List, Optional
from io import BytesIO
import subprocess
from vidgen.Kling.KlingGetTaskAPI import TaskStatusResult

class VideoGeneration:
    def __init__(self, video_description: str,
        task_id: Optional[str] = None,
        submitting_user: Optional[str] = None):
        """
        Initialize a VideoGeneration instance.

        :param video_description: Description of the video idea
        :param task_id: Optional unique identifier for the video generation task
        :param submitting_user: Optional user who submitted the video idea
        """
        self.video_description = video_description
        self.task_id = task_id
        self.submitting_user = submitting_user
        self.url = None

    def __repr__(self):
        """
        Provide a readable string representation of the instance for debugging.
        """
        return (f"VideoGeneration("
                f"video_description='{self.video_description}', "
                f"task_id='{self.task_id}', "
                f"submitting_user='{self.submitting_user}')")

    def to_dict(self):
        """
        Convert the instance to a dictionary representation.
        """
        return {
            "video_description": self.video_description,
            "task_id": self.task_id,
            "submitting_user": self.submitting_user
        }

def get_placeholder_bytes(path: str) -> BytesIO:
    """
    Read placeholder video into BytesIO.
    """
    placeholder_bytes = BytesIO()
    decode_process = subprocess.Popen(
        [
            "ffmpeg",
            "-i", path,  # Input placeholder video
            "-f", "rawvideo",  # Decode to raw video
            "-pix_fmt", "yuv420p",  # Pixel format
            "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    for chunk in iter(lambda: decode_process.stdout.read(4096), b""):
        placeholder_bytes.write(chunk)
    decode_process.stdout.close()
    decode_process.wait()
    return placeholder_bytes

def get_next_generated_file(task_id: str) -> BytesIO:
    """
    If the video generation task is finished, return the Bytes of the generated video.
    Otherwise, return bytes of a placeholder (white noise) video.
    """
    file_id, status = query_video_generation(task_id)

    if file_id != "":
        file_bytes = fetch_video_result(file_id)  # Assumes this returns BytesIO object
        print("---------------Successful---------------")
        return file_bytes
    elif status == "Fail" or status == "Unknown":
        print("---------------Failed---------------")
        # Generate white noise placeholder video
        return None

from vidgen.Kling.KlingTextToVideo import submit_video_idea
from vidgen.Kling.KlingGetTaskAPI import send_get_text2vid_task_request

def get_ready_videos(pending_queue: List[VideoGeneration], ready_queue: List[VideoGeneration]):
    """
    Get a list of video ideas that are ready for viewing.
    """

    for idea in pending_queue:
        url = check_video_generation_status(idea.task_id)
        if url:
            # pending_queue.remove(idea)
            ready_queue.append(idea)
            idea.url = url

def submit_video_idea(description: str) -> VideoGeneration:
    """
    Submit a video idea to the video generation service.

    :param description: The description of the video idea.
    :return: A VideoGeneration instance representing the submitted idea.
    """
    task_id = submit_video_idea(description)
    return VideoGeneration(video_description=description, task_id=task_id)

def check_video_generation_status(task_id: str) -> str | None:
    """
    Check the status of a video generation task.

    :param task_id: The ID of the video generation task.
    :return: URL of video or None.
    """
    status = send_get_text2vid_task_request(task_id)
    if status and status.url != "":
        return status.url
    else: 
        return None
