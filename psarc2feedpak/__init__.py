"""Convert Rocksmith 2014 CDLC (.psarc) into got-feedBack .feedpak packages."""

from .convert import convert, ConversionError

__all__ = ["convert", "ConversionError"]
__version__ = "0.1.0"
