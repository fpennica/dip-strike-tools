# Testing the plugin

The plugin uses [pytest](https://docs.pytest.org/en/stable/) with [pytest-qgis](https://github.com/GispoCoding/pytest-qgis) and [pytest-qt](https://github.com/pytest-dev/pytest-qt) for comprehensive testing. Tests are organized in the `tests` directory in separate subfolders with clear separation of concerns:

- `tests/unit`: unit tests
- `tests/integration`: integration tests
- `tests/e2e`: end-to-end tests

## Test Organization Principles

### Unit Tests (`tests/unit/`)

- **Purpose**: Test individual functions and classes in isolation
- **Dependencies**: Keep dependencies minimal (if any), preferably use mocking to avoid QGIS dependencies
- **Example**: Testing mathematical calculations, utility functions

### Integration Tests (`tests/integration/`)

- **Purpose**: Test functionality that requires interaction between different components and/or QGIS environment
- **Dependencies**: Tests could depend on PyQGIS libraries or entire QGIS environment
- **Example**: Testing map tools, layer operations, GUI components

### End-to-End Tests (`tests/e2e/`)

- **Purpose**: Test complete workflows and user interactions
- **Dependencies**: Full QGIS environment, possibly with test data
- **Example**: Testing plugin initialization, configuration, and execution of main features

### Test Markers

Tests in each category are automatically marked as `unit`, `integration`, or `e2e` in the specific `conftest.py`. This allows easy filtering of tests during execution.

The test execution order is enforced by the `pytest_collection_modifyitems` hook in the root `conftest.py`:

- Unit tests (`unit`) execute first
- Integration tests (`integration`) execute second
- E2E tests (`e2e`) execute last

This works by examining each test item's file path and grouping them accordingly, then reordering the entire test collection before execution. This approach works regardless of how pytest is invoked.

Tests should be further organized by using appropriate markers to indicate particular characteristics:

- `@pytest.mark.no_qgis`: Tests that do not require QGIS environment. This can be useful to quickly filter tests for CI environments where QGIS is not available.
- `@pytest.mark.display`: Tests that display GUIs for visual inspection, but can be run in headless CI environments by using `QT_QPA_PLATFORM=offscreen` environment setting or other techniques.
- `@pytest.mark.visual`: Tests that require visual inspection of GUIs or visual output (e.g., map rendering) and are not suitable for headless CI environments.

### GUI Tests

GUI tests should use `pytest-qt` to simulate user interactions and verify GUI behavior. Use `qtbot` fixture for interacting with Qt widgets.

GUI tests can be configured to show the interface for visual inspection for a configurable timeout period. To facilitate this, use the `gui_timeout` fixture defined in `tests/conftest.py`, which reads the timeout value from the `GUI_TIMEOUT` environment variable (defaulting to 2000 ms if not set). This allows easy adjustment of the timeout duration for visual inspection during test runs. The `gui_timeout` fixture should be used to add a delay after showing the GUI in tests:

```python
dialog.show()
qtbot.wait(gui_timeout)
```

The gui tests can also be run in headless mode in CI environments by setting the `QT_QPA_PLATFORM` environment variable to `offscreen` or using the `--qgis_disable_gui` pytest option. The `gui_timeout` will be set to 0 in such cases to avoid unnecessary delays.

## Run tests

### Using justfile (recommended)

```bash
# Run all tests with coverage report
just test

# The justfile command is equivalent to:
uv sync --no-group ci
# the "--no-group ci" option might be required to avoid Qt library conflicts with qgis-plugin-ci dependencies
uv sync --group testing  
uv run pytest -v --cov=dip_strike_tools --cov-report=term-missing
```

### Using pytest directly

```bash
# Run all tests
uv run pytest -v

# Run with coverage report
uv run pytest -v --cov=dip_strike_tools --cov-report=term-missing

# Run only unit tests (no QGIS required)
uv run pytest -m unit -v

# Run only integration tests
uv run pytest -m integration -v

# Run only QGIS tests  
uv run pytest -m qgis -v

# Run unit and integration tests (no QGIS required)
uv run pytest -m "unit or integration" -v

# Run tests excluding QGIS tests (useful when QGIS is not available)
uv run pytest -m "not qgis" -v

# Run specific test file
uv run pytest tests/unit/test_plugin_main.py -v
uv run pytest tests/qgis/test_plugin_main_qgis.py -v

# Run specific test class
uv run pytest tests/unit/test_plugin_main.py::TestDipStrikeToolsPluginBasic -v

# Run specific test method
uv run pytest tests/unit/test_plugin_main.py::TestDipStrikeToolsPluginBasic::test_plugin_import -v
```

## Test Structure Examples

### Unit Test Example

Unit tests use mocking to isolate functionality and don't require a QGIS environment:

```python
@pytest.mark.unit
class TestMyModule:
    @patch('my_module.QgsProject')
    def test_something(self, mock_project):
        # Test with mocked QGIS dependencies
        pass
```

### Integration Test Example

Integration tests test interactions between components. They can be in the same file as unit tests but are marked separately:

```python
@pytest.mark.integration
class TestMyModuleIntegration:
    def test_component_interaction(self):
        # Test interactions between mocked components
        pass
```

### QGIS Integration Test Example

QGIS tests use pytest-qgis and run in a real QGIS environment:

```python
@pytest.mark.qgis  
class TestMyModuleQGIS:
    def test_with_qgis(self, qgis_iface):
        # Test with real QGIS interface
        pass
```

## Coverage

The project uses coverage.py to track test coverage:

```bash
# Generate coverage report
uv run pytest --cov=dip_strike_tools --cov-report=html

# View HTML coverage report
open htmlcov/index.html
```

Coverage configuration is in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["dip_strike_tools"]
omit = ["*/tests/*", "*/test_*", "*/__pycache__/*"]
```

## Writing Tests

### For new modules

1. **Unit tests** in `tests/unit/test_module_name.py`:
   - Test basic functionality with mocked dependencies
   - Test error handling and edge cases
   - Test without requiring QGIS

2. **Integration tests** in `tests/qgis/test_module_name_qgis.py`:
   - Test with real QGIS environment
   - Test GUI components and user interactions
   - Test QGIS API integration

### Example test structure

```python
# tests/unit/test_my_module.py
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
class TestMyModule:
    def test_basic_functionality(self):
        # Basic unit test
        pass

    @patch('my_module.qgis_dependency')
    def test_with_mocked_qgis(self, mock_qgis):
        # Test with mocked QGIS
        pass

# tests/qgis/test_my_module_qgis.py  
import pytest

@pytest.mark.qgis
class TestMyModuleQGIS:
    def test_with_real_qgis(self, qgis_iface):
        # Test with real QGIS
        pass
```
