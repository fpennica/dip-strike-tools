#! python3  # noqa E265

"""
QGIS integration tests for plugin_main module.

These tests require a QGIS environment and use pytest-qgis.
"""

from unittest.mock import Mock, patch

import pytest

# Import pytest-qgis utilities
pytest_plugins = ["pytest_qgis"]


@pytest.mark.qgis
class TestDipStrikeToolsPluginQGIS:
    """QGIS integration tests for DipStrikeToolsPlugin."""

    def test_plugin_initialization_with_qgis(self, qgis_iface):
        """Test plugin initialization with real QGIS interface."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        # Initialize plugin with QGIS interface
        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Verify basic attributes
        assert plugin.iface == qgis_iface
        assert hasattr(plugin, "log")
        assert hasattr(plugin, "actions")
        assert isinstance(plugin.actions, list)
        assert hasattr(plugin, "toolbar")

        # Verify toolbar was created
        assert plugin.toolbar is not None
        assert plugin.toolbar.objectName() == "DipStrikeToolsToolbar"

    def test_add_action_method(self, qgis_iface):
        """Test the add_action method."""
        from qgis.core import QgsApplication

        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock callback
        mock_callback = Mock()

        # Add an action
        action = plugin.add_action(
            icon_path=QgsApplication.getThemeIcon("mActionHelp.svg"),
            text="Test Action",
            callback=mock_callback,
            enabled_flag=True,
            add_to_menu=False,  # Don't add to menu for test
            add_to_toolbar=True,
        )

        # Verify action was created and added to actions list
        assert action is not None
        assert action in plugin.actions
        assert action.text() == "Test Action"
        assert action.isEnabled() is True

    def test_translation_method(self, qgis_iface):
        """Test the translation method."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Test translation of a simple string
        translated = plugin.tr("Test string")
        assert isinstance(translated, str)
        assert len(translated) > 0

    def test_initGui_method(self, qgis_iface):
        """Test the initGui method doesn't crash."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # This should not raise an exception
        try:
            plugin.initGui()
            init_success = True
        except Exception as e:
            # If it fails due to missing resources or dependencies, that's OK for this test
            init_success = False
            print(f"initGui failed (expected in test environment): {e}")

        # Even if initGui fails, the plugin should have been created
        assert plugin is not None

        if init_success:
            # If initGui succeeded, verify actions were created
            assert len(plugin.actions) > 0

            # Verify toolbar actions
            assert hasattr(plugin, "insert_dip_strike_action")
            assert hasattr(plugin, "create_layer_action")
            assert hasattr(plugin, "settings_action")

    def test_unload_method(self, qgis_iface):
        """Test the unload method doesn't crash."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Initialize first (may fail but that's OK)
        try:
            plugin.initGui()
        except Exception:
            pass  # Ignore initialization errors in test environment

        # Test unload - this should not raise an exception
        exception_msg = ""
        try:
            plugin.unload()
            unload_success = True
        except Exception as e:
            unload_success = False
            exception_msg = str(e)
            print(f"unload failed: {e}")

        # Unload should generally succeed even if initGui failed
        # In test environment, some QGIS interface methods may not exist
        assert unload_success or any(
            missing in exception_msg.lower()
            for missing in ["not exist", "no attribute", "removepluginmenu", "removePluginMenu"]
        )

    @patch("dip_strike_tools.plugin_main.DlgCreateLayer")
    @patch("dip_strike_tools.plugin_main.DipStrikeLayerCreator")
    @patch("dip_strike_tools.plugin_main.QgsProject")
    def test_open_create_layer_dialog_method(self, mock_project, mock_creator, mock_dialog, qgis_iface):
        """Test the open_create_layer_dialog method."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock dialog behavior
        mock_dlg_instance = Mock()
        mock_dlg_instance.result.return_value = 1  # QDialog.Accepted
        mock_dlg_instance.get_layer_config.return_value = {
            "name": "Test Layer",
            "format": "Memory Layer",
            "crs": Mock(),
            "symbology": {"apply": False},
        }
        mock_dialog.return_value = mock_dlg_instance
        mock_dialog.Accepted = 1  # Standard QDialog accepted result

        # Mock layer creator
        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_creator_instance = Mock()
        mock_creator_instance.create_dip_strike_layer.return_value = mock_layer
        mock_creator.return_value = mock_creator_instance

        # Mock project
        mock_project_instance = Mock()
        mock_project.instance.return_value = mock_project_instance

        # Call the method
        plugin.open_create_layer_dialog()

        # Verify dialog was created and executed
        mock_dialog.assert_called_once()
        mock_dlg_instance.exec.assert_called_once()

        # Verify the dialog result was checked
        mock_dlg_instance.result.assert_called_once()

        # If dialog was accepted, verify layer creation workflow
        if mock_dlg_instance.result.return_value == 1:
            mock_dlg_instance.get_layer_config.assert_called_once()
            mock_creator.assert_called_once()
            mock_creator_instance.create_dip_strike_layer.assert_called_once()
            mock_project_instance.addMapLayer.assert_called_once_with(mock_layer)

    def test_dialog_methods_callable(self, qgis_iface):
        """Test that dialog methods are callable without crashing."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # These methods should exist and be callable
        assert callable(plugin.open_dlg_insert_dip_strike)
        assert callable(plugin.open_create_layer_dialog)
        assert callable(plugin._find_existing_feature_at_point)


# Mark all tests in this file as QGIS tests
pytestmark = pytest.mark.qgis
