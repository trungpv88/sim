__author__ = 'User'
import StringIO
from PIL import Image


DATE_FORMAT = "%Y-%m-%d"
HIT_TEXT_DEFAULT = '-/- (--%)'


def convert_image_to_string(path):
    output = StringIO.StringIO()
    image = Image.open(path)
    image.save(output, format='JPEG')
    contents = output.getvalue()
    output.close()
    return contents


def convert_string_to_image(contents):
    buff = StringIO.StringIO()
    buff.write(contents)
    buff.seek(0)
    image = Image.open(buff)
    return image