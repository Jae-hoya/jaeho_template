# {{ cookiecutter.project_domain }} MCP Server

{{ cookiecutter.description }}

## Instructions

{{ cookiecutter.instructions }}

## Installation

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run the server
uv run {{ cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') }}-mcp-server
```

### Using pip

```bash
# Install in development mode
pip install -e ".[dev]"

# Run the server
{{ cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') }}-mcp-server
```

## Docker

Build and run the server using Docker:

```bash
# Build the image
docker build -t {{ cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') }}-mcp-server .

# Run the container
docker run -it {{ cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') }}-mcp-server
```

## Development

### Running Tests

```bash
# Run all tests with coverage
uv run --frozen pytest --cov --cov-branch --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_server.py

# Run with specific markers
uv run pytest -m "not live"
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type check
uv run pyright
```

## TODO

After generating this project from the cookiecutter template:

- [ ] Create an RFC issue for community review
- [ ] Generate `uv.lock` file: `uv sync`
- [ ] Remove example tools and implement your custom tools
- [ ] Maintain test coverage parity with main branch
- [ ] Document the server functionality in this README
- [ ] Add repository-level references
- [ ] Create documentation files with appropriate frontmatter
- [ ] Update sidebar navigation
- [ ] Add server card entries to JSON configuration
- [ ] Submit a PR with passing checks

Refer to `DESIGN_GUIDELINES.md` in the main repository for detailed design principles.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
