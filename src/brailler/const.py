from enum import IntEnum

DEFAULT_RESOLUTION = (40, 18)
DEFAULT_THRESHOLD = 210


class Dither(IntEnum):
    """Dithering algorithm."""
    
    FLOYDSTEINBERG = 1
    ATKINSON = 2
    BAYER4X4 = 3
    NONE = 4
