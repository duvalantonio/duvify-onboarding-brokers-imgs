import os

# Constants initialization
current_dir = os.path.dirname(os.path.abspath(__file__))
default_image_path = os.path.join(current_dir, 'default.jpg')

with open(default_image_path, 'rb') as f:
    DEFAULT_IMAGE_CONTENT = f.read()
