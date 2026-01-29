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

#! python3  # noqa E265

"""
Unit tests for plugin_main module.

These tests focus on basic functionality that doesn't require QGIS environment.
"""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
class TestDipStrikeToolsPluginBasic:
    """Basic tests for DipStrikeToolsPlugin that don't require QGIS."""

    def test_plugin_import(self):
        """Test that the plugin module can be imported."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

            assert DipStrikeToolsPlugin is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")

    @patch("dip_strike_tools.plugin_main.PluginInfo")
    @patch("dip_strike_tools.plugin_main.QgsSettings")
    @patch("dip_strike_tools.plugin_main.QLocale")
    @patch("dip_strike_tools.plugin_main.PlgLogger")
    def test_plugin_initialization(self, mock_logger, mock_locale, mock_settings, mock_plugin_info):
        """Test plugin initialization with mocked dependencies."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock the QGIS interface
        mock_iface = Mock()
        mock_iface.addToolBar.return_value = Mock()
        mock_iface.mainWindow.return_value = None  # Return None instead of Mock for Qt compatibility

        # Mock settings
        mock_settings.return_value.value.return_value = "en"
        mock_locale.return_value.name.return_value = "en_US"

        # Mock logger
        mock_log_instance = Mock()
        mock_logger.return_value.log = mock_log_instance

        # Mock PluginInfo dialog
        mock_plugin_info.return_value = Mock()

        # Initialize plugin
        plugin = DipStrikeToolsPlugin(mock_iface)

        # Verify basic attributes
        assert plugin.iface == mock_iface
        assert plugin.log == mock_log_instance
        assert hasattr(plugin, "locale")
        assert hasattr(plugin, "menu")
        assert hasattr(plugin, "toolbar")

    @patch("dip_strike_tools.plugin_main.PluginInfo")
    @patch("dip_strike_tools.plugin_main.QgsSettings")
    @patch("dip_strike_tools.plugin_main.QLocale")
    @patch("dip_strike_tools.plugin_main.PlgLogger")
    @patch("dip_strike_tools.plugin_main.QTranslator")
    @patch("dip_strike_tools.plugin_main.QCoreApplication")
    @patch("dip_strike_tools.plugin_main.DIR_PLUGIN_ROOT")
    def test_plugin_translation_setup(
        self, mock_dir, mock_app, mock_translator, mock_logger, mock_locale, mock_settings, mock_plugin_info
    ):
        """Test plugin translation setup with existing translation file."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock the QGIS interface
        mock_iface = Mock()
        mock_iface.addToolBar.return_value = Mock()
        mock_iface.mainWindow.return_value = None  # Return None instead of Mock for Qt compatibility

        # Mock settings to return Italian locale
        mock_settings.return_value.value.return_value = "it_IT"
        mock_locale.return_value.name.return_value = "it_IT"

        # Mock logger
        mock_log_instance = Mock()
        mock_logger.return_value.log = mock_log_instance

        # Mock translator
        mock_translator_instance = Mock()
        mock_translator_instance.load.return_value = True
        mock_translator.return_value = mock_translator_instance

        # Mock PluginInfo dialog
        mock_plugin_info.return_value = Mock()

        # Mock DIR_PLUGIN_ROOT as a Path-like object that supports division
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.resolve.return_value = "fake/path/to/translation.qm"

        # Create a mock that supports path division operations
        mock_path_builder = Mock()
        mock_path_builder.__truediv__ = Mock(return_value=mock_path_builder)
        mock_path_builder.exists.return_value = True
        mock_path_builder.resolve.return_value = "fake/path/to/translation.qm"

        # Chain the path operations: DIR_PLUGIN_ROOT / "resources" / "i18n" / "{file}.qm"
        mock_dir.__truediv__.return_value = mock_path_builder

        # Initialize plugin
        plugin = DipStrikeToolsPlugin(mock_iface)

        # Verify translation setup
        assert plugin.locale == "it"
        mock_translator.assert_called_once()
        mock_translator_instance.load.assert_called_once()
        mock_app.installTranslator.assert_called_once_with(mock_translator_instance)

    def test_tr_method_exists(self):
        """Test that the translation method exists and is callable."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Check if the class has the tr method
        assert hasattr(DipStrikeToolsPlugin, "tr")
        assert callable(DipStrikeToolsPlugin.tr)

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
        ]

        for method_name in custom_methods:
            assert hasattr(DipStrikeToolsPlugin, method_name), f"Missing custom method: {method_name}"
            assert callable(getattr(DipStrikeToolsPlugin, method_name)), f"Method {method_name} is not callable"


