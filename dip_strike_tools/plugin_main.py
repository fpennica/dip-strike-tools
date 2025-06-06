#! python3  # noqa: E265

"""Main plugin module."""

# standard
from functools import partial
from pathlib import Path
from typing import Optional

# PyQGIS
from qgis.core import QgsApplication, QgsSettings
from qgis.gui import QgisInterface, QgsMapCanvasItem, QgsMapTool, QgsMapToolEmitPoint
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QTranslator, QUrl, pyqtSignal
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction

# project
from dip_strike_tools.__about__ import (
    DIR_PLUGIN_ROOT,
    __icon_path__,
    __title__,
    __uri_homepage__,
)
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
            callback=self.activate_dip_strike_tool,
            parent=self.iface.mainWindow(),
        )

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

    def activate_dip_strike_tool(self):
        self.custom_tool = CustomMapTool(self.iface.mapCanvas())
        self.custom_tool.canvasClicked["QgsPointXY"].connect(
            lambda point: self.open_dlg_insert_dip_strike(clicked_point=point)
        )
        # Set the custom map tool to the map canvas
        self.log(message=self.tr("Dip Strike Tool activated."), log_level=3)
        self.iface.mapCanvas().setMapTool(self.custom_tool)

    def open_dlg_insert_dip_strike(self, clicked_point=None):
        """Open the dialog to insert a dip strike point."""

        dlg = DlgInsertDipStrike(self.iface.mainWindow(), clicked_point=clicked_point)
        dlg.exec()
        if dlg.result() == DlgInsertDipStrike.Accepted:
            self.log(message=self.tr("Dip Strike Point created successfully."), log_level=3)
        else:
            self.log(message=self.tr("Dip Strike Point creation cancelled."), log_level=2)


class CustomMapTool(QgsMapToolEmitPoint):
    """Custom map tool to handle click events for inserting dip strike points."""

    canvasClicked = pyqtSignal([int], ["QgsPointXY"])

    def __init__(self, canvas):
        # super().__init__(canvas)
        super(QgsMapTool, self).__init__(canvas)
        # self.canvas = canvas

    def canvasReleaseEvent(self, event):
        """Handle canvas press event to open the dip strike dialog."""
        # clicked_point = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos())
        point_canvas_crs = event.mapPoint()
        self.canvasClicked["QgsPointXY"].emit(point_canvas_crs)
