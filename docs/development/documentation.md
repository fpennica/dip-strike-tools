# Documentation

This project uses Sphinx to generate documentation from docstrings (documentation in-code) and custom pages written in Markdown (through the [MyST parser](https://myst-parser.readthedocs.io/en/latest/)).

## Prerequisites

The project uses:

- **uv** for dependency management
- **just** for task automation

Make sure you have both tools installed and a proper development environment set up (see [environment.md](environment.md) for details).

## Build documentation website

The project provides several convenient tasks for building documentation:

### HTML Documentation

```bash
# Build HTML documentation
just docs-build-html
```

This will install the required dependencies from the `docs` group in `pyproject.toml` and build the HTML documentation to `docs/_build/html/`. Open `docs/_build/html/index.html` in a web browser to view it.

### PDF Documentation  

```bash
# Build PDF documentation (requires LaTeX)
just docs-build-pdf
```

This builds a PDF version of the documentation using LaTeX. The resulting PDF will be in `docs/_build/latex/`.

## Write documentation using live render

For development, you can use the auto-rebuild feature:

```bash
# Start auto-building server with live reload
just docs-autobuild
```

Open <http://localhost:8000> in a web browser to see the HTML render updated automatically when you save a documentation file.

## Manual commands

If you prefer to run the commands manually instead of using `just`:

```bash
# Install documentation dependencies
uv sync --group docs

# Build HTML manually
uv run sphinx-build -b html -j auto -d docs/_build/cache -q docs docs/_build/html

# Auto-build with live reload manually  
uv run sphinx-autobuild -b html docs/ docs/_build --port 8000
```

## MyST Markdown Features

Since this project uses MyST parser, you can leverage advanced Sphinx features in Markdown files, including:

- Cross-references
- Directives and roles
- Code block highlighting
- Admonitions (notes, warnings, etc.)

Refer to the [MyST documentation](https://myst-parser.readthedocs.io/en/latest/) for complete syntax reference.
