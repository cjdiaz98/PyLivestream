import http.client
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def imagine_task(api_key, prompt, aspect_ratio="16:9", process_mode="fast", skip_prompt_check=False, bot_id=0):
	"""
	Function to send an imagine task to the MidJourney API.
	"""
	conn = http.client.HTTPSConnection("api.goapi.ai")
	payload = json.dumps({
		"model": "midjourney",
		"task_type": "imagine",
		"input": {
			"prompt": prompt,
			"aspect_ratio": aspect_ratio,
			"process_mode": process_mode,
			"skip_prompt_check": skip_prompt_check,
			"bot_id": bot_id
		},
		"config": {
			"service_mode": "",
			"webhook_config": {
				"endpoint": "",
				"secret": ""
			}
		}
	})
	headers = {
		'x-api-key': api_key,
		'Content-Type': 'application/json'
	}
	conn.request("POST", "/api/v1/task", payload, headers)
	res = conn.getresponse()
	data = res.read()
	conn.close()
	return json.loads(data.decode("utf-8"))

def get_task(api_key, task_id=""):
	"""
	Function to retrieve the status or result of a task from the MidJourney API.
	If no task_id is specified, it retrieves all tasks.
	"""

	conn = http.client.HTTPSConnection("api.goapi.ai")
	url = f"/api/v1/task/{task_id}" if task_id else "/api/v1/task/"
	headers = {
		'x-api-key': api_key
	}
	conn.request("GET", url, headers=headers)
	res = conn.getresponse()
	data = res.read()
	conn.close()
	return json.loads(data.decode("utf-8"))

def describe_image(api_key, image_url):
	"""
	Sends an image description task to the MidJourney API and retrieves the response.

	Args:
		api_key (str): Your API key for the MidJourney API.
		image_url (str): The URL of the image to be described.

	Returns:
		dict: The API response as a dictionary.
	"""
	# Set up the connection
	conn = http.client.HTTPSConnection("api.goapi.ai")

	# Payload for the API request
	payload = json.dumps({
		"model": "midjourney",
		"task_type": "describe",
		"input": {
			"image_url": image_url,
			"process_mode": "fast",
			"bot_id": 0
		},
		"config": {
			"service_mode": "",
			"webhook_config": {
				"endpoint": "",
				"secret": ""
			}
		}
	})

	# Set headers with the API key
	headers = {
		'X-API-Key': api_key,
		'Content-Type': 'application/json'
	}

	# Send the POST request
	conn.request("POST", "/api/v1/task", payload, headers)

	# Get the response
	res = conn.getresponse()
	data = res.read()
	conn.close()

	# Return the response as a dictionary
	return json.loads(data.decode("utf-8"))

def extract_status(response):
    """
    Extracts the status from the given response dictionary.

    Args:
        response (dict): The API response dictionary.

    Returns:
        str: The extracted status.

    Raises:
        ValueError: If the response does not contain a valid status.
    """
    try:
        # Navigate to the status in the response
        status = response.get("data", {}).get("status", "")
        if not status:
            raise ValueError("Status not found in the response.")
        return status
    except AttributeError as e:
        raise ValueError("Invalid response format.") from e

def extract_task_id(response):
	"""
	Extracts the task ID from a MidJourney API response.

	Args:
		response (dict): The API response as a dictionary.

	Returns:
		str: The extracted task ID.

	Raises:
		ValueError: If the response does not contain a valid task ID.
	"""
	try:
		# Attempt to extract the task ID
		task_id = response.get("data", {}).get("task_id", "")
		if not task_id:
			raise ValueError("Task ID not found in the response.")
		return task_id
	except AttributeError as e:
		raise ValueError("Invalid response format.") from e

def extract_image_url(response):
	"""
	Extracts the image URL from the given response dictionary.

	Args:
		response (dict): The API response dictionary.

	Returns:
		str: The extracted image URL.

	Raises:
		ValueError: If the response does not contain a valid image URL.
	"""
	try:
		# Navigate to the image URL in the response
		image_url = response.get("data", {}).get("output", {}).get("image_url", "")
		if not image_url:
			raise ValueError("Image URL not found in the response.")
		return image_url
	except AttributeError as e:
		raise ValueError("Invalid response format.") from e

def extract_description(response):
	"""
	Extracts the description from the given response dictionary.

	Args:
		response (dict): The API response dictionary.

	Returns:
		str: The extracted description.

	Raises:
		ValueError: If the response does not contain a valid description.
	"""
	try:
		# Navigate to the description in the response
		description = response.get("data", {}).get("output", {}).get("description", "")
		if not description:
			raise ValueError("Description not found in the response.")
		return description
	except AttributeError as e:
		raise ValueError("Invalid response format.") from e

from ImageGen.split_image import split_image_from_url
# Example usage
if __name__ == "__main__":
	API_KEY = os.getenv("MIDJOURNEY_API_KEY")
	
	# Sending an imagine task
	# response = imagine_task(api_key=API_KEY, prompt="flying night city")
	# print("Imagine Task Response:", response)
	# task_id = response.get("data", {}).get("task_id", "")
	
	task_id ="619660ba-be0e-40e9-b5bf-35d9c36dab69"
	# Retrieving all tasks
	# tasks_response = get_task(API_KEY, task_id)
	# print("Get Task Response:", tasks_response)

	# split_image_from_url("https://img.theapi.app/mj/619660ba-be0e-40e9-b5bf-35d9c36dab69.png", "output_image")
	IMAGE_URL = "https://img.theapi.app/mj/619660ba-be0e-40e9-b5bf-35d9c36dab69.png"
	# response = describe_image(API_KEY, IMAGE_URL)
	# describe_task_id = extract_task_id(response)

	describe_task_id = "661efe40-5a55-4a77-9b2a-5f1857792f02"

	describe_response = get_task(API_KEY, describe_task_id)
	print("Describe Image Response:", describe_response)
