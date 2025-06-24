#! python3  # noqa: E265

"""
Dialog for creating new dip/strike feature layers.
"""

import os

from qgis.core import QgsProject
from qgis.gui import QgsFileWidget
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
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

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Create New Dip/Strike Layer")
        self.setModal(True)
        self.resize(500, 200)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Form layout for input fields
        form_layout = QFormLayout()

        # Layer name input
        self.name_edit = QLineEdit("Dip Strike Points")
        form_layout.addRow("Layer Name:", self.name_edit)

        # Output format selection
        self.format_combo = QComboBox()

        # Define supported output formats with their details
        self.formats = {
            "Memory Layer": {
                "driver": "memory",
                "extension": "",
                "description": "Temporary layer (lost when QGIS closes)",
            },
            "ESRI Shapefile": {
                "driver": "ESRI Shapefile",
                "extension": "shp",
                "description": "Standard shapefile format",
            },
            "GeoPackage": {
                "driver": "GPKG",
                "extension": "gpkg",
                "description": "SQLite-based OGC standard format (can contain multiple layers)",
            },
        }

        for format_name in self.formats.keys():
            self.format_combo.addItem(format_name)

        self.format_combo.setCurrentText("GeoPackage")  # Set default to GeoPackage
        form_layout.addRow("Output Format:", self.format_combo)

        # File path selection using QgsFileWidget (initially hidden for memory layers and GeoPackage)
        self.file_widget = QgsFileWidget()
        self.file_widget.setStorageMode(QgsFileWidget.SaveFile)
        self.file_widget.setDialogTitle("Save Dip/Strike Layer")

        # Set default root to current QGIS project directory
        project_path = QgsProject.instance().absolutePath()
        if project_path:
            self.file_widget.setDefaultRoot(project_path)
        else:
            self.file_widget.setDefaultRoot("")

        self.file_widget.setFilter("All Files (*)")  # Will be updated based on format selection

        self.path_label = QLabel("Output File:")
        form_layout.addRow(self.path_label, self.file_widget)

        # Geological type storage mode selection
        self.geo_type_combo = QComboBox()
        self.geo_type_combo.addItem("Store numerical code (1, 2, 3...)", "code")
        self.geo_type_combo.addItem("Store text description (Strata, Foliation...)", "description")
        self.geo_type_combo.setToolTip(
            "Choose whether the geo_type field should store numerical codes or text descriptions"
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

        form_layout.addRow("Geo Type Storage:", self.geo_type_combo)

        # Add form layout to main layout
        main_layout.addLayout(form_layout)

        # Description label
        self.desc_label = QLabel(self.formats["GeoPackage"]["description"])
        self.desc_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        main_layout.addWidget(self.desc_label)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        # Connect signals
        self.format_combo.currentTextChanged.connect(self.update_format_options)
        self.name_edit.textChanged.connect(self.update_output_filename)

        # Initialize visibility
        self.update_format_options()

    def update_format_options(self):
        """Update visibility and description based on format selection."""
        selected_format = self.format_combo.currentText()
        is_memory = selected_format == "Memory Layer"

        # Show file widget for all non-memory formats
        self.file_widget.setVisible(not is_memory)
        self.path_label.setVisible(not is_memory)

        self.desc_label.setText(self.formats[selected_format]["description"])

        if not is_memory:
            # Update file filter based on format
            extension = self.formats[selected_format]["extension"]
            if extension:
                # Set the file filter based on format
                filter_str = f"{selected_format} (*.{extension})"
                self.file_widget.setFilter(filter_str)

                # For GeoPackage, allow selecting existing files (to add layers)
                # For other formats, use SaveFile mode (to create new files)
                if selected_format == "GeoPackage":
                    self.file_widget.setStorageMode(QgsFileWidget.GetFile)
                    self.file_widget.setDialogTitle("Select or Create GeoPackage")
                else:
                    self.file_widget.setStorageMode(QgsFileWidget.SaveFile)
                    self.file_widget.setDialogTitle("Save Dip/Strike Layer")

            # Update the output filename
            self.update_output_filename()

    def update_output_filename(self):
        """Update the output filename based on current layer name and format."""
        selected_format = self.format_combo.currentText()

        # Only update for non-memory formats
        if selected_format != "Memory Layer":
            layer_name = self.name_edit.text().strip() or "dip_strike_points"
            extension = self.formats[selected_format]["extension"]

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
            QMessageBox.warning(self, "Invalid Input", "Please enter a layer name.")
            return False

        selected_format = self.format_combo.currentText()
        output_path = self.file_widget.filePath().strip() if selected_format != "Memory Layer" else ""

        # Normalize file path to prevent issues
        if output_path:
            output_path = os.path.normpath(output_path)

        # Validate file path for non-memory layers
        if selected_format != "Memory Layer":
            if not output_path:
                QMessageBox.warning(self, "Invalid Input", "Please specify an output file path.")
                return False

            # Ensure the file has the correct extension
            expected_extension = self.formats[selected_format]["extension"]
            if expected_extension and not output_path.lower().endswith(f".{expected_extension.lower()}"):
                output_path = f"{output_path}.{expected_extension}"

            # Validate file path characters (especially important for shapefiles)
            if selected_format == "ESRI Shapefile":
                # Check for invalid characters in shapefile names
                invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]
                filename = os.path.basename(output_path)
                if any(char in filename for char in invalid_chars):
                    QMessageBox.warning(
                        self,
                        "Invalid Filename",
                        f"Shapefile names cannot contain these characters: {', '.join(invalid_chars)}",
                    )
                    return False

                # Check filename length (shapefiles have a limit)
                name_without_ext = os.path.splitext(filename)[0]
                if len(name_without_ext) > 10:
                    reply = QMessageBox.question(
                        self,
                        "Long Filename",
                        f"Shapefile names longer than 10 characters may cause issues.\n"
                        f"Current name: '{name_without_ext}' ({len(name_without_ext)} characters)\n\n"
                        f"Continue anyway?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if reply == QMessageBox.No:
                        return False

            # Update the path in case extension was added
            self.file_widget.setFilePath(output_path)

            # Check if directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Cannot create output directory: {e}")
                    return False

            # Check if file already exists
            if os.path.exists(output_path):
                # For GeoPackage, allow adding to existing file
                if selected_format == "GeoPackage":
                    # GeoPackage can have multiple layers, so we don't need to overwrite
                    # Just inform the user that the layer will be added to existing GeoPackage
                    reply = QMessageBox.question(
                        self,
                        "Add to Existing GeoPackage",
                        f"The GeoPackage '{output_path}' already exists.\n\n"
                        f"The new layer will be added to this existing GeoPackage database.\n"
                        f"Continue?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes,
                    )
                    if reply == QMessageBox.No:
                        return False
                else:
                    # For other formats, ask about overwriting
                    reply = QMessageBox.question(
                        self,
                        "File Exists",
                        f"The file '{output_path}' already exists.\n\nOverwrite it?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if reply == QMessageBox.No:
                        return False

        # Store validated values
        self.layer_name = layer_name
        self.selected_format = selected_format
        self.output_path = output_path

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
        return {
            "name": self.layer_name,
            "format": self.selected_format,
            "output_path": self.output_path,
            "format_info": self.formats[self.selected_format],
            "geo_type_storage_mode": self.geo_type_combo.currentData(),
        }
