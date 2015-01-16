# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Change log:
# 2014/12/24  - Version 1.0
# 2015/01/16  - Version 1.1
#----------------------------------------------------------------------------
# Goal:
# - Provide some conversions between string and audio/image file

import unicodedata
import StringIO
import base64
import os.path
from pydub import AudioSegment
from PIL import Image
DATE_FORMAT = "%Y-%m-%d"
HIT_TEXT_DEFAULT = '-/- (--%)'


def convert_image_to_string(path):
    """
    Convert image to string for storing images in database
    :param path:
    :return:
    """
    output = StringIO.StringIO()
    image = Image.open(path).convert('RGB')
    image.save(output, format='JPEG')
    contents = output.getvalue()
    output.close()
    return contents


def convert_string_to_image(contents):
    """
    Convert string to image for extracting images from database
    :param contents:
    :return:
    """
    buff = StringIO.StringIO()
    buff.write(contents)
    buff.seek(0)
    image = Image.open(buff)
    return image


def convert_string_to_ogg(contents, path):
    """
    Convert string to audio file (.ogg)
    :param contents:
    :return:
    """
    app = base64.b64decode(contents)
    f = open(unicodedata.normalize('NFKD', path).encode('ascii', 'ignore'), 'wb')
    f.write(app)
    f.close()


def convert_ogg_to_string(path):
    """
    Convert mp3 file to string
    :param path:
    :return:
    """
    with open(path, "rb") as f:
        contents = base64.b64encode(f.read())
    return contents


def convert_mp3_to_ogg(mp3_path, ogg_path):
        """
        Convert mp3 file to ogg file for cross-platform.
        :return:
        """
        if os.path.exists(mp3_path):
            mp3_file = AudioSegment.from_mp3(mp3_path)
            mp3_file.export(ogg_path, format='ogg')


def delete_file(file_path):
    """
    Delete a file given its path.
    :return:
    """
    if os.path.exists(file_path):
        os.remove(file_path)