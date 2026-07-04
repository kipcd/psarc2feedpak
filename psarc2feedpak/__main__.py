import argparse
import sys

from .convert import convert, ConversionError


def main():
    ap = argparse.ArgumentParser(
        prog="psarc2feedpak",
        description="Convert a Rocksmith 2014 .psarc into a .feedpak package.")
    ap.add_argument("psarc", help="input .psarc file")
    ap.add_argument("-o", "--output", help="output path (default: '<artist> - <title>.feedpak')")
    ap.add_argument("--keep-dir", action="store_true",
                    help="also leave the unzipped package as <name>.feedpak.dir")
    args = ap.parse_args()
    try:
        convert(args.psarc, args.output, keep_dir=args.keep_dir)
    except ConversionError as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
