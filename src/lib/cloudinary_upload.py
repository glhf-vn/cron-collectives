"""
Uploading cover image to Cloudinary
"""

import os
import io
import requests
from PIL import Image
from dotenv import load_dotenv
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

load_dotenv()

cloudinary.config(cloud_name=os.environ.get('CLOUDINARY_NAME'),
                  api_key=os.environ.get('CLOUDINARY_KEY'),
                  api_secret=os.environ.get('CLOUDINARY_SECRET'))


def upload_cover(event_id, source_url):
    """
    Upload image from buffer to Cloudinary
    """
    buffer = io.BytesIO()
    size = 1000, 1000

    with Image.open(requests.get(source_url, stream=True, timeout=60).raw) as image:
        image.thumbnail(size)
        image.save(buffer, format='JPEG', quality=90)
        response = upload(
            buffer.getvalue(),
            public_id="covers/" + event_id,
            eager=dict(
                height=800,
                crop="scale"
            ),
        )

        image_url = cloudinary_url(
            response['public_id'],
            format=response['format'],
        )[0]

        print(f"Complete uploading, url: {image_url}\n")
        return image_url
