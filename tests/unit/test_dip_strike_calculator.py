#! python3  # noqa: E265

"""Unit tests for DipStrikeCalculator."""

import unittest

from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator


class TestDipStrikeCalculator(unittest.TestCase):
    """Test DipStrikeCalculator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = DipStrikeCalculator()

    def test_calculate_dip_from_strike(self):
        """Test calculating dip azimuth from strike azimuth."""
        # Test basic conversion: strike 0° -> dip 90°
        self.assertEqual(self.calculator.calculate_dip_from_strike(0), 90.0)

        # Test basic conversion: strike 90° -> dip 180°
        self.assertEqual(self.calculator.calculate_dip_from_strike(90), 180.0)

        # Test wrap around: strike 270° -> dip 0°
        self.assertEqual(self.calculator.calculate_dip_from_strike(270), 0.0)

        # Test wrap around: strike 315° -> dip 45°
        self.assertEqual(self.calculator.calculate_dip_from_strike(315), 45.0)

        # Test arbitrary value: strike 135° -> dip 225°
        self.assertEqual(self.calculator.calculate_dip_from_strike(135), 225.0)

    def test_calculate_strike_from_dip(self):
        """Test calculating strike azimuth from dip azimuth."""
        # Test basic conversion: dip 90° -> strike 0°
        self.assertEqual(self.calculator.calculate_strike_from_dip(90), 0.0)

        # Test basic conversion: dip 180° -> strike 90°
        self.assertEqual(self.calculator.calculate_strike_from_dip(180), 90.0)

        # Test wrap around: dip 0° -> strike 270°
        self.assertEqual(self.calculator.calculate_strike_from_dip(0), 270.0)

        # Test wrap around: dip 45° -> strike 315°
        self.assertEqual(self.calculator.calculate_strike_from_dip(45), 315.0)

        # Test arbitrary value: dip 225° -> strike 135°
        self.assertEqual(self.calculator.calculate_strike_from_dip(225), 135.0)

    def test_bidirectional_conversion(self):
        """Test that conversions are bidirectional."""
        test_values = [0, 45, 90, 135, 180, 225, 270, 315]

        for strike in test_values:
            dip = self.calculator.calculate_dip_from_strike(strike)
            back_to_strike = self.calculator.calculate_strike_from_dip(dip)
            self.assertEqual(back_to_strike, strike, f"Bidirectional conversion failed for strike {strike}")

    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Test None values
        self.assertIsNone(self.calculator.calculate_dip_from_strike(None))
        self.assertIsNone(self.calculator.calculate_strike_from_dip(None))

        # Test string that can't be converted
        self.assertIsNone(self.calculator.calculate_dip_from_strike("invalid"))
        self.assertIsNone(self.calculator.calculate_strike_from_dip("invalid"))

    def test_string_numeric_inputs(self):
        """Test handling of string numeric inputs."""
        # Test string numbers (should work)
        self.assertEqual(self.calculator.calculate_dip_from_strike("0"), 90.0)
        self.assertEqual(self.calculator.calculate_dip_from_strike("90.5"), 180.5)
        self.assertEqual(self.calculator.calculate_strike_from_dip("90"), 0.0)
        self.assertEqual(self.calculator.calculate_strike_from_dip("180.5"), 90.5)

    def test_normalization(self):
        """Test that results are properly normalized to 0-360 range."""
        # Test values that would exceed 360
        self.assertEqual(self.calculator.calculate_dip_from_strike(350), 80.0)  # 350 + 90 = 440 -> 80

        # Test negative results
        self.assertEqual(self.calculator.calculate_strike_from_dip(45), 315.0)  # 45 - 90 = -45 -> 315

    def test_rounding_functionality(self):
        """Test that rounding works correctly with different decimal places."""
        # Test with different decimal places
        test_value = 45.123456789

        # Test default rounding (2 decimal places)
        result = self.calculator.calculate_dip_from_strike(test_value)
        self.assertEqual(result, 135.12)

        # Test no rounding (0 decimal places)
        result = self.calculator.calculate_dip_from_strike(test_value, 0)
        self.assertEqual(result, 135.0)

        # Test 1 decimal place
        result = self.calculator.calculate_dip_from_strike(test_value, 1)
        self.assertEqual(result, 135.1)

        # Test 4 decimal places
        result = self.calculator.calculate_dip_from_strike(test_value, 4)
        self.assertEqual(result, 135.1235)

        # Test same for strike calculation
        result = self.calculator.calculate_strike_from_dip(test_value, 3)
        expected = round((test_value - 90) % 360, 3)  # (45.123456789 - 90) % 360 = 315.123456789 -> 315.123
        self.assertEqual(result, expected)

    def test_rounding_edge_cases(self):
        """Test rounding with edge cases."""
        # Test rounding that affects normalization
        test_value = 359.996  # This rounds to 360, which should normalize to 0

        # With 2 decimal places: 359.996 + 90 = 449.996 -> 450.00 -> 90.0 after normalization
        result = self.calculator.calculate_dip_from_strike(test_value, 2)
        expected = round((test_value + 90) % 360, 2)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
