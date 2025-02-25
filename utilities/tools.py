from PIL import Image
from io import BytesIO
from urllib.parse import quote


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


def replace_domain_url(url: str) -> str:
    """Replace the domain url from google cloud to firebase storage, because
    the domain url for firebase storage has permission to access the images.
    Ex:
    https://storage.googleapis.com/fotos-unidades-marca-agua/Kind%20Propiedades/edificio-nueva-cordova/local-105/fotos/nueva-cordova-local-105-01.jpg

    becomes:
    https://firebasestorage.googleapis.com/v0/b/duvify-brokers-fotos-unidades/o/Kind%2520Propiedades%2Fedificio-nueva-cordova%2Flocal-105%2Ffotos%2Fnueva-cordova-local-105-01.jpg

    Args:
        url (str): The url to replace the domain.

    Returns:
        str: The url with the domain replaced (using firebase).
    """

    url_parts = url.split('/')
    del url_parts[0:2]

    url_parts[1] = url_parts[1] + '/o/'

    uri = '/'.join(url_parts[2:])

    return 'https://firebasestorage.googleapis.com/v0/b/'+url_parts[1] + quote(uri, safe='%20') + '?alt=media'


def get_file_name_from_url(url: str) -> str:
    """Return the filename of the resource from a url. This function is used to get the name of the blueprint.
    Ex: https://firebasestorage.googleapis.com/v0/b/duvify-brokers-fotos-unidades/o/edificio-angular%2Flocal-7%2Fplanos%2Fangular-local-7-plano-ubicacion.jpg?alt=media

    returns 'angular-local-7-plano-ubicacion'

    Args:
        url (str): The url to extract the filename from.

    Returns:
        str: The filename extracted from the url.
    """
    url_parts = url.split('/')
    return url_parts[-1].split('?')[0].split("%2F")[-1]
