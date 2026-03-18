# agent-screenshot — Project Instructions

## Code Standards

- Python 3.10+, no type: ignore without comment
- Error messages to stderr, file paths to stdout
- This is a **public repo** — never commit internal IPs, hostnames, paths, API keys, or agent names
- All changes go through PRs — never push directly to master
- Version in `VERSION` file — update when releasing

## Documentation Freshness Rule (MANDATORY)

Before creating any PR, check whether your changes affect documentation:
1. If you renamed/moved/deleted any file, flag, or parameter — search README.md and CHANGELOG.md for stale refs
2. If you added a new feature or flag — add it to README.md
3. If you changed behavior — update docs describing the old behavior

## Release Procedure

1. Create branch: `git checkout -b release/vX.Y.Z`
2. Update `VERSION`, `CHANGELOG.md`, README version badge
3. Commit, push, create PR, merge
4. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
5. Release: `gh release create vX.Y.Z --title "vX.Y.Z — Summary" --notes "..."`
