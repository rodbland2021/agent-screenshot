#!/usr/bin/env python3
"""
MCP server for agent-screenshot tools.

Exposes screenshot and grab as MCP tools that AI agents can call natively
via Claude Code, OpenClaw, or any MCP-compatible client.

Usage (stdio — same machine):
    python mcp_server.py

Register in Claude Code (~/.claude.json):
    {
      "mcpServers": {
        "agent-screenshot": {
          "command": "python3",
          "args": ["/path/to/mcp_server.py"]
        }
      }
    }

Register in OpenClaw (mcporter config):
    {
      "mcpServers": {
        "agent-screenshot": {
          "command": "python3",
          "args": ["/path/to/mcp_server.py"]
        }
      }
    }

Requirements: pip install mcp playwright Pillow mss
"""

import os
import sys
import subprocess
import json

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("ERROR: MCP package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Resolve script directory (for calling screenshot.py and grab.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

mcp = FastMCP("agent-screenshot")


@mcp.tool()
def screenshot(
    url: str,
    full_page: bool = False,
    mobile: bool = False,
    dismiss_popups: bool = False,
    selector: str = "",
    wait_ms: int = 0,
    wait_until: str = "networkidle",
    quality: int = 85,
    output_dir: str = "/tmp/screenshots",
    headers: dict = None,
) -> str:
    """Take a screenshot of a web page using headless Chromium.

    Returns file paths of saved screenshots (one per line).
    With full_page=True, the page is tiled into 1072x1072 chunks
    optimised for Vision models (Claude, GPT-4o, Gemini).

    Args:
        url: URL to screenshot
        full_page: Capture entire page and tile into 1072x1072 chunks
        mobile: Use mobile viewport (375x812)
        dismiss_popups: Auto-close cookie banners, geo redirects, popups
        selector: CSS selector to screenshot a specific element
        wait_ms: Extra wait in milliseconds after page load
        wait_until: Page load strategy: load, domcontentloaded, networkidle
        quality: JPEG quality 1-100
        output_dir: Directory to save screenshots
        headers: Custom HTTP headers as {key: value} dict
    """
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, "screenshot.py"), url]

    if full_page:
        cmd.append("--full-page")
    if mobile:
        cmd.append("--mobile")
    if dismiss_popups:
        cmd.append("--dismiss-popups")
    if selector:
        cmd.extend(["--selector", selector])
    if wait_ms > 0:
        cmd.extend(["--wait", str(wait_ms)])
    if wait_until != "networkidle":
        cmd.extend(["--wait-until", wait_until])
    if quality != 85:
        cmd.extend(["--quality", str(quality)])
    if output_dir != "/tmp/screenshots":
        cmd.extend(["--out", output_dir])
    if headers:
        for k, v in headers.items():
            cmd.extend(["--header", f"{k}={v}"])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        return result.stderr.strip()

    # stdout has file paths (one per line), stderr has info messages
    paths = [p for p in result.stdout.strip().split("\n") if p and os.path.exists(p)]

    if not paths:
        return f"No screenshots saved. stderr: {result.stderr.strip()}"

    return f"{len(paths)} screenshot(s) saved:\n" + "\n".join(paths)


@mcp.tool()
def grab(
    region: str = "full",
    output_path: str = "/tmp/screen.jpg",
    quality: int = 85,
    monitor: int = 1,
) -> str:
    """Capture the desktop screen.

    Requires a physical or virtual display (X11, Wayland, macOS, Windows).
    Will not work on headless servers without a display.

    Args:
        region: Screen region — full, left, right, top, bottom, top-left,
                top-right, bottom-left, bottom-right, left-third,
                center-third, right-third, left-two-thirds, right-two-thirds
        output_path: Where to save the capture
        quality: JPEG quality 1-100
        monitor: Monitor number for multi-display setups
    """
    cmd = [
        sys.executable, os.path.join(SCRIPT_DIR, "grab.py"),
        region,
        "--out", output_path,
        "--quality", str(quality),
        "--monitor", str(monitor),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        return result.stderr.strip()

    path = result.stdout.strip().split("\n")[0]
    info = result.stderr.strip()
    return f"{info}\nSaved to: {path}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
