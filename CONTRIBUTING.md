# Contributing

Thanks for your interest in contributing! All contributions are welcome.

## Ways to Contribute

- **Report bugs** — open an [issue](https://github.com/rodbland2021/agent-screenshot/issues) with steps to reproduce
- **Suggest features** — open an issue with the `enhancement` label
- **Submit code** — fork, branch, test, PR
- **Improve docs** — README, comments, examples

## Submitting Code

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Test your changes manually (both CLI and MCP if applicable)
4. Commit with a clear message
5. Open a pull request

## Code Style

- Python 3.10+ type hints where practical
- No external dependencies beyond requirements.txt (Playwright, Pillow, mss, mcp)
- Error messages go to stderr, file paths go to stdout
- No internal IPs, hostnames, or credentials in any committed code
