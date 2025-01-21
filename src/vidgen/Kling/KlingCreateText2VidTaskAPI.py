from enum import Enum
from typing import Optional, List

class ServiceMode(Enum):
    """This field allows for more flexible switching between HYA and PAYG.
    - `public`->`Pay As You Go(PAYG)`
    - `private`->`Host Your Account(HYA)`
    """
    PRIVATE = "private"
    PUBLIC = "public"


class WebhookConfig:
    endpoint: str
    secret: str

    def __init__(self, endpoint: str, secret: str) -> None:
        self.endpoint = endpoint
        self.secret = secret


class KlingCreateTaskAPIConfig:
    """This field allows for more flexible switching between HYA and PAYG.
    - `public`->`Pay As You Go(PAYG)`
    - `private`->`Host Your Account(HYA)`
    """
    service_mode: Optional[ServiceMode]
    webhook_config: Optional[WebhookConfig]

    def __init__(self, service_mode: Optional[ServiceMode], webhook_config: Optional[WebhookConfig]) -> None:
        self.service_mode = service_mode
        self.webhook_config = webhook_config


class AspectRatio(Enum):
    """only required in text-to-video task"""
    THE_11 = "1:1"
    THE_169 = "16:9"
    THE_916 = "9:16"


class CameraControlConfig:
    horizontal: int
    pan: int
    roll: int
    tilt: int
    vertical: int
    zoom: int

    def __init__(self, horizontal: int, pan: int, roll: int, tilt: int, vertical: int, zoom: int) -> None:
        self.horizontal = horizontal
        self.pan = pan
        self.roll = roll
        self.tilt = tilt
        self.vertical = vertical
        self.zoom = zoom


class CameraControl:
    config: CameraControlConfig
    type: str

    def __init__(self, config: CameraControlConfig, type: str) -> None:
        self.config = config
        self.type = type


class Mode(Enum):
    PRO = "pro"
    STD = "std"


class Point:
    """positive value stands for right direction, and left_top of the image is (0,0)"""
    x: float
    """positive value stands for down direction, and left_top of the image is (0,0)"""
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class ControlPoints:
    """Up to 6 motion lines suggesting the motion direction of corresponding areas
    
    Control Points
    """
    """a series of bazier curve control point"""
    points: Optional[List[Point]]

    def __init__(self, points: Optional[List[Point]]) -> None:
        self.points = points


class MotionBrush:
    """It's highly recommended that you read our example doc before acutally use motion brush
    
    motion brush, It's highly recommended that you read our example doc before acutally use
    motion brush
    """
    dynamic_masks: Optional[List[ControlPoints]]
    """the mask image contains all mask areas, image should be exact same pixel size with the
    `image_url`. mask image can only be png with all pixcel's alpha channel set to zero. For
    more details please check our motion brush doc
    """
    mask_url: Optional[str]
    """you should always leave static mask to [{"points": []}]"""
    static_masks: Optional[List[ControlPoints]]

    def __init__(self, dynamic_masks: Optional[List[ControlPoints]], mask_url: Optional[str], static_masks: Optional[List[ControlPoints]]) -> None:
        self.dynamic_masks = dynamic_masks
        self.mask_url = mask_url
        self.static_masks = static_masks


class Version(Enum):
    """the model version"""
    THE_10 = "1.0"
    THE_15 = "1.5"
    THE_16 = "1.6"


class Input:
    """the input param of the kling task, depends on the `task_type` .refer to the example for
    more details.
    """
    """only required in text-to-video task"""
    aspect_ratio: Optional[AspectRatio]
    camera_control: Optional[CameraControl]
    """float between 0 and 1"""
    cfg_scale: Optional[str]
    duration: Optional[int]
    """End frame of the video. No larger than 10MB, and each side must be greater than 300
    pixels.Need to be used with `image_url`.
    """
    image_tail_url: Optional[str]
    """Only required in image-to-video task. Initial frame of the video.No larger than 10MB, and
    each side must be greater than 300 pixels.
    """
    image_url: Optional[str]
    """Use your audio file for lip_sync through this parameter. All tts related param will be
    ignored if this is set. Audio format:`mp3``wav``flac``ogg`, should be less than 20 MB and
    shorter than 60 seconds. After the audio is submitted, we will trim it to the exact
    length of the original video.
    """
    local_dubbing_url: Optional[str]
    mode: Optional[Mode]
    """It's highly recommended that you read our example doc before acutally use motion brush"""
    motion_brush: Optional[MotionBrush]
    negative_prompt: Optional[str]
    """The task_id of the video to extend or lip_sync."""
    origin_task_id: Optional[str]
    prompt: Optional[str]
    """The speed of the lip_sync speech, used in `lip_sync` task with valid `tts_text`only."""
    tts_speed: Optional[float]
    """The text that you want to lipsync in the video, used in `lip_sync` task only; will be
    ignored if `local_dubbing_url` is set
    """
    tts_text: Optional[str]
    """The voice that you want to use in `lip_sync` task with valid `ttx_text`, the full voice
    name list and demo list here: https://klingai.com/api/lip/sync/ttsList?type=
    """
    tts_timbre: Optional[str]
    """the model version"""
    version: Optional[Version]

    def __init__(self, aspect_ratio: Optional[AspectRatio], camera_control: Optional[CameraControl], cfg_scale: Optional[str], duration: Optional[int], image_tail_url: Optional[str], image_url: Optional[str], local_dubbing_url: Optional[str], mode: Optional[Mode], motion_brush: Optional[MotionBrush], negative_prompt: Optional[str], origin_task_id: Optional[str], prompt: Optional[str], tts_speed: Optional[float], tts_text: Optional[str], tts_timbre: Optional[str], version: Optional[Version]) -> None:
        self.aspect_ratio = aspect_ratio
        self.camera_control = camera_control
        self.cfg_scale = cfg_scale
        self.duration = duration
        self.image_tail_url = image_tail_url
        self.image_url = image_url
        self.local_dubbing_url = local_dubbing_url
        self.mode = mode
        self.motion_brush = motion_brush
        self.negative_prompt = negative_prompt
        self.origin_task_id = origin_task_id
        self.prompt = prompt
        self.tts_speed = tts_speed
        self.tts_text = tts_text
        self.tts_timbre = tts_timbre
        self.version = version


