import logging as lg
import sys
from argparse import ArgumentParser
from pathlib import Path

from colorlog import ColoredFormatter
from PIL import Image

from brailler import __version__
from brailler.const import (
    DEFAULT_RESOLUTION,
    RESAMPLING_ALGORITHM_NAMES,
    RESAMPLING_ALGORITHMS,
    THRESHOLD_MAX,
    THRESHOLD_MIN,
)
from brailler.generator import BrailleArtGenerator


class BraillerCLI:
    """Brailler command line interface."""

    def __init__(self) -> None:
        """Initialize brailler CLI."""
        self.argparser = ArgumentParser(
            description="Braille-based text art generator",
            epilog="Source: https://github.com/wandderq/brailler",
        )

        self.logger = lg.getLogger("brailler.cli")

        self._setup_args()
    

    def _setup_args(self) -> None:
        self.argparser.add_argument(
            "input",
            type=Path,
            help="Input image file path",
        )
        
        self.argparser.add_argument(
            "-r", "--resolution",
            type=self._parse_resolution,
            default=DEFAULT_RESOLUTION,
            help="Output resolution in characters (format: WxH) (default: 40x18)",
        )
        
        self.argparser.add_argument(
            "-t", "--threshold",
            type=self._parse_threshold,
            default=210,
            help="Binarization threshold (0-255) (default: 210)",
        )

        self.argparser.add_argument(
            "-R", "--resampling",
            type=self._parse_resampling,
            default=Image.Resampling.LANCZOS,
            help=f"Image resampling algorithm (available: {RESAMPLING_ALGORITHM_NAMES}) (default: lanczos)",
        )

        self.argparser.add_argument(
            "-i", "--invert",
            action="store_true",
            help="Invert image colors",
        )

        self.argparser.add_argument(
            "-V", "--version",
            action="version",
            version=__version__,
        )

        self.argparser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Verbose mode (INFO and DEBUG logs)",
        )
    

    def _parse_resolution(self, resolution_str: str) -> tuple:
        resolution = resolution_str.strip().lower().split("x")
        if len(resolution) != 2:  # noqa: PLR2004
            raise ValueError(resolution_str)
        
        if not (resolution[0].isdigit() and resolution[1].isdigit()):
            raise ValueError(resolution_str)
        
        return (int(resolution[0]), int(resolution[1]))
    

    def _parse_threshold(self, threshold: str) -> int:
        if not threshold.isdigit():
            raise ValueError(threshold)
        
        threshold = int(threshold)

        if threshold < THRESHOLD_MIN or threshold > THRESHOLD_MAX:
            raise ValueError(threshold)
        
        return threshold
    

    def _parse_resampling(self, resampling: str) -> Image.Resampling:
        if resampling.lower() not in RESAMPLING_ALGORITHMS:
            raise ValueError(resampling)
        
        return RESAMPLING_ALGORITHMS[resampling]
            

    def run(self) -> None:
        """Run brailler CLI."""
        args = self.argparser.parse_args()

        _setup_logger(verbose=args.verbose)

        generator = BrailleArtGenerator(args.input)

        art = generator.generate(
            resolution=args.resolution,
            threshold=args.threshold,
            resampling_algorithm=args.resampling,
            invert=args.invert,
        )

        sys.stdout.write(art+"\n")
        sys.stdout.flush()


def _setup_logger(*, verbose: bool) -> None:
    logger = lg.getLogger("brailler")
    logger.setLevel(lg.DEBUG if verbose else lg.WARNING)

    stream_handler = lg.StreamHandler()
    stream_handler.setFormatter(ColoredFormatter(
        fmt="[{log_color}{levelname}{reset} @ {name}] {message}",
        style="{",
        log_colors={
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
        },
    ))

    logger.addHandler(stream_handler)

    

def _run_cli() -> None:
    app = BraillerCLI()
    return app.run()
