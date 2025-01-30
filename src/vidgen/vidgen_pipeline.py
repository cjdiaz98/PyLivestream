"""
Inputs:
List of character ref photos - length n
Topic for generated photos

Outputs:
n videos generated from photos

STEPS:
Given the topic, generate good prompts for the images to be generated. 
(optional) hone the prompts specifically for the image generation task:
	https://github.com/jordip/prompt-generator-api

Submit ideas for photo generation, with inspiration photos

Wait for photos to be generated

Once photos are generated, generate good prompts for a video to be generated from the photos

Submit ideas for video generation, with generated photos

Wait for videos to be generated. Compile the links to the videos and put them in a file.
"""
from ImageGen.midjourney import imagine_task, get_task, extract_task_id, extract_image_url, describe_image, extract_description, extract_status
from ImageGen.split_image import split_image_from_url
from PromptGenerator import add_to_midjourney_prompt, prompt_generator
import time
from typing import List
from dotenv import load_dotenv
import os
from Kling.KlingImageToVideo import generate_video_from_image, get_task_id
from Kling.KlingGetTaskAPI import send_get_image2vid_task_request, process_kling_tasks

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("MIDJOURNEY_API_KEY")

def process_tasks(api_key, task_ids, success_callback, timeout=300):
	"""
	Processes a list of tasks by polling their status until all succeed, fail, or a timeout occurs.

	Args:
		task_ids (list): A list of task IDs to process.
		success_callback (function): A callback function for successful responses, takes a dictionary and returns a string.
		timeout (int): Maximum time in seconds to wait before timing out (default: 300 seconds).

	Returns:
		dict: A dictionary mapping task IDs to their results for successful tasks.
	
	Raises:
		TimeoutError: If the timeout limit is reached before tasks are fully processed.
	"""
	start_time = time.time()
	results = {}

	while task_ids:
		new_task_ids = []

		# Get the status of the tasks
		for task_id in task_ids:
			task = get_task(api_key, task_id)  # Assume `get_task` fetches the task details
			if extract_status(task) == "completed":
				# Use the success callback to process the task
				results[task_id] = success_callback(task)
			elif extract_status(task) != "failed":
				# Keep pending tasks for further polling
				new_task_ids.append(task_id)
			else:
				print("Failed Task:", task)

		# Update the list of pending tasks
		task_ids = new_task_ids

		# Check timeout
		if time.time() - start_time > timeout:
			raise TimeoutError("Timeout limit reached before all tasks were processed.")

		# Sleep to avoid hitting API rate limits
		if task_ids:
			time.sleep(10)

	return results

char_ref_urls = ["https://www.kyokovinyl.com/cdn/shop/products/YorFORGERFinish_1080x.png"]
style_ref_urls = ["https://cdn.midjourney.com/99dab670-22a5-478c-808c-31c1aa52fb41/0_2.png"]
topic = "futuristic neon cyberpunk"

# Generate prompts for the images
prompt = "a beautiful, confident pirate in a combat stance on the deck of a ship on the night of a full moon. She has thin daggers in her hands and is poised to attack. Anime, vibrant colors"

# Submit image generation tasks
print("Submitting image generation tasks...")
imagine_responses = [imagine_task(API_KEY, prompt=add_to_midjourney_prompt(prompt, ref_char_url=c_ref, style_ref_urls=style_ref_urls)) for c_ref in char_ref_urls]
imagine_task_ids = list(filter(lambda x: x is not None, map(lambda x: extract_task_id(x), imagine_responses)))
print("Imagine task IDs:", imagine_task_ids)

imagine_result_urls = process_tasks(API_KEY, imagine_task_ids, extract_image_url).values()
print("Imagine result URLs:", imagine_result_urls)

# Get photos
print("Getting photos...")
photo_paths = []
pic_no = 1
for url in imagine_result_urls:
	photos = split_image_from_url(url, "pic" + str(pic_no))
	photo_paths.extend(photos)
	pic_no+=1

print("Photo paths:", photo_paths)

from ImageGen.image_hosting import run_flask, start_ngrok
import threading

# Temporarily run a server for image hosting
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Start ngrok in the main thread and get the public URL
ngrok_tunnel = start_ngrok()
public_url = ngrok_tunnel.public_url

# Describe photos
print("Describing photos...")

task_ids_to_paths = {}
for photo_path in photo_paths:
	public_photo_url = public_url + "/" + photo_path
	describe_result = describe_image(API_KEY, public_photo_url)
	describe_task_id = extract_task_id(describe_result)

	if describe_task_id:
		task_ids_to_paths[describe_task_id] = photo_path

describe_task_ids = list(task_ids_to_paths.keys())
print("Describe task IDs:", describe_task_ids)
description_mapping = process_tasks(API_KEY, describe_task_ids, extract_description)
descriptions = description_mapping.values()
print("Descriptions:", descriptions)

# Submit video generation task
VIDEO_INSTRUCTIONS = (
	"Generate a prompt to send to the Hailuo image to video generator. "
	"It'll trigger the generation of a video for following image: "
	"{image_description}. "
	"The generated video will be relatively short (5 seconds) and should be cool, interesting, weird and/or funny--just overall entertaining."
)

import itertools
video_gen_task_ids = []
for describe_task_id in list(itertools.islice(description_mapping.keys(), 1)): # just look at first one for now
	description = description_mapping[describe_task_id]
	photo_path = task_ids_to_paths[describe_task_id]
	public_photo_url = public_url + "/" + photo_path

	video_prompt = prompt_generator(VIDEO_INSTRUCTIONS.format(image_description=description))
	print("Video prompt:", video_prompt)
	video_task_response = generate_video_from_image(public_photo_url, prompt=video_prompt)
	task_id = get_task_id(video_task_response)
	if task_id and task_id != "":
		video_gen_task_ids.append(task_id)

# Wait for video generation
vidgen_results = process_kling_tasks(send_get_image2vid_task_request, video_gen_task_ids, 600)
print(vidgen_results)