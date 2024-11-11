import requests
from typing import List
from . import tools, DEFAULT_IMAGE_CONTENT
from . import log_manager


class ImageManager:
    """
    An image manager to download image(s) and apply watermarks if its neccesary.

    Attributes:
        WATERMARK_RESOURCE_ENDPOINT (str): The endpoint for the watermark resource.
        TIMEOUT (int): The timeout for the requests.
    Args:
        timeout (int, optional): The timeout for waiting in the responses for the watermark service.
        n_tries (int, optional): The number of tries to request the resource from the watermark service if an error ocurres.
        logger (Logger, optional): The logger to save log errors while downloading images.
        watermark_url (str, optional): The url of the watermark image.
    """

    WATERMARK_RESOURCE_ENDPOINT = 'https://quickchart.io/watermark'
    TIMEOUT = 10
    N_TRIES = 1

    def __init__(self, timeout: int = TIMEOUT, n_tries: int = N_TRIES, log_mng: log_manager.LogManager = None, watermark_url: str = None) -> None:
        self.TIMEOUT = timeout
        self.N_TRIES = n_tries
        self.log_mng = log_mng
        self.watermark_url = watermark_url

    def _download_image(self, img_url: str) -> bytes:
        """
        Downloads an image from a public url.

        Args:
            img_url (str): The public url of the image.
        Returns:
            bytes: The image content.
        """
        try:
            r = requests.get(img_url, timeout=self.TIMEOUT)

            if r.status_code == 200:
                return r.content

            msg = f'Error downloading the image. Status code: {r.status_code}. \
                URL: {img_url}'
            if self.log_mng:
                self.log_mng.log(msg)
            print(msg)
            return DEFAULT_IMAGE_CONTENT
        except Exception as e:
            msg = f'{e}. Could not download the image. URL: {img_url}'
            print(msg)
            if self.log_mng:
                self.log_mng.log(msg)
            return DEFAULT_IMAGE_CONTENT

    def _apply_watermark(self, img_url: str, trying: bool = False) -> bytes:
        """
        Downloads an image from a public url applying the watermark `self.watermark_url` to it. The resource from where the watermark is applied is Watermark.io.
        It returns a compressed image on success because the watermark service returns an image with a size increased.

        Args:
            img_url (str): The public url of the image.
            trying (bool, optional): If it's trying to apply the watermark again. Defaults to False.
        Returns:
            bytes: The image content with the watermark
        """

        # Preconfigured watermark settings
        json = {
            "mainImageUrl": img_url,
            "markImageUrl": self.watermark_url,
            "opacity": 1.0,
            "markRatio": 1.0,
            "position": "bottomMiddle",
            "positionX": 0.0,
            "positionY": 0.0
        }

        try:
            r = requests.post(self.WATERMARK_RESOURCE_ENDPOINT,
                              json=json, timeout=self.TIMEOUT)

            if r.status_code != 200:
                if not trying:
                    for i in range(self.N_TRIES):
                        img = self._apply_watermark(img_url, trying=True)
                        if img:
                            # Returns a compressed image
                            return tools.compress_img(img)

                msg = f'Error applying watermark to the image. Status code: {
                    r.status_code}. URL: {img_url}'
                if self.log_mng:
                    self.log_mng.log(msg)
                print(msg)
                return DEFAULT_IMAGE_CONTENT

            return tools.compress_img(r.content)

        except Exception as e:
            msg = f'{e}. Could not apply watermark to the image. URL: {img_url}'
            print(msg)
            if self.log_mng:
                self.log_mng.log(msg)
            return DEFAULT_IMAGE_CONTENT

    def download_image(self, img_url: str) -> bytes:
        """
        Download the image, returning the bytes of these. If a `self.watermark_url` exists, then it applies to the image.

        Args:
            img_url (str): The public url of the image.
        Returns:
            Optional[bytes]: The image content.
        """

        try:
            if self.watermark_url:
                img = self._apply_watermark(img_url)
            else:
                img = self._download_image(img_url)
        except Exception as e:
            print(f'Unexpected error downloading the image. {e}')

        return img

    def download_images(self, img_urls: List[str]) -> List[bytes]:
        """
        Download a list of images, returning the bytes of these. If `self.watermark_url` exists, then it applies to the images.

        Args:
            img_urls (List[str]): The public urls of the images.
        Returns:
            List[bytes]: A list of images content.
        """
        images = []
        for img_url in img_urls:
            img = self.download_image(img_url)
            images.append(img)

        return images
