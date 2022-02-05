from enum import Enum


class ImageMode(Enum):
    L = 0
    RGB = 1
    RGBA = 2


class HeaderValue(Enum):
    VERSION = 0
    IMAGE_MODE = 1
    WIDTH = 2
    HEIGHT = 3
    PIXEL_SIZE = 4
    FRAME_COUNT = 5
    FRAME_DURATION = 6
