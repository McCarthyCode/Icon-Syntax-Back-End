import hashlib
import os

from base64 import b16encode, b64encode
from functools import partial

from django.conf import settings


class Base64Converter:
    """
    Utility class containing a method to encode files as a base-64 bytes string.
    """
    class ImproperlyDefinedPath(Exception):
        """
        Exception to be raised when zero or both paths (of relative_path and absolute_path) are defined.
        """
        def __init__(self):
            return super().__init__(
                'Either a path relative to settings.MEDIA_ROOT or an absolute path must be defined.'
            )

    @classmethod
    def encode(cls, relative_path=None, absolute_path=None, block_size=2**16):
        """
        Convert a file to a base-64 bytes string. Takes either a path relative to settings.MEDIA_ROOT or an absolute path as a keyword argument.
        """
        if not (bool(relative_path) ^ bool(absolute_path)):
            raise cls.ImproperlyDefinedPath()

        if bool(relative_path) and not bool(absolute_path):
            absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        if absolute_path != None:
            with open(absolute_path, 'rb') as f:
                bytes_str = b''
                for buffer in iter(partial(f.read, block_size), b''):
                    bytes_str += buffer
                return str(b64encode(bytes_str), 'utf-8')

        return None
