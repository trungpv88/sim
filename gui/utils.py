import StringIO
import base64
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
    f = open(path, 'wb')
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