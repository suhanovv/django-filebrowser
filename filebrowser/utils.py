# coding: utf-8

# PYTHON IMPORTS
import re
import os
import unicodedata

# DJANGO IMPORTS
from django.utils import six

# FILEBROWSER IMPORTS
from filebrowser.settings import STRICT_PIL, NORMALIZE_FILENAME, CONVERT_FILENAME

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


def convert_filename(value):
    """
    Convert Filename.
    """

    if NORMALIZE_FILENAME:
        chunks = value.split(os.extsep)
        normalized = []
        for v in chunks:
            v = unicodedata.normalize('NFKD', six.text_type(v)).encode('ascii', 'ignore').decode('ascii')
            v = re.sub(r'[^\w\s-]', '', v).strip()
            normalized.append(v)

        if len(normalized) > 1:
            value = '.'.join(normalized)
        else:
            value = normalized[0]

    if CONVERT_FILENAME:
        value = value.replace(" ", "_").lower()

    return value


def path_strip(path, root):
    if not path or not root:
        return path
    path = os.path.normcase(path)
    root = os.path.normcase(root)
    if path.startswith(root):
        return path[len(root):]
    return path


def scale_and_crop(im, width, height, opts):
    # if im.mode != 'RGB':
    #     im = im.convert('RGB')

    x, y = [float(v) for v in im.size]
    if width:
        xr = float(width)
    else:
        xr = float(x*height/y)
    if height:
        yr = float(height)
    else:
        yr = float(y*width/x)

    if 'crop' in opts:
        r = max(xr/x, yr/y)
    else:
        r = min(xr/x, yr/y)

    if r < 1.0 or (r > 1.0 and 'upscale' in opts):
        im = im.resize((int(x*r), int(y*r)), resample=Image.ANTIALIAS)

    if 'crop' in opts:
        if 'top_left' in opts and x < y:
            #draw cropping box from upper left corner of image
            im = im.crop((0, 0, int(min(x, xr)), int(min(y, yr))))
        elif 'top_right' in opts and x < y:
            #draw cropping box from upper right corner of image
            im = im.crop((int(x-min(x, xr)), 0, int(x), int(min(y, yr))))
        elif 'bottom_left' in opts and x < y:
            #draw cropping box from lower left corner of image
            im = im.crop((0, int(y-min(y, yr)), int(xr), int(y)))
        elif 'bottom_right' in opts and x < y:
            #draw cropping box from lower right corner of image
            im = im.crop((int(x-min(x, xr)), int(y-min(y, yr)), int(x), int(y)))
        elif 'upside' in opts and x < y:
            x, y = [float(v) for v in im.size]
            ex, ey = (x-min(x, xr))/2, (y-min(y, yr))/2
            if ex or ey:
                im = im.crop((int(ex), 0, int(x-ex), int(y)))
        else:
            x, y = [float(v) for v in im.size]
            ex, ey = (x-min(x, xr))/2, (y-min(y, yr))/2
            if ex or ey:
                im = im.crop((int(ex), int(ey), int(x-ex), int(y-ey)))
    return im

scale_and_crop.valid_options = ('crop', 'upscale', 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'upside')