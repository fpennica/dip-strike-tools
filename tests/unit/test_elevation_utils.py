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

"""Unit tests for elevation_utils module."""

import pytest

from dip_strike_tools.core.elevation_utils import ElevationExtractor


@pytest.mark.unit
class TestElevationExtractor:
    """Tests for ElevationExtractor class - unit tests only."""

    def test_elevation_extractor_initialization(self):
        """Test ElevationExtractor initialization."""
        extractor = ElevationExtractor()
        assert extractor is not None
        assert hasattr(extractor, "log")

    def test_is_suitable_dtm_layer_none_layer(self):
        """Test is_suitable_dtm_layer with None layer."""
        extractor = ElevationExtractor()
        is_suitable, error_msg = extractor.is_suitable_dtm_layer(None)

        assert is_suitable is False
        assert error_msg == "Layer is not a raster layer"

    def test_format_elevation_display_none(self):
        """Test format_elevation_display with None value."""
        extractor = ElevationExtractor()

        result = extractor.format_elevation_display(None)

        assert result == "N/A"

    def test_format_elevation_display_positive(self):
        """Test format_elevation_display with positive value."""
        extractor = ElevationExtractor()

        result = extractor.format_elevation_display(1234.7)

        assert result == "1235 m"

    def test_format_elevation_display_negative(self):
        """Test format_elevation_display with negative value."""
        extractor = ElevationExtractor()

        result = extractor.format_elevation_display(-123.4)

        assert result == "-123 m"

    def test_format_elevation_display_zero(self):
        """Test format_elevation_display with zero value."""
        extractor = ElevationExtractor()

        result = extractor.format_elevation_display(0.0)

        assert result == "0 m"

    def test_format_elevation_display_rounding(self):
        """Test format_elevation_display rounding behavior."""
        extractor = ElevationExtractor()

        # Test rounding up
        result1 = extractor.format_elevation_display(123.6)
        assert result1 == "124 m"

        # Test rounding down
        result2 = extractor.format_elevation_display(123.4)
        assert result2 == "123 m"

        # Test exact half (should round to nearest even)
        result3 = extractor.format_elevation_display(123.5)
        assert result3 == "124 m"

    def test_format_elevation_display_edge_cases(self):
        """Test format_elevation_display with edge cases."""
        extractor = ElevationExtractor()

        # Test very large values
        result1 = extractor.format_elevation_display(8848.86)  # Mount Everest
        assert result1 == "8849 m"

        # Test very low values
        result2 = extractor.format_elevation_display(-430.5)  # Dead Sea level
        assert result2 == "-430 m"

        # Test very small positive values
        result3 = extractor.format_elevation_display(0.1)
        assert result3 == "0 m"

        # Test very small negative values
        result4 = extractor.format_elevation_display(-0.1)
        assert result4 == "0 m"
