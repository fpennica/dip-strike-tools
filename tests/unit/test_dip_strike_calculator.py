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

"""Unit tests for DipStrikeCalculator."""

import unittest

import pytest

from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator


@pytest.mark.unit
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

    def test_initialization(self):
        """Test calculator initialization."""
        calculator = DipStrikeCalculator()
        self.assertIsNotNone(calculator.log)

    def test_process_layer_invalid_layer(self):
        """Test process_layer with invalid layer."""
        config = {
            "layer": None,
            "calculation_type": "dip_from_strike",
            "input_field": None,
            "create_new_field": True,
            "new_field_name": "test_field",
        }

        success, message = self.calculator.process_layer(config)
        self.assertFalse(success)
        self.assertEqual(message, "Invalid layer")

    def test_process_layer_missing_input_field(self):
        """Test process_layer with missing input field."""
        from unittest.mock import Mock, patch

        # Mock layer with proper isinstance behavior
        with patch("dip_strike_tools.core.dip_strike_calculator.isinstance") as mock_isinstance:
            mock_isinstance.return_value = True  # Make isinstance check pass

            mock_layer = Mock()
            mock_layer.isValid.return_value = True
            mock_layer.addAttribute.return_value = True
            mock_fields = Mock()
            # First call for output field (after creation) returns 0, second for input field returns -1
            mock_fields.indexFromName.side_effect = [0, -1]
            mock_layer.fields.return_value = mock_fields

            # Mock input field
            mock_input_field = Mock()
            mock_input_field.name.return_value = "nonexistent_field"

            config = {
                "layer": mock_layer,
                "calculation_type": "dip_from_strike",
                "input_field": mock_input_field,
                "create_new_field": True,
                "new_field_name": "test_field",
            }

            with patch("dip_strike_tools.core.dip_strike_calculator.edit"):
                success, message = self.calculator.process_layer(config)
                self.assertFalse(success)
                self.assertIn("Input field 'nonexistent_field' not found", message)

    def test_process_layer_missing_output_field(self):
        """Test process_layer with missing output field when not creating new field."""
        from unittest.mock import Mock, patch

        with patch("dip_strike_tools.core.dip_strike_calculator.isinstance") as mock_isinstance:
            mock_isinstance.return_value = True

            # Mock layer
            mock_layer = Mock()
            mock_layer.isValid.return_value = True
            mock_fields = Mock()
            # First call (output field) returns -1, second call (input field) returns 0
            mock_fields.indexFromName.side_effect = [-1, 0]
            mock_layer.fields.return_value = mock_fields

            # Mock fields
            mock_input_field = Mock()
            mock_input_field.name.return_value = "input_field"
            mock_output_field = Mock()
            mock_output_field.name.return_value = "nonexistent_output"

            config = {
                "layer": mock_layer,
                "calculation_type": "dip_from_strike",
                "input_field": mock_input_field,
                "output_field": mock_output_field,
                "create_new_field": False,
            }

            success, message = self.calculator.process_layer(config)
            self.assertFalse(success)
            self.assertIn("Output field 'nonexistent_output' not found", message)

    def test_process_layer_add_field_failure(self):
        """Test process_layer when adding new field fails."""
        from unittest.mock import Mock, patch

        with patch("dip_strike_tools.core.dip_strike_calculator.isinstance") as mock_isinstance:
            mock_isinstance.return_value = True

            # Mock layer
            mock_layer = Mock()
            mock_layer.isValid.return_value = True
            mock_layer.addAttribute.return_value = False
            mock_fields = Mock()
            mock_fields.indexFromName.return_value = 0  # Input field exists
            mock_layer.fields.return_value = mock_fields

            mock_input_field = Mock()
            mock_input_field.name.return_value = "input_field"

            config = {
                "layer": mock_layer,
                "calculation_type": "dip_from_strike",
                "input_field": mock_input_field,
                "create_new_field": True,
                "new_field_name": "test_field",
            }

            with patch("dip_strike_tools.core.dip_strike_calculator.edit"):
                success, message = self.calculator.process_layer(config)
                self.assertFalse(success)
                self.assertIn("Failed to add new field 'test_field'", message)

    def test_process_layer_field_not_found_after_creation(self):
        """Test process_layer when field is not found after creation."""
        from unittest.mock import Mock, patch

        with patch("dip_strike_tools.core.dip_strike_calculator.isinstance") as mock_isinstance:
            mock_isinstance.return_value = True

            # Mock layer
            mock_layer = Mock()
            mock_layer.isValid.return_value = True
            mock_layer.addAttribute.return_value = True
            mock_fields = Mock()
            # After field creation, indexFromName returns -1 (field not found)
            mock_fields.indexFromName.return_value = -1
            mock_layer.fields.return_value = mock_fields

            mock_input_field = Mock()
            mock_input_field.name.return_value = "input_field"

            config = {
                "layer": mock_layer,
                "calculation_type": "dip_from_strike",
                "input_field": mock_input_field,
                "create_new_field": True,
                "new_field_name": "test_field",
            }

            with patch("dip_strike_tools.core.dip_strike_calculator.edit"):
                success, message = self.calculator.process_layer(config)
                self.assertFalse(success)
                self.assertIn("Failed to find newly created field 'test_field'", message)

    def test_process_layer_no_features_processed(self):
        """Test process_layer when no features are processed."""
        from unittest.mock import Mock, patch

        with patch("dip_strike_tools.core.dip_strike_calculator.isinstance") as mock_isinstance:
            mock_isinstance.return_value = True

            # Mock layer
            mock_layer = Mock()
            mock_layer.isValid.return_value = True
            mock_layer.addAttribute.return_value = True

            # Mock fields
            mock_fields = Mock()
            mock_fields.indexFromName.side_effect = [0, 0]  # Input field index, then output field index
            mock_layer.fields.return_value = mock_fields

            # Mock features - empty list
            mock_layer.getFeatures.return_value = []

            mock_input_field = Mock()
            mock_input_field.name.return_value = "input_field"

            config = {
                "layer": mock_layer,
                "calculation_type": "dip_from_strike",
                "input_field": mock_input_field,
                "create_new_field": True,
                "new_field_name": "test_field",
            }

            with patch("dip_strike_tools.core.dip_strike_calculator.edit"):
                success, message = self.calculator.process_layer(config)
                self.assertFalse(success)
                self.assertIn("No features were processed", message)

    def test_process_layer_exception_handling(self):
        """Test process_layer exception handling."""
        from unittest.mock import Mock, patch

        # Create a mock that will raise an exception during processing
        with patch("dip_strike_tools.core.dip_strike_calculator.isinstance") as mock_isinstance:
            mock_isinstance.return_value = True

            mock_layer = Mock()
            mock_layer.isValid.return_value = True
            mock_layer.addAttribute.return_value = True
            mock_fields = Mock()
            mock_fields.indexFromName.side_effect = [0, 0]  # Both fields exist
            mock_layer.fields.return_value = mock_fields

            # Mock features that will cause exception
            mock_feature = Mock()
            mock_feature.attribute.side_effect = Exception("Test exception")
            mock_layer.getFeatures.return_value = [mock_feature]

            mock_input_field = Mock()
            mock_input_field.name.return_value = "input_field"

            config = {
                "layer": mock_layer,
                "calculation_type": "dip_from_strike",
                "input_field": mock_input_field,
                "create_new_field": True,
                "new_field_name": "test_field",
            }

            with patch("dip_strike_tools.core.dip_strike_calculator.edit"):
                success, message = self.calculator.process_layer(config)
                self.assertFalse(success)
                self.assertIn("Error during calculation:", message)

    def test_calculate_methods_with_decimal_places(self):
        """Test calculate methods with custom decimal places."""
        # Test calculate_dip_from_strike with various decimal places
        self.assertEqual(self.calculator.calculate_dip_from_strike(45.12345, 0), 135.0)
        self.assertEqual(self.calculator.calculate_dip_from_strike(45.12345, 1), 135.1)
        self.assertEqual(self.calculator.calculate_dip_from_strike(45.12345, 3), 135.123)

        # Test calculate_strike_from_dip with various decimal places
        self.assertEqual(self.calculator.calculate_strike_from_dip(135.12345, 0), 45.0)
        self.assertEqual(self.calculator.calculate_strike_from_dip(135.12345, 1), 45.1)
        self.assertEqual(self.calculator.calculate_strike_from_dip(135.12345, 3), 45.123)

    def test_process_layer_successful_processing(self):
        """Test process_layer with successful feature processing."""
        from unittest.mock import Mock, patch

        with patch("dip_strike_tools.core.dip_strike_calculator.isinstance") as mock_isinstance:
            mock_isinstance.return_value = True

            mock_layer = Mock()
            mock_layer.isValid.return_value = True
            mock_layer.addAttribute.return_value = True
            mock_fields = Mock()
            mock_fields.indexFromName.side_effect = [0, 0]  # Both fields exist
            mock_layer.fields.return_value = mock_fields

            # Mock feature with valid data
            mock_feature = Mock()
            mock_feature.attribute.return_value = 45.0  # Valid input value
            mock_feature.setAttributes.return_value = True
            mock_layer.getFeatures.return_value = [mock_feature]
            mock_layer.updateFeature.return_value = True

            mock_input_field = Mock()
            mock_input_field.name.return_value = "input_field"

            config = {
                "layer": mock_layer,
                "calculation_type": "dip_from_strike",
                "input_field": mock_input_field,
                "create_new_field": True,
                "new_field_name": "test_field",
            }

            with patch("dip_strike_tools.core.dip_strike_calculator.edit"):
                success, message = self.calculator.process_layer(config)
                self.assertTrue(success)
                self.assertIn("Successfully calculated 1 values", message)

    def test_process_layer_with_strike_calculation(self):
        """Test process_layer with strike calculation type."""
        from unittest.mock import Mock, patch

        with patch("dip_strike_tools.core.dip_strike_calculator.isinstance") as mock_isinstance:
            mock_isinstance.return_value = True

            mock_layer = Mock()
            mock_layer.isValid.return_value = True
            mock_layer.addAttribute.return_value = True
            mock_fields = Mock()
            mock_fields.indexFromName.side_effect = [0, 0]  # Both fields exist
            mock_layer.fields.return_value = mock_fields

            # Mock feature with valid data
            mock_feature = Mock()
            mock_feature.attribute.return_value = 135.0  # Valid dip value
            mock_feature.setAttributes.return_value = True
            mock_layer.getFeatures.return_value = [mock_feature]
            mock_layer.updateFeature.return_value = True

            mock_input_field = Mock()
            mock_input_field.name.return_value = "dip_field"

            config = {
                "layer": mock_layer,
                "calculation_type": "strike_from_dip",
                "input_field": mock_input_field,
                "create_new_field": True,
                "new_field_name": "strike_field",
            }

            with patch("dip_strike_tools.core.dip_strike_calculator.edit"):
                success, message = self.calculator.process_layer(config)
                self.assertTrue(success)
                self.assertIn("Successfully calculated 1 values", message)
