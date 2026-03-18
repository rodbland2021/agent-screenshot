# Changelog

All notable changes to agent-screenshot are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/). Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-03-18

Initial release.

### Added
- `screenshot.py` — Playwright-based web screenshots with 1072x1072 Vision-optimised tiling
- `grab.py` — Desktop screen capture with 14 region presets (halves, thirds, quadrants)
- `mcp_server.py` — MCP server exposing both tools for Claude Code, OpenClaw, and other MCP clients
- Full-page tiling (`--full-page`) splits long pages into chunks AI Vision models can read
- Mobile viewport (`--mobile`) at 375x812
- Popup dismissal (`--dismiss-popups`) for cookie banners, geo redirects, email signups
- Element screenshots (`--selector`)
- Custom HTTP headers (`--header KEY=VALUE`)
- Quality validation (0-100 range check)
- Width cap warning when exceeding 1072
- Clean error messages for all failure modes (no display, invalid region, bad quality)
