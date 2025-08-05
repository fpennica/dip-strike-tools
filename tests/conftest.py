"""Pytest configuration for dip-strike-tools tests."""

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests that don't require QGIS")
    config.addinivalue_line("markers", "qgis: Tests that require QGIS environment")
    config.addinivalue_line("markers", "integration: Integration tests")


def pytest_runtest_setup(item):
    """Set up test environment based on markers."""
    # Skip QGIS tests if QGIS is not available
    if item.get_closest_marker("qgis"):
        try:
            import qgis  # noqa: F401
        except ImportError:
            pytest.skip("QGIS not available")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to apply markers automatically."""
    for item in items:
        # Auto-apply markers based on test location
        if "tests/unit" in str(item.fspath):
            if not any(item.get_closest_marker(mark) for mark in ["unit", "qgis", "integration"]):
                item.add_marker(pytest.mark.unit)
        elif "tests/qgis" in str(item.fspath):
            if not item.get_closest_marker("qgis"):
                item.add_marker(pytest.mark.qgis)
