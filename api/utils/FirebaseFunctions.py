import base64
import datetime
import traceback

import requests

from firebase_admin import storage

from api.models.PostModel import PostType
from api.utils.Logger import Logger


def readFirebase(path):
    try:
        bucket = storage.bucket()
        imageBlob = bucket.blob(path)
        imageUrl = imageBlob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
        imageRequest = requests.get(imageUrl)
        imageBytes = imageRequest.content
        return base64.encodebytes(imageBytes).decode('ascii')
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        return None


def uploadFirebase(path, image, content_type):
    try:
        bucket = storage.bucket()
        imageBlob = bucket.blob(path)
        if content_type == PostType.VIDEO:
            content_type = 'video/{}'.format(type)
        elif content_type == PostType.IMAGE:
            content_type = 'image/{}'.format(type)
        Logger.add_to_log("info", content_type)
        imageBlob.upload_from_file(image, content_type=content_type)
    except Exception as ex:
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        return None


def deleteFirebase(path):
    try:
        bucket = storage.bucket()
        fileBlop = bucket.blob(path)
        fileBlop.delete()
    except Exception as ex:
        return None
