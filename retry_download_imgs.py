from urllib.parse import unquote
import re
import click
from utilities.image_manager import ImageManager
from utilities.firebase_manager import FirebaseUploaderManager
from utilities.log_manager import LogManager


@click.command()
@click.option('-d', '--download_bucket', type=click.STRING, required=True, help='ID of the Firebase Storage bucket where the images to download are located')
@click.option('-u', '--upload_bucket', type=click.STRING, required=True, help='ID of the Firebase Storage bucket where the images will be uploaded')
@click.option('-k', '--key', type=click.Path(exists=True, resolve_path=True), required=True, help='Path to the Firebase SDK credentials file')
@click.option('-br', '--broker', type=click.STRING, required=True, help='Name of the broker, used to save the images in a folder with the broker name')
@click.option('-w', '--watermark', type=click.STRING, required=True, help='URL of the image that will be used as a watermark')
@click.option('-l', '--log_file', type=click.Path(exists=True, resolve_path=True), required=True, help='Path to the log file to read and retry the download of the images')
@click.option('-to', '--timeout', type=click.INT, default=10, help='Timeout in seconds for the watermark service responses')
@click.option('-nt', '--n_tries', type=click.INT, default=1, help='Number of attempts to download the image if an error occurs from the watermark service')
def retry_download_imgs(download_bucket, upload_bucket, key, broker, watermark, log_file, timeout, n_tries):

    log_mng = LogManager(filename="retry_logs.log")
    img_mng = ImageManager(timeout=timeout, n_tries=n_tries,
                           log_mng=log_mng, watermark_url=watermark)
    fb_mng = FirebaseUploaderManager(
        download_bucket, upload_bucket, key, img_mng)

    with open(log_file, "r") as f:
        lines = f.readlines()
        public_urls = list(map(lambda line: re.search(
            r'https:.*\.jpg', line).group(0), lines))
        paths = list(map(lambda url: broker + "/" + unquote(url.replace(
            "https://firebasestorage.googleapis.com/v0/b/duvify-brokers-fotos-unidades/o/", "").replace("?alt=media", "")), public_urls))

    click.echo('*******************************************************')
    click.echo(
        f'Downloading images from public urls ({len(public_urls)} images)\n\n')
    imgs = img_mng.download_images(public_urls)

    click.echo('*******************************************************')
    click.echo(
        f'Uploading images to the new bucket: {upload_bucket}\n\n')
    for img, path in zip(imgs, paths):
        fb_mng._upload_img(path, img)

    click.echo('*******************************************************')
    click.echo('Task completed!')


if __name__ == '__main__':
    retry_download_imgs()
