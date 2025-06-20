#! python3  # noqa: E265

"""
Dialog for creating new dip/strike feature layers.
"""

import os

from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
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

        layout = QVBoxLayout(self)

        # Layer name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Layer Name:"))
        self.name_edit = QLineEdit("Dip Strike Points")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Output format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Output Format:"))
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
            "GeoPackage": {"driver": "GPKG", "extension": "gpkg", "description": "SQLite-based OGC standard format"},
            "GeoJSON": {
                "driver": "GeoJSON",
                "extension": "geojson",
                "description": "JSON-based format for web applications",
            },
            "KML": {"driver": "KML", "extension": "kml", "description": "Google Earth format"},
            "CSV": {"driver": "CSV", "extension": "csv", "description": "Comma-separated values with geometry as WKT"},
        }

        for format_name in self.formats.keys():
            self.format_combo.addItem(format_name)

        self.format_combo.setCurrentText("GeoPackage")  # Set default to GeoPackage
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # File path selection (initially hidden for memory layers)
        self.path_layout = QHBoxLayout()
        self.path_label = QLabel("Output File:")
        self.path_layout.addWidget(self.path_label)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select output file location...")
        self.browse_btn = QPushButton("Browse...")
        self.path_layout.addWidget(self.path_edit)
        self.path_layout.addWidget(self.browse_btn)
        layout.addLayout(self.path_layout)

        # Description label
        self.desc_label = QLabel(self.formats["GeoPackage"]["description"])
        self.desc_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        layout.addWidget(self.desc_label)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        # Connect signals
        self.format_combo.currentTextChanged.connect(self.update_format_options)
        self.browse_btn.clicked.connect(self.browse_file)

        # Initialize visibility
        self.update_format_options()

    def update_format_options(self):
        """Update visibility and description based on format selection."""
        selected_format = self.format_combo.currentText()
        is_memory = selected_format == "Memory Layer"

        self.path_edit.setVisible(not is_memory)
        self.browse_btn.setVisible(not is_memory)
        self.path_label.setVisible(not is_memory)

        self.desc_label.setText(self.formats[selected_format]["description"])

        if not is_memory and not self.path_edit.text():
            # Set default filename based on layer name and format
            layer_name = self.name_edit.text().strip() or "dip_strike_points"
            extension = self.formats[selected_format]["extension"]
            if extension:
                self.path_edit.setText(f"{layer_name}.{extension}")

    def browse_file(self):
        """Open file browser to select output file."""
        selected_format = self.format_combo.currentText()
        extension = self.formats[selected_format]["extension"]

        if extension:
            filter_str = f"{selected_format} (*.{extension})"
            filename, _ = QFileDialog.getSaveFileName(
                self,
                f"Save {selected_format} File",
                self.path_edit.text() or f"dip_strike_points.{extension}",
                filter_str,
            )
            if filename:
                self.path_edit.setText(filename)

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
        output_path = self.path_edit.text().strip() if selected_format != "Memory Layer" else ""

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
            self.path_edit.setText(output_path)

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
        """Handle dialog acceptance - validate input before closing."""
        if self.validate_input():
            super().accept()

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
        }
