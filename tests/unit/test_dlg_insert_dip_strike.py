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

"""
Unit tests for DlgInsertDipStrike dialog.

These tests focus on methods that can be tested without Qt widget initialization.
For integration tests with Qt widgets, see tests/qgis/test_dlg_insert_dip_strike.py
"""

import unittest
from unittest.mock import Mock

import pytest


@pytest.mark.unit
class TestDlgInsertDipStrikeUnit(unittest.TestCase):
    """Unit tests for DlgInsertDipStrike dialog methods."""

    def test_format_bearing_comprehensive(self):
        """Test comprehensive bearing formatting scenarios."""
        from dip_strike_tools.core import dip_strike_math

        # Test comprehensive bearing cases
        test_cases = [
            (-0.0, "0.00°"),
            (-0.001, "0.00°"),
            (-0.004, "0.00°"),
            (-0.005, "-0.01°"),
            (0.0, "0.00°"),
            (0.001, "0.00°"),
            (45.5, "45.50°"),
            (-45.5, "-45.50°"),
            (90.0, "90.00°"),
            (180.0, "180.00°"),
            (270.0, "270.00°"),
            (359.99, "359.99°"),
            (360.0, "360.00°"),
        ]

        for input_val, expected in test_cases:
            result = dip_strike_math.format_bearing(input_val)
            assert result == expected, f"Failed for {input_val}: expected {expected}, got {result}"

    def test_is_layer_suitable_for_dip_strike(self):
        """Test layer suitability check for dip/strike features."""
        from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike

        dialog = DlgInsertDipStrike.__new__(DlgInsertDipStrike)

        # Test with point layer (geometry type 0)
        mock_layer = Mock()
        mock_layer.isValid.return_value = True
        mock_layer.geometryType.return_value = 0  # Point geometry
        assert dialog._is_layer_suitable_for_dip_strike(mock_layer) is True

        # Test with line layer (geometry type 1)
        mock_layer.geometryType.return_value = 1  # Line geometry
        assert dialog._is_layer_suitable_for_dip_strike(mock_layer) is False

        # Test with polygon layer (geometry type 2)
        mock_layer.geometryType.return_value = 2  # Polygon geometry
        assert dialog._is_layer_suitable_for_dip_strike(mock_layer) is False

        # Test with invalid layer
        mock_layer.isValid.return_value = False
        assert dialog._is_layer_suitable_for_dip_strike(mock_layer) is False


if __name__ == "__main__":
    unittest.main()
