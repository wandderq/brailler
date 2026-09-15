from PIL.Image import Resampling

DEFAULT_RESOLUTION = (40, 18)
THRESHOLD_MIN = 0
THRESHOLD_MAX = 255
RESAMPLING_ALGORITHMS = {
    "lanczos": Resampling.LANCZOS,
    "bicubic": Resampling.BICUBIC,
    "bilinear": Resampling.BILINEAR,
    "nearest": Resampling.NEAREST,
    "box": Resampling.BOX,
    "hamming": Resampling.HAMMING,
}
RESAMPLING_ALGORITHM_NAMES = ",".join(RESAMPLING_ALGORITHMS.keys())
