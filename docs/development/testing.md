# Testing the plugin

The plugin uses pytest with pytest-qgis for comprehensive testing. Tests are organized in 2 separate folders:

- `tests/unit`: testing code which is independent of QGIS API (uses mocking)
- `tests/qgis`: testing code which depends on QGIS API (integration tests)

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit`: Unit tests that don't require QGIS
- `@pytest.mark.qgis`: Tests that require QGIS environment
- `@pytest.mark.integration`: Integration tests

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

## Test Structure

### Unit Tests (`tests/unit/`)

Unit tests use mocking to isolate functionality and don't require a QGIS environment:

```python
@pytest.mark.unit
class TestMyModule:
    @patch('my_module.QgsProject')
    def test_something(self, mock_project):
        # Test with mocked QGIS dependencies
        pass
```

### Integration Tests

Integration tests test interactions between components. They can be in the same file as unit tests but are marked separately:

```python
@pytest.mark.integration
class TestMyModuleIntegration:
    def test_component_interaction(self):
        # Test interactions between mocked components
        pass
```

### QGIS Integration Tests (`tests/qgis/`)

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
