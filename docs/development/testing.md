# Testing the plugin

The plugin uses pytest with pytest-qgis for comprehensive testing. Tests are organized in 2 separate folders:

- `tests/unit`: testing code which is independent of QGIS API (uses mocking)
- `tests/qgis`: testing code which depends on QGIS API (integration tests)

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit`: Unit tests that don't require QGIS
- `@pytest.mark.qgis`: Tests that require QGIS environment
- `@pytest.mark.integration`: Integration tests

## Requirements

- Python >= 3.11
- QGIS 3.40 - 3.99
- uv for dependency management

```bash
# Install testing dependencies with uv
uv sync --group testing

# Or with pip
python -m pip install -U -r requirements/testing.txt
```

## Run tests

### Using justfile (recommended)

```bash
# Run all tests with coverage report
just test

# The justfile command is equivalent to:
# uv sync --no-group ci
# uv sync --group testing  
# uv run pytest -v --cov=dip_strike_tools --cov-report=term-missing
```

### Using pytest directly

```bash
# Run all tests
uv run pytest -v

# Run with coverage report
uv run pytest -v --cov=dip_strike_tools --cov-report=term-missing

# Run only unit tests (no QGIS required)
uv run pytest -m unit -v

# Run only QGIS tests  
uv run pytest -m qgis -v

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

### Legacy unittest commands (still supported)

```bash
# run only unit tests with pytest launcher (disabling pytest-qgis)
python -m pytest -p no:qgis tests/unit

# run only QGIS tests with pytest launcher
python -m pytest tests/qgis

# run a specific test module using standard unittest
python -m unittest tests.unit.test_plg_metadata

# run a specific test function using standard unittest
python -m unittest tests.unit.test_plg_metadata.TestPluginMetadata.test_version_semver
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

## Current Test Status

As of the latest version, the plugin has **95 tests** with the following coverage:

### Modules with Tests

- **plugin_main.py**: 29 tests (70% coverage)
  - 18 unit tests for basic functionality
  - 26 QGIS integration tests
- **env_var_parser.py**: 11 tests (100% coverage)
- **dlg_create_layer.py**: 4 unit tests (12% coverage)
- **dlg_field_config.py**: 8 unit tests (10% coverage)
- **layer_creator.py**: 13 unit tests (46% coverage)
- **dlg_insert_dip_strike.py**: 10 QGIS tests (34% coverage)
- **plg_preferences.py**: 2 QGIS tests (61% coverage)
- **plg_metadata.py**: 2 unit tests (96% coverage)

### Test Distribution

- **Unit tests**: 57 tests (no QGIS required)
- **QGIS tests**: 38 tests (require QGIS environment)

### Test Organization

Tests are now correctly organized according to their dependencies:

#### `tests/unit/` (57 tests)

- `test_plugin_main.py` - Plugin basic functionality with mocking
- `test_plg_metadata.py` - Plugin metadata validation
- `test_env_var_parser.py` - Environment variable parsing
- `test_dlg_create_layer.py` - Layer creation dialog (mocked)
- `test_dlg_field_config.py` - Field configuration dialog (mocked)
- `test_layer_creator.py` - Layer creation functionality (mocked)

#### `tests/qgis/` (38 tests)

- `test_plugin_main_qgis.py` - Plugin integration with real QGIS
- `test_dlg_insert_dip_strike.py` - Dip/strike dialog with QGIS integration
- `test_plg_preferences.py` - Plugin preferences with QGIS testing framework

Run `just test` to see the current coverage report with detailed line-by-line coverage information.

## Continuous Integration

Tests are designed to work in CI environments. The project structure supports:

- **Local development**: Full test suite with QGIS
- **CI environments**: Unit tests only (when QGIS unavailable)
- **Docker**: Tests can run in QGIS Docker containers

Use markers to run appropriate test subsets in different environments.
