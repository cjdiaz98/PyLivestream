import os
import time
import requests
import json
from io import BytesIO

from dotenv import load_dotenv

load_dotenv('../../.env')

api_key = os.getenv("HAILUO_API_KEY")
if not api_key:
    raise EnvironmentError("HAILUO_API_KEY environment variable is not set.")

prompt = "an anime style gorilla pounding on his chest and sending shockwaves as a result"
model = "video-01" 
output_file_name = "output.mp4" 

def invoke_video_generation()->str | None:
    print("-----------------Submit video generation task-----------------")
    url = "https://api.minimaxi.chat/v1/video_generation"
    payload = json.dumps({
      "prompt": prompt,
      "model": model
    })
    headers = {
      'authorization': 'Bearer ' + api_key,
      'content-type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    task_id = response.json()['task_id']

    if task_id == "":
        print("Video generation task failed")
        return None

    print("Video generation task submitted successfully, task ID.："+task_id)
    return task_id

def query_video_generation(task_id: str):
    if not task_id:
        return "", "Fail"
        
    url = "https://api.minimaxi.chat/v1/query/video_generation?task_id="+task_id
    headers = {
      'authorization': 'Bearer ' + api_key
    }
    response = requests.request("GET", url, headers=headers)
    status = response.json()['status']
    if status == 'Queueing':
        print("...In the queue...")
        return "", 'Queueing'
    elif status == 'Processing':
        print("...Generating...")
        return "", 'Processing'
    elif status == 'Success':
        return response.json()['file_id'], "Finished"
    elif status == 'Fail':
        return "", "Fail"
    else:
        return "", "Unknown"

def fetch_video_and_save_to_file(file_id: str) -> None:
    print("---------------Video generated successfully, downloading now---------------")
    url = "https://api.minimaxi.chat/v1/files/retrieve?file_id="+file_id
    headers = {
        'authorization': 'Bearer '+api_key,
    }

    response = requests.request("GET", url, headers=headers)
    print(response.text)

    download_url = response.json()['file']['download_url']
    print("Video download link：" + download_url)
    with open(output_file_name, 'wb') as f:
        f.write(requests.get(download_url).content)
    print("THe video has been downloaded in："+os.getcwd()+'/'+output_file_name)

def fetch_video_result(file_id: str) -> BytesIO:
    """
    Fetches a video from the API and stores its content in memory as a BytesIO object.

    :param file_id: The file ID of the video to fetch.
    :return: A BytesIO object containing the video content.
    """
    print("---------------Video generated successfully, downloading now---------------")
    url = f"https://api.minimaxi.chat/v1/files/retrieve?file_id={file_id}"
    headers = {
        'authorization': f'Bearer {api_key}',
    }

    # Step 1: Fetch file metadata
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    download_url = response.json()['file']['download_url']
    print("Video download link：" + download_url)

    # Step 2: Download file content into memory
    video_content = requests.get(download_url).content
    video_in_memory = BytesIO(video_content)
    print("The video has been downloaded and stored in memory.")

    # Step 3: Return video as a BytesIO object
    return video_in_memory

# to do: create a data structure that'll hold the bytes for each video. 
# We flush this every once and awhile and will check for each video on that list whether it received enough upvotes to save (to tell us whether it was garbo or not)
# we can have chatbot keep track of votes. We can save the file as well as metadata about its reception.

if __name__ == '__main__':
    task_id = invoke_video_generation()
    print("-----------------Video generation task submitted -----------------")
    while True:
        time.sleep(10)

        file_id, status = query_video_generation(task_id)
        if file_id != "":
            fetch_video_and_save_to_file(file_id)
            print("---------------Successful---------------")
            break
        elif status == "Fail" or status == "Unknown":
            print("---------------Failed---------------")
            break