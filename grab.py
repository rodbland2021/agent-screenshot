#!/usr/bin/env python3
"""
grab.py — Capture the desktop screen for AI agent context.

Uses Python's mss library to capture the display. Supports region presets
for common screen layouts (halves, thirds, quadrants).

Usage:
    python grab.py                 # Full screen
    python grab.py left            # Left half
    python grab.py right           # Right half
    python grab.py top-left        # Top-left quadrant
    python grab.py --out /tmp/grab.jpg

Regions: full, left, right, top, bottom, top-left, top-right,
         bottom-left, bottom-right, left-third, center-third,
         right-third, left-two-thirds, right-two-thirds

Requirements: pip install mss Pillow
"""

import argparse
import sys

REGIONS = {
    "full":             (0.0, 0.0, 1.0, 1.0),
    "left":             (0.0, 0.0, 0.5, 1.0),
    "right":            (0.5, 0.0, 1.0, 1.0),
    "top":              (0.0, 0.0, 1.0, 0.5),
    "bottom":           (0.0, 0.5, 1.0, 1.0),
    "top-left":         (0.0, 0.0, 0.5, 0.5),
    "top-right":        (0.5, 0.0, 1.0, 0.5),
    "bottom-left":      (0.0, 0.5, 0.5, 1.0),
    "bottom-right":     (0.5, 0.5, 1.0, 1.0),
    "left-third":       (0.0, 0.0, 0.33, 1.0),
    "center-third":     (0.33, 0.0, 0.66, 1.0),
    "right-third":      (0.66, 0.0, 1.0, 1.0),
    "left-two-thirds":  (0.0, 0.0, 0.66, 1.0),
    "right-two-thirds": (0.33, 0.0, 1.0, 1.0),
}


def main():
    parser = argparse.ArgumentParser(description="Capture desktop screen for AI agent context")
    parser.add_argument("region", nargs="?", default="full",
                        help="Screen region to capture (default: full)")
    parser.add_argument("--out", default="/tmp/screen.jpg", help="Output file path")
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality (1-100)")
    parser.add_argument("--monitor", type=int, default=1, help="Monitor number (default: 1)")
    args = parser.parse_args()

    if args.region not in REGIONS:
        valid = ", ".join(sorted(REGIONS.keys()))
        print(f"Error: unknown region '{args.region}'.\nValid regions: {valid}", file=sys.stderr)
        sys.exit(1)

    try:
        import mss
        from PIL import Image
    except ImportError:
        print("ERROR: Install dependencies: pip install mss Pillow", file=sys.stderr)
        sys.exit(1)

    try:
        sct_ctx = mss.mss()
    except Exception as e:
        err = str(e)
        if "DISPLAY" in err or "display" in err:
            print("ERROR: No display available. grab.py requires a physical or virtual display "
                  "(X11, Wayland, macOS desktop, or Windows). It cannot run on headless servers.",
                  file=sys.stderr)
        else:
            print(f"ERROR: Screen capture failed: {e}", file=sys.stderr)
        sys.exit(1)

    with sct_ctx as sct:
        if args.monitor > len(sct.monitors) - 1:
            print(f"ERROR: Monitor {args.monitor} not found. Available: {len(sct.monitors) - 1}",
                  file=sys.stderr)
            sys.exit(1)

        mon = sct.monitors[args.monitor]
        screenshot = sct.grab(mon)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    # Crop to region
    w, h = img.size
    rx1, ry1, rx2, ry2 = REGIONS[args.region]
    crop_box = (int(w * rx1), int(h * ry1), int(w * rx2), int(h * ry2))
    img = img.crop(crop_box)

    # Save
    if args.out.endswith(".png"):
        img.save(args.out, "PNG")
    else:
        img.save(args.out, "JPEG", quality=args.quality)

    print(args.out)
    cw, ch = img.size
    print(f"Captured {args.region}: {cw}x{ch}px -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
