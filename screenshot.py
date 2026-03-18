#!/usr/bin/env python3
"""
agent-screenshot — Playwright screenshot tool with Vision-optimised tiling.

Takes automated screenshots from the command line using headless Chromium.
Full-page captures are tiled into 1072x1072 chunks optimised for Claude Vision
and other multimodal AI models.

Usage:
    python screenshot.py <url> [options]

Options:
    --full-page          Capture full page and tile into 1072x1072 chunks
    --selector SEL       Screenshot a specific CSS selector
    --mobile             Use mobile viewport (375x812)
    --width N            Custom viewport width (default 1072)
    --height N           Custom viewport height (default 1072)
    --wait N             Extra wait time in ms after page load
    --wait-until EVENT   load, domcontentloaded, or networkidle (default)
    --dismiss-popups     Auto-close cookie banners, geo redirects, email popups
    --png                Output PNG instead of JPEG
    --quality N          JPEG quality 1-100 (default 85)
    --out DIR            Output directory (default /tmp/screenshots)
    --max-height N       Max page height before truncation (default 15000)
    --header KEY=VALUE   Add custom HTTP header (repeatable)

Examples:
    python screenshot.py https://example.com
    python screenshot.py https://example.com --full-page
    python screenshot.py https://example.com --mobile --dismiss-popups
    python screenshot.py https://example.com --header "Authorization=Bearer token123"

Output: Prints file paths of saved screenshots, one per line.
"""

import argparse
import math
import os
import sys
import time


def _dismiss_popups(page):
    """Auto-dismiss common e-commerce popups: geo redirects, cookie banners, email signups."""
    dismiss_selectors = [
        "text=No, stay on the North America store",
        "text=Stay on this store",
        "text=Continue to store",
        "button:has-text('Accept')",
        "button:has-text('Accept all')",
        "button:has-text('Got it')",
        "button[aria-label='Close']",
        "button[aria-label='Close dialog']",
        ".modal-close",
        ".popup-close",
    ]

    for sel in dismiss_selectors:
        try:
            page.click(sel, timeout=1500)
            page.wait_for_timeout(500)
        except Exception:
            pass

    page.evaluate("""
        const selectors = [
            '[class*="cookie"]', '[id*="cookie"]',
            '[class*="popup"]', '[id*="popup"]',
            '[class*="modal"]:not(body)', '[id*="modal"]',
            '[class*="overlay"]:not(body)',
            '.shopify-preview-bar', '[id*="preview-bar"]',
            '[class*="geo-"]', '[id*="geo-"]',
            '[class*="klaviyo"]', '[id*="klaviyo"]',
        ];
        selectors.forEach(s => {
            document.querySelectorAll(s).forEach(el => {
                if (el.offsetHeight > 0) el.remove();
            });
        });
        document.body.style.overflow = 'auto';
        document.documentElement.style.overflow = 'auto';
    """)
    page.wait_for_timeout(500)


