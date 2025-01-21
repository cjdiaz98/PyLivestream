from runwayml import RunwayML
import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

api_key=os.environ.get("RUNWAYML_API_SECRET")
print(api_key)
client = RunwayML()

task = client.image_to_video.create(
  model='gen3a_turbo',
  prompt_image='https://example.com/assets/bunny.jpg',
  prompt_text='The bunny is eating a carrot',
)
print(task.id)