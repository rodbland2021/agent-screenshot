# agent-screenshot

[![CI](https://github.com/rodbland2021/agent-screenshot/actions/workflows/ci.yml/badge.svg)](https://github.com/rodbland2021/agent-screenshot/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)

**Two tools for giving AI agents eyes.** Automated web screenshots with Vision-optimised tiling, plus desktop screen capture.

**[Blog post: Why these tools exist and how I use them](https://rodbland.com/blog/screenshot-and-grab-tools/)**

```bash
# Screenshot a web page (tiled for AI Vision models)
python screenshot.py https://example.com --full-page

# Capture your desktop screen
python grab.py
```

## What's in the box

| Tool | What it does |
|------|-------------|
| `screenshot.py` | Playwright-based web screenshots. Full-page captures are automatically tiled into 1072x1072 chunks optimised for Claude Vision and other multimodal models. |
| `grab.py` | Desktop screen capture using Python's `mss` library. 14 region presets (halves, thirds, quadrants) for targeting specific parts of your display. |

## Install

```bash
git clone https://github.com/rodbland2021/agent-screenshot.git
cd agent-screenshot
pip install -r requirements.txt
playwright install chromium
```

Verify it works:

```bash
python screenshot.py https://example.com
# Should print a file path like /tmp/screenshots/example-com_1234567890.jpg
```

## Screenshot tool

Takes automated screenshots of any URL using headless Chromium.

```bash
# Basic screenshot
python screenshot.py https://example.com

# Mobile viewport (375x812)
python screenshot.py https://example.com --mobile

# Full page, tiled for AI Vision models
python screenshot.py https://example.com --full-page

# Dismiss cookie banners and popups
python screenshot.py https://example.com --dismiss-popups --wait-until load --wait 3000

# Custom auth header
python screenshot.py https://my-app.example.com --header "Authorization=Bearer mytoken"

# Screenshot a specific element
python screenshot.py https://example.com --selector ".hero-section"
```

### Why 1072x1072 tiles?

Claude Vision and similar multimodal models have a maximum effective resolution. A 1072x15000 pixel full-page screenshot is too large to process in detail — text blurs, UI elements become unreadable. Tiling the page into 1072x1072 chunks lets the model read every label, button, and table cell.

The tool handles this automatically with `--full-page`. A long page produces 4-8 tiles, each saved as a separate file.

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--full-page` | off | Capture entire page, tile into 1072x1072 chunks |
| `--mobile` | off | Mobile viewport (375x812) |
| `--dismiss-popups` | off | Auto-close cookie banners, geo redirects, email popups |
| `--selector` | — | CSS selector to screenshot a specific element |
| `--wait N` | 0 | Extra wait in ms after page load (for SPAs) |
| `--wait-until` | networkidle | `load`, `domcontentloaded`, or `networkidle` |
| `--width` | 1072 | Viewport width |
| `--height` | 1072 | Viewport height |
| `--quality` | 85 | JPEG quality (1-100) |
| `--png` | off | Output PNG instead of JPEG |
| `--out` | /tmp/screenshots | Output directory |
| `--max-height` | 15000 | Truncate pages taller than this |
| `--header` | — | Custom HTTP header as `KEY=VALUE` (repeatable) |

## Grab tool

Captures the physical desktop screen. Useful for sharing visual context that isn't a web page — design mockups, spreadsheets, error dialogs, anything on your monitor.

> **Requires a display.** `grab.py` needs X11 or Wayland (Linux), a desktop session (macOS/Windows), or a virtual framebuffer (`Xvfb`). It will not work on headless servers, Docker containers, or CI runners without a display server.

```bash
# Full screen
python grab.py

# Left half of screen
python grab.py left

# Top-right quadrant
python grab.py top-right

# Custom output path
python grab.py --out /tmp/my-capture.jpg
```

### Regions

`full`, `left`, `right`, `top`, `bottom`, `top-left`, `top-right`, `bottom-left`, `bottom-right`, `left-third`, `center-third`, `right-third`, `left-two-thirds`, `right-two-thirds`

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--out` | /tmp/screen.jpg | Output file path |
| `--quality` | 85 | JPEG quality (1-100) |
| `--monitor` | 1 | Monitor number for multi-display setups |

## MCP server (native agent integration)

The MCP server gives AI agents direct tool access — no shell commands needed. The agent calls `screenshot` or `grab` as native tools.

### Claude Code

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "agent-screenshot": {
      "command": "python3",
      "args": ["/path/to/agent-screenshot/mcp_server.py"]
    }
  }
}
```

Restart Claude Code. The agent now has `screenshot` and `grab` tools available natively.

### OpenClaw / mcporter

Add to your MCP config (e.g. `~/.mcporter/mcporter.json`):

```json
{
  "mcpServers": {
    "agent-screenshot": {
      "command": "python3",
      "args": ["/path/to/agent-screenshot/mcp_server.py"]
    }
  }
}
```

### MCP tool reference

| Tool | Parameters | Description |
|------|-----------|-------------|
| `screenshot` | `url`, `full_page`, `mobile`, `dismiss_popups`, `selector`, `wait_ms`, `quality`, `headers` | Screenshot a URL, optionally tiled for Vision |
| `grab` | `region`, `output_path`, `quality`, `monitor` | Capture desktop screen |

### Additional dependency

The MCP server requires the `mcp` package in addition to the base requirements:

```bash
pip install mcp
```

## Add to your agent's instructions

For agents that don't support MCP (or as a fallback), add to your agent's instructions:

**Claude Code** (`CLAUDE.md`):
```markdown
After any visual/UI change, verify with a screenshot before reporting done:
python /path/to/screenshot.py <url> --full-page
Read the resulting screenshots and check for visual regressions.
```

**Cursor** (`.cursorrules`), **Aider** (`.aider.conf.yml`), **[OpenClaw](https://github.com/openclaw/openclaw)** (agent system prompt) — same instruction, adapted to your config format.

## Requirements

- **Python 3.10+** on Linux, macOS, or Windows (including WSL)
- **screenshot.py**: Playwright + Chromium. Works on any platform including headless servers, Docker, and CI.
- **grab.py**: mss + Pillow. Requires a physical or virtual display (X11, Wayland, macOS desktop, or Windows).
- **mcp_server.py** (optional): `mcp` package. For native tool integration with Claude Code and OpenClaw.

## License

MIT