def main():
    parser = argparse.ArgumentParser(
        description="Playwright screenshot tool with Vision-optimised tiling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples:")[1] if "Examples:" in __doc__ else "",
    )
    parser.add_argument("url", help="URL to screenshot")
    parser.add_argument("--full-page", action="store_true", help="Capture full page with tiling")
    parser.add_argument("--selector", help="CSS selector to screenshot")
    parser.add_argument("--mobile", action="store_true", help="Mobile viewport (375x812)")
    parser.add_argument("--width", type=int, default=1072, help="Viewport width (default 1072)")
    parser.add_argument("--height", type=int, default=1072, help="Viewport height (default 1072)")
    parser.add_argument("--wait", type=int, default=0, help="Extra wait ms after load")
    parser.add_argument("--wait-until", default="networkidle",
                        choices=["load", "domcontentloaded", "networkidle"])
    parser.add_argument("--png", action="store_true", help="Output PNG instead of JPEG")
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality (1-100)")
    parser.add_argument("--out", default="/tmp/screenshots", help="Output directory")
    parser.add_argument("--max-height", type=int, default=15000, help="Max page height in px")
    parser.add_argument("--dismiss-popups", action="store_true",
                        help="Auto-close cookie banners, geo redirects, email popups")
    parser.add_argument("--header", action="append", default=[],
                        help="Custom HTTP header as KEY=VALUE (repeatable)")
    args = parser.parse_args()

    vw = min(args.width, 1072)
    vh = 812 if args.mobile else args.height
    if args.mobile:
        vw = 375

    TILE_SIZE = 1072
    fmt = "png" if args.png else "jpeg"
    ext = "png" if args.png else "jpg"

    os.makedirs(args.out, exist_ok=True)

    from urllib.parse import urlparse
    parsed = urlparse(args.url)
    host_slug = parsed.hostname.replace(".", "-") if parsed.hostname else "page"
    ts = int(time.time())
    base_name = f"{host_slug}_{ts}"

    # Parse custom headers
    headers = {}
    for h in args.header:
        if "=" in h:
            k, v = h.split("=", 1)
            headers[k.strip()] = v.strip()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium",
              file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": vw, "height": vh},
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        if headers:
            page.set_extra_http_headers(headers)

        # Navigate with automatic fallback
        try:
            page.goto(args.url, wait_until=args.wait_until, timeout=60000)
        except Exception as e:
            if args.wait_until == "networkidle":
                print("WARNING: networkidle timed out, retrying with 'load'...", file=sys.stderr)
                try:
                    page.goto(args.url, wait_until="load", timeout=60000)
                    page.wait_for_timeout(3000)
                except Exception as e2:
                    print(f"ERROR: Navigation failed on retry: {e2}", file=sys.stderr)
                    browser.close()
                    sys.exit(1)
            else:
                print(f"ERROR: Navigation failed: {e}", file=sys.stderr)
                browser.close()
                sys.exit(1)

        if args.wait > 0:
            page.wait_for_timeout(args.wait)

        if args.dismiss_popups:
            _dismiss_popups(page)

        saved_paths = []

        if args.selector:
            el = page.query_selector(args.selector)
            if not el:
                print(f"ERROR: Selector '{args.selector}' not found on page", file=sys.stderr)
                browser.close()
                sys.exit(1)
            path = os.path.join(args.out, f"{base_name}_element.{ext}")
            el.screenshot(path=path, type=fmt, **({"quality": args.quality} if fmt == "jpeg" else {}))
            saved_paths.append(path)

        elif args.full_page:
            full_path = os.path.join(args.out, f"{base_name}_full.png")
            page.screenshot(path=full_path, full_page=True, type="png")

            from PIL import Image
            img = Image.open(full_path)
            w, h = img.size

            if h > args.max_height:
                print(f"WARNING: Page height {h}px exceeds max {args.max_height}px, truncating",
                      file=sys.stderr)
                img = img.crop((0, 0, w, args.max_height))
                h = args.max_height

            cols = math.ceil(w / TILE_SIZE)
            rows = math.ceil(h / TILE_SIZE)
            tile_count = 0

            for row in range(rows):
                for col in range(cols):
                    x = col * TILE_SIZE
                    y = row * TILE_SIZE
                    tile_w = min(TILE_SIZE, w - x)
                    tile_h = min(TILE_SIZE, h - y)
                    tile = img.crop((x, y, x + tile_w, y + tile_h))
                    tile_path = os.path.join(args.out, f"{base_name}_tile_{row}_{col}.{ext}")

                    if fmt == "jpeg":
                        tile = tile.convert("RGB")
                        tile.save(tile_path, "JPEG", quality=args.quality)
                    else:
                        tile.save(tile_path, "PNG")

                    saved_paths.append(tile_path)
                    tile_count += 1

            os.remove(full_path)
            print(f"Page: {w}x{h}px -> {tile_count} tiles ({TILE_SIZE}x{TILE_SIZE})", file=sys.stderr)

        else:
            path = os.path.join(args.out, f"{base_name}.{ext}")
            page.screenshot(
                path=path, type=fmt,
                **({"quality": args.quality} if fmt == "jpeg" else {}),
            )
            saved_paths.append(path)

        browser.close()

    for p in saved_paths:
        print(p)
    print(f"\n{len(saved_paths)} screenshot(s) saved to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
