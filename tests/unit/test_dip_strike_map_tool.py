# -----------------------------------------------------------------------------
# Copyright (C) 2025-2026, F. Pennica
# This file is part of Dip-Strike Tools QGIS plugin.
#
# Dip-Strike Tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Dip-Strike Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dip-Strike Tools.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

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
