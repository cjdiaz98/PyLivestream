import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()

def format_prompt(reference_description, style_theme):
    """
    Formats a prompt to be used for generating a styled image.

    Args:
        reference_description (str): A description of the reference image being passed in.
        style_theme (str): A style, topic, or theme that the output image should match.

    Returns:
        str: A formatted prompt for the `prompt_generator` function.
    """
    # Construct the formatted prompt
    prompt = (
        f"Generate a detailed prompt for an AI art generator to create an image that matches "
        f"the following reference: {reference_description}. "
        f"The output image should reflect the style, topic, or theme of: {style_theme}. "
        f"Ensure the description includes details about composition, colors, and atmosphere "
        f"to match the style."
    )
    return prompt

def prompt_generator(instructions):
	"""
	Generates a prompt based on the provided instructions by calling an LLM.

	Args:
		instructions (str): Instructions for the type of prompt to generate.

	Returns:
		str: The generated prompt that matches the instructions.

	Raises:
		Exception: If the LLM call fails or returns an invalid response.
	"""
	try:
		# Get the OpenAI API key from environment variables
		api_key = os.getenv("OPENAI_API_KEY")
		print(api_key)
		if not api_key:
			raise ValueError("API key not found in environment variables. Make sure OPENAI_API_KEY is set in .env.")

		# Initialize the OpenAI client
		client = OpenAI(api_key=api_key)

		# Call the LLM to generate a matching prompt
		response = client.chat.completions.create(
			messages=[
				{
					"role": "system",
					"content": "You are a prompt crafting assistant. Generate prompts exactly as described in the user's instructions."
				},
				{
					"role": "user",
					"content": instructions
				}
			],
			model="gpt-4o",  # Use the specified model
		)

		# Extract the prompt from the LLM response
		prompt = response.choices[0].message.content.strip()

		if not prompt:
			raise ValueError("Failed to generate a prompt. The response is empty.")

		return prompt
	except Exception as e:
		raise Exception(f"Error generating prompt: {str(e)}")

def add_to_midjourney_prompt(prompt: str, ref_char_url: str = "", style_ref_urls: List[str] = [], is_anime: bool = False) -> str:
	if is_anime:
		prompt += " --niji 6"
	if ref_char_url != "":
		prompt += f" --cref {ref_char_url}"
	for style_url in style_ref_urls:
		prompt += f" --sref {style_url}"
	return prompt

# Example Usage
if __name__ == "__main__":
	INSTRUCTIONS = (
		"Generate a prompt to send to the MidJourney image generator. "
		"It'll trigger the generation of an image for a cool cat. "
		"The image should be in the following style: futuristic neon cyberpunk."
	)

	try:
		generated_prompt = prompt_generator(INSTRUCTIONS)
		print("Generated Prompt:", generated_prompt)
	except Exception as e:
		print("Error:", str(e))
