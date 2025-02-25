import click
from utilities.image_manager import ImageManager
from utilities.firebase_manager import FirebaseUploaderManager
from utilities.log_manager import LogManager


@click.command()
@click.option("-d", "--download_bucket", type=click.STRING, required=True, help="ID of the Firebase Storage bucket where the images to download are located")
@click.option("-u", "--upload_bucket", type=click.STRING, required=True, help="ID of the Firebase Storage bucket where the images will be uploaded")
@click.option("-k", "--key", type=click.Path(exists=True, resolve_path=True), required=True, help="Path to the Firebase SDK credentials file")
@click.option("-br", "--broker_name", type=click.STRING, required=True, help="Name of the broker, used to save the images in a folder with the broker name")
@click.option("-w", "--watermark", type=click.STRING, help="URL of the image that will be used as a watermark")
@click.option("-f", "--file", type=click.Path(exists=True, resolve_path=True), help="Path to the log file where the logs will be saved (Tip: Use a .log extension, its the default format when the command is executed)")
@click.option("-t", "--threads", type=click.INT, default=5, help="Number of threads to use for downloading and uploading images")
@click.option("-to", "--timeout", type=click.INT, default=10, help="Timeout in seconds for the watermark service responses")
@click.option("-nt", "--n_tries", type=click.INT, default=1, help="Number of attempts to download the image if an error occurs from the watermark service")
def onboarding_brokers_imgs(file, broker_name, download_bucket, upload_bucket, key, watermark, threads, timeout, n_tries):
    """
    Download images from a Firebase Storage bucket, apply a watermark to them, 
    and upload them to another Firebase Storage bucket.
    """

    log_mng = LogManager(filename=file)
    img_mng = ImageManager(timeout=timeout, n_tries=n_tries,
                           log_mng=log_mng, watermark_url=watermark)
    fb_mng = FirebaseUploaderManager(
        download_bucket, upload_bucket, key, img_mng)

    click.echo("*******************************************************")
    click.echo(f"Getting all images public urls from bucket: \
               {download_bucket}")

    all_imgs_urls = fb_mng.get_all_imgs_public_urls()

    click.echo(f"Getting all blueprint images from bucket: \
               {download_bucket}")

    all_blueprint_urls = fb_mng.get_all_blueprint_imgs_public_urls()

    click.echo("*******************************************************")
    click.echo(f"Downloading images from public urls obtained and uploading them to the new bucket: {upload_bucket} \
                ({len(all_imgs_urls)} aproximated images and {len(all_blueprint_urls)*2} blueprint aproximated images)\n\n")

    fb_mng.upload_all_imgs(all_imgs_urls, broker_name, max_workers=threads)

    click.echo("*******************************************************")
    click.echo("All images uploaded successfully!")

    fb_mng.upload_all_blueprints_imgs(all_blueprint_urls, broker_name)

    click.echo("*******************************************************")
    click.echo("All blueprint images uploaded successfully!")


if __name__ == "__main__":
    onboarding_brokers_imgs()
