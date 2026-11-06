import logging as lg
import re
import sys
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from colorlog import ColoredFormatter
from PIL.Image import Resampling

from brailler import __version__
from brailler.generator import BrailleArtGenerator

DEFAULT_RESOLUTION = (40, 18)
DEFAULT_THRESHOLD = 210
RESOLUTION_RE = re.compile(r"([0-9]+)x([0-9]+)")

logger = lg.getLogger(__name__)

def _build_argparser() -> ArgumentParser:
    argparser = ArgumentParser(
        description="braille-based text art generator",
        epilog="source: https://github.com/wandderq/brailler",
    )

    argparser.add_argument(
        "input",
        type=Path,
        help="input image file path",
    )

    argparser.add_argument(
        "-r", "--resolution",
        type=_resolution,
        default=DEFAULT_RESOLUTION,
        help=(
            "output resolution in characters "
            "(format: WIDTHxHEIGHT) "
            f"(default: {DEFAULT_RESOLUTION[0]}x{DEFAULT_RESOLUTION[1]})"
        ),
    )

    argparser.add_argument(
        "-t", "--threshold",
        type=_threshold,
        default=DEFAULT_THRESHOLD,
        help=f"binarization threshold (0-255) (default: {DEFAULT_THRESHOLD})",
    )

    argparser.add_argument(
        "-R", "--resampling",
        type=_resampling,
        default=Resampling.LANCZOS,
        help=(
            "resampling algorithm "
            "(default: lanczos) "
            f"(available: {','.join(r.name.lower() for r in Resampling)})"
        ),
    )

    argparser.add_argument(
        "-i", "--invert",
        action="store_true",
        help="invert image colors",
    )

    argparser.add_argument(
        "-V", "--version",
        action="version",
        version=__version__,
    )

    argparser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="verbose mode (INFO logs)",
    )

    argparser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug features",
    )
    
    return argparser

def _resampling(name: str) -> Resampling:
    try:
        return Resampling[name.upper()]
    
    except KeyError:
        raise ArgumentTypeError from None

def _resolution(string: str) -> tuple[int, int]:
    match = RESOLUTION_RE.match(string.lower().strip())

    if match:
        return (
            int(match.group(1)),
            int(match.group(2)),
        )

    raise ArgumentTypeError

def _threshold(string: str) -> int:
    if not string.isdigit():
        raise ArgumentTypeError
    
    threshold = int(string)

    if threshold < 0 or threshold > 255:
        raise ArgumentTypeError
    
    return threshold

def _setup_logger(*, debug: bool, verbose: bool) -> None:
    logger = lg.getLogger("brailler")
    logger.handlers.clear()
    logger.setLevel(lg.DEBUG if debug else lg.INFO if verbose else lg.WARNING)

    stream_handler = lg.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(ColoredFormatter(
        log_colors={
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
        },
        fmt="{name}: {log_color}{message}{reset}",
        style="{",
    ))

def main() -> None:
    """Run brailler CLI."""
    argparser = _build_argparser()
    args = argparser.parse_args()
    
    _setup_logger(debug=args.debug, verbose=args.verbose)

    generator = BrailleArtGenerator(
        image_filepath=args.input,
        debug=args.debug,
    )

    art = generator.generate(
        resolution=args.resolution,
        threshold=args.threshold,
        resampling_algorithm=args.resampling,
        invert=args.invert,
    )

    sys.stdout.write(art + "\n")
    sys.stdout.flush()
