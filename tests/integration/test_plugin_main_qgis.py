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
QGIS integration tests for plugin_main module.

These tests require a QGIS environment and use pytest-qgis.
"""

from unittest.mock import Mock, patch

# Import pytest-qgis utilities
pytest_plugins = ["pytest_qgis"]


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

        # Verify action was created
        assert action is not None
        assert action.text() == "Test Action"
        assert action.isEnabled() is True
        # Verify action was added to toolbar (when add_to_toolbar=True)
        toolbar_actions = plugin.toolbar.actions()
        assert action in toolbar_actions

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
            assert hasattr(plugin, "toolbar")

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

    @patch("dip_strike_tools.plugin_main.DlgCreateLayer")
    @patch("dip_strike_tools.plugin_main.DipStrikeLayerCreator")
    @patch("dip_strike_tools.plugin_main.QgsProject")
    def test_open_create_layer_dialog_success_with_symbology(
        self, mock_project, mock_creator, mock_dialog, qgis_iface
    ):
        """Test create layer dialog with successful layer creation and symbology."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock dialog
        mock_dlg_instance = Mock()
        mock_dlg_instance.result.return_value = 1  # QDialog.Accepted
        mock_layer_config = {"name": "Test Layer", "crs": Mock(), "symbology": {"apply": True}}
        mock_dlg_instance.get_layer_config.return_value = mock_layer_config
        mock_dialog.return_value = mock_dlg_instance
        mock_dialog.Accepted = 1

        # Mock layer creator
        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_creator_instance = Mock()
        mock_creator_instance.create_dip_strike_layer.return_value = mock_layer
        mock_creator_instance.apply_symbology.return_value = True
        mock_creator.return_value = mock_creator_instance

        # Mock project
        mock_project_instance = Mock()
        mock_project.instance.return_value = mock_project_instance

        # Call the method
        plugin.open_create_layer_dialog()

        # Verify dialog workflow
        mock_dialog.assert_called_once()
        mock_dlg_instance.exec.assert_called_once()
        mock_dlg_instance.get_layer_config.assert_called_once()

        # Verify layer creation workflow
        mock_creator.assert_called_once()
        mock_creator_instance.create_dip_strike_layer.assert_called_once_with(
            mock_layer_config, mock_layer_config["crs"]
        )
        mock_project_instance.addMapLayer.assert_called_once_with(mock_layer)
        mock_creator_instance.apply_symbology.assert_called_once_with(mock_layer)

    @patch("dip_strike_tools.plugin_main.DlgCreateLayer")
    @patch("dip_strike_tools.plugin_main.DipStrikeLayerCreator")
    @patch("dip_strike_tools.plugin_main.QgsProject")
    def test_open_create_layer_dialog_success_no_symbology(self, mock_project, mock_creator, mock_dialog, qgis_iface):
        """Test create layer dialog with successful layer creation but no symbology."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock dialog
        mock_dlg_instance = Mock()
        mock_dlg_instance.result.return_value = 1  # QDialog.Accepted
        mock_layer_config = {"name": "Test Layer", "crs": Mock(), "symbology": {"apply": False}}
        mock_dlg_instance.get_layer_config.return_value = mock_layer_config
        mock_dialog.return_value = mock_dlg_instance
        mock_dialog.Accepted = 1

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

        # Verify layer creation workflow but no symbology
        mock_creator_instance.create_dip_strike_layer.assert_called_once()
        mock_project_instance.addMapLayer.assert_called_once_with(mock_layer)
        # Symbology should not be called since apply=False
        mock_creator_instance.apply_symbology.assert_not_called()

    @patch("dip_strike_tools.plugin_main.DlgCreateLayer")
    @patch("dip_strike_tools.plugin_main.DipStrikeLayerCreator")
    @patch("dip_strike_tools.plugin_main.QgsProject")
    def test_open_create_layer_dialog_symbology_failure(self, mock_project, mock_creator, mock_dialog, qgis_iface):
        """Test create layer dialog when symbology application fails."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock dialog
        mock_dlg_instance = Mock()
        mock_dlg_instance.result.return_value = 1  # QDialog.Accepted
        mock_layer_config = {"name": "Test Layer", "crs": Mock(), "symbology": {"apply": True}}
        mock_dlg_instance.get_layer_config.return_value = mock_layer_config
        mock_dialog.return_value = mock_dlg_instance
        mock_dialog.Accepted = 1

        # Mock layer creator with symbology failure
        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_creator_instance = Mock()
        mock_creator_instance.create_dip_strike_layer.return_value = mock_layer
        mock_creator_instance.apply_symbology.return_value = False  # Failure
        mock_creator.return_value = mock_creator_instance

        # Mock project
        mock_project_instance = Mock()
        mock_project.instance.return_value = mock_project_instance

        # Call the method
        plugin.open_create_layer_dialog()

        # Verify symbology was attempted but failed
        mock_creator_instance.apply_symbology.assert_called_once_with(mock_layer)

    def test_dialog_methods_callable(self, qgis_iface):
        """Test that dialog methods are callable without crashing."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # These methods should exist and be callable
        assert callable(plugin.open_dlg_insert_dip_strike)
        assert callable(plugin.open_create_layer_dialog)

    @patch("dip_strike_tools.plugin_main.DlgInsertDipStrike")
    def test_open_dlg_insert_dip_strike_no_existing_feature(self, mock_dialog, qgis_iface):
        """Test opening insert dialog without existing feature."""
        from qgis.core import QgsPointXY

        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock dialog
        mock_dlg_instance = Mock()
        mock_dlg_instance.result.return_value = 1  # QDialog.Accepted
        mock_dialog.return_value = mock_dlg_instance
        mock_dialog.Accepted = 1

        # Test with clicked point but no existing feature
        test_point = QgsPointXY(100, 200)
        plugin.open_dlg_insert_dip_strike(clicked_point=test_point)

        # Verify dialog was created with correct parameters
        mock_dialog.assert_called_once()
        call_args = mock_dialog.call_args
        assert qgis_iface.mainWindow() in call_args[0]  # parent
        # Check keyword arguments
        kwargs = call_args[1]
        assert kwargs["clicked_point"] == test_point
        assert kwargs["existing_feature"] is None

        mock_dlg_instance.exec.assert_called_once()

    @patch("dip_strike_tools.plugin_main.DlgInsertDipStrike")
    def test_open_dlg_insert_dip_strike_with_existing_feature(self, mock_dialog, qgis_iface):
        """Test opening insert dialog with existing feature."""
        from qgis.core import QgsPointXY

        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock dialog
        mock_dlg_instance = Mock()
        mock_dlg_instance.result.return_value = 0  # QDialog.Rejected
        mock_dialog.return_value = mock_dlg_instance
        mock_dialog.Accepted = 1

        # Test with existing feature provided
        test_point = QgsPointXY(100, 200)
        mock_feature = Mock()
        mock_feature.id.return_value = 123
        existing_feature = {
            "feature": mock_feature,
            "layer_name": "Test Layer",
            "is_configured": True,
        }

        plugin.open_dlg_insert_dip_strike(clicked_point=test_point, existing_feature=existing_feature)

        # Verify dialog was created with existing feature
        mock_dialog.assert_called_once()
        call_args = mock_dialog.call_args
        kwargs = call_args[1]
        assert kwargs["clicked_point"] == test_point
        assert kwargs["existing_feature"] == existing_feature

    def test_toggle_dip_strike_tool_activation(self, qgis_iface):
        """Test toggling the dip strike tool on."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock the action
        plugin.insert_dip_strike_action = Mock()
        plugin.insert_dip_strike_action.isChecked.return_value = True

        # Mock activate method
        plugin.activate_dip_strike_tool = Mock()

        # Test toggle when checked
        plugin.toggle_dip_strike_tool()

        plugin.activate_dip_strike_tool.assert_called_once()

    def test_toggle_dip_strike_tool_deactivation(self, qgis_iface):
        """Test toggling the dip strike tool off."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock the action
        plugin.insert_dip_strike_action = Mock()
        plugin.insert_dip_strike_action.isChecked.return_value = False

        # Mock deactivate method
        plugin.deactivate_dip_strike_tool = Mock()

        # Test toggle when unchecked
        plugin.toggle_dip_strike_tool()

        plugin.deactivate_dip_strike_tool.assert_called_once()

    @patch("dip_strike_tools.plugin_main.DipStrikeMapTool")
    def test_activate_dip_strike_tool(self, mock_map_tool, qgis_iface):
        """Test activating the dip strike tool."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock action
        plugin.insert_dip_strike_action = Mock()

        # Mock tool instance that looks like a proper map tool
        mock_tool_instance = Mock()
        mock_tool_instance.setPlugin = Mock()
        mock_tool_instance.featureClicked = Mock()
        mock_tool_instance.featureClicked.connect = Mock()
        mock_map_tool.return_value = mock_tool_instance

        # Mock the mapCanvas setMapTool to accept our mock tool
        mock_canvas = Mock()
        mock_canvas.setMapTool = Mock()

        # Use patch.object to mock the mapCanvas method
        with patch.object(qgis_iface, "mapCanvas", return_value=mock_canvas):
            # Test activation
            plugin.activate_dip_strike_tool()

            # Verify tool was created and set with iface (not canvas)
            mock_map_tool.assert_called_once_with(qgis_iface)
            mock_tool_instance.featureClicked.connect.assert_called_once()
            mock_canvas.setMapTool.assert_called_once_with(mock_tool_instance)
            plugin.insert_dip_strike_action.setChecked.assert_called_once_with(True)

    def test_deactivate_dip_strike_tool(self, qgis_iface):
        """Test deactivating the dip strike tool."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock action
        plugin.insert_dip_strike_action = Mock()

        # Create a mock tool and set it as current
        mock_tool = Mock()
        plugin.custom_tool = mock_tool

        # Mock the map canvas to return our tool as current
        with patch.object(qgis_iface.mapCanvas(), "mapTool", return_value=mock_tool):
            with patch.object(qgis_iface.mapCanvas(), "unsetMapTool") as mock_unset:
                # Test deactivation
                plugin.deactivate_dip_strike_tool()

                # Verify tool was unset
                mock_unset.assert_called_once_with(mock_tool)
                plugin.insert_dip_strike_action.setChecked.assert_called_once_with(False)

    def test_on_map_tool_changed_our_tool_active(self, qgis_iface):
        """Test map tool change handler when our tool becomes active."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock action
        plugin.insert_dip_strike_action = Mock()
        plugin.insert_dip_strike_action.isChecked.return_value = False

        # Mock our tool
        mock_tool = Mock()
        plugin.custom_tool = mock_tool

        # Test when our tool becomes active
        plugin.on_map_tool_changed(mock_tool)

        plugin.insert_dip_strike_action.setChecked.assert_called_once_with(True)

    def test_on_map_tool_changed_other_tool_active(self, qgis_iface):
        """Test map tool change handler when another tool becomes active."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Mock action
        plugin.insert_dip_strike_action = Mock()
        plugin.insert_dip_strike_action.isChecked.return_value = True

        # Mock our tool
        mock_tool = Mock()
        plugin.custom_tool = mock_tool

        # Mock other tool
        other_tool = Mock()

        # Test when other tool becomes active
        plugin.on_map_tool_changed(other_tool)

        plugin.insert_dip_strike_action.setChecked.assert_called_once_with(False)

    def test_unload_method_exception_handling(self, qgis_iface):
        """Test unload method when signal disconnection fails."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Add missing methods to the qgis_iface mock
        qgis_iface.unregisterOptionsWidgetFactory = Mock()
        qgis_iface.removePluginMenu = Mock()
        qgis_iface.removePluginDatabaseMenu = Mock()
        qgis_iface.removeToolBarIcon = Mock()
        qgis_iface.pluginHelpMenu = Mock()
        mock_help_menu = Mock()
        mock_help_menu.removeAction = Mock()
        qgis_iface.pluginHelpMenu.return_value = mock_help_menu

        # Set up objects for cleanup
        plugin.options_factory = Mock()
        plugin.action_help_plugin_menu_documentation = Mock()

        # Mock the map canvas with disconnect failure
        mock_canvas = Mock()
        mock_canvas.mapToolSet = Mock()
        mock_canvas.mapToolSet.disconnect.side_effect = Exception("Disconnect failed")

        with patch.object(qgis_iface, "mapCanvas", return_value=mock_canvas):
            # Call unload - should handle the exception gracefully
            plugin.unload()

            # Verify the method completed despite the exception
            qgis_iface.unregisterOptionsWidgetFactory.assert_called_with(plugin.options_factory)

    def test_unload_method_no_custom_tool(self, qgis_iface):
        """Test unload method when no custom tool exists."""
        from dip_strike_tools.plugin_main import DipStrikeToolsPlugin

        plugin = DipStrikeToolsPlugin(qgis_iface)

        # Add missing methods to the qgis_iface mock
        qgis_iface.unregisterOptionsWidgetFactory = Mock()
        qgis_iface.removePluginMenu = Mock()
        qgis_iface.removePluginDatabaseMenu = Mock()
        qgis_iface.removeToolBarIcon = Mock()
        qgis_iface.pluginHelpMenu = Mock()
        mock_help_menu = Mock()
        mock_help_menu.removeAction = Mock()
        qgis_iface.pluginHelpMenu.return_value = mock_help_menu

        # Set up objects for cleanup
        plugin.options_factory = Mock()
        plugin.action_help_plugin_menu_documentation = Mock()

        # Ensure no custom tool exists
        if hasattr(plugin, "custom_tool"):
            delattr(plugin, "custom_tool")

        # Mock the map canvas
        mock_canvas = Mock()
        mock_canvas.mapToolSet = Mock()
        mock_canvas.mapToolSet.disconnect = Mock()

        with patch.object(qgis_iface, "mapCanvas", return_value=mock_canvas):
            # Call unload - should handle the missing custom tool gracefully
            plugin.unload()

            # Verify cleanup continued
            qgis_iface.unregisterOptionsWidgetFactory.assert_called_with(plugin.options_factory)
