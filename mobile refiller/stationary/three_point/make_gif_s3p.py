"""Frames of animate_s3p -> GIF with caption, tank / pump / beacon panel and a map from above (../stc_gif.py).

    python make_gif_s3p.py <folder_with_frames> <out.gif> [fps] [--clean]     (--clean: no text in the image)
"""
import os
import sys

try:
    import stc_gif
except ImportError:                                  # run from another folder
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import stc_gif


def main(folder, out_path, fps=10, last_hold_ms=2500, overlay=True):
    return stc_gif.main(folder, out_path, fps, last_hold_ms, overlay)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--clean"]
    main(args[0], args[1], int(args[2]) if len(args) > 2 else 10, overlay="--clean" not in sys.argv)
