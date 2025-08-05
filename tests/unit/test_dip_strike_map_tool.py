#! python3  # noqa: E265

"""Unit tests for DipStrikeMapTool."""

import unittest

import pytest


@pytest.mark.unit
class TestDipStrikeMapToolUnit(unittest.TestCase):
    """Unit tests for DipStrikeMapTool that don't require QGIS environment."""

    def test_map_tool_import(self):
        """Test that DipStrikeMapTool can be imported."""
        try:
            from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

            assert DipStrikeMapTool is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")

    def test_module_has_expected_class(self):
        """Test that the module exports the expected class."""
        try:
            import dip_strike_tools.core.dip_strike_map_tool as module

            assert hasattr(module, "DipStrikeMapTool")
            assert callable(module.DipStrikeMapTool)
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")


if __name__ == "__main__":
    unittest.main()
