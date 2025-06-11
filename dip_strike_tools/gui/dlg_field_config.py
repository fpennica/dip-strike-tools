#! python3  # noqa: E265

"""
Dialog for configuring field mappings for dip/strike feature layers.
"""

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
)

from ..toolbelt import PlgLogger


class DlgFieldConfig(QDialog):
    """Dialog for configuring field mappings for dip/strike layers.

    This dialog allows users to map the actual field names in their vector layer
    to the standardized field names expected by the dip/strike tools plugin.

    Required field mappings:
    - strike_azimuth: Numeric field containing strike azimuth values (0-360°)
    - dip_azimuth: Numeric field containing dip azimuth values (0-360°)
    - dip_value: Numeric field containing dip angle values (0-90°)

    Optional field mappings:
    - geo_type: Text field for geological type/formation information
    - age: Text field for geological age/period information
    - lithology: Text field for rock type/lithology information
    - notes: Text field for additional notes or comments

    The dialog provides:
    - Automatic field suggestion based on field names and types
    - Real-time validation with visual feedback
    - Support for loading and saving existing configurations
    - Clear indication of required vs optional fields
    - Prevention of duplicate field mappings with visual highlighting
    - Comprehensive error messages for invalid configurations
    - Automatic filtering of ID fields (id, fid, objectid, etc.) from selection options

    Configuration is stored as custom properties on the layer using the
    "dip_strike_tools/" prefix.
    """

    def __init__(self, layer, parent=None):
        """Initialize the field configuration dialog.

        :param layer: The layer to configure field mappings for
        :type layer: QgsVectorLayer
        :param parent: Parent widget
        :type parent: QWidget
        """
        super().__init__(parent)
        self.layer = layer
        self.log = PlgLogger().log

        # Define required and optional fields
        self.required_fields = {
            "strike_azimuth": "Strike Azimuth",
            "dip_azimuth": "Dip Azimuth",
            "dip_value": "Dip Value",
        }

        self.optional_fields = {
            "geo_type": "Geological Type",
            "age": "Age",
            "lithology": "Lithology",
            "notes": "Notes",
        }

        # Store field mapping comboboxes
        self.field_combos = {}

        # Initialize UI components references
        self.ok_button = None
        self.button_box = None

        self.setup_ui()
        self.load_current_mappings()

    def _is_id_field(self, field_name):
        """Check if a field is an ID field that should be excluded from mapping options.

        :param field_name: The name of the field to check
        :type field_name: str
        :return: True if the field is an ID field that should be excluded
        :rtype: bool
        """
        if not field_name:
            return False

        field_name_lower = field_name.lower()

        # Common ID field patterns to exclude
        id_patterns = [
            "id",  # Generic ID
            "fid",  # Feature ID
            "objectid",  # Object ID
            "gid",  # Geographic ID
            "uid",  # Unique ID
            "oid",  # Object identifier
            "pk",  # Primary key
            "key",  # Key fields
            "rowid",  # Row ID
            "geom_id",  # Geometry ID
            "feat_id",  # Feature ID variation
        ]

        # Check if field name exactly matches any ID pattern
        if field_name_lower in id_patterns:
            return True

        # Check if field name starts or ends with ID patterns
        for pattern in ["id", "fid", "objectid", "gid"]:
            if (
                field_name_lower.startswith(pattern + "_")
                or field_name_lower.endswith("_" + pattern)
                or field_name_lower == pattern
            ):
                return True

        return False

    def _suggest_field_mapping(self, combo, field_key, numeric_fields, text_fields):
        """Suggest appropriate field mapping based on field name and type."""
        # Define suggestion patterns for each field
        suggestions = {
            "strike_azimuth": ["strike", "azimuth", "bearing", "direction"],
            "dip_azimuth": ["dip", "azimuth", "bearing", "direction"],
            "dip_value": ["dip", "angle", "value", "degree"],
            "geo_type": ["type", "geology", "geo", "formation"],
            "age": ["age", "period", "era", "time"],
            "lithology": ["lithology", "litho", "rock", "material"],
            "notes": ["notes", "comment", "description", "remark"],
        }

        if field_key not in suggestions:
            return

        # Get the appropriate field list based on field type
        if field_key in ["strike_azimuth", "dip_azimuth", "dip_value"]:
            candidate_fields = numeric_fields
        else:
            candidate_fields = text_fields

        # Get currently mapped fields to avoid suggesting duplicates
        currently_mapped = set()
        for other_combo in self.field_combos.values():
            if other_combo != combo:  # Don't check the current combo
                selected = other_combo.currentText()
                if selected != "<None>" and selected:
                    currently_mapped.add(selected)

        # Look for matching field names that aren't already mapped
        for pattern in suggestions[field_key]:
            for field_name in candidate_fields:
                if field_name not in currently_mapped and pattern.lower() in field_name.lower():
                    index = combo.findText(field_name)
                    if index >= 0:
                        combo.setCurrentIndex(index)
                        self.log(f"Auto-suggested field '{field_name}' for {field_key}", log_level=4)
                        return

    def validate_mappings(self):
        """Validate current field mappings and update status."""
        missing_required = []
        mapped_optional = []
        duplicate_mappings = []

        # Track which fields are already mapped
        used_fields = {}

        # Check all field mappings for duplicates
        all_fields = {**self.required_fields, **self.optional_fields}
        for field_key, field_label in all_fields.items():
            combo = self.field_combos[field_key]
            selected_field = combo.currentText()

            if selected_field != "<None>" and selected_field:
                if selected_field in used_fields:
                    # Found a duplicate mapping
                    duplicate_mappings.append(
                        {"field": selected_field, "mapped_to": [used_fields[selected_field], field_label]}
                    )
                else:
                    used_fields[selected_field] = field_label

        # Check required fields
        for field_key, field_label in self.required_fields.items():
            combo = self.field_combos[field_key]
            selected_field = combo.currentText()

            if selected_field == "<None>" or not selected_field:
                missing_required.append(field_label)

        # Check optional fields
        for field_key, field_label in self.optional_fields.items():
            combo = self.field_combos[field_key]
            selected_field = combo.currentText()

            if selected_field != "<None>" and selected_field:
                mapped_optional.append(field_label)

        # Update status message based on validation results
        if duplicate_mappings:
            # Show duplicate mapping error with highest priority
            duplicate_info = []
            for dup in duplicate_mappings:
                duplicate_info.append(f"'{dup['field']}' → {' & '.join(dup['mapped_to'])}")

            status_msg = f"❌ Duplicate field mappings: {'; '.join(duplicate_info)}"
            self.status_label.setStyleSheet(
                "padding: 8px; border-radius: 4px; background-color: #f8d7da; color: #721c24;"
            )

            # Highlight combo boxes with duplicate mappings
            self._highlight_duplicate_combos(used_fields)

        elif missing_required:
            status_msg = f"⚠️ Missing required fields: {', '.join(missing_required)}"
            self.status_label.setStyleSheet(
                "padding: 8px; border-radius: 4px; background-color: #fff3cd; color: #856404;"
            )

            # Clear any duplicate highlighting
            self._clear_duplicate_highlighting()

        else:
            status_msg = "✅ All required fields are mapped"
            if mapped_optional:
                status_msg += f" | Optional fields: {', '.join(mapped_optional)}"
            self.status_label.setStyleSheet(
                "padding: 8px; border-radius: 4px; background-color: #d4edda; color: #155724;"
            )

            # Clear any duplicate highlighting
            self._clear_duplicate_highlighting()

        self.status_label.setText(status_msg)

        # Enable/disable OK button based on validation state
        is_valid = len(duplicate_mappings) == 0 and len(missing_required) == 0
        if self.ok_button is not None:
            self.ok_button.setEnabled(is_valid)
            # Update button tooltip to provide helpful feedback
            if not is_valid:
                if duplicate_mappings:
                    self.ok_button.setToolTip("Cannot save: duplicate field mappings detected")
                elif missing_required:
                    self.ok_button.setToolTip("Cannot save: required fields are missing")
                # Add subtle visual styling for disabled state
                self.ok_button.setStyleSheet("QPushButton:disabled { color: #999; }")
            else:
                self.ok_button.setToolTip("Save field mappings and close dialog")
                # Clear any custom styling for enabled state
                self.ok_button.setStyleSheet("")

        # Return validation state for use in save_mappings
        return is_valid

    def _highlight_duplicate_combos(self, used_fields):
        """Highlight combo boxes that have duplicate field mappings."""
        # Count occurrences of each field
        field_counts = {}
        for field_key, field_label in {**self.required_fields, **self.optional_fields}.items():
            combo = self.field_combos[field_key]
            selected_field = combo.currentText()

            if selected_field != "<None>" and selected_field:
                field_counts[selected_field] = field_counts.get(selected_field, 0) + 1

        # Find duplicated fields
        duplicated_fields = {field for field, count in field_counts.items() if count > 1}

        # Apply highlighting to combos with duplicated selections
        for field_key, combo in self.field_combos.items():
            selected_field = combo.currentText()
            if selected_field in duplicated_fields:
                combo.setStyleSheet("QComboBox { border: 2px solid #dc3545; background-color: #f8d7da; }")
            else:
                combo.setStyleSheet("")  # Clear styling

    def _clear_duplicate_highlighting(self):
        """Clear duplicate highlighting from all combo boxes."""
        for combo in self.field_combos.values():
            combo.setStyleSheet("")  # Clear all styling

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(f"Configure Field Mappings - {self.layer.name()}")
        self.setWindowIcon(QIcon(QgsApplication.iconPath("mActionNewAttribute.svg")))
        self.setModal(True)
        self.resize(400, 300)

        # Main layout
        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel(
            f"Map the required and optional fields for layer: <b>{self.layer.name()}</b><br/>"
            f"<small>Layer has {self.layer.featureCount()} features and {len(self.layer.fields())} fields.</small>"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Required fields group
        required_group = QGroupBox("Required Fields")
        required_layout = QFormLayout(required_group)

        # Get available field names from the layer with type information
        field_names = ["<None>"]
        numeric_fields = []
        text_fields = []
        filtered_count = 0

        for field in self.layer.fields():
            field_name = field.name()

            # Filter out ID fields that are not suitable for dip/strike mapping
            if self._is_id_field(field_name):
                filtered_count += 1
                self.log(f"Filtered out ID field: {field_name}", log_level=4)
                continue

            field_names.append(field_name)

            # Categorize fields by type for better suggestions
            if field.isNumeric():
                numeric_fields.append(field_name)
            else:
                text_fields.append(field_name)

        if filtered_count > 0:
            self.log(f"Filtered out {filtered_count} ID field(s) from field mapping options", log_level=4)

        # Create comboboxes for required fields
        for field_key, field_label in self.required_fields.items():
            combo = QComboBox()
            combo.addItems(field_names)
            combo.setToolTip(f"Select the layer field that contains {field_label.lower()} data")

            # Try to auto-suggest fields based on name similarity
            self._suggest_field_mapping(combo, field_key, numeric_fields, text_fields)

            label = QLabel(f"{field_label} *")
            label.setStyleSheet("font-weight: bold; color: #d32f2f;")

            required_layout.addRow(label, combo)
            self.field_combos[field_key] = combo

        layout.addWidget(required_group)

        # Optional fields group
        optional_group = QGroupBox("Optional Fields")
        optional_layout = QFormLayout(optional_group)

        # Create comboboxes for optional fields
        for field_key, field_label in self.optional_fields.items():
            combo = QComboBox()
            combo.addItems(field_names)
            combo.setToolTip(f"Select the layer field that contains {field_label.lower()} data (optional)")

            # Try to auto-suggest fields based on name similarity
            self._suggest_field_mapping(combo, field_key, numeric_fields, text_fields)

            label = QLabel(field_label)
            label.setStyleSheet("color: #666;")

            optional_layout.addRow(label, combo)
            self.field_combos[field_key] = combo

        layout.addWidget(optional_group)

        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("padding: 8px; border-radius: 4px; background-color: #f5f5f5;")
        layout.addWidget(self.status_label)

        # Connect all combos to validation
        for combo in self.field_combos.values():
            combo.currentTextChanged.connect(self.validate_mappings)

        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Store reference to OK button for enabling/disabling
        self.ok_button = self.button_box.button(QDialogButtonBox.Ok)

        layout.addWidget(self.button_box)

        # Perform initial validation to set button state correctly
        # This will be called again in load_current_mappings, but ensures proper state
        self.validate_mappings()

    def load_current_mappings(self):
        """Load current field mappings from layer custom properties."""
        try:
            for field_key in list(self.required_fields.keys()) + list(self.optional_fields.keys()):
                combo = self.field_combos[field_key]

                # Get current mapping from layer custom properties
                current_mapping = self.layer.customProperty(f"dip_strike_tools/{field_key}", "")

                if current_mapping:
                    # Find and select the current mapping in the combobox
                    index = combo.findText(current_mapping)
                    if index >= 0:
                        combo.setCurrentIndex(index)
                        self.log(f"Loaded mapping for {field_key}: {current_mapping}", log_level=4)
                    else:
                        self.log(f"Field {current_mapping} not found for {field_key}", log_level=2)

        except Exception as e:
            self.log(f"Error loading current mappings: {e}", log_level=1)

        # Validate mappings after loading
        self.validate_mappings()

    def save_mappings(self):
        """Save field mappings to layer custom properties."""
        try:
            # First validate all mappings
            is_valid = self.validate_mappings()

            if not is_valid:
                from qgis.PyQt.QtWidgets import QMessageBox

                # Check for specific validation issues
                missing_required = []
                duplicate_mappings = []
                used_fields = {}

                # Check for duplicates and missing required fields
                all_fields = {**self.required_fields, **self.optional_fields}
                for field_key, field_label in all_fields.items():
                    combo = self.field_combos[field_key]
                    selected_field = combo.currentText()

                    if selected_field != "<None>" and selected_field:
                        if selected_field in used_fields:
                            duplicate_mappings.append(
                                {"field": selected_field, "mapped_to": [used_fields[selected_field], field_label]}
                            )
                        else:
                            used_fields[selected_field] = field_label

                # Check for missing required fields
                for field_key, field_label in self.required_fields.items():
                    combo = self.field_combos[field_key]
                    selected_field = combo.currentText()

                    if selected_field == "<None>" or not selected_field:
                        missing_required.append(field_label)

                # Show appropriate error message
                if duplicate_mappings:
                    duplicate_info = []
                    for dup in duplicate_mappings:
                        duplicate_info.append(
                            f"• Field '{dup['field']}' is mapped to both {' and '.join(dup['mapped_to'])}"
                        )

                    QMessageBox.warning(
                        self,
                        "Duplicate Field Mappings",
                        "Each layer field can only be mapped once:\n\n"
                        + "\n".join(duplicate_info)
                        + "\n\nPlease select different fields for each mapping.",
                    )
                elif missing_required:
                    QMessageBox.warning(
                        self,
                        "Missing Required Fields",
                        "The following required fields must be mapped:\n\n"
                        + "\n".join(f"• {field}" for field in missing_required),
                    )

                return False

            # Save all field mappings since validation passed
            for field_key, field_label in self.required_fields.items():
                combo = self.field_combos[field_key]
                selected_field = combo.currentText()

                if selected_field != "<None>" and selected_field:
                    self.layer.setCustomProperty(f"dip_strike_tools/{field_key}", selected_field)
                    self.log(f"Saved mapping for {field_key}: {selected_field}", log_level=4)

            # Save optional field mappings
            for field_key, field_label in self.optional_fields.items():
                combo = self.field_combos[field_key]
                selected_field = combo.currentText()

                if selected_field != "<None>" and selected_field:
                    self.layer.setCustomProperty(f"dip_strike_tools/{field_key}", selected_field)
                    self.log(f"Saved optional mapping for {field_key}: {selected_field}", log_level=4)
                else:
                    # Remove the custom property if no field is selected
                    self.layer.removeCustomProperty(f"dip_strike_tools/{field_key}")

            # Mark layer as configured for dip/strike features
            self.layer.setCustomProperty("dip_strike_tools/layer_role", "dip_strike_feature_layer")

            self.log(f"Successfully configured field mappings for layer: {self.layer.name()}", log_level=3)

            return True

        except Exception as e:
            self.log(f"Error saving field mappings: {e}", log_level=1)
            return False

    def accept(self):
        """Handle dialog acceptance - save mappings if valid."""
        if self.save_mappings():
            super().accept()

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)
