#! python3  # noqa E265

"""
Unit tests for plugin_main module.

These tests focus on basic functionality that doesn't require QGIS environment.
"""

from unittest.mock import Mock, patch

import pytest


class TestDipStrikeToolsPluginBasic:
    """Basic tests for DipStrikeToolsPlugin that don't require QGIS."""

    def test_plugin_import(self):
        """Test that the plugin module can be imported."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

            assert DipStrikeToolsPlugin is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")

    @patch("dip_strike_tools.plugin_main.QgsSettings")
    @patch("dip_strike_tools.plugin_main.QLocale")
    @patch("dip_strike_tools.plugin_main.PlgLogger")
    def test_plugin_initialization(self, mock_logger, mock_locale, mock_settings):
        """Test plugin initialization with mocked dependencies."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock the QGIS interface
        mock_iface = Mock()
        mock_iface.addToolBar.return_value = Mock()

        # Mock settings
        mock_settings.return_value.value.return_value = "en"
        mock_locale.return_value.name.return_value = "en_US"

        # Mock logger
        mock_log_instance = Mock()
        mock_logger.return_value.log = mock_log_instance

        # Initialize plugin
        plugin = DipStrikeToolsPlugin(mock_iface)

        # Verify basic attributes
        assert plugin.iface == mock_iface
        assert plugin.log == mock_log_instance
        assert hasattr(plugin, "actions")
        assert isinstance(plugin.actions, list)
        assert hasattr(plugin, "locale")
        assert hasattr(plugin, "menu")
        assert hasattr(plugin, "toolbar")

    def test_tr_method_exists(self):
        """Test that the translation method exists and is callable."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Check if the class has the tr method
        assert hasattr(DipStrikeToolsPlugin, "tr")
        assert callable(getattr(DipStrikeToolsPlugin, "tr"))

    def test_plugin_methods_exist(self):
        """Test that required plugin methods exist."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Check for required QGIS plugin methods
        required_methods = [
            "initGui",
            "unload",
            "tr",
        ]

        for method_name in required_methods:
            assert hasattr(DipStrikeToolsPlugin, method_name), f"Missing required method: {method_name}"
            assert callable(getattr(DipStrikeToolsPlugin, method_name)), f"Method {method_name} is not callable"

    def test_custom_methods_exist(self):
        """Test that custom plugin methods exist."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Check for custom methods we added
        custom_methods = [
            "toggle_dip_strike_tool",
            "activate_dip_strike_tool",
            "deactivate_dip_strike_tool",
            "on_map_tool_changed",
            "open_dlg_insert_dip_strike",
            "open_create_layer_dialog",
            "_find_existing_feature_at_point",
        ]

        for method_name in custom_methods:
            assert hasattr(DipStrikeToolsPlugin, method_name), f"Missing custom method: {method_name}"
            assert callable(getattr(DipStrikeToolsPlugin, method_name)), f"Method {method_name} is not callable"


class TestPluginConstants:
    """Test plugin constants and configuration."""

    def test_about_module_accessible(self):
        """Test that __about__ module is accessible."""
        try:
            from dip_strike_tools.__about__ import __title__, __version__

            assert __title__ is not None
            assert __version__ is not None
        except ImportError:
            pytest.fail("Could not import plugin metadata")

    def test_core_modules_importable(self):
        """Test that core modules can be imported."""
        try:
            from dip_strike_tools.core import DipStrikeMapTool
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator

            assert DipStrikeLayerCreator is not None
            assert DipStrikeMapTool is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")

    def test_gui_modules_importable(self):
        """Test that GUI modules can be imported."""
        try:
            from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
            from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike

            assert DlgCreateLayer is not None
            assert DlgInsertDipStrike is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")


# Mark all tests in this file as unit tests
pytestmark = pytest.mark.unit
