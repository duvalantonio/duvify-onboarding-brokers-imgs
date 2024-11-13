from urllib.parse import unquote
import re
from utilities.image_manager import ImageManager
from utilities.firebase_manager import FirebaseUploaderManager

WATERMARK_URL = "URL DE LA MARCA DE AGUA DEL BROKER (DEBE SER PUBLICA)"
BROKER_NAME = "NOMBRE DEL BROKER (MISMO NOMBRE QUE LA CARPETA EN FIREBASE)"
LOG_FILENAME = "logs.log"
BUCKET_ID = 'fotos-unidades-marca-agua'
BUCKET_IMGIX = 'duvify-brokers-fotos-unidades'
CREDENTIALS_PATH = "CREDENTIALS DE FIREBASE"

with open(LOG_FILENAME, "r") as f:
    lines = f.readlines()
    public_urls = list(map(lambda line: re.search(
        r'https:.*\.jpg', line).group(0), lines))
    paths = list(map(lambda url: BROKER_NAME + "/" + unquote(url.replace(
        "https://firebasestorage.googleapis.com/v0/b/duvify-brokers-fotos-unidades/o/", "").replace("?alt=media", "")), public_urls))

img_manager = ImageManager(watermark_url=WATERMARK_URL)
fb_manager = FirebaseUploaderManager(
    BUCKET_IMGIX, BUCKET_ID, CREDENTIALS_PATH, img_manager)

imgs = img_manager.download_images(public_urls)
for img, path in zip(imgs, paths):
    fb_manager._upload_img(path, img)
