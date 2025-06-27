"""
Tests for the DlgCreateLayer dialog.
"""

from unittest.mock import patch

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
