## Project Overview

This project ("Dip-Strike Tools") is a QGIS plugin that aims to provide a set of tools for digitizing, managing, and analyzing plane orientation or attitude data (dip and strike) of planar geologic features. It currently provides basic tools to streamline the workflow for geologists working with structural geology datasets, enabling efficient dip and strike data capture and management within QGIS. The plugin is designed to grow, with future updates planned to add more advanced tools for data management and geological analysis.

## Structure and Development Tools

The primary development tools are **uv** for dependency management and **just** for task automation. The `justfile` defines tasks for running tests, managing dependencies, translations, and more.

`pyproject.toml` organizes dependencies into groups such as `ci`, `testing`, and `development`.

[qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci) is used for tasks such as plugin packaging, changelog generation, and continuous integration through GitHub Actions.

When launching terminal commands, use `uv run` to ensure the correct environment is activated. To avoid possible issues with the fish shell, the use of `bash -c` might be required to run commands that require a shell environment.

## Coding Guidelines

Python code should be Python 3.10+ compatible. PyQt is used for GUI development, and the plugin should be compatible with both PyQt5 and PyQt6, until QGIS fully transitions to PyQt6.

When defining text messages directed to the user, use the `QCoreApplication.translate` function to ensure proper translation support. Use a module level function or method for translations (keeping it at the bottom of the file), like this:

```python
msg = self.tr("This is a message.")
QMessageBox.information(None, self.tr("Title"), msg)
...

def tr(self, message: str) -> str:
    return QCoreApplication.translate(self.__class__.__name__, message)
```

Avoid translation of log messages, especially at debug level, as these are meant for developers and not end-users. Avoid translation of technical identifiers such as field names or variable names, as these should remain consistent across languages for clarity and maintainability.

## Testing

The plugin uses pytest and [pytest-qgis](https://github.com/GispoCoding/pytest-qgis) for testing, with specific markers for unit tests and QGIS-related tests.

Tests are organized in 2 separate folders:

- `tests/unit`: testing code which is independent of QGIS API (uses mocking)
- `tests/qgis`: testing code which depends on QGIS API (integration tests)

Tests are organized using pytest markers:

- `@pytest.mark.unit`: Unit tests that don't require QGIS
- `@pytest.mark.qgis`: Tests that require QGIS environment
- `@pytest.mark.integration`: Integration tests

When running tests, use the `uv run pytest` command to ensure the correct environment is activated. If there are Qt library issues, use the `--no-group ci` option:

```bash
uv sync --no-group ci
uv sync --group testing
uv run pytest -v
```

## Documentation

The documentation is built using Sphinx with `MyST` for Markdown support, so markdown files can leverage the additional syntax to use all Sphinx features.

Refer to `docs/development/*.md` files for more details on specific development tasks.
