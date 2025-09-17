#! python3  # noqa: E265

"""Main plugin module."""

from functools import partial
from pathlib import Path
from typing import Optional

from qgis.core import QgsApplication, QgsProject, QgsSettings
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QTranslator, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton

from dip_strike_tools.__about__ import (
    DIR_PLUGIN_ROOT,
    __icon_path__,
    __title__,
    __uri_docs__,
)
from dip_strike_tools.core import DipStrikeMapTool
from dip_strike_tools.core.dip_strike_calculator import DipStrikeCalculator
from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
from dip_strike_tools.gui.dlg_calculate_values import DlgCalculateValues
from dip_strike_tools.gui.dlg_create_layer import DlgCreateLayer
from dip_strike_tools.gui.dlg_info import PluginInfo
from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike
from dip_strike_tools.gui.dlg_settings import PlgOptionsFactory
from dip_strike_tools.toolbelt import DIALOG_ACCEPTED, PlgLogger


class DipStrikeToolsPlugin:
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.log = PlgLogger().log

        # initialize the locale
        self.locale: str = QgsSettings().value("locale/userLocale", QLocale().name())[0:2]

        # FOR TESTING: Force Italian locale
        # self.locale = "it"  # Comment this line to use system locale

        locale_path: Path = DIR_PLUGIN_ROOT / "resources" / "i18n" / f"dip_strike_tools_{self.locale}.qm"
        self.log(message=f"Translation: {self.locale}, {locale_path}", log_level=4)
        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path.resolve()))
            QCoreApplication.installTranslator(self.translator)

        self.dlg_info = PluginInfo(self.iface.mainWindow())

        self.menu = self.tr("&Dip-Strike Tools")

        # toolbar
        self.toolbar = self.iface.addToolBar("Dip-Strike Tools")
        self.toolbar.setObjectName("DipStrikeToolsToolbar")

    def add_action(
        self,
        icon_path,
        text: str,
        callback,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: Optional[str] = None,
        whats_this: Optional[str] = None,
        parent=None,
    ):
        # Use toolbar as parent for toolbar actions, or provided parent
        action_parent = self.toolbar if add_to_toolbar and parent is None else parent

        icon = QIcon(icon_path)
        action = QAction(icon, text, action_parent)  # type: ignore
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(self.menu, action)

        return action

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # -- Actions

        # -- Create new dip strike layer action
        self.create_layer_action = self.add_action(
            QgsApplication.getThemeIcon("mActionAddLayer.svg"),
            text=self.tr("Create New Dip Strike Layer"),
            callback=self.open_create_layer_dialog,
        )

        # -- Create new dip strike point action
        self.insert_dip_strike_action = self.add_action(
            QgsApplication.getThemeIcon("north_arrow.svg"),
            text=self.tr("Create or Update a Dip Strike Point"),
            callback=self.toggle_dip_strike_tool,
        )

        # Make the dip strike point action toggleable
        self.insert_dip_strike_action.setCheckable(True)
        self.insert_dip_strike_action.setChecked(False)

        # Connect to map canvas tool changes to update button state
        self.iface.mapCanvas().mapToolSet.connect(self.on_map_tool_changed)

        # -- Calculate dip or strike action
        self.calculate_values_action = self.add_action(
            QgsApplication.getThemeIcon("mActionCalculateField.svg"),
            text=self.tr("Calculate Dip/Strike Values"),
            callback=self.open_calculate_values_dialog,
        )

        self.toolbar.addSeparator()

        # -- Tools menu button
        tools_menu_button = QToolButton(self.toolbar)  # Set toolbar as parent
        tools_menu_button.setIcon(QgsApplication.getThemeIcon("mActionOptions.svg"))
        tools_menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        tools_menu_button.setToolTip(self.tr("Additional Tools and Plugin Info"))
        tools_menu = QMenu(tools_menu_button)  # Set button as parent for menu
        self.toolbar.addWidget(tools_menu_button)

        self.settings_action = self.add_action(
            QgsApplication.getThemeIcon("mActionOptions.svg"),
            text=self.tr("Dip-Strike Tools Settings"),
            callback=lambda: self.iface.showOptionsDialog(currentPage="mOptionsPage{}".format(__title__)),
            add_to_toolbar=False,
        )
        tools_menu.addAction(self.settings_action)  # type: ignore[arg-type]

        self.info_action = self.add_action(
            QgsApplication.getThemeIcon("mActionHelpContents.svg"),
            text=self.tr("Dip-Strike Tools Info"),
            callback=self.dlg_info.show,
            add_to_toolbar=False,
        )
        tools_menu.addAction(self.info_action)  # type: ignore[arg-type]

        tools_menu_button.setMenu(tools_menu)

        # -- Plugin Help menu docs link
        self.action_help_plugin_menu_documentation = QAction(
            QIcon(str(__icon_path__)),  # type: ignore
            __title__,
            self.iface.mainWindow(),
        )
        self.action_help_plugin_menu_documentation.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_docs__))
        )
        self.iface.pluginHelpMenu().addAction(self.action_help_plugin_menu_documentation)

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        self.log(message="Starting plugin cleanup", log_level=4)

        # Safe cleanup helper
        def safe_cleanup(name, cleanup_func):
            try:
                cleanup_func()
                self.log(message=f"Cleanup '{name}' completed", log_level=4)
            except Exception as e:
                self.log(message=f"Error in cleanup '{name}': {e}", log_level=2)

        # Cleanup in order to prevent cascade failures
        safe_cleanup("translator", self._cleanup_translator)
        safe_cleanup("map_tool", self._cleanup_map_tool)
        safe_cleanup("options_widget", self._cleanup_options_widget)
        safe_cleanup("toolbar", self._cleanup_toolbar)
        safe_cleanup("help_menu", self._cleanup_help_menu)

        self.log(message="Plugin cleanup completed", log_level=4)

    def _cleanup_translator(self):
        """Remove translator from Qt application."""
        if hasattr(self, "translator") and self.translator:
            try:
                QCoreApplication.removeTranslator(self.translator)
                delattr(self, "translator")  # Remove the attribute entirely
            except (AttributeError, RuntimeError):
                pass

    def _cleanup_map_tool(self):
        """Clean up map tool and signals."""
        # Disconnect signals
        try:
            canvas = self.iface.mapCanvas()
            if canvas and hasattr(canvas, "mapToolSet"):
                canvas.mapToolSet.disconnect(self.on_map_tool_changed)
        except (AttributeError, TypeError, RuntimeError):
            pass

        # Clean up custom tool
        if hasattr(self, "custom_tool") and self.custom_tool:
            try:
                # Deactivate if active
                canvas = self.iface.mapCanvas()
                if canvas and canvas.mapTool() == self.custom_tool:
                    canvas.unsetMapTool(self.custom_tool)
                # Clean up the tool
                if hasattr(self.custom_tool, "clean_up"):
                    self.custom_tool.clean_up()
            except (AttributeError, RuntimeError):
                pass
            finally:
                self.custom_tool = None

    def _cleanup_options_widget(self):
        """Unregister options widget factory."""
        if hasattr(self, "options_factory") and self.options_factory:
            try:
                self.iface.unregisterOptionsWidgetFactory(self.options_factory)
            except (AttributeError, RuntimeError):
                pass

    def _cleanup_toolbar(self):
        """Remove toolbar and plugin menu actions."""
        # Remove actions from the database menu that were added both to the toolbar and to the menu
        # Removing the toolbar would not remove the menu actions
        # TODO: empty menu still remains
        try:
            if hasattr(self, "settings_action") and self.settings_action:
                self.iface.removePluginDatabaseMenu(self.tr("&Dip-Strike Tools"), self.settings_action)
            if hasattr(self, "info_action") and self.info_action:
                self.iface.removePluginDatabaseMenu(self.tr("&Dip-Strike Tools"), self.info_action)
        except (AttributeError, RuntimeError):
            pass

        # Remove toolbar - this will automatically destroy all child actions and widgets
        if hasattr(self, "toolbar") and self.toolbar:
            try:
                self.iface.mainWindow().removeToolBar(self.toolbar)
                self.toolbar.deleteLater()  # Qt handles all children automatically
            except (AttributeError, RuntimeError):
                pass
            finally:
                self.toolbar = None

    def _cleanup_help_menu(self):
        """Remove help menu action and close dialog."""
        # Clean up help menu action
        if hasattr(self, "action_help_plugin_menu_documentation") and self.action_help_plugin_menu_documentation:
            try:
                self.iface.pluginHelpMenu().removeAction(self.action_help_plugin_menu_documentation)
                self.action_help_plugin_menu_documentation.deleteLater()
            except (AttributeError, RuntimeError):
                pass
            finally:
                self.action_help_plugin_menu_documentation = None

        # Clean up dialog
        if hasattr(self, "dlg_info") and self.dlg_info:
            try:
                self.dlg_info.close()
                self.dlg_info.deleteLater()
            except (AttributeError, RuntimeError):
                pass
            finally:
                self.dlg_info = None

    def toggle_dip_strike_tool(self):
        """Toggle the dip strike tool on/off based on button state."""
        if self.insert_dip_strike_action.isChecked():
            self.activate_dip_strike_tool()
        else:
            self.deactivate_dip_strike_tool()

    def activate_dip_strike_tool(self):
        """Activate the dip strike map tool."""
        # Create custom tool if it doesn't exist or reuse existing one
        if not hasattr(self, "custom_tool") or self.custom_tool is None:
            self.custom_tool = DipStrikeMapTool(self.iface)
            self.custom_tool.featureClicked.connect(
                lambda point, existing_feature: self.open_dlg_insert_dip_strike(
                    clicked_point=point, existing_feature=existing_feature
                )
            )

        # Set the custom map tool to the map canvas
        self.log(message="Dip Strike Tool activated.", log_level=4)
        self.iface.mapCanvas().setMapTool(self.custom_tool)

        # Update button state
        self.insert_dip_strike_action.setChecked(True)

    def deactivate_dip_strike_tool(self):
        """Deactivate the dip strike map tool."""
        # Get the current map tool
        current_tool = self.iface.mapCanvas().mapTool()

        # If our tool is active, unset it
        if hasattr(self, "custom_tool") and current_tool == self.custom_tool:
            self.iface.mapCanvas().unsetMapTool(self.custom_tool)
            self.log(message="Dip Strike Tool deactivated.", log_level=4)

        # Update button state
        self.insert_dip_strike_action.setChecked(False)

    def on_map_tool_changed(self, new_tool):
        """Handle map tool changes to update button state."""
        # Check if our tool is still active
        if hasattr(self, "custom_tool") and new_tool == self.custom_tool:
            # Our tool is active, ensure button is checked
            if not self.insert_dip_strike_action.isChecked():
                self.insert_dip_strike_action.setChecked(True)
        else:
            # Another tool is active, ensure button is unchecked
            if self.insert_dip_strike_action.isChecked():
                self.insert_dip_strike_action.setChecked(False)

    def open_dlg_insert_dip_strike(self, clicked_point=None, existing_feature=None):
        """Open the dialog to insert a dip strike point."""
        from dip_strike_tools.core.feature_finder import FeatureFinder

        # If existing_feature wasn't passed, search for it (backward compatibility)
        if existing_feature is None and clicked_point:
            feature_finder = FeatureFinder(self.iface)
            existing_feature = feature_finder.find_feature_at_point(clicked_point)

        if existing_feature:
            self.log(
                message=f"Found existing feature at clicked location: {existing_feature['layer_name']} - Feature ID {existing_feature['feature'].id()}",
                log_level=3,
            )

        dlg = DlgInsertDipStrike(
            self.iface.mainWindow(), clicked_point=clicked_point, existing_feature=existing_feature
        )
        dlg.exec()
        if dlg.result() == DIALOG_ACCEPTED:
            self.log(message="Dip Strike Point created successfully.", log_level=3)
        else:
            self.log(message="Dip Strike Point creation cancelled.", log_level=4)

    def open_create_layer_dialog(self):
        """Open the dialog to create a new dip strike layer."""
        dlg = DlgCreateLayer(self.iface.mainWindow())
        dlg.exec()
        if dlg.result() == DIALOG_ACCEPTED:
            try:
                # Get the layer configuration from the dialog
                config = dlg.get_layer_config()

                # Create the layer using the layer creator
                layer_creator = DipStrikeLayerCreator()
                layer = layer_creator.create_dip_strike_layer(config, config["crs"])

                # Add the layer to the project
                QgsProject.instance().addMapLayer(layer)

                # Apply symbology if requested
                if config.get("symbology", {}).get("apply", False):
                    success = layer_creator.apply_symbology(layer)
                    if success:
                        self.log(message=self.tr("Symbology applied successfully."), log_level=3)
                    else:
                        self.log(message=self.tr("Failed to apply symbology."), log_level=1)

                self.log(
                    message=self.tr("New dip strike layer '{}' created and added to project.").format(layer.name()),
                    log_level=3,
                )

            except Exception as e:
                self.log(message=self.tr("Error creating layer: {}").format(str(e)), log_level=1)
        else:
            self.log(message=self.tr("Layer creation cancelled."), log_level=4)

    def open_calculate_values_dialog(self):
        """Open the dialog to calculate dip/strike values from existing fields."""
        dlg = DlgCalculateValues(self.iface.mainWindow())
        dlg.exec()
        if dlg.result() == DIALOG_ACCEPTED:
            try:
                # Get the calculation configuration from the dialog
                config = dlg.get_calculation_config()

                # Perform the calculation
                calculator = DipStrikeCalculator()
                success, message = calculator.process_layer(config)

                if success:
                    self.log(
                        message=self.tr("Calculation completed successfully: {}").format(message),
                        log_level=3,
                        push=True,
                    )
                    # Refresh the layer to show updated values
                    config["layer"].triggerRepaint()
                else:
                    self.log(message=self.tr("Calculation failed: {}").format(message), log_level=1, push=True)

            except Exception as e:
                self.log(message=self.tr("Error during calculation: {}").format(str(e)), log_level=1, push=True)
        else:
            self.log(message=self.tr("Calculation cancelled."), log_level=4)
