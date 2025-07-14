The project is a QGIS plugin for geological strike and dip data management and analysis.

The main development tools are uv for dependency management and just for task automation.
In the `justfile` there are tasks for running tests, managing dependencies and
translations, etc.
In `pyproject.toml` dependencies are grouped into categories such as `ci`, `testing`, and
`development`.

When launching terminal commands, use `uv run` to ensure the correct environment
is activated. Moreover, to avoid possible issues with the fish shell, use `bash -c` to run
commands that require a shell environment.

The plugin uses pytest and pytest-qgis for testing, with specific markers for unit tests
and QGIS-related tests.

The documentation is built using Sphinx with `MyST` for Markdown support, so markdown files
can leverage the additional syntax to use all Sphinx features.

Refer to `docs/development/*.md` files for more details on specific development tasks.
