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

#! python3  # noqa: E265

"""
Dialog for creating new dip/strike feature layers.
"""

import os

from qgis.core import QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgsFileWidget, QgsProjectionSelectionWidget
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QRadioButton,
    QVBoxLayout,
)

from ..toolbelt import PlgLogger


class DlgCreateLayer(QDialog):
    """Dialog for creating new dip/strike layers with format selection."""

    def __init__(self, parent=None):
        """Initialize the layer creation dialog.

        :param parent: Parent widget
        :type parent: QWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log

        # Store dialog results
        self.layer_name = ""
        self.selected_format = ""
        self.output_path = ""
        self.formats = {}
        self.apply_symbology = True
        self.selected_crs = None

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(self.tr("Create New Dip/Strike Layer"))
        self.setModal(True)
        self.resize(500, 350)  # Increased height to accommodate symbology options

        # Main layout
        main_layout = QVBoxLayout(self)

        # Form layout for input fields
        form_layout = QFormLayout()

        # Layer name input
        self.name_edit = QLineEdit("dip_strike_points")
        form_layout.addRow(self.tr("Layer Name:"), self.name_edit)

        # Output format selection
        self.format_combo = QComboBox()

        # Define supported output formats with their details using internal keys
        self.formats = {
            "memory": {
                "driver": "memory",
                "extension": "",
                "description": self.tr("Temporary layer (lost when QGIS closes)"),
                "display_name": self.tr("Memory Layer"),
            },
            "shapefile": {
                "driver": "ESRI Shapefile",
                "extension": "shp",
                "description": self.tr("Standard shapefile format"),
                "display_name": self.tr("ESRI Shapefile"),
            },
            "gpkg": {
                "driver": "GPKG",
                "extension": "gpkg",
                "description": self.tr("SQLite-based OGC standard format (can contain multiple layers)"),
                "display_name": self.tr("GeoPackage"),
            },
        }

        # Populate combo box with display names but store internal keys as data
        for format_key, format_info in self.formats.items():
            self.format_combo.addItem(format_info["display_name"], format_key)

        # Set default to GeoPackage (gpkg key)
        default_index = self.format_combo.findData("gpkg")
        if default_index >= 0:
            self.format_combo.setCurrentIndex(default_index)
        form_layout.addRow(self.tr("Output Format:"), self.format_combo)

        # File path selection using QgsFileWidget (initially hidden for memory layers and GeoPackage)
        self.file_widget = QgsFileWidget()
        self.file_widget.setStorageMode(QgsFileWidget.StorageMode.SaveFile)
        self.file_widget.setDialogTitle(self.tr("Save Dip/Strike Layer"))

        # Set default root to current QGIS project directory
        project_path = QgsProject.instance().absolutePath()
        if project_path:
            self.file_widget.setDefaultRoot(project_path)
        else:
            self.file_widget.setDefaultRoot("")

        self.file_widget.setFilter("All Files (*)")  # Will be updated based on format selection

        self.path_label = QLabel(self.tr("Output File:"))
        form_layout.addRow(self.path_label, self.file_widget)

        # Coordinate Reference System selection
        crs_group = QGroupBox(self.tr("Coordinate Reference System"))
        crs_layout = QVBoxLayout(crs_group)

        # Radio buttons for CRS selection method
        self.use_canvas_crs_radio = QRadioButton(self.tr("Use current map canvas CRS"))
        self.use_custom_crs_radio = QRadioButton(self.tr("Select custom CRS:"))

        # Set default to use canvas CRS
        self.use_canvas_crs_radio.setChecked(True)

        crs_layout.addWidget(self.use_canvas_crs_radio)
        crs_layout.addWidget(self.use_custom_crs_radio)

        # CRS selection widget
        self.crs_widget = QgsProjectionSelectionWidget()

        # Get current map canvas CRS and set it as default
        try:
            from qgis.utils import iface

            if iface and iface.mapCanvas():  # type: ignore
                canvas_crs = iface.mapCanvas().mapSettings().destinationCrs()  # type: ignore
                self.crs_widget.setCrs(canvas_crs)

                # Add canvas CRS info to the radio button text
                if canvas_crs.isValid():
                    crs_desc = f"{canvas_crs.authid()} - {canvas_crs.description()}"
                    self.use_canvas_crs_radio.setText(self.tr("Use current map canvas CRS ({})").format(crs_desc))
            else:
                # Fallback to WGS84 if no canvas available
                fallback_crs = QgsCoordinateReferenceSystem("EPSG:4326")
                self.crs_widget.setCrs(fallback_crs)
        except Exception:
            # Fallback to WGS84
            fallback_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            self.crs_widget.setCrs(fallback_crs)

        # Initially disable the CRS widget since canvas CRS is selected by default
        self.crs_widget.setEnabled(False)

        crs_layout.addWidget(self.crs_widget)

        # Connect radio button signals
        self.use_canvas_crs_radio.toggled.connect(self.update_crs_selection_mode)
        self.use_custom_crs_radio.toggled.connect(self.update_crs_selection_mode)

        form_layout.addRow(crs_group)

        # Optional fields selection
        optional_fields_group = QGroupBox(self.tr("Optional Fields"))
        optional_fields_layout = QVBoxLayout(optional_fields_group)

        # Geo type field checkbox
        self.geo_type_check = QCheckBox(self.tr("Geological type (geo_type)"))
        self.geo_type_check.setChecked(True)  # Default to enabled
        self.geo_type_check.setToolTip(self.tr("Add a field to store geological type information"))
        optional_fields_layout.addWidget(self.geo_type_check)

        # Geological type storage mode selection (shown only when geo_type is checked)
        geo_type_storage_layout = QFormLayout()
        self.geo_type_combo = QComboBox()
        self.geo_type_combo.addItem(self.tr("Store numerical code (1, 2, 3...)"), "code")
        self.geo_type_combo.addItem(self.tr("Store text description (Strata, Foliation...)"), "description")
        self.geo_type_combo.setToolTip(
            self.tr("Choose whether the geo_type field should store numerical codes or text descriptions")
        )

        # Load current storage mode from preferences
        try:
            from ..toolbelt.preferences import PlgOptionsManager

            current_mode = PlgOptionsManager.get_geo_type_storage_mode()
            for i in range(self.geo_type_combo.count()):
                if self.geo_type_combo.itemData(i) == current_mode:
                    self.geo_type_combo.setCurrentIndex(i)
                    break
        except Exception:
            pass  # Use default selection

        geo_type_storage_layout.addRow(self.tr("    Storage mode:"), self.geo_type_combo)
        optional_fields_layout.addLayout(geo_type_storage_layout)

        # Age field checkbox
        self.age_check = QCheckBox(self.tr("Age (age)"))
        self.age_check.setChecked(True)  # Default to enabled
        self.age_check.setToolTip(self.tr("Add a field to store age information"))
        optional_fields_layout.addWidget(self.age_check)

        # Lithology field checkbox
        self.lithology_check = QCheckBox(self.tr("Lithology (lithology)"))
        self.lithology_check.setChecked(True)  # Default to enabled
        self.lithology_check.setToolTip(self.tr("Add a field to store lithology information"))
        optional_fields_layout.addWidget(self.lithology_check)

        # Notes field checkbox
        self.notes_check = QCheckBox(self.tr("Notes (notes)"))
        self.notes_check.setChecked(True)  # Default to enabled
        self.notes_check.setToolTip(self.tr("Add a field to store additional notes"))
        optional_fields_layout.addWidget(self.notes_check)

        # Z-value field checkbox
        self.z_value_check = QCheckBox(self.tr("Elevation (z_value)"))
        self.z_value_check.setChecked(True)  # Default to enabled
        self.z_value_check.setToolTip(self.tr("Add a field to store elevation/z-value information"))
        optional_fields_layout.addWidget(self.z_value_check)

        # Connect geo_type checkbox to show/hide storage mode
        self.geo_type_check.toggled.connect(self.update_geo_type_storage_visibility)

        form_layout.addRow(optional_fields_group)

        # Symbology options
        symbology_group = QGroupBox(self.tr("Symbology Options"))
        symbology_layout = QFormLayout(symbology_group)

        # Apply symbology checkbox
        self.apply_symbology_check = QCheckBox(self.tr("Apply default symbology"))
        self.apply_symbology_check.setChecked(True)  # Default to enabled
        self.apply_symbology_check.setToolTip(
            self.tr("Apply predefined single symbol symbology with rotated symbols and dip value labels")
        )
        symbology_layout.addRow(self.apply_symbology_check)

        # Add symbology group to main form layout
        form_layout.addRow(symbology_group)

        # Add form layout to main layout
        main_layout.addLayout(form_layout)

        # Description label
        self.desc_label = QLabel(self.formats["gpkg"]["description"])
        self.desc_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        main_layout.addWidget(self.desc_label)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)  # type: ignore
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        # Connect signals
        self.format_combo.currentTextChanged.connect(self.update_format_options)
        self.name_edit.textChanged.connect(self.update_output_filename)

        # Initialize visibility
        self.update_format_options()

    def update_crs_selection_mode(self):
        """Update CRS selection widget state based on radio button selection."""
        # Enable/disable the CRS widget based on which radio button is selected
        use_custom = self.use_custom_crs_radio.isChecked()
        self.crs_widget.setEnabled(use_custom)

    def get_selected_crs(self):
        """Get the selected CRS based on the current selection mode.

        :returns: Selected coordinate reference system
        :rtype: QgsCoordinateReferenceSystem
        """
        if self.use_canvas_crs_radio.isChecked():
            # Return current map canvas CRS
            try:
                from qgis.utils import iface

                if iface and hasattr(iface, "mapCanvas") and iface.mapCanvas():  # type: ignore
                    return iface.mapCanvas().mapSettings().destinationCrs()  # type: ignore
                else:
                    # Fallback to project CRS if no canvas available
                    project_crs = QgsProject.instance().crs()
                    if project_crs.isValid():
                        return project_crs
                    else:
                        # Final fallback to WGS84
                        return QgsCoordinateReferenceSystem("EPSG:4326")
            except Exception:
                # Fallback to WGS84
                return QgsCoordinateReferenceSystem("EPSG:4326")
        else:
            # Return selected custom CRS
            return self.crs_widget.crs()

    def update_format_options(self):
        """Update visibility and description based on format selection."""
        # Get the internal format key from combo box data
        selected_format_key = self.format_combo.currentData()
        if not selected_format_key:
            return

        format_info = self.formats[selected_format_key]
        is_memory = selected_format_key == "memory"

        # Show file widget for all non-memory formats
        self.file_widget.setVisible(not is_memory)
        self.path_label.setVisible(not is_memory)

        self.desc_label.setText(format_info["description"])

        if not is_memory:
            # Update file filter based on format
            extension = format_info["extension"]
            if extension:
                # Set the file filter based on format
                filter_str = f"{format_info['display_name']} (*.{extension})"
                self.file_widget.setFilter(filter_str)

                # For GeoPackage, allow selecting existing files (to add layers)
                # For other formats, use SaveFile mode (to create new files)
                if selected_format_key == "gpkg":
                    self.file_widget.setStorageMode(QgsFileWidget.StorageMode.GetFile)
                    self.file_widget.setDialogTitle(self.tr("Select or Create GeoPackage"))
                else:
                    self.file_widget.setStorageMode(QgsFileWidget.StorageMode.SaveFile)
                    self.file_widget.setDialogTitle(self.tr("Save Dip/Strike Layer"))

            # Update the output filename
            self.update_output_filename()

    def update_output_filename(self):
        """Update the output filename based on current layer name and format."""
        # Get the internal format key from combo box data
        selected_format_key = self.format_combo.currentData()
        if not selected_format_key:
            return

        # Only update for non-memory formats
        if selected_format_key != "memory":
            layer_name = self.name_edit.text().strip() or "dip_strike_points"
            format_info = self.formats[selected_format_key]
            extension = format_info["extension"]

            if extension:
                # Use project directory if available, otherwise use current directory
                project_path = QgsProject.instance().absolutePath()
                if project_path:
                    default_path = os.path.join(project_path, f"{layer_name}.{extension}")
                else:
                    default_path = f"{layer_name}.{extension}"
                self.file_widget.setFilePath(default_path)

    def validate_input(self):
        """Validate user input and show appropriate warnings.

        :returns: True if input is valid, False otherwise
        :rtype: bool
        """
        layer_name = self.name_edit.text().strip()
        if not layer_name:
            QMessageBox.warning(self, self.tr("Invalid Input"), self.tr("Please enter a layer name."))
            return False

        # Get the internal format key from combo box data
        selected_format_key = self.format_combo.currentData()
        if not selected_format_key:
            return False

        format_info = self.formats[selected_format_key]
        output_path = self.file_widget.filePath().strip() if selected_format_key != "memory" else ""

        # Normalize file path to prevent issues
        if output_path:
            output_path = os.path.normpath(output_path)

        # Validate file path for non-memory layers
        if selected_format_key != "memory":
            if not output_path:
                QMessageBox.warning(self, self.tr("Invalid Input"), self.tr("Please specify an output file path."))
                return False

            # Ensure the file has the correct extension
            expected_extension = format_info["extension"]
            if expected_extension and not output_path.lower().endswith(f".{expected_extension.lower()}"):
                output_path = f"{output_path}.{expected_extension}"

            # Validate file path characters (especially important for shapefiles)
            if selected_format_key == "shapefile":
                # Check for invalid characters in shapefile names
                invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]
                filename = os.path.basename(output_path)
                if any(char in filename for char in invalid_chars):
                    QMessageBox.warning(
                        self,
                        self.tr("Invalid Filename"),
                        self.tr("Shapefile names cannot contain these characters: {}").format(
                            ", ".join(invalid_chars)
                        ),
                    )
                    return False

                # Check filename length (shapefiles have a limit)
                name_without_ext = os.path.splitext(filename)[0]
                if len(name_without_ext) > 10:
                    reply = QMessageBox.question(
                        self,
                        self.tr("Long Filename"),
                        self.tr(
                            "Shapefile names longer than 10 characters may cause issues.\n"
                            "Current name: '{}' ({} characters)\n\n"
                            "Continue anyway?"
                        ).format(name_without_ext, len(name_without_ext)),
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # type: ignore
                        QMessageBox.StandardButton.No,
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return False

            # Update the path in case extension was added
            self.file_widget.setFilePath(output_path)

            # Check if directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except Exception as e:
                    QMessageBox.critical(
                        self, self.tr("Error"), self.tr("Cannot create output directory: {}").format(e)
                    )
                    return False

            # Check if file already exists
            if os.path.exists(output_path):
                # For GeoPackage, allow adding to existing file
                if selected_format_key == "gpkg":
                    # GeoPackage can have multiple layers, so we don't need to overwrite
                    # Just inform the user that the layer will be added to existing GeoPackage
                    reply = QMessageBox.question(
                        self,
                        self.tr("Add to Existing GeoPackage"),
                        self.tr(
                            "The GeoPackage '{}' already exists.\n\n"
                            "The new layer will be added to this existing GeoPackage database.\n"
                            "Continue?"
                        ).format(output_path),
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # type: ignore
                        QMessageBox.StandardButton.Yes,
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return False
                else:
                    # For other formats, ask about overwriting
                    reply = QMessageBox.question(
                        self,
                        self.tr("File Exists"),
                        self.tr("The file '{}' already exists.\n\nOverwrite it?").format(output_path),
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # type: ignore
                        QMessageBox.StandardButton.No,
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return False

        # Store validated values
        self.layer_name = layer_name
        self.selected_format = selected_format_key  # Store the internal key
        self.output_path = output_path
        self.apply_symbology = self.apply_symbology_check.isChecked()
        self.selected_crs = self.get_selected_crs()

        return True

    def accept(self):
        """Handle dialog acceptance - validate input and save preferences before closing."""
        # Use standard validation for all formats
        if self.validate_input():
            # Save preferences and close
            self.save_preferences()
            super().accept()

    def save_preferences(self):
        """Save the geological type storage mode preference."""
        try:
            from ..toolbelt.preferences import PlgOptionsManager

            selected_mode = self.geo_type_combo.currentData()
            if selected_mode:
                PlgOptionsManager.set_geo_type_storage_mode(selected_mode)
                self.log(f"Saved geo_type storage mode preference: {selected_mode}", log_level=4)
        except Exception as e:
            self.log(f"Error saving geo_type storage mode preference: {e}", log_level=2)

    def get_layer_config(self):
        """Get the layer configuration from dialog input.

        :returns: Dictionary with layer configuration
        :rtype: dict
        """
        # Get selected optional fields
        optional_fields = {
            "geo_type": self.geo_type_check.isChecked(),
            "age": self.age_check.isChecked(),
            "lithology": self.lithology_check.isChecked(),
            "notes": self.notes_check.isChecked(),
            "z_value": self.z_value_check.isChecked(),
        }

        return {
            "name": self.layer_name,
            "format": self.selected_format,
            "output_path": self.output_path,
            "format_info": self.formats[self.selected_format],
            "geo_type_storage_mode": self.geo_type_combo.currentData(),
            "symbology": {"apply": self.apply_symbology},
            "crs": self.selected_crs,
            "optional_fields": optional_fields,
        }

    def update_geo_type_storage_visibility(self):
        """Update geo type storage mode visibility based on geo_type checkbox state."""
        # Show/hide the geo type storage mode based on checkbox state
        is_checked = self.geo_type_check.isChecked()
        self.geo_type_combo.setVisible(is_checked)

    def tr(self, source_text, disambiguation=None, n=-1):
        """Translate the given text to the user's language.

        :param source_text: The text to translate
        :type source_text: str
        :param disambiguation: Optional disambiguation context
        :type disambiguation: str
        :param n: Optional plural form index (0 for singular, 1 for plural)
        :type n: int
        :returns: Translated text
        :rtype: str
        """
        # Use QCoreApplication's translate method for translation
        return QCoreApplication.translate("DlgCreateLayer", source_text, disambiguation, n)
