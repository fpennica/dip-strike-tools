#! python3  # noqa: E265

"""Main plugin module."""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication, QgsSettings
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QTranslator, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction

# project
from dip_strike_tools.__about__ import (
    DIR_PLUGIN_ROOT,
    __icon_path__,
    __title__,
    __uri_homepage__,
)
from dip_strike_tools.core import DipStrikeMapTool
from dip_strike_tools.gui.dlg_insert_dip_strike import DlgInsertDipStrike
from dip_strike_tools.gui.dlg_settings import PlgOptionsFactory
from dip_strike_tools.toolbelt import PlgLogger

# ############################################################################
# ########## Classes ###############
# ##################################


class DipStrikeToolsPlugin:
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.log = PlgLogger().log

        # translation
        # initialize the locale
        self.locale: str = QgsSettings().value("locale/userLocale", QLocale().name())[0:2]
        locale_path: Path = DIR_PLUGIN_ROOT / "resources" / "i18n" / f"{__title__.lower()}_{self.locale}.qm"
        self.log(message=f"Translation: {self.locale}, {locale_path}", log_level=4)
        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path.resolve()))
            QCoreApplication.installTranslator(self.translator)

        self.actions = []

        self.menu = self.tr("&Dip Strike Tools")

        # toolbar
        self.toolbar = self.iface.addToolBar("Dip Strike Tools")
        self.toolbar.setObjectName("DipStrikeToolsToolbar")

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
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
        self.actions.append(action)
        return action

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # -- Actions
        self.action_help = QAction(
            QgsApplication.getThemeIcon("mActionHelpContents.svg"),
            self.tr("Help"),
            self.iface.mainWindow(),
        )
        self.action_help.triggered.connect(partial(QDesktopServices.openUrl, QUrl(__uri_homepage__)))

        self.action_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings"),
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(
            lambda: self.iface.showOptionsDialog(currentPage="mOptionsPage{}".format(__title__))
        )

        # -- Toolbar Actions
        self.insert_dip_strike_action = self.add_action(
            QgsApplication.getThemeIcon("mActionAddArrow.svg"),
            # enabled_flag=enabled_flag,
            text=self.tr("Create a Dip Strike Point"),
            callback=self.toggle_dip_strike_tool,
            parent=self.iface.mainWindow(),
        )

        # Make the action toggleable
        self.insert_dip_strike_action.setCheckable(True)
        self.insert_dip_strike_action.setChecked(False)

        # Connect to map canvas tool changes to update button state
        self.iface.mapCanvas().mapToolSet.connect(self.on_map_tool_changed)

        # -- Menu
        self.iface.addPluginToMenu(__title__, self.action_settings)
        self.iface.addPluginToMenu(__title__, self.action_help)

        # -- Help menu

        # documentation
        self.iface.pluginHelpMenu().addSeparator()
        self.action_help_plugin_menu_documentation = QAction(
            QIcon(str(__icon_path__)),
            f"{__title__} - Documentation",
            self.iface.mainWindow(),
        )
        self.action_help_plugin_menu_documentation.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
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
        # -- Disconnect map tool change signal
        try:
            self.iface.mapCanvas().mapToolSet.disconnect(self.on_map_tool_changed)
        except Exception:
            pass  # Connection might not exist

        # -- Clean up custom map tool
        if hasattr(self, "custom_tool") and self.custom_tool:
            # Deactivate the tool if it's currently active
            current_tool = self.iface.mapCanvas().mapTool()
            if current_tool == self.custom_tool:
                self.iface.mapCanvas().unsetMapTool(self.custom_tool)

            self.custom_tool.clean_up()
            self.custom_tool = None

        # -- Clean up menu
        self.iface.removePluginMenu(__title__, self.action_help)
        self.iface.removePluginMenu(__title__, self.action_settings)

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        for action in self.actions:
            self.iface.removePluginDatabaseMenu(self.tr("&Dip Strike Tools"), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

        # remove from QGIS help/extensions menu
        if self.action_help_plugin_menu_documentation:
            self.iface.pluginHelpMenu().removeAction(self.action_help_plugin_menu_documentation)

        # remove actions
        del self.action_settings
        del self.action_help

    def run(self):
        """Main process.

        :raises Exception: if there is no item in the feed
        """
        try:
            self.log(
                message=self.tr("Everything ran OK."),
                log_level=3,
                push=False,
            )
        except Exception as err:
            self.log(
                message=self.tr("Houston, we've got a problem: {}".format(err)),
                log_level=2,
                push=True,
            )

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
            self.custom_tool = DipStrikeMapTool(self.iface.mapCanvas())
            self.custom_tool.setPlugin(self)  # Set plugin reference for feature searching
            self.custom_tool.featureClicked.connect(
                lambda point, existing_feature: self.open_dlg_insert_dip_strike(
                    clicked_point=point, existing_feature=existing_feature
                )
            )

        # Set the custom map tool to the map canvas
        self.log(message=self.tr("Dip Strike Tool activated."), log_level=3)
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
            self.log(message=self.tr("Dip Strike Tool deactivated."), log_level=3)

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

        # If existing_feature wasn't passed, search for it (backward compatibility)
        if existing_feature is None and clicked_point:
            existing_feature = self._find_existing_feature_at_point(clicked_point)

        if existing_feature:
            self.log(
                message=f"Found existing feature at clicked location: {existing_feature['layer_name']} - Feature ID {existing_feature['feature'].id()}",
                log_level=3,
            )

        dlg = DlgInsertDipStrike(
            self.iface.mainWindow(), clicked_point=clicked_point, existing_feature=existing_feature
        )
        dlg.exec()
        if dlg.result() == DlgInsertDipStrike.Accepted:
            self.log(message=self.tr("Dip Strike Point created successfully."), log_level=3)
        else:
            self.log(message=self.tr("Dip Strike Point creation cancelled."), log_level=2)

    def _find_existing_feature_at_point(self, clicked_point, tolerance_pixels=10):
        """Find existing dip/strike features near the clicked point.

        :param clicked_point: The point where user clicked (in map canvas CRS)
        :type clicked_point: QgsPointXY
        :param tolerance_pixels: Search tolerance in pixels
        :type tolerance_pixels: int
        :return: Dictionary with feature info or None if no feature found
        :rtype: dict or None
        """
        from qgis.core import (
            QgsCoordinateTransform,
            QgsFeatureRequest,
            QgsGeometry,
            QgsPointXY,
            QgsProject,
        )

        # Convert pixel tolerance to map units
        canvas = self.iface.mapCanvas()
        tolerance_map_units = tolerance_pixels * canvas.mapUnitsPerPixel()

        # Get map canvas CRS
        canvas_crs = canvas.mapSettings().destinationCrs()

        # Get all point layers from the project that are currently visible
        project = QgsProject.instance()
        if not project:
            return None

        # Get the layer tree root to check visibility
        root = project.layerTreeRoot()
        if not root:
            return None

        point_layers = []
        for layer in project.mapLayers().values():
            if (
                hasattr(layer, "geometryType")
                and layer.geometryType() == 0  # Point geometry type
                and layer.isValid()
            ):
                # Always include configured dip/strike layers, even if not visible
                is_configured_layer = layer.customProperty("dip_strike_tools/layer_role") == "dip_strike_feature_layer"

                if is_configured_layer:
                    point_layers.append(layer)
                else:
                    # For other layers, check if they are visible using layer tree
                    layer_tree_layer = root.findLayer(layer.id())
                    if layer_tree_layer and layer_tree_layer.isVisible():
                        point_layers.append(layer)

        # First, check the currently configured feature layer if available
        configured_layers = []
        other_layers = []

        for layer in point_layers:
            # Check if layer is configured for dip/strike tools
            if layer.customProperty("dip_strike_tools/layer_role") == "dip_strike_feature_layer":
                configured_layers.append(layer)
            else:
                other_layers.append(layer)

        # Search in configured layers first, then others
        for layer in configured_layers + other_layers:
            try:
                # Get layer CRS
                layer_crs = layer.crs()

                # Transform clicked point to layer CRS if needed
                if canvas_crs != layer_crs:
                    transform = QgsCoordinateTransform(canvas_crs, layer_crs, project)
                    try:
                        search_point = transform.transform(clicked_point)
                        # Also transform tolerance: create a small offset point and transform it to calculate proper tolerance
                        offset_point = QgsPointXY(clicked_point.x() + tolerance_map_units, clicked_point.y())
                        transformed_offset = transform.transform(offset_point)
                        layer_tolerance = abs(transformed_offset.x() - search_point.x())
                    except Exception as e:
                        self.log(
                            message=f"Error transforming coordinates for layer '{layer.name()}': {e}", log_level=2
                        )
                        continue
                else:
                    search_point = clicked_point
                    layer_tolerance = tolerance_map_units

                # Create search geometry (circle around search point in layer CRS)
                search_geometry = QgsGeometry.fromPointXY(search_point).buffer(layer_tolerance, 8)

                # Use spatial index for more efficient searching if available
                request = QgsFeatureRequest()
                request.setFilterRect(search_geometry.boundingBox())

                # Get features that intersect with search geometry
                features = layer.getFeatures(request)
                for feature in features:
                    if feature.geometry() and feature.geometry().intersects(search_geometry):
                        # Found a feature within tolerance - only log success
                        # self.log(
                        #     message=f"Found existing feature in layer '{layer.name()}' (ID: {feature.id()})",
                        #     log_level=3,
                        # )
                        return {
                            "feature": feature,
                            "layer": layer,
                            "layer_name": layer.name(),
                            "is_configured": layer.customProperty("dip_strike_tools/layer_role")
                            == "dip_strike_feature_layer",
                        }

            except Exception as e:
                self.log(message=f"Error searching layer '{layer.name()}': {e}", log_level=2)
                continue

        # No feature found - no logging needed for normal operation
        return None
