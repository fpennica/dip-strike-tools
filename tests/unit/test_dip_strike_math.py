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

"""
Unit tests for dip_strike_math module.
"""

import pytest

from dip_strike_tools.core import dip_strike_math


@pytest.mark.unit
class TestValidateAzimuthRange:
    """Test azimuth range validation."""

    def test_valid_ranges(self):
        """Test valid azimuth values."""
        assert dip_strike_math.validate_azimuth_range(0.0) is True
        assert dip_strike_math.validate_azimuth_range(45.5) is True
        assert dip_strike_math.validate_azimuth_range(180.0) is True
        assert dip_strike_math.validate_azimuth_range(359.9) is True
        assert dip_strike_math.validate_azimuth_range(360.0) is True

    def test_invalid_ranges(self):
        """Test invalid azimuth values."""
        assert dip_strike_math.validate_azimuth_range(-0.1) is False
        assert dip_strike_math.validate_azimuth_range(-45.0) is False
        assert dip_strike_math.validate_azimuth_range(360.1) is False
        assert dip_strike_math.validate_azimuth_range(450.0) is False

    def test_invalid_types(self):
        """Test invalid input types."""
        assert dip_strike_math.validate_azimuth_range(None) is False
        assert dip_strike_math.validate_azimuth_range("invalid") is False
        assert dip_strike_math.validate_azimuth_range([]) is False


@pytest.mark.unit
class TestNormalizeAzimuth:
    """Test azimuth normalization."""

    def test_positive_values(self):
        """Test positive values within range."""
        assert dip_strike_math.normalize_azimuth(45.0) == 45.0
        assert dip_strike_math.normalize_azimuth(180.0) == 180.0
        assert dip_strike_math.normalize_azimuth(359.0) == 359.0

    def test_values_over_360(self):
        """Test values over 360."""
        assert dip_strike_math.normalize_azimuth(450.0) == 90.0
        assert dip_strike_math.normalize_azimuth(720.0) == 0.0
        assert dip_strike_math.normalize_azimuth(370.5) == 10.5

    def test_negative_values(self):
        """Test negative values."""
        assert dip_strike_math.normalize_azimuth(-90.0) == 270.0
        assert dip_strike_math.normalize_azimuth(-180.0) == 180.0
        assert dip_strike_math.normalize_azimuth(-45.5) == 314.5


@pytest.mark.unit
class TestCalculateDipFromStrike:
    """Test dip calculation from strike."""

    def test_basic_calculations(self):
        """Test basic dip calculations."""
        assert dip_strike_math.calculate_dip_from_strike(0.0) == 90.0
        assert dip_strike_math.calculate_dip_from_strike(90.0) == 180.0
        assert dip_strike_math.calculate_dip_from_strike(180.0) == 270.0
        assert dip_strike_math.calculate_dip_from_strike(270.0) == 0.0

    def test_decimal_places(self):
        """Test rounding to different decimal places."""
        assert dip_strike_math.calculate_dip_from_strike(45.123, 0) == 135.0
        assert dip_strike_math.calculate_dip_from_strike(45.123, 1) == 135.1
        assert dip_strike_math.calculate_dip_from_strike(45.123, 2) == 135.12
        assert dip_strike_math.calculate_dip_from_strike(45.123, 3) == 135.123

    def test_normalization(self):
        """Test that values are normalized to 0-360 range."""
        assert dip_strike_math.calculate_dip_from_strike(315.0) == 45.0
        assert dip_strike_math.calculate_dip_from_strike(350.0) == 80.0

    def test_invalid_input(self):
        """Test invalid input handling."""
        assert dip_strike_math.calculate_dip_from_strike(None) is None
        assert dip_strike_math.calculate_dip_from_strike("invalid") is None


@pytest.mark.unit
class TestCalculateStrikeFromDip:
    """Test strike calculation from dip."""

    def test_basic_calculations(self):
        """Test basic strike calculations."""
        assert dip_strike_math.calculate_strike_from_dip(90.0) == 0.0
        assert dip_strike_math.calculate_strike_from_dip(180.0) == 90.0
        assert dip_strike_math.calculate_strike_from_dip(270.0) == 180.0
        assert dip_strike_math.calculate_strike_from_dip(0.0) == 270.0

    def test_decimal_places(self):
        """Test rounding to different decimal places."""
        assert dip_strike_math.calculate_strike_from_dip(135.456, 0) == 45.0
        assert dip_strike_math.calculate_strike_from_dip(135.456, 1) == 45.5
        assert dip_strike_math.calculate_strike_from_dip(135.456, 2) == 45.46
        assert dip_strike_math.calculate_strike_from_dip(135.456, 3) == 45.456

    def test_normalization(self):
        """Test that values are normalized to 0-360 range."""
        assert dip_strike_math.calculate_strike_from_dip(45.0) == 315.0
        assert dip_strike_math.calculate_strike_from_dip(80.0) == 350.0

    def test_invalid_input(self):
        """Test invalid input handling."""
        assert dip_strike_math.calculate_strike_from_dip(None) is None
        assert dip_strike_math.calculate_strike_from_dip("invalid") is None


