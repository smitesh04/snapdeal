import requests
from PIL import Image
from io import BytesIO


# Function to get image dimensions from a URL
def get_image_dimensions(url):
    # Send a GET request to fetch the image
    response = requests.get(url)

    # Raise an error if the image could not be downloaded
    if response.status_code != 200:
        raise Exception("Failed to fetch image from URL.")

    # Open the image using Pillow
    image = Image.open(BytesIO(response.content))

    # Get image dimensions (width, height)
    width, height = image.size

    return width, height


# Example usage
# image_url = 'https://example.com/image.jpg'  # Replace with your image URL
# width, height = get_image_dimensions(image_url)
# print(f"Image Dimensions: {width}x{height}")
