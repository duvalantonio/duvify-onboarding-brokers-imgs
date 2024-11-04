from PIL import Image
from io import BytesIO


def format_name(name: str) -> str:
    """
    Format a string converting tildes to their corresponding letter without tilde and lowercasing the string.
    Args:
        name (str): The string to be formatted.
    Returns:
        str: The formatted string.
    """
    tildes_map = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N'
    }
    formatted_name = ''.join(tildes_map.get(char, char) for char in name)

    return formatted_name.lower()


def compress_img(img: bytes, quality: int = 20) -> bytes:
    """
    Compress an image to a certain quality

    Args:
        img (bytes): The image to compress
        quality (int, optional): The quality of the compressed image

    Returns:
        bytes: The compressed image
    """

    image = Image.open(BytesIO(img))

    # Convert the image to RGB mode if it has an alpha channel or is in a different mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    try:
        # Compress the image and save to a BytesIO object
        output_buffer = BytesIO()
        # Adjust quality as needed (0-100)
        image.save(output_buffer, "JPEG", quality=quality)

        # Get the bytes of the compressed image
        compressed_image_bytes = output_buffer.getvalue()
    except Exception as e:
        print(f'(compress_img) Error compressing image. {e}')

    return compressed_image_bytes