@pytest.mark.unit
class TestConvertAzimuthWithTrueNorth:
    """Test azimuth conversion with true north bearing."""

    def test_to_true_north(self):
        """Test conversion from map relative to true north."""
        # Map bearing 90°, true north bearing 10° → true north bearing 80°
        result = dip_strike_math.convert_azimuth_with_true_north(90.0, 10.0, from_true_north=False)
        assert result == 80.0

        # Map bearing 30°, true north bearing 45° → true north bearing 345°
        result = dip_strike_math.convert_azimuth_with_true_north(30.0, 45.0, from_true_north=False)
        assert result == 345.0

    def test_from_true_north(self):
        """Test conversion from true north to map relative."""
        # True north bearing 80°, true north bearing 10° → map bearing 90°
        result = dip_strike_math.convert_azimuth_with_true_north(80.0, 10.0, from_true_north=True)
        assert result == 90.0

        # True north bearing 345°, true north bearing 45° → map bearing 30°
        result = dip_strike_math.convert_azimuth_with_true_north(345.0, 45.0, from_true_north=True)
        assert result == 30.0

    def test_normalization(self):
        """Test that results are properly normalized."""
        # Should wrap around 360°
        result = dip_strike_math.convert_azimuth_with_true_north(10.0, 20.0, from_true_north=False)
        assert result == 350.0


@pytest.mark.unit
class TestGetStrikeAndDipFromAzimuth:
    """Test comprehensive strike and dip calculation from azimuth input."""

    def test_strike_mode_no_true_north(self):
        """Test when input is strike azimuth without true north adjustment."""
        strike, dip = dip_strike_math.get_strike_and_dip_from_azimuth(
            azimuth=90.0, is_strike_mode=True, apply_true_north=False
        )
        assert strike == 90.0
        assert dip == 180.0

    def test_dip_mode_no_true_north(self):
        """Test when input is dip azimuth without true north adjustment."""
        strike, dip = dip_strike_math.get_strike_and_dip_from_azimuth(
            azimuth=90.0, is_strike_mode=False, apply_true_north=False
        )
        assert strike == 0.0
        assert dip == 90.0

    def test_strike_mode_with_true_north(self):
        """Test when input is strike azimuth with true north adjustment."""
        strike, dip = dip_strike_math.get_strike_and_dip_from_azimuth(
            azimuth=90.0, is_strike_mode=True, true_north_bearing=10.0, apply_true_north=True
        )
        assert strike == 80.0  # 90 - 10
        assert dip == 170.0  # 180 - 10

    def test_dip_mode_with_true_north(self):
        """Test when input is dip azimuth with true north adjustment."""
        strike, dip = dip_strike_math.get_strike_and_dip_from_azimuth(
            azimuth=90.0, is_strike_mode=False, true_north_bearing=10.0, apply_true_north=True
        )
        assert strike == 350.0  # (0 - 10) % 360 = 350
        assert dip == 80.0  # 90 - 10

    def test_decimal_places(self):
        """Test decimal place rounding."""
        strike, dip = dip_strike_math.get_strike_and_dip_from_azimuth(
            azimuth=45.6789, is_strike_mode=True, apply_true_north=False, decimal_places=1
        )
        assert strike == 45.7
        assert dip == 135.7

    def test_wraparound_cases(self):
        """Test cases that require normalization."""
        # Strike mode: azimuth 350° becomes strike 350°, dip 80°
        strike, dip = dip_strike_math.get_strike_and_dip_from_azimuth(
            azimuth=350.0, is_strike_mode=True, apply_true_north=False
        )
        assert strike == 350.0
        assert dip == 80.0

        # Dip mode: azimuth 10° becomes strike 280°, dip 10°
        strike, dip = dip_strike_math.get_strike_and_dip_from_azimuth(
            azimuth=10.0, is_strike_mode=False, apply_true_north=False
        )
        assert strike == 280.0  # (10 - 90) % 360 = 280
        assert dip == 10.0


@pytest.mark.integration
class TestIntegrationWithExistingLogic:
    """Test integration with existing calculation patterns."""

    def test_consistency_with_old_dip_from_strike(self):
        """Test that new functions match old dip from strike logic."""
        for strike in [0, 45, 90, 135, 180, 225, 270, 315]:
            old_result = (strike + 90) % 360
            new_result = dip_strike_math.calculate_dip_from_strike(strike, 0)
            assert new_result == old_result, f"Mismatch for strike {strike}"

    def test_consistency_with_old_strike_from_dip(self):
        """Test that new functions match old strike from dip logic."""
        for dip in [0, 45, 90, 135, 180, 225, 270, 315]:
            old_result = (dip - 90) % 360
            new_result = dip_strike_math.calculate_strike_from_dip(dip, 0)
            assert new_result == old_result, f"Mismatch for dip {dip}"

    def test_roundtrip_calculations(self):
        """Test that strike->dip->strike returns original value."""
        for azimuth in [0, 45.5, 90, 135.7, 180, 225.3, 270, 315.9]:
            dip = dip_strike_math.calculate_dip_from_strike(azimuth)
            if dip is not None:  # Guard against None return
                back_to_strike = dip_strike_math.calculate_strike_from_dip(dip)
                if back_to_strike is not None:  # Guard against None return
                    assert abs(back_to_strike - azimuth) < 0.01, f"Roundtrip failed for {azimuth}"
