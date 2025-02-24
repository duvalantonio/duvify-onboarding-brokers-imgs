from google.cloud import storage
import os
import re
import concurrent.futures
from typing import Dict, List
from . import image_manager
from google.oauth2 import service_account
from google.cloud.storage.blob import Blob
import urllib


class FirebaseUploaderManager:
    """
    A class to handle Firebase operations.
    - Download images from Firebase Storage.
    - Upload images to Firebase Storage.

    Args:
        download_bucket_id (str): The id of the bucket to download images.
        upload_bucket_id (str): The id of the bucket to upload images.
        cred_fb_sdk (str): The path to the Firebase SDK credentials.
        img_mng (image_manager.ImageManager): An instance of ImageManager to process the images.
    """

    def __init__(self, download_bucket_id: str, upload_bucket_id: str,  cred_fb_path: str, img_mng: image_manager.ImageManager) -> None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_fb_path
        credentials = service_account.Credentials.from_service_account_file(
            cred_fb_path)
        self.client = storage.Client(credentials=credentials)
        self.download_bucket = self.client.bucket(download_bucket_id)
        self.upload_bucket = self.client.bucket(upload_bucket_id)
        self.img_mng = img_mng

    def _upload_img(self, blob_name: str, img: bytes) -> str:
        """
        Upload an image to Firebase Storage in `self.upload_bucket` bucket.

        Args:
            blob_name (str): The name of the blob.
            img (bytes): The image to upload.
        Returns:
            str: The public url of the blob.
        """
        blob = self.upload_bucket.blob(blob_name)
        try:
            blob.upload_from_string(img, content_type='image/jpeg')
        except Exception as e:
            print(f'Error uploading image: {e}')
            return ''

        # blob.make_public()
        return blob.public_url

    def get_all_imgs_public_urls(self) -> Dict[str, List[str]]:
        """
        Get all public urls for images in the bucket: `self.download_bucket`, grouped by folder.
        The dictionary has the format:
        {
            'folder_path_1': ['url1', 'url2', ...],
            'folder_path_2': ['url3', 'url4', ...],
            ...
        }

        Ex:
        {"edificio-parque-andino/local-3/fotos/parque-andino-local-3":
            ["https://firebasestorage.googleapis.com/v0/b/..."],}

        It has this format so when uploading the images, we can name the files with the same name as the original,
        indexing them by the position in the list.

        Returns:
            Dict[str, List[str]]: A dictionary with the public urls of the blobs.
        """

        blobs = self.download_bucket.list_blobs()
        folders = {}
        for blob in blobs:
            if blob.name.endswith('/') or '.DS_Store' in blob.name or '0.-antecedentes' in blob.name.lower() or '/' not in blob.name or 'fotos/' not in blob.name:
                # Ignore all type of files that are not images
                continue

            # Remove the indexing
            filename = re.sub(r'\d{2}\.jpg$', '', blob.name)

            if filename not in folders:
                folders[filename] = []

            public_url = f"https://firebasestorage.googleapis.com/v0/b/" +\
                f"{self.download_bucket.name}/o/{urllib.parse.quote(blob.name, safe='')}?alt=media"

            # folders[filename].append(blob.public_url)
            folders[filename].append(public_url)
        return folders

    def get_all_blueprint_imgs_public_urls(self) -> Dict[str, List[str]]:
        """
        Get all public urls for blueprint images in the bucket: `self.download_bucket`, grouped by folder.
        The dictionary has the format:
        {
            'folder_path_1': ['url1', 'url2', ...],
            'folder_path_2': ['url3', 'url4', ...],
            ...
        }

        Ex:
        {"edificio-parque-andino/local-3/planos":
            ["https://firebasestorage.googleapis.com/v0/b/..."],}

        It has this format so when uploading the blueprint images, we can name the files with the same name as the original,
        indexing them by the position in the list.

        Returns:
            Dict[str, List[str]]: A dictionary where the key is the folder path to folder planos and the value is a list of public urls.
        """

        blobs = self.download_bucket.list_blobs()
        paths = {}
        for blob in blobs:
            if '.DS_Store' in blob.name or 'planos/' not in blob.name:
                # Ignore all type of files that are not images
                continue

            path_to_blueprint: str = blob.name
            path_to_blueprint = "/".join(path_to_blueprint.split('/')[:-1])
            if path_to_blueprint not in paths:
                paths[path_to_blueprint] = []

            public_url = f"https://firebasestorage.googleapis.com/v0/b/" +\
                f"{self.download_bucket.name}/o/{urllib.parse.quote(blob.name, safe='')}?alt=media"

            paths[path_to_blueprint].append(public_url)

        return paths

    def _background_imgs_process(self, blob_name: str, public_imgs_url: List[str]) -> str:
        """
        Process a list of images by downloading them from bucket `self.download_bucket`, and
        applying a watermark for then uploading them to `self.upload_bucket`.
        This method is used as handler for the concurrent processing of images.

        Args:
            blob_name (str): The blob name for upload in to the bucket.
            imgs (List[str]): The list of images to apply watermark and upload.
        Returns:
            str: The folder where the images were uploaded.
        """
        watermark_imgs = self.img_mng.download_images(public_imgs_url)

        for index, img in enumerate(watermark_imgs):
            index = index + 1
            path = f'{blob_name}{index:02}.jpg'
            self._upload_img(path, img)

        return re.sub(r'fotos\/.*', '', blob_name)

    def upload_all_imgs(self, publics_urls_data: Dict[str, List[str]], broker_name: str, max_workers: int = 5) -> None:
        """
        Upload all images obtained from `publics_urls_data` to the bucket `self.upload_bucket` for the
        broker `broker_name`. This task is done concurrently.

        Args:
            publics_urls_data (Dict[str, List[str]]): A dictionary with the public urls of the blobs.
        Returns:
            None
        """

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for blob_name, public_imgs_url in publics_urls_data.items():
                blob_name = f'{broker_name}/{blob_name}'
                futures.append(executor.submit(
                    self._background_imgs_process, blob_name, public_imgs_url))

            for future in concurrent.futures.as_completed(futures):
                folder = future.result()
                print(f'---- Images uploaded to folder: {folder}')

    def upload_blueprints_imgs(self, publics_urls: List[str], broker_name: str, path: str) -> None:
        """
        Upload all blueprint images obtained from `publics_urls` to the bucket `self.upload_bucket` for the
        broker `broker_name`. This task is done concurrently.

        Args:
            publics_urls (List[str]): A list with the public urls of the blobs.
            broker_name (str): The name of the broker.
            path (str): The path where the blueprint images will be uploaded.
        Returns:
            None
        """
        watermark_imgs = self.img_mng.download_images(publics_urls)

        # NOTE: Upload plano ubicacion
        plano_ubicacion = f"{broker_name}/{path}/plano-ubicacion.jpg"
        self._upload_img(plano_ubicacion, watermark_imgs[0])

        # NOTE: Upload plano uso
        plano_uso = f"{broker_name}/{path}/plano-uso.jpg"
        self._upload_img(plano_uso, watermark_imgs[1])

    def upload_all_blueprints_imgs(self, public_blueprint_urls: Dict[str, List[str]], broker_name: str) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for path, publics_urls in public_blueprint_urls.items():
                futures.append(executor.submit(
                    self.upload_blueprints_imgs, publics_urls, broker_name, path))

            for future in concurrent.futures.as_completed(futures):
                future.result()


if __name__ == "__main__":
    from . import image_manager

    img_mng = image_manager.ImageManager()
    fb_mng = FirebaseUploaderManager(
        "duvify-brokers-fotos-unidades", "fotos-unidades-marca-agua", "/home/nahuel/Downloads/duvify-brokers-afa85bd75e36.json", img_mng)
    blobs = fb_mng.download_bucket.list_blobs()
    paths = {}
    for blob in blobs:
        if '.DS_Store' in blob.name or 'planos/' not in blob.name:
            # Ignore all type of files that are not images
            continue

        path_to_blueprint: str = blob.name
        path_to_blueprint = "/".join(path_to_blueprint.split('/')[:-1])
        if path_to_blueprint not in paths:
            paths[path_to_blueprint] = []

        public_url = f"https://firebasestorage.googleapis.com/v0/b/" +\
            f"{fb_mng.download_bucket.name}/o/{urllib.parse.quote(blob.name, safe='')}?alt=media"

        paths[path_to_blueprint].append(public_url)
        print(paths)