@pytest.mark.unit
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


@pytest.mark.integration
class TestDipStrikeToolsPluginAdvanced:
    """Advanced tests for DipStrikeToolsPlugin functionality."""

    @patch("dip_strike_tools.plugin_main.PluginInfo")
    @patch("dip_strike_tools.plugin_main.QgsSettings")
    @patch("dip_strike_tools.plugin_main.QLocale")
    @patch("dip_strike_tools.plugin_main.PlgLogger")
    def test_plugin_translation_setup_no_file(self, mock_logger, mock_locale, mock_settings, mock_plugin_info):
        """Test plugin initialization when translation file doesn't exist."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock the QGIS interface
        mock_iface = Mock()
        mock_iface.addToolBar.return_value = Mock()
        mock_iface.mainWindow.return_value = None  # Return None instead of Mock for Qt compatibility

        # Mock settings to return a locale that we know doesn't have a translation file
        mock_settings.return_value.value.return_value = "zz_ZZ"  # Fake locale
        mock_locale.return_value.name.return_value = "zz_ZZ"

        # Mock logger
        mock_log_instance = Mock()
        mock_logger.return_value.log = mock_log_instance

        # Mock PluginInfo dialog
        mock_plugin_info.return_value = Mock()

        # Initialize plugin - should not find translation file for fake locale
        plugin = DipStrikeToolsPlugin(mock_iface)

        # Verify basic setup worked
        assert plugin.locale == "zz"
        # Should not have translator if translation file doesn't exist for this locale
        assert not hasattr(plugin, "translator")

    @patch("dip_strike_tools.plugin_main.PluginInfo")
    @patch("dip_strike_tools.plugin_main.QgsSettings")
    @patch("dip_strike_tools.plugin_main.QLocale")
    @patch("dip_strike_tools.plugin_main.PlgLogger")
    def test_add_action_method(self, mock_logger, mock_locale, mock_settings, mock_plugin_info):
        """Test the add_action method with various parameters."""
        try:
            # Import Qt classes for proper mocking
            from qgis.PyQt.QtWidgets import QToolBar

            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock the QGIS interface
        mock_iface = Mock()
        # Create a real QToolBar instance for proper Qt compatibility
        mock_toolbar = QToolBar()
        mock_iface.addToolBar.return_value = mock_toolbar
        mock_iface.addPluginToDatabaseMenu = Mock()
        mock_iface.mainWindow.return_value = None  # Return None instead of Mock for Qt compatibility

        # Mock settings
        mock_settings.return_value.value.return_value = "en"
        mock_locale.return_value.name.return_value = "en_US"

        # Mock logger
        mock_log_instance = Mock()
        mock_logger.return_value.log = mock_log_instance

        # Mock PluginInfo dialog
        mock_plugin_info.return_value = Mock()

        plugin = DipStrikeToolsPlugin(mock_iface)

        # Mock callback
        mock_callback = Mock()

        # Test add_action with all parameters
        action = plugin.add_action(
            icon_path="test_icon.png",
            text="Test Action",
            callback=mock_callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip="Test status tip",
            whats_this="Test whats this",
            parent=None,
        )

        # Verify action was created
        assert action is not None

        # Verify the action was added to toolbar and menu
        # QToolBar.addAction doesn't have mock assertions, but we can check action properties
        assert action.parent() == mock_toolbar  # Action should be parented to toolbar
        mock_iface.addPluginToDatabaseMenu.assert_called()

    @patch("dip_strike_tools.plugin_main.PluginInfo")
    @patch("dip_strike_tools.plugin_main.QgsSettings")
    @patch("dip_strike_tools.plugin_main.QLocale")
    @patch("dip_strike_tools.plugin_main.PlgLogger")
    def test_add_action_minimal_parameters(self, mock_logger, mock_locale, mock_settings, mock_plugin_info):
        """Test the add_action method with minimal parameters."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock the QGIS interface
        mock_iface = Mock()
        mock_toolbar = Mock()
        mock_iface.addToolBar.return_value = mock_toolbar
        mock_iface.mainWindow.return_value = None  # Return None instead of Mock for Qt compatibility

        # Mock settings
        mock_settings.return_value.value.return_value = "en"
        mock_locale.return_value.name.return_value = "en_US"

        # Mock logger
        mock_log_instance = Mock()
        mock_logger.return_value.log = mock_log_instance

        # Mock PluginInfo dialog
        mock_plugin_info.return_value = Mock()

        plugin = DipStrikeToolsPlugin(mock_iface)

        # Mock callback
        mock_callback = Mock()

        # Test add_action with minimal parameters
        action = plugin.add_action(
            icon_path="test_icon.png",
            text="Test Action",
            callback=mock_callback,
            add_to_menu=False,
            add_to_toolbar=False,
        )

        # Verify action was created but not added to toolbar/menu
        assert action is not None

        # Should not have been called with this action since add_to_* are False
        assert mock_toolbar.addAction.call_count == 0  # Only called during init

    @patch("dip_strike_tools.plugin_main.PluginInfo")
    @patch("dip_strike_tools.plugin_main.PlgLogger")
    def test_open_create_layer_dialog_cancelled(self, mock_logger, mock_plugin_info):
        """Test create layer dialog when user cancels."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock the QGIS interface
        mock_iface = Mock()
        mock_iface.addToolBar.return_value = Mock()
        mock_iface.mainWindow.return_value = None  # Return None instead of Mock for Qt compatibility

        # Mock logger
        mock_log_instance = Mock()
        mock_logger.return_value.log = mock_log_instance

        # Mock PluginInfo dialog
        mock_plugin_info.return_value = Mock()

        plugin = DipStrikeToolsPlugin(mock_iface)

        # Mock the dialog to be cancelled
        with patch("dip_strike_tools.plugin_main.DlgCreateLayer") as mock_dialog:
            mock_dlg_instance = Mock()
            mock_dlg_instance.result.return_value = 0  # QDialog.Rejected
            mock_dialog.return_value = mock_dlg_instance

            # Call the method
            plugin.open_create_layer_dialog()

            # Verify dialog was created and executed
            mock_dialog.assert_called_once_with(mock_iface.mainWindow())
            mock_dlg_instance.exec.assert_called_once()

            # Verify cancellation was logged
            assert mock_log_instance.call_count >= 1
            calls = mock_log_instance.call_args_list
            cancel_call_found = any(
                "cancelled" in str(call).lower() or "annullat" in str(call).lower()  # English or Italian
                for call in calls
            )
            assert cancel_call_found

    @patch("dip_strike_tools.plugin_main.PluginInfo")
    @patch("dip_strike_tools.plugin_main.PlgLogger")
    def test_open_create_layer_dialog_error(self, mock_logger, mock_plugin_info):
        """Test create layer dialog when an error occurs during layer creation."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock the QGIS interface
        mock_iface = Mock()
        mock_iface.addToolBar.return_value = Mock()
        mock_iface.mainWindow.return_value = None  # Return None instead of Mock for Qt compatibility

        # Mock logger
        mock_log_instance = Mock()
        mock_logger.return_value.log = mock_log_instance

        # Mock PluginInfo dialog
        mock_plugin_info.return_value = Mock()

        plugin = DipStrikeToolsPlugin(mock_iface)

        # Mock the dialog to be accepted but with error in layer creation
        with patch("dip_strike_tools.plugin_main.DlgCreateLayer") as mock_dialog:
            mock_dlg_instance = Mock()
            mock_dlg_instance.result.return_value = 1  # QDialog.Accepted
            mock_dlg_instance.get_layer_config.side_effect = Exception("Test error")
            mock_dialog.return_value = mock_dlg_instance
            mock_dialog.Accepted = 1

            # Call the method
            plugin.open_create_layer_dialog()

            # Verify error was logged
            assert mock_log_instance.call_count >= 1
            calls = mock_log_instance.call_args_list
            error_call_found = any("error" in str(call).lower() for call in calls)
            assert error_call_found

    @patch("dip_strike_tools.plugin_main.PluginInfo")
    @patch("dip_strike_tools.plugin_main.PlgLogger")
    def test_toggle_dip_strike_tool_methods(self, mock_logger, mock_plugin_info):
        """Test toggle, activate, and deactivate methods."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock the QGIS interface
        mock_iface = Mock()
        mock_iface.addToolBar.return_value = Mock()
        mock_iface.mainWindow.return_value = None  # Return None instead of Mock for Qt compatibility

        # Mock logger
        mock_log_instance = Mock()
        mock_logger.return_value.log = mock_log_instance

        # Mock PluginInfo dialog
        mock_plugin_info.return_value = Mock()

        plugin = DipStrikeToolsPlugin(mock_iface)

        # Mock the action
        plugin.insert_dip_strike_action = Mock()

        # Test toggle when checked (should activate)
        plugin.insert_dip_strike_action.isChecked.return_value = True
        plugin.activate_dip_strike_tool = Mock()
        plugin.toggle_dip_strike_tool()
        plugin.activate_dip_strike_tool.assert_called_once()

        # Test toggle when unchecked (should deactivate)
        plugin.insert_dip_strike_action.isChecked.return_value = False
        plugin.deactivate_dip_strike_tool = Mock()
        plugin.toggle_dip_strike_tool()
        plugin.deactivate_dip_strike_tool.assert_called_once()

    @patch("dip_strike_tools.plugin_main.PluginInfo")
    @patch("dip_strike_tools.plugin_main.PlgLogger")
    def test_map_tool_changed_handler(self, mock_logger, mock_plugin_info):
        """Test the map tool change handler."""
        try:
            from dip_strike_tools.plugin_main import DipStrikeToolsPlugin
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Mock the QGIS interface
        mock_iface = Mock()
        mock_iface.addToolBar.return_value = Mock()
        mock_iface.mainWindow.return_value = None  # Return None instead of Mock for Qt compatibility

        # Mock logger
        mock_log_instance = Mock()
        mock_logger.return_value.log = mock_log_instance

        # Mock PluginInfo dialog
        mock_plugin_info.return_value = Mock()

        plugin = DipStrikeToolsPlugin(mock_iface)

        # Mock the action
        plugin.insert_dip_strike_action = Mock()

        # Mock our custom tool
        mock_tool = Mock()
        plugin.custom_tool = mock_tool

        # Test when our tool becomes active
        plugin.insert_dip_strike_action.isChecked.return_value = False
        plugin.on_map_tool_changed(mock_tool)
        plugin.insert_dip_strike_action.setChecked.assert_called_with(True)

        # Reset mock
        plugin.insert_dip_strike_action.reset_mock()

        # Test when another tool becomes active
        other_tool = Mock()
        plugin.insert_dip_strike_action.isChecked.return_value = True
        plugin.on_map_tool_changed(other_tool)
        plugin.insert_dip_strike_action.setChecked.assert_called_with(False)

        # Test when no custom tool exists
        delattr(plugin, "custom_tool")
        plugin.insert_dip_strike_action.reset_mock()
        plugin.insert_dip_strike_action.isChecked.return_value = True
        plugin.on_map_tool_changed(other_tool)
        plugin.insert_dip_strike_action.setChecked.assert_called_with(False)
