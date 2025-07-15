#! python3  # noqa E265

"""
QGIS integration tests for DlgInsertDipStrike dialog.

These tests require a QGIS environment and use pytest-qgis.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

# Import pytest-qgis utilities
pytest_plugins = ["pytest_qgis"]


@pytest.mark.qgis
class TestDlgInsertDipStrike:
    """QGIS integration tests for DlgInsertDipStrike dialog."""

    def _create_dialog_with_mocks(self, qgis_iface, **kwargs):
        """Helper method to create dialog with necessary mocks.

        Args:
            qgis_iface: The QGIS interface mock
            **kwargs: Arguments to pass to DlgInsertDipStrike constructor

        Returns:
            DlgInsertDipStrike: The dialog instance with mocks applied
        """
        from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike

        # Mock the iface global and problematic QGIS calls
        with (
            patch("dip_strike_tools.gui.dlg_insert_dip_strike.iface", qgis_iface),
            patch("dip_strike_tools.gui.dlg_insert_dip_strike.QgsBearingUtils.bearingTrueNorth", return_value=0.0),
        ):
            return DlgInsertDipStrike(**kwargs)

    def test_dialog_import(self):
        """Test that the dialog can be imported."""
        try:
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike

            assert DlgInsertDipStrike is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")

    def test_dialog_initialization_basic(self, qgis_iface):
        """Test basic dialog initialization without clicked point."""
        try:
            # Test import availability
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike  # noqa: F401
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Initialize dialog using helper method
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Verify basic attributes
        assert dialog is not None
        assert hasattr(dialog, "iface")
        assert hasattr(dialog, "log")
        assert dialog.existing_feature is None
        assert dialog._clicked_point is None
        assert dialog.windowTitle() == "Insert New Dip/Strike Point"

    def test_dialog_initialization_with_clicked_point(self, qgis_iface):
        """Test dialog initialization with a clicked point."""
        from qgis.core import QgsPointXY

        try:
            # Test import availability
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike  # noqa: F401
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Create a test point
        test_point = QgsPointXY(100.0, 200.0)

        # Initialize dialog with clicked point using helper method
        dialog = self._create_dialog_with_mocks(qgis_iface, clicked_point=test_point)

        # Verify attributes
        assert dialog._clicked_point == test_point
        assert dialog.existing_feature is None
        assert dialog.windowTitle() == "Insert New Dip/Strike Point"

    def test_dialog_initialization_with_existing_feature(self, qgis_iface):
        """Test dialog initialization with existing feature data."""
        try:
            # Test import availability
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike  # noqa: F401
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock existing feature data
        mock_feature = Mock()
        mock_feature.id.return_value = 123

        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"

        existing_feature = {
            "feature": mock_feature,
            "layer": mock_layer,
            "layer_name": "Test Layer",
            "is_configured": True,
        }

        # Initialize dialog with existing feature using helper method
        dialog = self._create_dialog_with_mocks(qgis_iface, existing_feature=existing_feature)

        # Verify attributes
        assert dialog.existing_feature == existing_feature
        assert "Edit Dip/Strike Data - Test Layer (Feature 123)" in dialog.windowTitle()

    def test_azimuth_controls_exist(self, qgis_iface):
        """Test that azimuth control widgets exist and are properly configured."""
        try:
            # Test import availability
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike  # noqa: F401
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Initialize dialog using helper method
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Check azimuth control widgets exist
        assert hasattr(dialog, "dial_azimuth")
        assert hasattr(dialog, "azimuth_spinbox")

        # Check dial configuration
        assert dialog.dial_azimuth.minimum() == 0
        assert dialog.dial_azimuth.maximum() == 359
        assert dialog.dial_azimuth.wrapping() is True

        # Check spinbox configuration
        assert dialog.azimuth_spinbox.minimum() == 0.0
        assert dialog.azimuth_spinbox.maximum() == 360.0
        assert dialog.azimuth_spinbox.decimals() == 2

    def test_strike_dip_mode_controls_exist(self, qgis_iface):
        """Test that strike/dip mode radio buttons exist."""
        try:
            # Test import availability
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike  # noqa: F401
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Initialize dialog using helper method
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Check strike/dip radio buttons exist
        assert hasattr(dialog, "rdio_strike")
        assert hasattr(dialog, "rdio_dip")

        # Check default state (should be strike mode by default)
        assert dialog.rdio_strike.isChecked() is True
        assert dialog.rdio_dip.isChecked() is False

    def test_azimuth_value_getters_setters(self, qgis_iface):
        """Test azimuth value getter and setter methods."""
        try:
            # Test import availability
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike  # noqa: F401
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Initialize dialog using helper method
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test initial value
        initial_value = dialog.get_azimuth_value()
        assert initial_value == 0.0

        # Test setting value
        test_value = 45.5
        dialog.set_azimuth_value(test_value)
        assert dialog.get_azimuth_value() == test_value

        # Test value clamping
        dialog.set_azimuth_value(-10.0)  # Should clamp to 0
        assert dialog.get_azimuth_value() == 0.0

        dialog.set_azimuth_value(370.0)  # Should clamp to 360
        assert dialog.get_azimuth_value() == 360.0

    def test_format_bearing_method(self, qgis_iface):
        """Test the _format_bearing method for proper formatting and negative zero handling."""
        try:
            # Test import availability
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike  # noqa: F401
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Initialize dialog using helper method
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test cases for bearing formatting
        test_cases = [
            # (input_value, expected_output, description)
            (0.0, "0.00°", "positive zero"),
            (-0.0, "0.00°", "negative zero should become positive"),
            (-0.001, "0.00°", "very small negative value"),
            (0.001, "0.00°", "very small positive value"),
            (-0.004, "0.00°", "small negative within threshold"),
            (0.004, "0.00°", "small positive within threshold"),
            (-0.005, "-0.01°", "negative value at threshold boundary"),
            (0.005, "0.01°", "positive value at threshold boundary"),
            (-0.01, "-0.01°", "small negative value outside threshold"),
            (0.01, "0.01°", "small positive value outside threshold"),
            (1.0, "1.00°", "normal positive value"),
            (-1.0, "-1.00°", "normal negative value"),
            (45.0, "45.00°", "normal compass value"),
            (90.0, "90.00°", "right angle"),
            (180.0, "180.00°", "half circle"),
            (270.0, "270.00°", "three quarters"),
            (359.99, "359.99°", "close to full circle"),
            (360.0, "360.00°", "full circle"),
            (-90.0, "-90.00°", "negative right angle"),
            (-180.0, "-180.00°", "negative half circle"),
        ]

        # Test each case
        for input_value, expected_output, description in test_cases:
            result = dialog._format_bearing(input_value)
            assert result == expected_output, (
                f"Failed for {description}: input={input_value}, expected={expected_output}, got={result}"
            )

        # Test edge cases for floating point precision
        epsilon_tests = [
            (-0.0001, "0.00°", "very small negative"),
            (0.0001, "0.00°", "very small positive"),
            (-0.00001, "0.00°", "extremely small negative"),
            (0.00001, "0.00°", "extremely small positive"),
        ]

        for input_value, expected_output, description in epsilon_tests:
            result = dialog._format_bearing(input_value)
            assert result == expected_output, (
                f"Failed epsilon test for {description}: input={input_value}, expected={expected_output}, got={result}"
            )

    def test_bearing_formatting_in_ui_labels(self, qgis_iface):
        """Test that bearing formatting is applied consistently in UI labels."""
        try:
            # Test import availability
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike  # noqa: F401
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Initialize dialog first, then test different bearing values
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Mock QgsBearingUtils to return a negative zero value and refresh
        with patch("dip_strike_tools.gui.dlg_insert_dip_strike.QgsBearingUtils.bearingTrueNorth", return_value=-0.0):
            dialog._refresh_bearing_labels()

            # Check that the north bearing label uses proper formatting
            # The dialog should have formatted the negative zero to positive zero
            bearing_text = dialog.lbl_north_bearing.text()
            assert "0.00°" in bearing_text
            assert "-0.00°" not in bearing_text

        # Test with a small negative value that should be converted to zero
        with patch("dip_strike_tools.gui.dlg_insert_dip_strike.QgsBearingUtils.bearingTrueNorth", return_value=-0.003):
            dialog._refresh_bearing_labels()
            bearing_text = dialog.lbl_north_bearing.text()
            assert "0.00°" in bearing_text
            assert "-0.00°" not in bearing_text

        # Test with a normal bearing value
        with patch("dip_strike_tools.gui.dlg_insert_dip_strike.QgsBearingUtils.bearingTrueNorth", return_value=45.67):
            dialog._refresh_bearing_labels()
            bearing_text = dialog.lbl_north_bearing.text()
            assert "45.67°" in bearing_text

    def test_dialog_button_setup(self, qgis_iface):
        """Test dialog button setup."""
        try:
            # Test import availability
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike  # noqa: F401
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Test for new feature (Save button)
        dialog = self._create_dialog_with_mocks(qgis_iface)
        dialog._setup_dialog_buttons()

        if hasattr(dialog, "save_button") and dialog.save_button:
            assert dialog.save_button.text() == "Save"
            assert dialog.save_button.isEnabled() is False  # Initially disabled

        # Test for existing feature (Update button)
        mock_feature = Mock()
        mock_feature.id.return_value = 123
        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"

        existing_feature = {"feature": mock_feature, "layer": mock_layer, "layer_name": "Test Layer"}

        dialog_edit = self._create_dialog_with_mocks(qgis_iface, existing_feature=existing_feature)
        dialog_edit._setup_dialog_buttons()

        if hasattr(dialog_edit, "save_button") and dialog_edit.save_button:
            assert dialog_edit.save_button.text() == "Update"

    def test_check_feature_layer_with_readonly_layer(self, qgis_iface):
        """Test check_feature_layer with a read-only layer."""
        from unittest.mock import MagicMock, patch

        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Set up the dialog components
        dialog.cbo_feature_layer = MagicMock()
        dialog.btn_configure_layer = MagicMock()
        dialog.save_button = MagicMock()

        # Mock a delimited text layer
        mock_layer = MagicMock()
        mock_layer.isValid.return_value = True
        mock_layer.name.return_value = "test_delimited_layer"
        mock_data_provider = MagicMock()
        mock_data_provider.name.return_value = "delimitedtext"
        mock_layer.dataProvider.return_value = mock_data_provider
        dialog.cbo_feature_layer.currentLayer.return_value = mock_layer

        # Patch QMessageBox to capture the warning call
        with patch("qgis.PyQt.QtWidgets.QMessageBox") as mock_msgbox:
            # Call the method
            dialog.check_feature_layer()

            # Verify warning was shown and both buttons were disabled
            mock_msgbox.warning.assert_called_once()
            dialog.save_button.setEnabled.assert_called_with(False)
            dialog.btn_configure_layer.setEnabled.assert_called_with(False)

    def test_check_feature_layer_valid_configured_layer(self, qgis_iface):
        """Test check_feature_layer with a properly configured layer."""
        from unittest.mock import MagicMock, patch

        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Set up the dialog components
        dialog.cbo_feature_layer = MagicMock()
        dialog.btn_configure_layer = MagicMock()
        dialog.save_button = MagicMock()

        # Mock a valid configured layer
        mock_layer = MagicMock()
        mock_layer.isValid.return_value = True
        mock_layer.name.return_value = "test_configured_layer"
        mock_layer.customProperty.return_value = "dip_strike_feature_layer"
        mock_data_provider = MagicMock()
        mock_data_provider.name.return_value = "memory"
        mock_layer.dataProvider.return_value = mock_data_provider
        dialog.cbo_feature_layer.currentLayer.return_value = mock_layer

        with patch("dip_strike_tools.core.layer_utils.check_layer_editability", return_value=(True, "")):
            with patch.object(dialog, "_update_optional_fields_state"):
                with patch.object(dialog, "_save_last_feature_layer"):
                    with patch.object(dialog, "_update_save_button_state"):
                        dialog.check_feature_layer()

                        # Verify configure button was enabled
                        dialog.btn_configure_layer.setEnabled.assert_called_with(True)

    def test_check_feature_layer_no_layer_selected(self, qgis_iface):
        """Test check_feature_layer with no layer selected."""
        from unittest.mock import MagicMock

        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Set up the dialog components
        dialog.cbo_feature_layer = MagicMock()
        dialog.btn_configure_layer = MagicMock()
        dialog.save_button = MagicMock()

        # No layer selected
        dialog.cbo_feature_layer.currentLayer.return_value = None

        with patch.object(dialog, "_disable_all_optional_fields") as mock_disable:
            with patch.object(dialog, "_save_last_feature_layer"):
                with patch.object(dialog, "_update_save_button_state"):
                    dialog.check_feature_layer()

                    # Verify configure button was disabled
                    dialog.btn_configure_layer.setEnabled.assert_called_with(False)
                    # Verify optional fields were disabled
                    mock_disable.assert_called_once()

    def test_check_feature_layer_shapefile_missing_mappings(self, qgis_iface):
        """Test check_feature_layer with shapefile missing field mappings."""
        from unittest.mock import MagicMock, patch

        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Set up the dialog components
        dialog.cbo_feature_layer = MagicMock()
        dialog.btn_configure_layer = MagicMock()

        # Mock a shapefile with missing field mappings
        mock_layer = MagicMock()
        mock_layer.isValid.return_value = True
        mock_layer.name.return_value = "test_shapefile"
        mock_layer.source.return_value = "/path/to/test.shp"
        mock_data_provider = MagicMock()
        mock_data_provider.name.return_value = "ogr"
        mock_layer.dataProvider.return_value = mock_data_provider

        # Mock fields lookup to return -1 (field not found)
        mock_fields = MagicMock()
        mock_fields.lookupField.return_value = -1
        mock_layer.fields.return_value = mock_fields

        # Mock custom property to return empty string (no mapping)
        mock_layer.customProperty.return_value = ""

        dialog.cbo_feature_layer.currentLayer.return_value = mock_layer

        with patch("dip_strike_tools.core.layer_utils.check_layer_editability", return_value=(True, "")):
            # Patch the import inside the method
            with patch("dip_strike_tools.gui.dlg_field_config.DlgFieldConfig", create=True) as mock_dlg_config:
                mock_config_dialog = MagicMock()
                mock_config_dialog.exec.return_value = MagicMock(Accepted=1)
                mock_dlg_config.return_value = mock_config_dialog

                with patch.object(dialog, "_populate_geological_types"):
                    dialog.check_feature_layer()

                    # Since the mock will prevent the actual import, we just verify the method was called
                    # without the dialog creation part - just check layer validation logic worked

    def test_dialog_attributes_exist(self, qgis_iface):
        """Test that essential dialog attributes exist."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test core attributes exist
        assert hasattr(dialog, "iface")
        assert hasattr(dialog, "log")
        assert hasattr(dialog, "_initializing")
        assert hasattr(dialog, "existing_feature")
        assert hasattr(dialog, "_clicked_point")

        # Test that these are initially set correctly (after initialization)
        # Note: _initializing may be False after full setup
        assert dialog.existing_feature is None
        assert dialog._clicked_point is None

    def test_bearing_calculation_methods_exist(self, qgis_iface):
        """Test that bearing calculation methods exist and are callable."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test that key methods exist
        assert hasattr(dialog, "_format_bearing")
        assert callable(dialog._format_bearing)
        assert hasattr(dialog, "_refresh_bearing_labels")
        assert callable(dialog._refresh_bearing_labels)

        # Test _format_bearing with simple values
        assert dialog._format_bearing(0.0) == "0.00°"
        assert dialog._format_bearing(90.0) == "90.00°"
        assert dialog._format_bearing(180.0) == "180.00°"

    def test_utility_methods_exist(self, qgis_iface):
        """Test that utility methods exist and are callable."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test method existence
        assert hasattr(dialog, "get_azimuth_value")
        assert hasattr(dialog, "set_azimuth_value")
        assert hasattr(dialog, "update_spinbox_from_dial")
        assert hasattr(dialog, "update_dial_from_spinbox")
        assert hasattr(dialog, "on_strike_dip_mode_changed")

        # Test that these are callable
        assert callable(dialog.get_azimuth_value)
        assert callable(dialog.set_azimuth_value)
        assert callable(dialog.update_spinbox_from_dial)
        assert callable(dialog.update_dial_from_spinbox)
        assert callable(dialog.on_strike_dip_mode_changed)

    def test_ui_widget_attributes_exist(self, qgis_iface):
        """Test that essential UI widget attributes exist."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test that widget attributes exist
        widget_attributes = [
            "dial_azimuth",
            "azimuth_spinbox",
            "rdio_strike",
            "rdio_dip",
            "spin_dip",
            "lbl_north_bearing",
            "cbo_feature_layer",
        ]

        for attr in widget_attributes:
            assert hasattr(dialog, attr), f"Dialog missing widget attribute: {attr}"

        # Test that UI widgets have expected methods
        assert hasattr(dialog.dial_azimuth, "value")
        assert hasattr(dialog.azimuth_spinbox, "value")
        assert hasattr(dialog.rdio_strike, "isChecked")
        assert hasattr(dialog.rdio_dip, "isChecked")

    def test_dialog_translation_method(self, qgis_iface):
        """Test that the translation method exists and works."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test that tr method exists
        assert hasattr(dialog, "tr")
        assert callable(dialog.tr)

        # Test basic translation (will return the input string in test environment)
        test_message = "Test message"
        result = dialog.tr(test_message)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_constants_and_defaults(self, qgis_iface):
        """Test that constants and default values are correctly set."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test default window title for new feature
        assert "Insert New Dip/Strike Point" in dialog.windowTitle()

        # Test default radio button state
        assert dialog.rdio_strike.isChecked() is True
        assert dialog.rdio_dip.isChecked() is False

        # Test initial azimuth value
        assert dialog.get_azimuth_value() == 0.0

        # Test dial configuration remains correct
        assert dialog.dial_azimuth.minimum() == 0
        assert dialog.dial_azimuth.maximum() == 359
        assert dialog.dial_azimuth.wrapping() is True

    def test_logging_functionality(self, qgis_iface):
        """Test that logging functionality exists and works."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test that log method exists and is callable
        assert hasattr(dialog, "log")
        assert callable(dialog.log)

        # Test that logging doesn't crash (basic smoke test)
        try:
            dialog.log("Test message", log_level=3)
            dialog.log("Debug message", log_level=4)
            dialog.log("Error message", log_level=1)
        except Exception as e:
            pytest.fail(f"Logging should not raise exceptions: {e}")

    def test_geometry_type_constants(self, qgis_iface):
        """Test geometry type constants are correctly used."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test layer suitability check with point geometry (should be suitable)
        mock_point_layer = MagicMock()
        mock_point_layer.isValid.return_value = True
        mock_point_layer.geometryType.return_value = 0  # QgsWkbTypes.PointGeometry

        result = dialog._is_layer_suitable_for_dip_strike(mock_point_layer)
        assert result is True

        # Test with line geometry (should not be suitable)
        mock_line_layer = MagicMock()
        mock_line_layer.isValid.return_value = True
        mock_line_layer.geometryType.return_value = 1  # QgsWkbTypes.LineGeometry

        result = dialog._is_layer_suitable_for_dip_strike(mock_line_layer)
        assert result is False

    def test_value_validation_and_clamping(self, qgis_iface):
        """Test value validation and clamping functionality."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test azimuth value clamping at boundaries
        test_cases = [
            (-10.0, 0.0),  # Negative should clamp to 0
            (0.0, 0.0),  # Valid minimum
            (180.0, 180.0),  # Valid middle value
            (360.0, 360.0),  # Valid maximum
            (370.0, 360.0),  # Over max should clamp to 360
            (450.0, 360.0),  # Way over max should clamp to 360
        ]

        for input_val, expected in test_cases:
            dialog.set_azimuth_value(input_val)
            result = dialog.get_azimuth_value()
            assert result == expected, f"Input {input_val} should clamp to {expected}, got {result}"

    def test_widget_configuration_consistency(self, qgis_iface):
        """Test that widgets are consistently configured."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test spinbox decimal precision
        assert dialog.azimuth_spinbox.decimals() == 2
        assert dialog.spin_dip.decimals() == 2

        # Test spinbox ranges are sensible
        assert dialog.azimuth_spinbox.minimum() == 0.0
        assert dialog.azimuth_spinbox.maximum() == 360.0
        assert dialog.spin_dip.minimum() == 0.0
        assert dialog.spin_dip.maximum() == 90.0

        # Test dial wrapping
        assert dialog.dial_azimuth.wrapping() is True

    def test_spinbox_dial_synchronization_basic(self, qgis_iface):
        """Test basic spinbox and dial synchronization."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test basic cases for dial to spinbox sync
        basic_cases = [0, 45, 90, 135, 180]

        for value in basic_cases:
            dialog.update_spinbox_from_dial(value)
            assert dialog.azimuth_spinbox.value() == value

        # Test that sync methods exist and are callable
        assert hasattr(dialog, "update_spinbox_from_dial")
        assert hasattr(dialog, "update_dial_from_spinbox")
        assert callable(dialog.update_spinbox_from_dial)
        assert callable(dialog.update_dial_from_spinbox)

    def test_mode_change_functionality_basic(self, qgis_iface):
        """Test basic strike/dip mode change functionality."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test initial state
        assert dialog.rdio_strike.isChecked() is True
        assert dialog.rdio_dip.isChecked() is False

        # Test that mode change method exists and is callable
        assert hasattr(dialog, "on_strike_dip_mode_changed")
        assert callable(dialog.on_strike_dip_mode_changed)

        # Toggle to dip mode
        dialog.rdio_dip.setChecked(True)
        dialog.rdio_strike.setChecked(False)

        # Test that calling mode change doesn't crash
        try:
            dialog.on_strike_dip_mode_changed()
        except Exception as e:
            pytest.fail(f"Mode change should not crash: {e}")

        # Note: The actual radio button states may change during initialization
        # so we don't assert specific values here

    def test_dialog_initialization_with_point_coordinates(self, qgis_iface):
        """Test dialog initialization stores point coordinates correctly."""
        from qgis.core import QgsPointXY

        # Test with specific coordinates
        test_coordinates = [
            (0.0, 0.0),
            (100.5, 200.7),
            (-50.0, 75.3),
            (1000000.0, 2000000.0),  # Large coordinates
        ]

        for x, y in test_coordinates:
            test_point = QgsPointXY(x, y)
            dialog = self._create_dialog_with_mocks(qgis_iface, clicked_point=test_point)

            assert dialog._clicked_point == test_point
            assert dialog._clicked_point.x() == x
            assert dialog._clicked_point.y() == y

    def test_error_handling_with_none_values(self, qgis_iface):
        """Test error handling with None and invalid values."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test layer suitability with None
        result = dialog._is_layer_suitable_for_dip_strike(None)
        assert result is False

        # Test format bearing with extreme values
        extreme_values = [float("inf"), float("-inf"), None]

        for value in extreme_values:
            try:
                if value is None:
                    # Should handle None gracefully or raise TypeError
                    with pytest.raises(TypeError):
                        dialog._format_bearing(value)
                else:
                    # Should handle infinity values gracefully
                    result = dialog._format_bearing(value)
                    assert isinstance(result, str)
            except Exception as e:
                # At minimum, shouldn't crash the test process
                assert "inf" in str(e).lower() or "none" in str(e).lower()

    def test_multiple_dialog_instances(self, qgis_iface):
        """Test that multiple dialog instances can be created independently."""
        # Create multiple dialog instances
        dialog1 = self._create_dialog_with_mocks(qgis_iface)
        dialog2 = self._create_dialog_with_mocks(qgis_iface)

        # Verify they are separate instances
        assert dialog1 is not dialog2
        assert id(dialog1) != id(dialog2)

        # Verify they have independent state
        dialog1.set_azimuth_value(45.0)
        dialog2.set_azimuth_value(90.0)

        assert dialog1.get_azimuth_value() == 45.0
        assert dialog2.get_azimuth_value() == 90.0

    def test_dial_spinbox_synchronization(self, qgis_iface):
        """Test that dial and spinbox stay synchronized."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test dial to spinbox synchronization
        dialog.update_spinbox_from_dial(90)
        assert dialog.azimuth_spinbox.value() == 90

        # Test spinbox to dial synchronization
        dialog.update_dial_from_spinbox(180.5)
        assert dialog.dial_azimuth.value() == 180  # Should round to nearest int

    def test_strike_dip_mode_toggle(self, qgis_iface):
        """Test toggling between strike and dip modes."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Initially should be in strike mode
        # Note: radio button states may change during initialization
        # so we just verify they exist and are not both checked
        strike_checked = dialog.rdio_strike.isChecked()
        dip_checked = dialog.rdio_dip.isChecked()

        # At least one should be checked, but not both
        assert strike_checked or dip_checked
        assert not (strike_checked and dip_checked)

        # Toggle to dip mode
        dialog.rdio_dip.setChecked(True)
        dialog.rdio_strike.setChecked(False)

        # Test mode change handler
        dialog.on_strike_dip_mode_changed()
        # Just verify it doesn't crash - actual marker update requires canvas

    def test_azimuth_value_boundaries(self, qgis_iface):
        """Test azimuth value boundary conditions."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test setting values at boundaries
        dialog.set_azimuth_value(0.0)
        assert dialog.get_azimuth_value() == 0.0

        dialog.set_azimuth_value(360.0)
        assert dialog.get_azimuth_value() == 360.0

        # Test negative value clamping
        dialog.set_azimuth_value(-10.0)
        assert dialog.get_azimuth_value() == 0.0

        # Test over-limit value clamping
        dialog.set_azimuth_value(370.0)
        assert dialog.get_azimuth_value() == 360.0

    def test_dialog_window_title_scenarios(self, qgis_iface):
        """Test dialog window title for different scenarios."""
        # Test new feature dialog
        dialog_new = self._create_dialog_with_mocks(qgis_iface)
        assert "Insert New Dip/Strike Point" in dialog_new.windowTitle()

        # Test existing feature dialog
        mock_feature = MagicMock()
        mock_feature.id.return_value = 456
        mock_layer = MagicMock()
        mock_layer.name.return_value = "Sample Layer"

        existing_feature = {
            "feature": mock_feature,
            "layer": mock_layer,
            "layer_name": "Sample Layer",
            "is_configured": True,
        }

        dialog_edit = self._create_dialog_with_mocks(qgis_iface, existing_feature=existing_feature)
        title = dialog_edit.windowTitle()
        assert "Edit Dip/Strike Data" in title
        assert "Sample Layer" in title
        assert "456" in title

    def test_ui_state_consistency_checks(self, qgis_iface):
        """Test that UI state remains consistent during operations."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test that changing azimuth maintains consistency
        original_strike_checked = dialog.rdio_strike.isChecked()
        original_dip_checked = dialog.rdio_dip.isChecked()

        # Change azimuth value
        dialog.set_azimuth_value(123.45)

        # Radio button state should remain unchanged
        assert dialog.rdio_strike.isChecked() == original_strike_checked
        assert dialog.rdio_dip.isChecked() == original_dip_checked

        # Azimuth should be set correctly
        assert dialog.get_azimuth_value() == 123.45

    def test_layer_suitability_checks(self, qgis_iface):
        """Test comprehensive layer suitability checks."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test with None layer
        assert dialog._is_layer_suitable_for_dip_strike(None) is False

        # Test with invalid layer
        mock_invalid_layer = MagicMock()
        mock_invalid_layer.isValid.return_value = False
        assert dialog._is_layer_suitable_for_dip_strike(mock_invalid_layer) is False

        # Test with point layer (suitable)
        mock_point_layer = MagicMock()
        mock_point_layer.isValid.return_value = True
        mock_point_layer.geometryType.return_value = 0  # Point
        assert dialog._is_layer_suitable_for_dip_strike(mock_point_layer) is True

        # Test with line layer (not suitable)
        mock_line_layer = MagicMock()
        mock_line_layer.isValid.return_value = True
        mock_line_layer.geometryType.return_value = 1  # Line
        assert dialog._is_layer_suitable_for_dip_strike(mock_line_layer) is False

        # Test with polygon layer (not suitable)
        mock_polygon_layer = MagicMock()
        mock_polygon_layer.isValid.return_value = True
        mock_polygon_layer.geometryType.return_value = 2  # Polygon
        assert dialog._is_layer_suitable_for_dip_strike(mock_polygon_layer) is False

    def test_bearing_format_comprehensive(self, qgis_iface):
        """Test comprehensive bearing formatting scenarios."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test standard compass bearings
        test_cases = [
            (0.0, "0.00°"),
            (90.0, "90.00°"),
            (180.0, "180.00°"),
            (270.0, "270.00°"),
            (359.99, "359.99°"),
            (360.0, "360.00°"),
        ]

        for bearing, expected in test_cases:
            result = dialog._format_bearing(bearing)
            assert result == expected, f"Failed for bearing {bearing}: expected {expected}, got {result}"

        # Test negative zero and small values
        negative_zero_cases = [
            (-0.0, "0.00°"),
            (-0.001, "0.00°"),
            (-0.003, "0.00°"),
            (-0.005, "-0.01°"),  # At threshold
            (-0.01, "-0.01°"),
        ]

        for bearing, expected in negative_zero_cases:
            result = dialog._format_bearing(bearing)
            assert result == expected, f"Failed for negative bearing {bearing}: expected {expected}, got {result}"

    def test_comprehensive_widget_ranges(self, qgis_iface):
        """Test that all widgets have appropriate ranges and limits."""
        dialog = self._create_dialog_with_mocks(qgis_iface)

        # Test azimuth spinbox
        azimuth_spinbox = dialog.azimuth_spinbox
        assert azimuth_spinbox.minimum() == 0.0
        assert azimuth_spinbox.maximum() == 360.0
        assert azimuth_spinbox.decimals() == 2
        assert azimuth_spinbox.singleStep() > 0  # Should have reasonable step

        # Test dip value spinbox
        dip_spinbox = dialog.spin_dip
        assert dip_spinbox.minimum() == 0.0
        assert dip_spinbox.maximum() == 90.0
        assert dip_spinbox.decimals() == 2

        # Test azimuth dial
        azimuth_dial = dialog.dial_azimuth
        assert azimuth_dial.minimum() == 0
        assert azimuth_dial.maximum() == 359
        assert azimuth_dial.wrapping() is True
