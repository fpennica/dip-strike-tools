#! python3  # noqa: E265

"""
Plugin settings form integrated into QGIS 'Options' menu.
"""

# standard
import platform
from functools import partial
from pathlib import Path
from urllib.parse import quote

# PyQGIS
from qgis.core import Qgis, QgsApplication
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QCoreApplication, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QMessageBox, QTableWidgetItem

# project
from dip_strike_tools.__about__ import (
    __icon_path__,
    __title__,
    __uri_homepage__,
    __uri_tracker__,
    __version__,
)
from dip_strike_tools.toolbelt import PlgLogger, PlgOptionsManager
from dip_strike_tools.toolbelt.preferences import PlgSettingsStructure

# ############################################################################
# ########## Globals ###############
# ##################################

FORM_CLASS, _ = uic.loadUiType(Path(__file__).parent / "{}.ui".format(Path(__file__).stem))


# ############################################################################
# ########## Classes ###############
# ##################################


class ConfigOptionsPage(FORM_CLASS, QgsOptionsPageWidget):
    """Settings form embedded into QGIS 'options' menu."""

    def __init__(self, parent):
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()

        # load UI and set objectName
        self.setupUi(self)
        self.setObjectName("mOptionsPage{}".format(__title__))

        report_context_message = quote(
            "> Reported from plugin settings\n\n"
            f"- operating system: {platform.system()} "
            f"{platform.release()}_{platform.version()}\n"
            f"- QGIS: {Qgis.version()}"
            f"- plugin version: {__version__}\n"
        )

        # header
        self.lbl_title.setText(f"{__title__} - Version {__version__}")

        # customization
        self.btn_help.setIcon(QIcon(QgsApplication.iconPath("mActionHelpContents.svg")))
        self.btn_help.pressed.connect(partial(QDesktopServices.openUrl, QUrl(__uri_homepage__)))

        self.btn_report.setIcon(QIcon(QgsApplication.iconPath("console/iconSyntaxErrorConsole.svg")))

        self.btn_report.pressed.connect(
            partial(
                QDesktopServices.openUrl,
                QUrl(f"{__uri_tracker__}new/?template=10_bug_report.yml&about-info={report_context_message}"),
            )
        )

        self.btn_reset.setIcon(QIcon(QgsApplication.iconPath("mActionUndo.svg")))
        self.btn_reset.pressed.connect(self.reset_settings)

        # Setup geological types table
        self.setup_geological_types_table()

        # Connect geological types buttons
        self.btn_add_geo_type.clicked.connect(self.add_geological_type)
        self.btn_remove_geo_type.clicked.connect(self.remove_geological_type)
        self.btn_sort_geo_types.clicked.connect(lambda: self.sort_geological_types_table(0))
        self.btn_reset_geo_types.clicked.connect(self.reset_geological_types)

        # load previously saved settings
        self.load_settings()

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: String to translate
        :type message: str

        :returns: Translated string
        :rtype: str
        """
        return QCoreApplication.translate("ConfigOptionsPage", message)

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        settings = self.plg_settings.get_plg_settings()

        # misc
        settings.debug_mode = self.opt_debug.isChecked()
        settings.version = __version__

        # geological types
        geo_types = self.get_geological_types_from_table()
        settings.geological_types = ",".join([f"{code}:{desc}" for code, desc in geo_types.items()])

        # dump new settings into QgsSettings
        self.plg_settings.save_from_object(settings)

        if __debug__:
            self.log(
                message="DEBUG - Settings successfully saved.",
                log_level=4,
            )

    def load_settings(self):
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()

        # global
        self.opt_debug.setChecked(settings.debug_mode)
        self.lbl_version_saved_value.setText(settings.version)

        # geological types
        self.load_geological_types()

    def reset_settings(self):
        """Reset settings to default values (set in preferences.py module)."""
        default_settings = PlgSettingsStructure()

        # dump default settings into QgsSettings
        self.plg_settings.save_from_object(default_settings)

        # update the form
        self.load_settings()

    def setup_geological_types_table(self):
        """Setup the geological types table widget."""
        # Set table properties
        self.table_geological_types.setColumnCount(2)
        self.table_geological_types.setHorizontalHeaderLabels([self.tr("Code"), self.tr("Description")])

        # Set column widths
        header = self.table_geological_types.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 80)  # Code column width

        # Enable selection but disable automatic sorting
        self.table_geological_types.setSortingEnabled(False)  # Keep disabled
        self.table_geological_types.setSelectionBehavior(self.table_geological_types.SelectRows)

        # Allow manual header clicking for sorting when needed
        header = self.table_geological_types.horizontalHeader()
        header.sectionClicked.connect(self.sort_geological_types_table)

    def load_geological_types(self):
        """Load geological types from settings into the table."""
        geo_types = self.plg_settings.get_geological_types()

        # Clear existing rows
        self.table_geological_types.setRowCount(0)

        # Add rows for each geological type
        for code, description in geo_types.items():
            row_position = self.table_geological_types.rowCount()
            self.table_geological_types.insertRow(row_position)

            # Create items
            code_item = QTableWidgetItem(str(code))
            description_item = QTableWidgetItem(str(description))

            # Set items in table
            self.table_geological_types.setItem(row_position, 0, code_item)
            self.table_geological_types.setItem(row_position, 1, description_item)

        # Sort by code manually (one time only)
        self.table_geological_types.sortItems(0)

    def add_geological_type(self):
        """Add a new row to the geological types table."""
        # Ensure sorting is disabled to prevent interference
        self.table_geological_types.setSortingEnabled(False)

        # Get current row count and add new row at the end
        row_count = self.table_geological_types.rowCount()
        self.table_geological_types.insertRow(row_count)

        # Create and set empty items for the new row
        code_item = QTableWidgetItem("")
        description_item = QTableWidgetItem("")

        self.table_geological_types.setItem(row_count, 0, code_item)
        self.table_geological_types.setItem(row_count, 1, description_item)

        # Clear any existing selection and select the new row
        self.table_geological_types.clearSelection()
        self.table_geological_types.selectRow(row_count)

        # Start editing the code cell
        self.table_geological_types.editItem(code_item)

    def remove_geological_type(self):
        """Remove the selected geological type from the table."""
        current_row = self.table_geological_types.currentRow()
        if current_row >= 0:
            self.table_geological_types.removeRow(current_row)

    def reset_geological_types(self):
        """Reset geological types to default values."""
        reply = QMessageBox.question(
            self,
            self.tr("Reset Geological Types"),
            self.tr(
                "Are you sure you want to reset the geological types to default values?\n\n"
                "This will replace all current entries with:\n"
                "1: Strata, 2: Foliation, 3: Fault, 4: Joint, 5: Cleavage"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # type: ignore
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Clear the table
            self.table_geological_types.setRowCount(0)

            # Add default types
            default_types = {"1": "Strata", "2": "Foliation", "3": "Fault", "4": "Joint", "5": "Cleavage"}

            for code, description in default_types.items():
                row_position = self.table_geological_types.rowCount()
                self.table_geological_types.insertRow(row_position)

                code_item = QTableWidgetItem(str(code))
                description_item = QTableWidgetItem(str(description))

                self.table_geological_types.setItem(row_position, 0, code_item)
                self.table_geological_types.setItem(row_position, 1, description_item)

            # Sort by code manually (one time only)
            self.table_geological_types.sortItems(0)

    def get_geological_types_from_table(self):
        """Get geological types from the table as a dictionary.

        :return: Dictionary with code as key and description as value
        :rtype: dict
        """
        geo_types = {}

        for row in range(self.table_geological_types.rowCount()):
            code_item = self.table_geological_types.item(row, 0)
            description_item = self.table_geological_types.item(row, 1)

            if code_item and description_item:
                code = code_item.text().strip()
                description = description_item.text().strip()

                if code and description:  # Only add if both code and description are not empty
                    geo_types[code] = description

        return geo_types

    def sort_geological_types_table(self, column):
        """Manually sort the geological types table by the specified column."""
        if column == 0:  # Code column
            # Sort by code (try numeric if possible, otherwise string)
            self.table_geological_types.sortItems(column)
        else:  # Description column
            # Sort by description alphabetically
            self.table_geological_types.sortItems(column)


class PlgOptionsFactory(QgsOptionsWidgetFactory):
    """Factory for options widget."""

    def __init__(self):
        """Constructor."""
        super().__init__()

    def icon(self) -> QIcon:
        """Returns plugin icon, used to as tab icon in QGIS options tab widget.

        :return: _description_
        :rtype: QIcon
        """
        return QIcon(str(__icon_path__))

    def createWidget(self, parent) -> ConfigOptionsPage:
        """Create settings widget.

        :param parent: Qt parent where to include the options page.
        :type parent: QObject

        :return: options page for tab widget
        :rtype: ConfigOptionsPage
        """
        return ConfigOptionsPage(parent)

    def title(self) -> str:
        """Returns plugin title, used to name the tab in QGIS options tab widget.

        :return: plugin title from about module
        :rtype: str
        """
        return __title__

    def helpId(self) -> str:
        """Returns plugin help URL.

        :return: plugin homepage url from about module
        :rtype: str
        """
        return __uri_homepage__
