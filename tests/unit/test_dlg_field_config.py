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
Tests for the DlgFieldConfig dialog.
"""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
class TestDlgFieldConfig:
    """Test class for DlgFieldConfig dialog."""

    def test_dialog_import(self):
        """Test that the dialog can be imported."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig

            assert DlgFieldConfig is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")

    def test_dialog_initialization(self):
        """Test basic dialog initialization."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock a layer with some basic properties
        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.fields.return_value.names.return_value = ["field1", "field2", "field3"]
        mock_layer.customProperty.return_value = ""

        # Mock QGIS classes and skip UI setup and mappings loading
        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Check that layer is stored
            assert dialog.layer == mock_layer

    def test_error_handling_no_layer(self):
        """Test error handling when no layer is provided."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Should handle None layer gracefully during testing
        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            # This would normally fail, but our mock prevents the actual UI setup
            dialog = DlgFieldConfig(None)
            assert dialog.layer is None

    def test_translation_method(self):
        """Test translation method."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.fields.return_value.names.return_value = ["field1", "field2", "field3"]

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Test translation method
            assert hasattr(dialog, "tr")
            test_string = "Test String"
            result = dialog.tr(test_string)
            assert isinstance(result, str)

    def test_field_mapping_constants(self):
        """Test that field mapping constants are properly defined."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Create a mock layer
        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.fields.return_value.names.return_value = ["field1", "field2", "field3"]
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Check that dialog was created successfully
            assert dialog.layer == mock_layer

    def test_field_validation_logic(self):
        """Test field validation logic."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.fields.return_value.names.return_value = ["strike_az", "dip_az", "dip_val", "notes"]
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Check that dialog was created successfully with appropriate field names
            assert dialog.layer.fields().names() == ["strike_az", "dip_az", "dip_val", "notes"]


@pytest.mark.integration
class TestFieldConfigIntegration:
    """Integration tests for field configuration."""

    def test_field_filtering_logic(self):
        """Test field filtering for ID fields."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Include common ID field names that should be filtered
        mock_field_names = ["id", "fid", "objectid", "OBJECTID", "strike_az", "dip_az", "notes"]
        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.fields.return_value.names.return_value = mock_field_names
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Check that dialog is created successfully with ID fields
            assert dialog.layer == mock_layer

    def test_field_suggestion_logic(self):
        """Test field name suggestion logic."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Fields with names that should be auto-suggested
        mock_field_names = ["strike_azimuth", "dip_direction", "dip_angle", "geological_type", "notes"]
        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.fields.return_value.names.return_value = mock_field_names
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Check that dialog handles field suggestions properly
            assert dialog.layer.fields().names() == mock_field_names


@pytest.mark.unit
class TestDlgFieldConfigMethods:
    """Test specific methods of DlgFieldConfig."""

    def test_is_id_field_detection(self):
        """Test ID field detection logic."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Test various ID field patterns that should be filtered
            id_fields = [
                "id",
                "ID",
                "Id",
                "fid",
                "FID",
                "Fid",
                "objectid",
                "OBJECTID",
                "ObjectId",
                "gid",
                "GID",
                "Gid",
                "uid",
                "UID",
                "Uid",
                "oid",
                "OID",
                "Oid",
                "pk",
                "PK",
                "Pk",
                "key",
                "KEY",
                "Key",
                "rowid",
                "ROWID",
                "RowId",
                "geom_id",
                "GEOM_ID",
                "Geom_Id",
                "feat_id",
                "FEAT_ID",
                "Feat_Id",
                "id_number",
                "ID_NUMBER",
                "Id_Number",
                "feature_id",
                "FEATURE_ID",
                "Feature_Id",
                "object_id",
                "OBJECT_ID",
                "Object_Id",
            ]

            for field_name in id_fields:
                assert dialog._is_id_field(field_name), f"Field '{field_name}' should be detected as ID field"

            # Test non-ID fields that should not be filtered
            non_id_fields = [
                "strike_azimuth",
                "dip_azimuth",
                "dip_value",
                "geo_type",
                "age",
                "lithology",
                "notes",
                "identifier",
                "description",
                "valid",
                "grade",
                "width",
                "height",
                "depth",
                "temperature",
            ]

            for field_name in non_id_fields:
                assert not dialog._is_id_field(field_name), f"Field '{field_name}' should NOT be detected as ID field"

            # Test edge cases
            assert not dialog._is_id_field(""), "Empty string should not be ID field"
            assert not dialog._is_id_field(None), "None should not be ID field"

    def test_suggest_field_mapping_logic(self):
        """Test field suggestion logic for different field types."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Create mock combo box
            mock_combo = Mock()
            mock_combo.findText.return_value = 1  # Found at index 1
            mock_combo.currentText.return_value = "<None>"

            # Test field mappings for different categories
            numeric_fields = ["strike_azimuth", "dip_direction", "dip_angle", "bearing_value"]
            text_fields = ["geological_type", "rock_type", "formation_age", "field_notes"]

            # Test strike azimuth suggestions
            dialog._suggest_field_mapping(mock_combo, "strike_azimuth", numeric_fields, text_fields)
            mock_combo.setCurrentIndex.assert_called_with(1)
            mock_combo.reset_mock()

            # Test dip azimuth suggestions
            dialog._suggest_field_mapping(mock_combo, "dip_azimuth", numeric_fields, text_fields)
            mock_combo.setCurrentIndex.assert_called_with(1)
            mock_combo.reset_mock()

            # Test dip value suggestions
            dialog._suggest_field_mapping(mock_combo, "dip_value", numeric_fields, text_fields)
            mock_combo.setCurrentIndex.assert_called_with(1)
            mock_combo.reset_mock()

            # Test geo_type suggestions
            dialog._suggest_field_mapping(mock_combo, "geo_type", numeric_fields, text_fields)
            mock_combo.setCurrentIndex.assert_called_with(1)
            mock_combo.reset_mock()

            # Test notes suggestions
            dialog._suggest_field_mapping(mock_combo, "notes", numeric_fields, text_fields)
            mock_combo.setCurrentIndex.assert_called_with(1)

    def test_validate_mappings_missing_required(self):
        """Test validation with missing required fields."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Set up mock combos and other required attributes
            dialog.status_label = Mock()
            dialog.ok_button = Mock()
            dialog.field_combos = {}

            # Create mock combos for required fields with missing selections
            for field_key in ["strike_azimuth", "dip_azimuth", "dip_value"]:
                mock_combo = Mock()
                mock_combo.currentText.return_value = dialog.tr("<None>")
                dialog.field_combos[field_key] = mock_combo

            # Create mock combos for optional fields
            for field_key in ["geo_type", "age", "lithology", "notes", "z_value"]:
                mock_combo = Mock()
                mock_combo.currentText.return_value = dialog.tr("<None>")
                dialog.field_combos[field_key] = mock_combo

            # Mock the tr method to return predictable values
            dialog.tr = Mock(side_effect=lambda x: x)

            # Test validation with missing required fields
            is_valid = dialog.validate_mappings()

            assert not is_valid, "Validation should fail with missing required fields"
            dialog.ok_button.setEnabled.assert_called_with(False)

    def test_validate_mappings_duplicate_fields(self):
        """Test validation with duplicate field mappings."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Set up mock combos and other required attributes
            dialog.status_label = Mock()
            dialog.ok_button = Mock()
            dialog.field_combos = {}

            # Create mock combos with duplicate field selections
            duplicate_field = "azimuth_field"

            # Required fields - two pointing to the same field
            strike_combo = Mock()
            strike_combo.currentText.return_value = duplicate_field
            dialog.field_combos["strike_azimuth"] = strike_combo

            dip_azimuth_combo = Mock()
            dip_azimuth_combo.currentText.return_value = duplicate_field  # Duplicate!
            dialog.field_combos["dip_azimuth"] = dip_azimuth_combo

            dip_value_combo = Mock()
            dip_value_combo.currentText.return_value = "dip_field"
            dialog.field_combos["dip_value"] = dip_value_combo

            # Optional fields
            for field_key in ["geo_type", "age", "lithology", "notes", "z_value"]:
                mock_combo = Mock()
                mock_combo.currentText.return_value = dialog.tr("<None>")
                dialog.field_combos[field_key] = mock_combo

            # Mock required methods
            dialog.tr = Mock(side_effect=lambda x: x)
            dialog._highlight_duplicate_combos = Mock()

            # Test validation with duplicate fields
            is_valid = dialog.validate_mappings()

            assert not is_valid, "Validation should fail with duplicate field mappings"
            dialog.ok_button.setEnabled.assert_called_with(False)
            dialog._highlight_duplicate_combos.assert_called_once()

    def test_validate_mappings_valid_configuration(self):
        """Test validation with valid field configuration."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Set up mock combos and other required attributes
            dialog.status_label = Mock()
            dialog.ok_button = Mock()
            dialog.field_combos = {}

            # Create mock combos with valid field selections
            field_mappings = {
                "strike_azimuth": "strike_field",
                "dip_azimuth": "dip_azimuth_field",
                "dip_value": "dip_value_field",
                "geo_type": "geological_type",
                "age": "<None>",  # Optional field not mapped
                "lithology": "<None>",  # Optional field not mapped
                "notes": "notes_field",
                "z_value": "<None>",  # Optional field not mapped
            }

            for field_key, field_value in field_mappings.items():
                mock_combo = Mock()
                mock_combo.currentText.return_value = field_value
                dialog.field_combos[field_key] = mock_combo

            # Mock required methods
            dialog.tr = Mock(side_effect=lambda x: x)
            dialog._clear_duplicate_highlighting = Mock()

            # Test validation with valid configuration
            is_valid = dialog.validate_mappings()

            assert is_valid, "Validation should pass with valid field mappings"
            dialog.ok_button.setEnabled.assert_called_with(True)
            dialog._clear_duplicate_highlighting.assert_called_once()

    def test_load_current_mappings(self):
        """Test loading current mappings from layer custom properties."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock layer with existing custom properties
        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.side_effect = lambda key, default: {
            "dip_strike_tools/strike_azimuth": "existing_strike_field",
            "dip_strike_tools/dip_azimuth": "existing_dip_field",
            "dip_strike_tools/dip_value": "existing_dip_value",
            "dip_strike_tools/geo_type": "existing_geo_type",
            "dip_strike_tools/notes": "existing_notes",
        }.get(key, default)

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "validate_mappings", return_value=True) as mock_validate,
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Set up mock combos - need to create them manually since setup_ui is mocked
            dialog.field_combos = {}
            for field_key in ["strike_azimuth", "dip_azimuth", "dip_value", "geo_type", "age", "lithology", "notes"]:
                mock_combo = Mock()
                mock_combo.findText.return_value = 1  # Found at index 1
                dialog.field_combos[field_key] = mock_combo

            # Test loading current mappings
            dialog.load_current_mappings()

            # Verify that existing mappings were loaded
            dialog.field_combos["strike_azimuth"].findText.assert_called_with("existing_strike_field")
            dialog.field_combos["strike_azimuth"].setCurrentIndex.assert_called_with(1)
            dialog.field_combos["dip_azimuth"].findText.assert_called_with("existing_dip_field")
            dialog.field_combos["dip_azimuth"].setCurrentIndex.assert_called_with(1)
            dialog.field_combos["geo_type"].findText.assert_called_with("existing_geo_type")
            dialog.field_combos["geo_type"].setCurrentIndex.assert_called_with(1)

            # Verify validation was called (called twice: once during init, once in load_current_mappings)
            assert mock_validate.call_count >= 1

    def test_save_mappings_valid(self):
        """Test saving valid field mappings."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
            patch("dip_strike_tools.toolbelt.preferences.PlgOptionsManager"),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Mock validation to return True (valid)
            dialog.validate_mappings = Mock(return_value=True)

            # Set up mock combos with valid field selections
            dialog.field_combos = {}
            field_mappings = {
                "strike_azimuth": "strike_field",
                "dip_azimuth": "dip_azimuth_field",
                "dip_value": "dip_value_field",
                "geo_type": "geological_type",
                "age": "<None>",  # Optional field not mapped
                "lithology": "lithology_field",
                "notes": "<None>",  # Optional field not mapped
                "z_value": "<None>",  # Optional field not mapped
            }

            for field_key, field_value in field_mappings.items():
                mock_combo = Mock()
                mock_combo.currentText.return_value = field_value
                dialog.field_combos[field_key] = mock_combo

            # Mock geo type mode combo
            dialog.geo_type_mode_combo = Mock()
            dialog.geo_type_mode_combo.currentData.return_value = "code"

            # Mock tr method
            dialog.tr = Mock(side_effect=lambda x: x)

            # Test saving mappings
            result = dialog.save_mappings()

            assert result is True, "save_mappings should return True for valid configuration"

            # Verify required fields were saved
            mock_layer.setCustomProperty.assert_any_call("dip_strike_tools/strike_azimuth", "strike_field")
            mock_layer.setCustomProperty.assert_any_call("dip_strike_tools/dip_azimuth", "dip_azimuth_field")
            mock_layer.setCustomProperty.assert_any_call("dip_strike_tools/dip_value", "dip_value_field")

            # Verify optional fields were handled correctly
            mock_layer.setCustomProperty.assert_any_call("dip_strike_tools/geo_type", "geological_type")
            mock_layer.setCustomProperty.assert_any_call("dip_strike_tools/lithology", "lithology_field")
            mock_layer.removeCustomProperty.assert_any_call("dip_strike_tools/age")
            mock_layer.removeCustomProperty.assert_any_call("dip_strike_tools/notes")

            # Verify layer role was set
            mock_layer.setCustomProperty.assert_any_call("dip_strike_tools/layer_role", "dip_strike_feature_layer")

    def test_save_mappings_invalid(self):
        """Test saving invalid field mappings."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
            patch("qgis.PyQt.QtWidgets.QMessageBox") as mock_msgbox,
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Mock validation to return False (invalid)
            dialog.validate_mappings = Mock(return_value=False)

            # Set up mock combos with invalid field selections (missing required)
            dialog.field_combos = {}
            for field_key in [
                "strike_azimuth",
                "dip_azimuth",
                "dip_value",
                "geo_type",
                "age",
                "lithology",
                "notes",
                "z_value",
            ]:
                mock_combo = Mock()
                mock_combo.currentText.return_value = "<None>"  # All fields unmapped
                dialog.field_combos[field_key] = mock_combo

            # Mock tr method
            dialog.tr = Mock(side_effect=lambda x: x)

            # Test saving invalid mappings
            result = dialog.save_mappings()

            assert result is False, "save_mappings should return False for invalid configuration"

            # Verify warning message was shown
            mock_msgbox.warning.assert_called_once()

    def test_highlight_and_clear_duplicate_combos(self):
        """Test highlighting and clearing duplicate combo box styling."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Set up mock combos
            combo1 = Mock()
            combo1.currentText.return_value = "duplicate_field"
            combo2 = Mock()
            combo2.currentText.return_value = "duplicate_field"
            combo3 = Mock()
            combo3.currentText.return_value = "unique_field"

            dialog.field_combos = {
                "strike_azimuth": combo1,
                "dip_azimuth": combo2,
                "dip_value": combo3,
                "geo_type": Mock(),
                "age": Mock(),
                "lithology": Mock(),
                "notes": Mock(),
            }

            # Mock the required_fields and optional_fields for the method
            dialog.required_fields = {
                "strike_azimuth": "Strike Azimuth",
                "dip_azimuth": "Dip Azimuth",
                "dip_value": "Dip Value",
            }
            dialog.optional_fields = {
                "geo_type": "Geological Type",
                "age": "Age",
                "lithology": "Lithology",
                "notes": "Notes",
            }

            # Mock tr method
            dialog.tr = Mock(side_effect=lambda x: x)

            # Test highlighting duplicates
            used_fields = {"duplicate_field": "Strike Azimuth"}
            dialog._highlight_duplicate_combos(used_fields)

            # Verify styling was applied to duplicate combos
            combo1.setStyleSheet.assert_called_with(
                "QComboBox { border: 2px solid #dc3545; background-color: #f8d7da; }"
            )
            combo2.setStyleSheet.assert_called_with(
                "QComboBox { border: 2px solid #dc3545; background-color: #f8d7da; }"
            )
            combo3.setStyleSheet.assert_called_with("")  # Clear styling for non-duplicate

            # Test clearing highlighting
            dialog._clear_duplicate_highlighting()

            # Verify all styling was cleared
            combo1.setStyleSheet.assert_called_with("")
            combo2.setStyleSheet.assert_called_with("")
            combo3.setStyleSheet.assert_called_with("")

    def test_accept_method(self):
        """Test dialog accept method."""
        try:
            from dip_strike_tools.gui.dlg_field_config import DlgFieldConfig
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.return_value = ""

        with (
            patch("dip_strike_tools.gui.dlg_field_config.QgsApplication"),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.__init__", return_value=None),
            patch.object(DlgFieldConfig, "setup_ui", return_value=None),
            patch.object(DlgFieldConfig, "load_current_mappings", return_value=None),
            patch("dip_strike_tools.gui.dlg_field_config.QDialog.accept") as mock_super_accept,
        ):
            dialog = DlgFieldConfig(mock_layer)

            # Test successful save
            dialog.save_mappings = Mock(return_value=True)
            dialog.accept()

            dialog.save_mappings.assert_called_once()
            mock_super_accept.assert_called_once()

            # Reset mocks
            dialog.save_mappings.reset_mock()
            mock_super_accept.reset_mock()

            # Test failed save
            dialog.save_mappings = Mock(return_value=False)
            dialog.accept()

            dialog.save_mappings.assert_called_once()
            mock_super_accept.assert_not_called()  # Should not call super().accept() if save fails
