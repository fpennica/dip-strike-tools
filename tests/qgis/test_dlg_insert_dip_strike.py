#! python3  # noqa E265

"""
QGIS integration tests for DlgInsertDipStrike dialog.

These tests require a QGIS environment and use pytest-qgis.
"""

from unittest.mock import Mock, patch

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


# Mark all tests in this file as QGIS tests
pytestmark = pytest.mark.qgis
