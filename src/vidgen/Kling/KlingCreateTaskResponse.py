from typing import Optional, Dict, Any, List
from enum import Enum
from KlingGetTaskAPI import Error, Meta, Usage, Status

class Data:
    detail: None
    error: Error
    input: Dict[str, Any]
    logs: List[Dict[str, Any]]
    meta: Meta
    model: str
    output: Dict[str, Any]
    """Hover on the "Completed" option and you coult see the explaintion of all status:
    completed/processing/pending/failed/staged
    """
    status: Status
    task_id: str
    task_type: str

    def __init__(self, detail: None, error: Error, input: Dict[str, Any], logs: List[Dict[str, Any]], meta: Meta, model: str, output: Dict[str, Any], status: Status, task_id: str, task_type: str) -> None:
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

class KlingCreateTaskResponse:
    code: int
    data: Data
    """If you get non-null error message, here are some steps you chould follow:
    - Check our [common error
    message](https://climbing-adapter-afb.notion.site/Common-Error-Messages-6d108f5a8f644238b05ca50d47bbb0f4)
    - Retry for several times
    - If you have retried for more than 3 times and still not work, file a ticket on Discord
    and our support will be with you soon.
    """
    message: str

    def __init__(self, code: int, data: Data, message: str) -> None:
        self.code = code
        self.data = data
        self.message = message


import json
from typing import Optional, List

def parse_response(api_response: str) -> KlingCreateTaskResponse:
    # Parse the JSON response into a Python dictionary
    response_dict = json.loads(api_response)

    # Parse the `error` object
    error_data = response_dict['data']['error']
    error = Error(
        code=error_data.get('code'),
        message=error_data.get('message')
    )

    # Parse the `meta` object
    meta_data = response_dict['data'].get('meta', {})
    usage_data = meta_data.get('usage', {})
    usage = Usage(
        consume=usage_data.get('consume', 0.0),
        frozen=usage_data.get('frozen', 0.0),
        type=usage_data.get('type', '')
    )
    meta = Meta(
        created_at=meta_data.get('created_at'),
        ended_at=meta_data.get('ended_at'),
        is_using_private_pool=meta_data.get('is_using_private_pool', False),
        started_at=meta_data.get('started_at'),
        usage=usage
    )

    # Parse the `output` object
    output_data = response_dict['data']['output']

    # Create the `Data` object
    data = Data(
        detail=response_dict['data'].get('detail'),
        error=error,
        input=response_dict['data']['input'],
        logs=response_dict['data']['logs'],
        meta=meta,
        model=response_dict['data']['model'],
        output=output_data,
        status=Status(response_dict['data']['status'].capitalize()),  # Convert status to Enum
        task_id=response_dict['data']['task_id'],
        task_type=response_dict['data']['task_type']
    )

    # Create and return the `KlingCreateTaskResponse` object
    return KlingCreateTaskResponse(
        code=response_dict['code'],
        data=data,
        message=response_dict['message']
    )

api_response = '''
{
    "code": 200,
    "data": {
        "task_id": "6e269e8c-2091-46c4-b4a5-40a4704a766a",
        "model": "kling",
        "task_type": "video_generation",
        "status": "pending",
        "config": {
            "service_mode": "public",
            "webhook_config": {
                "endpoint": "",
                "secret": ""
            }
        },
        "input": {},
        "output": {
            "video_url": ""
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

# Example usage
parsed_response = parse_response(api_response)

# Access parsed fields
print(f"Task ID: {parsed_response.data.task_id}")
print(f"Status: {parsed_response.data.status}")
print(f"Model: {parsed_response.data.model}")
print(f"Output Video URL: {parsed_response.data.output.get('video_url', 'N/A')}")