class Model(Enum):
    """the model name"""
    KLING = "kling"


class TaskType(Enum):
    """type of the task. If you want to extend video,set to `extend_video` and include
    `origin_task_id` filed in `input`; if you want lipsync, use `lip_sync` and include
    `origin_task_id` in `input`
    """
    EXTEND_VIDEO = "extend_video"
    LIP_SYNC = "lip_sync"
    VIDEO_GENERATION = "video_generation"


class KlingCreateTaskAPI:
    config: Optional[KlingCreateTaskAPIConfig]
    """the input param of the kling task, depends on the `task_type` .refer to the example for
    more details.
    """
    input: Input
    """the model name"""
    model: Model
    """type of the task. If you want to extend video,set to `extend_video` and include
    `origin_task_id` filed in `input`; if you want lipsync, use `lip_sync` and include
    `origin_task_id` in `input`
    """
    task_type: TaskType

    def __init__(self, config: Optional[KlingCreateTaskAPIConfig], input: Input, model: Model, task_type: TaskType) -> None:
        self.config = config
        self.input = input
        self.model = model
        self.task_type = task_type

import json
import requests
from typing import Optional

# Helper function to create the JSON payload from the classes
def create_task_request():
    # Configure the webhook
    webhook_config = WebhookConfig(endpoint="", secret="")
    api_config = KlingCreateTaskAPIConfig(
        service_mode=ServiceMode.PUBLIC,  # Replace with `ServiceMode.PRIVATE` if needed
        webhook_config=webhook_config
    )

    # Configure the camera control
    camera_control_config = CameraControlConfig(
        horizontal=0,
        pan=-10,
        roll=0,
        tilt=0,
        vertical=0,
        zoom=0
    )
    camera_control = CameraControl(
        config=camera_control_config,
        type="simple"
    )

    # Create the input object
    task_input = Input(
        aspect_ratio=AspectRatio.THE_11,
        camera_control=camera_control,
        cfg_scale="0.5",
        duration=5,
        image_tail_url=None,
        image_url=None,
        local_dubbing_url=None,
        mode=Mode.STD,
        motion_brush=None,
        negative_prompt="",
        origin_task_id=None,
        prompt="White egrets fly over the vast paddy fields",
        tts_speed=None,
        tts_text=None,
        tts_timbre=None,
        version=None
    )

    # Build the full request
    task_request = KlingCreateTaskAPI(
        config=api_config,
        input=task_input,
        model=Model.KLING,
        task_type=TaskType.VIDEO_GENERATION
    )

    # Convert to JSON payload
    payload = {
        "model": task_request.model.value,
        "task_type": task_request.task_type.value,
        "input": {
            "prompt": task_request.input.prompt,
            "negative_prompt": task_request.input.negative_prompt,
            "cfg_scale": task_request.input.cfg_scale,
            "duration": task_request.input.duration,
            "aspect_ratio": task_request.input.aspect_ratio.value,
            "camera_control": {
                "type": task_request.input.camera_control.type,
                "config": {
                    "horizontal": task_request.input.camera_control.config.horizontal,
                    "vertical": task_request.input.camera_control.config.vertical,
                    "pan": task_request.input.camera_control.config.pan,
                    "tilt": task_request.input.camera_control.config.tilt,
                    "roll": task_request.input.camera_control.config.roll,
                    "zoom": task_request.input.camera_control.config.zoom
                }
            },
            "mode": task_request.input.mode.value
        },
        "config": {
            "service_mode": task_request.config.service_mode.value if task_request.config.service_mode else "",
            "webhook_config": {
                "endpoint": task_request.config.webhook_config.endpoint,
                "secret": task_request.config.webhook_config.secret
            }
        }
    }

    return payload

from KlingAuth import get_api_token

# Send the request
def send_task_request():
    API_URL = "https://api.klingai.com/v1/videos/text2video"

    # Create the payload
    payload = create_task_request()
    api_key = get_api_token()
    # Set headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }

    # Send the POST request
    print(payload)
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        print("Task created successfully!")
        print("Response:", response.json())
    else:
        print("Failed to create task. Status Code:", response.status_code)
        print("Error:", response.text)


# Call the function to send the request
send_task_request()
