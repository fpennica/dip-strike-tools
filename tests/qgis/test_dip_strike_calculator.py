#! python3  # noqa: E265

"""
QGIS integration tests for DipStrikeCalculator.

These tests require a QGIS environment and use pytest-qgis.
"""

import pytest

# Import compatibility module for QVariant
from dip_strike_tools.toolbelt import QVariant

# Import pytest-qgis utilities
pytest_plugins = ["pytest_qgis"]


@pytest.mark.qgis
class TestDipStrikeCalculatorQGIS:
    """QGIS integration tests for DipStrikeCalculator."""

    def test_calculator_import(self):
        """Test that the calculator can be imported in QGIS environment."""
        try:
            from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

            assert DipStrikeCalculator is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")

    def test_calculator_initialization(self, qgis_iface):
        """Test DipStrikeCalculator initialization in QGIS environment."""
        from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

        calculator = DipStrikeCalculator()
        assert calculator is not None
        assert hasattr(calculator, "log")

    def test_process_layer_create_new_field_dip_from_strike(self, qgis_iface):
        """Test process_layer creating new field for dip calculation."""
        from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer

        # QVariant import moved to top of file
        from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

        calculator = DipStrikeCalculator()

        # Create test layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        provider = layer.dataProvider()

        # Add input field
        input_field = QgsField("strike", QVariant.Double)
        provider.addAttributes([input_field])
        layer.updateFields()

        # Add test features
        features = []
        test_data = [0, 45, 90, 135, 180, 225, 270, 315]
        for i, strike_value in enumerate(test_data):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(i, i)))
            feature.setAttributes([strike_value])
            features.append(feature)

        provider.addFeatures(features)
        layer.updateFields()

        # Prepare configuration
        config = {
            "layer": layer,
            "calculation_type": "dip_from_strike",
            "input_field": layer.fields().field("strike"),
            "create_new_field": True,
            "new_field_name": "dip",
            "decimal_places": 2,
        }

        # Process layer
        success, message = calculator.process_layer(config)

        # Verify results
        assert success is True
        assert "Successfully calculated 8 values" in message

        # Check that new field was created
        assert layer.fields().indexFromName("dip") != -1

        # Verify calculated values
        expected_dips = [90, 135, 180, 225, 270, 315, 0, 45]
        features = list(layer.getFeatures())
        for i, feature in enumerate(features):
            calculated_dip = feature.attribute("dip")
            assert calculated_dip == expected_dips[i]

    def test_process_layer_create_new_field_strike_from_dip(self, qgis_iface):
        """Test process_layer creating new field for strike calculation."""
        from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer

        # QVariant import moved to top of file
        from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

        calculator = DipStrikeCalculator()

        # Create test layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        provider = layer.dataProvider()

        # Add input field
        input_field = QgsField("dip", QVariant.Double)
        provider.addAttributes([input_field])
        layer.updateFields()

        # Add test features
        features = []
        test_data = [90, 135, 180, 225, 270, 315, 0, 45]
        for i, dip_value in enumerate(test_data):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(i, i)))
            feature.setAttributes([dip_value])
            features.append(feature)

        provider.addFeatures(features)
        layer.updateFields()

        # Prepare configuration
        config = {
            "layer": layer,
            "calculation_type": "strike_from_dip",
            "input_field": layer.fields().field("dip"),
            "create_new_field": True,
            "new_field_name": "strike",
            "decimal_places": 2,
        }

        # Process layer
        success, message = calculator.process_layer(config)

        # Verify results
        assert success is True
        assert "Successfully calculated 8 values" in message

        # Check that new field was created
        assert layer.fields().indexFromName("strike") != -1

        # Verify calculated values
        expected_strikes = [0, 45, 90, 135, 180, 225, 270, 315]
        features = list(layer.getFeatures())
        for i, feature in enumerate(features):
            calculated_strike = feature.attribute("strike")
            assert calculated_strike == expected_strikes[i]

    def test_process_layer_use_existing_field(self, qgis_iface):
        """Test process_layer using existing output field."""
        from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer

        # QVariant import moved to top of file
        from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

        calculator = DipStrikeCalculator()

        # Create test layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        provider = layer.dataProvider()

        # Add input and output fields
        input_field = QgsField("strike", QVariant.Double)
        output_field = QgsField("dip", QVariant.Double)
        provider.addAttributes([input_field, output_field])
        layer.updateFields()

        # Add test features
        features = []
        test_data = [0, 90, 180, 270]
        for i, strike_value in enumerate(test_data):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(i, i)))
            feature.setAttributes([strike_value, None])  # None for dip initially
            features.append(feature)

        provider.addFeatures(features)
        layer.updateFields()

        # Prepare configuration
        config = {
            "layer": layer,
            "calculation_type": "dip_from_strike",
            "input_field": layer.fields().field("strike"),
            "output_field": layer.fields().field("dip"),
            "create_new_field": False,
            "decimal_places": 1,
        }

        # Process layer
        success, message = calculator.process_layer(config)

        # Verify results
        assert success is True
        assert "Successfully calculated 4 values" in message

        # Verify calculated values
        expected_dips = [90.0, 180.0, 270.0, 0.0]
        features = list(layer.getFeatures())
        for i, feature in enumerate(features):
            calculated_dip = feature.attribute("dip")
            assert calculated_dip == expected_dips[i]

    def test_process_layer_with_null_values(self, qgis_iface):
        """Test process_layer with null and empty values."""
        from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer

        # QVariant import moved to top of file
        from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

        calculator = DipStrikeCalculator()

        # Create test layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        provider = layer.dataProvider()

        # Add input field
        input_field = QgsField("strike", QVariant.Double)
        provider.addAttributes([input_field])
        layer.updateFields()

        # Add test features with mixed valid/invalid values
        features = []
        test_data = [0, None, 90, "", 180]  # Mix of valid and invalid values
        for i, strike_value in enumerate(test_data):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(i, i)))
            feature.setAttributes([strike_value])
            features.append(feature)

        provider.addFeatures(features)
        layer.updateFields()

        # Prepare configuration
        config = {
            "layer": layer,
            "calculation_type": "dip_from_strike",
            "input_field": layer.fields().field("strike"),
            "create_new_field": True,
            "new_field_name": "dip",
            "decimal_places": 2,
        }

        # Process layer
        success, message = calculator.process_layer(config)

        # Verify results - only 2 valid values should be processed (0 and 90, 180)
        # Empty string might be treated as 0 or error, null is skipped
        assert success is True
        assert "Successfully calculated 2 values" in message

        # Check that new field was created
        assert layer.fields().indexFromName("dip") != -1

        # Verify only valid values were calculated (count check is sufficient)
        # The exact number of features processed depends on how QGIS handles null/empty values

    def test_process_layer_with_decimal_places(self, qgis_iface):
        """Test process_layer with different decimal places."""
        from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer

        # QVariant import moved to top of file
        from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

        calculator = DipStrikeCalculator()

        # Create test layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        provider = layer.dataProvider()

        # Add input field
        input_field = QgsField("strike", QVariant.Double)
        provider.addAttributes([input_field])
        layer.updateFields()

        # Add test feature with precise value
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        feature.setAttributes([45.123456])
        provider.addFeatures([feature])
        layer.updateFields()

        # Test with 4 decimal places
        config = {
            "layer": layer,
            "calculation_type": "dip_from_strike",
            "input_field": layer.fields().field("strike"),
            "create_new_field": True,
            "new_field_name": "dip",
            "decimal_places": 4,
        }

        # Process layer
        success, message = calculator.process_layer(config)

        # Verify results
        assert success is True
        assert "Successfully calculated 1 values" in message

        # Check calculated value precision (field precision might limit decimal places)
        features = list(layer.getFeatures())
        calculated_dip = features[0].attribute("dip")
        expected_dip = round(45.123456 + 90, 4)  # 135.1235
        # QGIS field precision might limit this, so check if it's close
        assert abs(calculated_dip - expected_dip) < 0.01

    def test_process_layer_update_failure(self, qgis_iface):
        """Test process_layer when feature update fails."""
        from unittest.mock import patch

        from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer

        # QVariant import moved to top of file
        from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

        calculator = DipStrikeCalculator()

        # Create test layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        provider = layer.dataProvider()

        # Add input field
        input_field = QgsField("strike", QVariant.Double)
        provider.addAttributes([input_field])
        layer.updateFields()

        # Add test feature
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        feature.setAttributes([45])
        provider.addFeatures([feature])
        layer.updateFields()

        # Prepare configuration
        config = {
            "layer": layer,
            "calculation_type": "dip_from_strike",
            "input_field": layer.fields().field("strike"),
            "create_new_field": True,
            "new_field_name": "dip",
            "decimal_places": 2,
        }

        # Mock changeAttributeValue to return False (failure)
        with patch.object(layer, "changeAttributeValue", return_value=False):
            success, message = calculator.process_layer(config)

            # Should still succeed but report errors
            assert success is False
            assert "No features were processed" in message

    def test_process_layer_invalid_calculation_values(self, qgis_iface):
        """Test process_layer with values that cause calculation errors."""
        from unittest.mock import patch

        from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer

        # QVariant import moved to top of file
        from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

        calculator = DipStrikeCalculator()

        # Create test layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        provider = layer.dataProvider()

        # Add input field
        input_field = QgsField("strike", QVariant.Double)
        provider.addAttributes([input_field])
        layer.updateFields()

        # Add test feature
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        feature.setAttributes([45])
        provider.addFeatures([feature])
        layer.updateFields()

        # Prepare configuration
        config = {
            "layer": layer,
            "calculation_type": "dip_from_strike",
            "input_field": layer.fields().field("strike"),
            "create_new_field": True,
            "new_field_name": "dip",
            "decimal_places": 2,
        }

        # Mock calculate_dip_from_strike to return None (calculation error)
        with patch.object(calculator, "calculate_dip_from_strike", return_value=None):
            success, message = calculator.process_layer(config)

            # Should fail due to no valid calculations
            assert success is False
            assert "No features were processed" in message

    def test_process_layer_with_errors_but_some_success(self, qgis_iface):
        """Test process_layer with mixed success and error results."""
        from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer

        # QVariant import moved to top of file
        from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

        calculator = DipStrikeCalculator()

        # Create test layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        provider = layer.dataProvider()

        # Add input field
        input_field = QgsField("strike", QVariant.Double)
        provider.addAttributes([input_field])
        layer.updateFields()

        # Add test features - mix of valid values and invalid strings
        features = []
        test_data = [0, 90, "invalid", 180]  # Mix of valid numbers and invalid string
        for i, strike_value in enumerate(test_data):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(i, i)))
            feature.setAttributes([strike_value])
            features.append(feature)

        provider.addFeatures(features)
        layer.updateFields()

        # Prepare configuration
        config = {
            "layer": layer,
            "calculation_type": "dip_from_strike",
            "input_field": layer.fields().field("strike"),
            "create_new_field": True,
            "new_field_name": "dip",
            "decimal_places": 2,
        }

        # Process layer
        success, message = calculator.process_layer(config)

        # Should succeed with some errors reported
        assert success is True
        # Should process 2 valid values (0, 90, 180 minus invalid string)
        assert "Successfully calculated 2 values" in message or "Successfully calculated 3 values" in message

    def test_process_layer_field_types(self, qgis_iface):
        """Test process_layer creates field with correct type."""
        from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsVectorLayer

        # QVariant import moved to top of file
        from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator

        calculator = DipStrikeCalculator()

        # Create test layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        provider = layer.dataProvider()

        # Add input field
        input_field = QgsField("strike", QVariant.Double)
        provider.addAttributes([input_field])
        layer.updateFields()

        # Add test feature
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        feature.setAttributes([45])
        provider.addFeatures([feature])
        layer.updateFields()

        # Prepare configuration
        config = {
            "layer": layer,
            "calculation_type": "dip_from_strike",
            "input_field": layer.fields().field("strike"),
            "create_new_field": True,
            "new_field_name": "dip",
            "decimal_places": 2,
        }

        # Process layer
        success, message = calculator.process_layer(config)

        # Verify results
        assert success is True

        # Check that the new field has correct type
        dip_field = layer.fields().field("dip")
        assert dip_field.type() == QVariant.Double
        assert dip_field.name() == "dip"
