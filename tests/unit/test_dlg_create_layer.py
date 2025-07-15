"""
Tests for the DlgCreateLayer dialog.
"""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
class TestDlgCreateLayer:
    """Test class for DlgCreateLayer dialog."""

    def test_dialog_import(self):
        """Test that the dialog can be imported."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer

            assert DlgCreateLayer is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")

    def test_dialog_initialization(self):
        """Test basic dialog initialization."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock necessary QGIS classes and functions - skip setup_ui to avoid widget creation
        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Check basic initialization - these should be set by constructor
            assert hasattr(dialog, "layer_name")
            assert hasattr(dialog, "selected_format")
            assert hasattr(dialog, "output_path")
            assert hasattr(dialog, "apply_symbology")
            assert hasattr(dialog, "selected_crs")

    def test_translation_method(self):
        """Test translation method."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Test translation method
            assert hasattr(dialog, "tr")
            test_string = "Test String"
            result = dialog.tr(test_string)
            assert isinstance(result, str)

    def test_validation_methods(self):
        """Test input validation methods."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Test validation method exists
            assert hasattr(dialog, "validate_input")
            assert hasattr(dialog, "get_layer_config")


@pytest.mark.unit
class TestDlgCreateLayerMethods:
    """Test specific methods of DlgCreateLayer."""

    def test_update_crs_selection_mode(self):
        """Test CRS selection mode toggling."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.use_canvas_crs_radio = Mock()
            dialog.use_custom_crs_radio = Mock()
            dialog.crs_widget = Mock()

            # Test canvas CRS mode (default)
            dialog.use_canvas_crs_radio.isChecked.return_value = True
            dialog.use_custom_crs_radio.isChecked.return_value = False
            dialog.update_crs_selection_mode()
            dialog.crs_widget.setEnabled.assert_called_with(False)

            # Test custom CRS mode
            dialog.use_canvas_crs_radio.isChecked.return_value = False
            dialog.use_custom_crs_radio.isChecked.return_value = True
            dialog.update_crs_selection_mode()
            dialog.crs_widget.setEnabled.assert_called_with(True)

    def test_get_selected_crs_canvas_mode(self):
        """Test getting CRS in canvas mode."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch("qgis.utils.iface") as mock_iface,
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.use_canvas_crs_radio = Mock()
            dialog.use_custom_crs_radio = Mock()
            dialog.crs_widget = Mock()

            # Mock canvas CRS
            mock_canvas_crs = Mock()
            mock_canvas = Mock()
            mock_canvas.mapSettings.return_value.destinationCrs.return_value = mock_canvas_crs
            mock_iface.mapCanvas.return_value = mock_canvas

            # Test canvas CRS mode
            dialog.use_canvas_crs_radio.isChecked.return_value = True
            result = dialog.get_selected_crs()
            assert result == mock_canvas_crs

            # Test fallback when no iface available
            mock_iface.mapCanvas.return_value = None
            mock_project_crs = Mock()
            mock_project_crs.isValid.return_value = True
            with patch("dip_strike_tools.gui.dlg_create_layer.QgsProject.instance") as mock_project:
                mock_project.return_value.crs.return_value = mock_project_crs
                result = dialog.get_selected_crs()
                assert result == mock_project_crs

    def test_get_selected_crs_custom_mode(self):
        """Test getting CRS in custom mode."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.use_canvas_crs_radio = Mock()
            dialog.use_custom_crs_radio = Mock()
            dialog.crs_widget = Mock()

            # Mock custom CRS
            mock_custom_crs = Mock()
            dialog.crs_widget.crs.return_value = mock_custom_crs

            # Test custom CRS mode
            dialog.use_canvas_crs_radio.isChecked.return_value = False
            result = dialog.get_selected_crs()
            assert result == mock_custom_crs

    def test_update_format_options_memory(self):
        """Test format options update for memory layers."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components and formats
            dialog.format_combo = Mock()
            dialog.file_widget = Mock()
            dialog.path_label = Mock()
            dialog.desc_label = Mock()

            # Set up formats dictionary
            dialog.formats = {
                "memory": {
                    "driver": "memory",
                    "extension": "",
                    "description": "Temporary layer (lost when QGIS closes)",
                    "display_name": "Memory Layer",
                },
                "shapefile": {
                    "driver": "ESRI Shapefile",
                    "extension": "shp",
                    "description": "Standard shapefile format",
                    "display_name": "ESRI Shapefile",
                },
            }

            # Test memory format selection
            dialog.format_combo.currentData.return_value = "memory"
            dialog.update_format_options()

            # Verify file widget is hidden for memory layers
            dialog.file_widget.setVisible.assert_called_with(False)
            dialog.path_label.setVisible.assert_called_with(False)
            dialog.desc_label.setText.assert_called_with("Temporary layer (lost when QGIS closes)")

    def test_update_format_options_shapefile(self):
        """Test format options update for shapefile."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget") as mock_file_widget_class,
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch.object(DlgCreateLayer, "update_output_filename", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components and formats
            dialog.format_combo = Mock()
            dialog.file_widget = Mock()
            dialog.path_label = Mock()
            dialog.desc_label = Mock()

            # Set up formats dictionary
            dialog.formats = {
                "memory": {
                    "driver": "memory",
                    "extension": "",
                    "description": "Temporary layer (lost when QGIS closes)",
                    "display_name": "Memory Layer",
                },
                "shapefile": {
                    "driver": "ESRI Shapefile",
                    "extension": "shp",
                    "description": "Standard shapefile format",
                    "display_name": "ESRI Shapefile",
                },
            }

            # Test shapefile format selection
            dialog.format_combo.currentData.return_value = "shapefile"
            dialog.update_format_options()

            # Verify file widget is shown for shapefile
            dialog.file_widget.setVisible.assert_called_with(True)
            dialog.path_label.setVisible.assert_called_with(True)
            dialog.desc_label.setText.assert_called_with("Standard shapefile format")
            dialog.file_widget.setFilter.assert_called_with("ESRI Shapefile (*.shp)")
            dialog.file_widget.setStorageMode.assert_called_with(mock_file_widget_class.StorageMode.SaveFile)

    def test_update_format_options_geopackage(self):
        """Test format options update for GeoPackage."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget") as mock_file_widget_class,
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch.object(DlgCreateLayer, "update_output_filename", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components and formats
            dialog.format_combo = Mock()
            dialog.file_widget = Mock()
            dialog.path_label = Mock()
            dialog.desc_label = Mock()

            # Set up formats dictionary
            dialog.formats = {
                "gpkg": {
                    "driver": "GPKG",
                    "extension": "gpkg",
                    "description": "SQLite-based OGC standard format (can contain multiple layers)",
                    "display_name": "GeoPackage",
                },
            }

            # Test geopackage format selection
            dialog.format_combo.currentData.return_value = "gpkg"
            dialog.update_format_options()

            # Verify GeoPackage uses GetFile mode (for adding to existing files)
            dialog.file_widget.setStorageMode.assert_called_with(mock_file_widget_class.StorageMode.GetFile)
            dialog.file_widget.setDialogTitle.assert_called_with("Select or Create GeoPackage")

    def test_update_output_filename(self):
        """Test output filename generation."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject.instance") as mock_project,
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components and formats
            dialog.format_combo = Mock()
            dialog.file_widget = Mock()
            dialog.name_edit = Mock()

            # Set up formats dictionary
            dialog.formats = {
                "shapefile": {
                    "driver": "ESRI Shapefile",
                    "extension": "shp",
                    "description": "Standard shapefile format",
                    "display_name": "ESRI Shapefile",
                },
            }

            # Test with project path available
            mock_project.return_value.absolutePath.return_value = "/project/path"
            dialog.format_combo.currentData.return_value = "shapefile"
            dialog.name_edit.text.return_value.strip.return_value = "test_layer"

            dialog.update_output_filename()

            dialog.file_widget.setFilePath.assert_called_with("/project/path/test_layer.shp")

            # Test with no project path
            mock_project.return_value.absolutePath.return_value = ""
            dialog.update_output_filename()

            dialog.file_widget.setFilePath.assert_called_with("test_layer.shp")

            # Test memory format (should not update filename)
            dialog.format_combo.currentData.return_value = "memory"
            dialog.file_widget.setFilePath.reset_mock()
            dialog.update_output_filename()

            dialog.file_widget.setFilePath.assert_not_called()

    def test_validate_input_empty_layer_name(self):
        """Test validation with empty layer name."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch("dip_strike_tools.gui.dlg_create_layer.QMessageBox") as mock_msgbox,
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.name_edit = Mock()
            dialog.name_edit.text.return_value.strip.return_value = ""

            # Test empty layer name
            result = dialog.validate_input()

            assert result is False
            mock_msgbox.warning.assert_called_once()

    def test_validate_input_memory_layer_success(self):
        """Test successful validation for memory layer."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch.object(DlgCreateLayer, "get_selected_crs") as mock_get_crs,
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.name_edit = Mock()
            dialog.format_combo = Mock()
            dialog.apply_symbology_check = Mock()
            mock_crs = Mock()
            mock_get_crs.return_value = mock_crs

            # Set up for memory layer
            dialog.name_edit.text.return_value.strip.return_value = "test_layer"
            dialog.format_combo.currentData.return_value = "memory"
            dialog.apply_symbology_check.isChecked.return_value = True

            # Set up formats dictionary
            dialog.formats = {
                "memory": {
                    "driver": "memory",
                    "extension": "",
                    "description": "Temporary layer (lost when QGIS closes)",
                    "display_name": "Memory Layer",
                },
            }

            # Test successful validation
            result = dialog.validate_input()

            assert result is True
            assert dialog.layer_name == "test_layer"
            assert dialog.selected_format == "memory"
            assert dialog.output_path == ""
            assert dialog.apply_symbology is True
            assert dialog.selected_crs == mock_crs

    def test_validate_input_shapefile_empty_path(self):
        """Test validation failure for shapefile without path."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch("dip_strike_tools.gui.dlg_create_layer.QMessageBox") as mock_msgbox,
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.name_edit = Mock()
            dialog.format_combo = Mock()
            dialog.file_widget = Mock()

            # Set up for shapefile without path
            dialog.name_edit.text.return_value.strip.return_value = "test_layer"
            dialog.format_combo.currentData.return_value = "shapefile"
            dialog.file_widget.filePath.return_value.strip.return_value = ""

            # Set up formats dictionary
            dialog.formats = {
                "shapefile": {
                    "driver": "ESRI Shapefile",
                    "extension": "shp",
                    "description": "Standard shapefile format",
                    "display_name": "ESRI Shapefile",
                },
            }

            # Test validation failure
            result = dialog.validate_input()

            assert result is False
            mock_msgbox.warning.assert_called_once()

    def test_validate_input_shapefile_invalid_characters(self):
        """Test validation failure for shapefile with invalid characters."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch("dip_strike_tools.gui.dlg_create_layer.QMessageBox") as mock_msgbox,
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.name_edit = Mock()
            dialog.format_combo = Mock()
            dialog.file_widget = Mock()

            # Set up for shapefile with invalid characters
            dialog.name_edit.text.return_value.strip.return_value = "test_layer"
            dialog.format_combo.currentData.return_value = "shapefile"
            dialog.file_widget.filePath.return_value.strip.return_value = "/path/to/test<file.shp"

            # Set up formats dictionary
            dialog.formats = {
                "shapefile": {
                    "driver": "ESRI Shapefile",
                    "extension": "shp",
                    "description": "Standard shapefile format",
                    "display_name": "ESRI Shapefile",
                },
            }

            # Test validation failure
            result = dialog.validate_input()

            assert result is False
            mock_msgbox.warning.assert_called_once()

    def test_validate_input_shapefile_long_filename(self):
        """Test validation warning for long shapefile filename."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch("dip_strike_tools.gui.dlg_create_layer.QMessageBox") as mock_msgbox,
            patch("os.path.exists", return_value=False),
            patch("os.makedirs"),
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.name_edit = Mock()
            dialog.format_combo = Mock()
            dialog.file_widget = Mock()
            dialog.apply_symbology_check = Mock()

            # Set up for shapefile with long filename
            dialog.name_edit.text.return_value.strip.return_value = "test_layer"
            dialog.format_combo.currentData.return_value = "shapefile"
            dialog.file_widget.filePath.return_value.strip.return_value = "/path/to/very_long_shapefile_name.shp"
            dialog.apply_symbology_check.isChecked.return_value = True

            # Set up formats dictionary
            dialog.formats = {
                "shapefile": {
                    "driver": "ESRI Shapefile",
                    "extension": "shp",
                    "description": "Standard shapefile format",
                    "display_name": "ESRI Shapefile",
                },
            }

            # Mock user choosing "No" (don't continue)
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.No

            # Test validation failure when user chooses not to continue
            result = dialog.validate_input()

            assert result is False
            mock_msgbox.question.assert_called_once()

    def test_validate_input_geopackage_existing_file(self):
        """Test validation for GeoPackage with existing file."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch.object(DlgCreateLayer, "get_selected_crs") as mock_get_crs,
            patch("dip_strike_tools.gui.dlg_create_layer.QMessageBox") as mock_msgbox,
            patch("os.path.exists", return_value=True),
            patch("os.path.dirname", return_value="/path/to"),
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.name_edit = Mock()
            dialog.format_combo = Mock()
            dialog.file_widget = Mock()
            dialog.apply_symbology_check = Mock()
            mock_crs = Mock()
            mock_get_crs.return_value = mock_crs

            # Set up for GeoPackage with existing file
            dialog.name_edit.text.return_value.strip.return_value = "test_layer"
            dialog.format_combo.currentData.return_value = "gpkg"
            dialog.file_widget.filePath.return_value.strip.return_value = "/path/to/existing.gpkg"
            dialog.apply_symbology_check.isChecked.return_value = True

            # Set up formats dictionary
            dialog.formats = {
                "gpkg": {
                    "driver": "GPKG",
                    "extension": "gpkg",
                    "description": "SQLite-based OGC standard format (can contain multiple layers)",
                    "display_name": "GeoPackage",
                },
            }

            # Mock user choosing "Yes" (continue with existing GeoPackage)
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes

            # Test successful validation
            result = dialog.validate_input()

            assert result is True
            assert dialog.layer_name == "test_layer"
            assert dialog.selected_format == "gpkg"
            mock_msgbox.question.assert_called_once()

    def test_accept_method(self):
        """Test dialog accept method."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch.object(DlgCreateLayer, "validate_input") as mock_validate,
            patch.object(DlgCreateLayer, "save_preferences") as mock_save_prefs,
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.accept") as mock_super_accept,
        ):
            dialog = DlgCreateLayer()

            # Test successful validation
            mock_validate.return_value = True
            dialog.accept()

            mock_validate.assert_called_once()
            mock_save_prefs.assert_called_once()
            mock_super_accept.assert_called_once()

            # Reset mocks
            mock_validate.reset_mock()
            mock_save_prefs.reset_mock()
            mock_super_accept.reset_mock()

            # Test failed validation
            mock_validate.return_value = False
            dialog.accept()

            mock_validate.assert_called_once()
            mock_save_prefs.assert_not_called()
            mock_super_accept.assert_not_called()

    def test_save_preferences(self):
        """Test saving preferences."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch("dip_strike_tools.toolbelt.preferences.PlgOptionsManager") as mock_options_manager,
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.geo_type_combo = Mock()
            dialog.log = Mock()

            # Test successful preference save
            dialog.geo_type_combo.currentData.return_value = "code"
            dialog.save_preferences()

            mock_options_manager.set_geo_type_storage_mode.assert_called_with("code")
            dialog.log.assert_called()

    def test_get_layer_config(self):
        """Test getting layer configuration."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components and dialog state
            dialog.geo_type_check = Mock()
            dialog.age_check = Mock()
            dialog.lithology_check = Mock()
            dialog.notes_check = Mock()
            dialog.geo_type_combo = Mock()
            dialog.apply_symbology_check = Mock()

            # Set up dialog state
            dialog.layer_name = "test_layer"
            dialog.selected_format = "shapefile"
            dialog.output_path = "/path/to/test.shp"
            dialog.selected_crs = Mock()
            dialog.formats = {
                "shapefile": {
                    "driver": "ESRI Shapefile",
                    "extension": "shp",
                    "description": "Standard shapefile format",
                    "display_name": "ESRI Shapefile",
                },
            }

            # Set up checkbox states
            dialog.geo_type_check.isChecked.return_value = True
            dialog.age_check.isChecked.return_value = False
            dialog.lithology_check.isChecked.return_value = True
            dialog.notes_check.isChecked.return_value = False
            dialog.geo_type_combo.currentData.return_value = "code"
            dialog.apply_symbology_check.isChecked.return_value = True

            # Test getting configuration
            config = dialog.get_layer_config()

            expected_config = {
                "name": "test_layer",
                "format": "shapefile",
                "output_path": "/path/to/test.shp",
                "format_info": dialog.formats["shapefile"],
                "geo_type_storage_mode": "code",
                "symbology": {"apply": True},
                "crs": dialog.selected_crs,
                "optional_fields": {
                    "geo_type": True,
                    "age": False,
                    "lithology": True,
                    "notes": False,
                },
            }

            assert config == expected_config

    def test_update_geo_type_storage_visibility(self):
        """Test geo type storage visibility update."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Mock the UI components
            dialog.geo_type_check = Mock()
            dialog.geo_type_combo = Mock()

            # Test when geo_type is checked
            dialog.geo_type_check.isChecked.return_value = True
            dialog.update_geo_type_storage_visibility()
            dialog.geo_type_combo.setVisible.assert_called_with(True)

            # Test when geo_type is unchecked
            dialog.geo_type_check.isChecked.return_value = False
            dialog.update_geo_type_storage_visibility()
            dialog.geo_type_combo.setVisible.assert_called_with(False)


@pytest.mark.integration
class TestDlgCreateLayerIntegration:
    """Integration tests for DlgCreateLayer."""

    def test_format_combo_integration(self):
        """Test format combo box behavior with different formats."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
        ):
            dialog = DlgCreateLayer()

            # Mock UI components for integration test
            dialog.format_combo = Mock()
            dialog.file_widget = Mock()
            dialog.path_label = Mock()
            dialog.desc_label = Mock()
            dialog.name_edit = Mock()

            # Set up formats dictionary
            dialog.formats = {
                "memory": {
                    "driver": "memory",
                    "extension": "",
                    "description": "Temporary layer",
                    "display_name": "Memory Layer",
                },
                "shapefile": {
                    "driver": "ESRI Shapefile",
                    "extension": "shp",
                    "description": "Standard shapefile format",
                    "display_name": "ESRI Shapefile",
                },
                "gpkg": {
                    "driver": "GPKG",
                    "extension": "gpkg",
                    "description": "SQLite-based OGC standard format",
                    "display_name": "GeoPackage",
                },
            }

            # Test memory format -> shapefile format transition
            dialog.format_combo.currentData.return_value = "memory"
            dialog.update_format_options()
            dialog.file_widget.setVisible.assert_called_with(False)

            # Change to shapefile
            dialog.format_combo.currentData.return_value = "shapefile"
            dialog.update_format_options()
            dialog.file_widget.setVisible.assert_called_with(True)

            # Change to GeoPackage
            dialog.format_combo.currentData.return_value = "gpkg"
            dialog.update_format_options()
            dialog.file_widget.setVisible.assert_called_with(True)

    def test_validation_workflow_integration(self):
        """Test complete validation workflow."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
        except ImportError:
            pytest.skip("QGIS modules not available")

        with (
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProject"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsCoordinateReferenceSystem"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsFileWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QgsProjectionSelectionWidget"),
            patch("dip_strike_tools.gui.dlg_create_layer.QMessageBox"),
            patch("dip_strike_tools.gui.dlg_create_layer.QDialog.__init__", return_value=None),
            patch.object(DlgCreateLayer, "setup_ui", return_value=None),
            patch.object(DlgCreateLayer, "get_selected_crs") as mock_get_crs,
            patch("os.path.exists", return_value=False),
            patch("os.makedirs"),
        ):
            dialog = DlgCreateLayer()

            # Mock the tr method to avoid translation issues
            dialog.tr = Mock(side_effect=lambda x: x)

            # Mock UI components for complete workflow
            dialog.name_edit = Mock()
            dialog.format_combo = Mock()
            dialog.file_widget = Mock()
            dialog.apply_symbology_check = Mock()
            dialog.geo_type_check = Mock()
            dialog.age_check = Mock()
            dialog.lithology_check = Mock()
            dialog.notes_check = Mock()
            dialog.geo_type_combo = Mock()
            mock_crs = Mock()
            mock_get_crs.return_value = mock_crs

            # Set up complete dialog state
            dialog.name_edit.text.return_value.strip.return_value = "geological_survey"
            dialog.format_combo.currentData.return_value = "shapefile"
            dialog.file_widget.filePath.return_value.strip.return_value = "/project/geological_survey.shp"
            dialog.apply_symbology_check.isChecked.return_value = True
            dialog.geo_type_check.isChecked.return_value = True
            dialog.age_check.isChecked.return_value = False
            dialog.lithology_check.isChecked.return_value = True
            dialog.notes_check.isChecked.return_value = True
            dialog.geo_type_combo.currentData.return_value = "description"

            # Set up formats dictionary
            dialog.formats = {
                "shapefile": {
                    "driver": "ESRI Shapefile",
                    "extension": "shp",
                    "description": "Standard shapefile format",
                    "display_name": "ESRI Shapefile",
                },
            }

            # Test complete validation process
            result = dialog.validate_input()

            assert result is True
            assert dialog.layer_name == "geological_survey"
            assert dialog.selected_format == "shapefile"
            assert dialog.output_path == "/project/geological_survey.shp"
            assert dialog.apply_symbology is True
            assert dialog.selected_crs == mock_crs

            # Test getting the complete configuration
            config = dialog.get_layer_config()

            assert config["name"] == "geological_survey"
            assert config["format"] == "shapefile"
            assert config["output_path"] == "/project/geological_survey.shp"
            assert config["geo_type_storage_mode"] == "description"
            assert config["symbology"]["apply"] is True
            assert config["optional_fields"]["geo_type"] is True
            assert config["optional_fields"]["age"] is False
            assert config["optional_fields"]["lithology"] is True
            assert config["optional_fields"]["notes"] is True
