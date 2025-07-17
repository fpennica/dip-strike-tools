#! python3  # noqa: E265

"""Unit tests for DlgCalculateValues."""

import unittest
from unittest.mock import MagicMock, patch

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QApplication

from dip_strike_tools.gui.dlg_calculate_values import DlgCalculateValues


class TestDlgCalculateValues(unittest.TestCase):
    """Test DlgCalculateValues dialog functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for Qt widgets."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        # Mock QGIS components
        self.mock_layer = MagicMock()
        self.mock_layer.name.return_value = "Test Layer"
        self.mock_layer.isValid.return_value = True

        # Create mock fields
        self.mock_field1 = MagicMock()
        self.mock_field1.name.return_value = "strike_azimuth"
        self.mock_field1.type.return_value = QVariant.Double

        self.mock_field2 = MagicMock()
        self.mock_field2.name.return_value = "dip_azimuth"
        self.mock_field2.type.return_value = QVariant.Double

        self.mock_layer.fields.return_value = [self.mock_field1, self.mock_field2]

    @patch("dip_strike_tools.gui.dlg_calculate_values.QgsProject")
    def test_initialization(self, mock_project):
        """Test dialog initialization."""
        # Mock QgsProject.instance()
        mock_project_instance = MagicMock()
        mock_project.instance.return_value = mock_project_instance
        mock_project_instance.mapLayers.return_value = {"layer1": self.mock_layer}

        # Create dialog
        dialog = DlgCalculateValues()

        # Check that dialog was initialized
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.calculation_type, "dip_from_strike")
        self.assertFalse(dialog.create_new_field)

    @patch("dip_strike_tools.gui.dlg_calculate_values.QgsProject")
    def test_populate_layers(self, mock_project):
        """Test layer population."""
        # Mock QgsProject.instance()
        mock_project_instance = MagicMock()
        mock_project.instance.return_value = mock_project_instance
        mock_project_instance.mapLayers.return_value = {"layer1": self.mock_layer}

        # Create dialog
        dialog = DlgCalculateValues()

        # Check that layer combo was populated
        self.assertGreater(dialog.layer_combo.count(), 0)

    def test_calculation_type_change(self):
        """Test calculation type radio button behavior."""
        dialog = DlgCalculateValues()

        # Test initial state
        self.assertTrue(dialog.radio_dip_from_strike.isChecked())
        self.assertEqual(dialog.calculation_type, "dip_from_strike")

        # Change to strike from dip
        dialog.radio_strike_from_dip.setChecked(True)
        dialog.on_calculation_type_changed()
        self.assertEqual(dialog.calculation_type, "strike_from_dip")

    def test_create_field_toggle(self):
        """Test create new field checkbox behavior."""
        dialog = DlgCalculateValues()

        # Test initial state
        self.assertFalse(dialog.create_new_field)
        self.assertFalse(dialog.new_field_name_edit.isEnabled())

        # Toggle create field
        dialog.create_field_checkbox.setChecked(True)
        dialog.on_create_field_toggled(True)

        self.assertTrue(dialog.create_new_field)
        self.assertTrue(dialog.new_field_name_edit.isEnabled())
        self.assertFalse(dialog.output_field_combo.isEnabled())

    @patch("dip_strike_tools.gui.dlg_calculate_values.QMessageBox")
    def test_validation_no_layer(self, mock_msgbox):
        """Test validation when no layer is selected."""
        dialog = DlgCalculateValues()
        dialog.selected_layer = None

        result = dialog.validate_inputs()

        self.assertFalse(result)
        mock_msgbox.warning.assert_called_once()

    @patch("dip_strike_tools.gui.dlg_calculate_values.QMessageBox")
    def test_validation_no_input_field(self, mock_msgbox):
        """Test validation when no input field is selected."""
        dialog = DlgCalculateValues()
        dialog.selected_layer = self.mock_layer
        # Set to first item which should be "-- Select input field --" with None data
        dialog.input_field_combo.setCurrentIndex(0)

        result = dialog.validate_inputs()

        self.assertFalse(result)
        mock_msgbox.warning.assert_called_once()

    def test_get_calculation_config(self):
        """Test getting calculation configuration."""
        dialog = DlgCalculateValues()
        dialog.selected_layer = self.mock_layer
        dialog.calculation_type = "dip_from_strike"
        dialog.input_field = self.mock_field1
        dialog.output_field = self.mock_field2
        dialog.create_new_field = False
        dialog.new_field_name = ""
        dialog.decimal_places = 3  # Test non-default value

        config = dialog.get_calculation_config()

        expected_config = {
            "layer": self.mock_layer,
            "calculation_type": "dip_from_strike",
            "input_field": self.mock_field1,
            "output_field": self.mock_field2,
            "create_new_field": False,
            "new_field_name": "",
            "decimal_places": 3,
        }

        self.assertEqual(config, expected_config)

    def test_input_value_range_check(self):
        """Test the input value range checking functionality."""
        dialog = DlgCalculateValues()
        dialog.selected_layer = self.mock_layer
        dialog.input_field = self.mock_field1

        # Mock layer.getFeatures() to return features with various values
        mock_feature1 = MagicMock()
        mock_feature1.attribute.return_value = 45.0  # Valid value

        mock_feature2 = MagicMock()
        mock_feature2.attribute.return_value = -10.0  # Invalid (negative)

        mock_feature3 = MagicMock()
        mock_feature3.attribute.return_value = 370.0  # Invalid (>360)

        mock_feature4 = MagicMock()
        mock_feature4.attribute.return_value = 180.0  # Valid value

        mock_feature5 = MagicMock()
        mock_feature5.attribute.return_value = None  # Null value (should be skipped)

        self.mock_layer.getFeatures.return_value = [
            mock_feature1,
            mock_feature2,
            mock_feature3,
            mock_feature4,
            mock_feature5,
        ]

        # Mock field index lookup
        mock_fields = MagicMock()
        mock_fields.indexFromName.return_value = 0
        self.mock_layer.fields.return_value = mock_fields

        # Test the range checking
        has_invalid, invalid_count, total_count = dialog.check_input_value_range()

        # Should detect 2 invalid values out of 4 total (null value skipped)
        self.assertTrue(has_invalid)
        self.assertEqual(invalid_count, 2)
        self.assertEqual(total_count, 4)

    @patch("dip_strike_tools.gui.dlg_calculate_values.QMessageBox")
    def test_validation_with_invalid_range_user_continues(self, mock_msgbox):
        """Test validation when input has invalid range but user chooses to continue."""
        dialog = DlgCalculateValues()
        dialog.selected_layer = self.mock_layer
        dialog.input_field = self.mock_field1
        dialog.output_field = self.mock_field2
        dialog.create_new_field = False

        # Mock the range check to return invalid values
        dialog.check_input_value_range = MagicMock(return_value=(True, 5, 20))

        # Mock user clicking "Yes" to continue
        mock_msgbox.warning.return_value = mock_msgbox.StandardButton.Yes

        # Set up combo boxes to return valid data
        dialog.input_field_combo = MagicMock()
        dialog.input_field_combo.currentData.return_value = self.mock_field1
        dialog.output_field_combo = MagicMock()
        dialog.output_field_combo.currentData.return_value = self.mock_field2

        result = dialog.validate_inputs()

        # Should return True (user chose to continue)
        self.assertTrue(result)
        mock_msgbox.warning.assert_called_once()

    @patch("dip_strike_tools.gui.dlg_calculate_values.QMessageBox")
    def test_validation_with_invalid_range_user_cancels(self, mock_msgbox):
        """Test validation when input has invalid range and user chooses to cancel."""
        dialog = DlgCalculateValues()
        dialog.selected_layer = self.mock_layer
        dialog.input_field = self.mock_field1
        dialog.output_field = self.mock_field2
        dialog.create_new_field = False

        # Mock the range check to return invalid values
        dialog.check_input_value_range = MagicMock(return_value=(True, 8, 15))

        # Mock user clicking "No" to cancel
        mock_msgbox.warning.return_value = mock_msgbox.StandardButton.No

        # Set up combo boxes to return valid data
        dialog.input_field_combo = MagicMock()
        dialog.input_field_combo.currentData.return_value = self.mock_field1
        dialog.output_field_combo = MagicMock()
        dialog.output_field_combo.currentData.return_value = self.mock_field2

        result = dialog.validate_inputs()

        # Should return False (user chose to cancel)
        self.assertFalse(result)
        mock_msgbox.warning.assert_called_once()

    @patch("dip_strike_tools.gui.dlg_calculate_values.QMessageBox")
    def test_on_layer_changed_with_readonly_layer(self, mock_msgbox):
        """Test on_layer_changed with a read-only layer."""
        dialog = DlgCalculateValues()

        # Set up the UI components
        dialog.layer_combo = MagicMock()
        dialog.input_field_combo = MagicMock()
        dialog.output_field_combo = MagicMock()
        dialog.button_box = MagicMock()
        mock_ok_button = MagicMock()
        dialog.button_box.button.return_value = mock_ok_button

        # Mock a delimited text layer
        mock_layer = MagicMock()
        mock_data_provider = MagicMock()
        mock_data_provider.name.return_value = "delimitedtext"
        mock_layer.dataProvider.return_value = mock_data_provider
        dialog.layer_combo.currentData.return_value = mock_layer

        # Call the method
        dialog.on_layer_changed()

        # Verify warning was shown and OK button was disabled
        mock_msgbox.warning.assert_called_once()
        mock_ok_button.setEnabled.assert_called_once_with(False)

    @patch("dip_strike_tools.gui.dlg_calculate_values.QMessageBox")
    def test_on_layer_changed_with_editable_layer(self, mock_msgbox):
        """Test on_layer_changed with an editable layer."""
        dialog = DlgCalculateValues()

        # Set up the UI components
        dialog.layer_combo = MagicMock()
        dialog.input_field_combo = MagicMock()
        dialog.output_field_combo = MagicMock()
        dialog.button_box = MagicMock()
        mock_ok_button = MagicMock()
        dialog.button_box.button.return_value = mock_ok_button

        # Mock an editable layer
        mock_layer = MagicMock()
        mock_data_provider = MagicMock()
        mock_data_provider.name.return_value = "ogr"
        mock_layer.dataProvider.return_value = mock_data_provider
        mock_layer.isEditable.return_value = False
        mock_layer.startEditing.return_value = True
        mock_layer.rollBack.return_value = True
        mock_layer.fields.return_value = [self.mock_field1, self.mock_field2]
        dialog.layer_combo.currentData.return_value = mock_layer

        # Call the method
        dialog.on_layer_changed()

        # Verify no warning was shown and OK button was enabled
        mock_msgbox.warning.assert_not_called()
        mock_ok_button.setEnabled.assert_called_once_with(True)
        # Verify field combos were populated
        dialog.input_field_combo.addItem.assert_called()
        dialog.output_field_combo.addItem.assert_called()


if __name__ == "__main__":
    unittest.main()
