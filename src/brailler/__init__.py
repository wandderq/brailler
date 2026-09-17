"""Braille-based text art generator."""
from importlib.metadata import version

from brailler.generator import BrailleArtGenerator

__version__ = version("brailler")
__all__ = ["BrailleArtGenerator"]
