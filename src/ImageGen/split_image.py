import requests
from PIL import Image
from io import BytesIO
from typing import List

def split_image_from_url(image_url, output_prefix: str, output_dir: str = "out") -> List[str]:
    """
    Downloads an image from a URL, splits it into four equal parts (2x2 grid),
    and saves the parts as separate files.

    Args:
        image_url (str): URL of the image to be split.
        output_prefix (str): Prefix for the output file names.

    Returns:
        list: List of output file paths.
    """
    # Download the image from the URL
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")
    
    image = Image.open(BytesIO(response.content))

    # Get dimensions of the image
    width, height = image.size

    # Calculate dimensions of each split
    split_width = width // 2
    split_height = height // 2

    # Crop the image into four parts
    split_images = [
        image.crop((0, 0, split_width, split_height)),  # Top-left
        image.crop((split_width, 0, width, split_height)),  # Top-right
        image.crop((0, split_height, split_width, height)),  # Bottom-left
        image.crop((split_width, split_height, width, height)),  # Bottom-right
    ]

    # Save the cropped images
    output_paths = []
    for idx, img in enumerate(split_images, start=1):
        output_path = f"{output_prefix}_split_{idx}.png"
        img.save(output_dir + "\\" + output_path)
        output_paths.append(output_path)

    return output_paths

# Example usage
if __name__ == "__main__":
    image_url = "https://img.theapi.app/mj/619660ba-be0e-40e9-b5bf-35d9c36dab69.png"
    output_prefix = "output_image"

    try:
        result_paths = split_image_from_url(image_url, output_prefix)
        print("Split images saved at:")
        for path in result_paths:
            print(path)
    except Exception as e:
        print("Error:", str(e))
