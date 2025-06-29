#! python3  # noqa: E265

"""
Dialog for calculating dip or strike values from existing fields.
"""

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication, QVariant
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
    QSpinBox,
    QVBoxLayout,
)

from ..toolbelt import PlgLogger


class DlgCalculateValues(QDialog):
    """Dialog for calculating dip or strike values from existing fields."""

    def __init__(self, parent=None):
        """Initialize the calculation dialog.

        :param parent: Parent widget
        :type parent: QWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log

        # Store dialog results
        self.selected_layer = None
        self.calculation_type = "dip_from_strike"  # or "strike_from_dip"
        self.input_field = None
        self.output_field = None
        self.create_new_field = False
        self.new_field_name = ""
        self.decimal_places = 2  # Default rounding to 2 decimal places

        self.setup_ui()
        self.populate_layers()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(self.tr("Calculate Dip/Strike Values"))
        self.setModal(True)
        self.resize(450, 400)

        # Main layout
        layout = QVBoxLayout(self)

        # Layer selection group
        layer_group = QGroupBox(self.tr("Layer Selection"))
        layer_layout = QFormLayout(layer_group)

        self.layer_combo = QComboBox()
        self.layer_combo.currentTextChanged.connect(self.on_layer_changed)
        layer_layout.addRow(QLabel(self.tr("Select Layer:")), self.layer_combo)

        layout.addWidget(layer_group)

        # Calculation type group
        calc_group = QGroupBox(self.tr("Calculation Type"))
        calc_layout = QVBoxLayout(calc_group)

        self.radio_dip_from_strike = QRadioButton(self.tr("Calculate Dip Azimuth from Strike Azimuth"))
        self.radio_strike_from_dip = QRadioButton(self.tr("Calculate Strike Azimuth from Dip Azimuth"))
        self.radio_dip_from_strike.setChecked(True)

        self.radio_dip_from_strike.toggled.connect(self.on_calculation_type_changed)
        self.radio_strike_from_dip.toggled.connect(self.on_calculation_type_changed)

        calc_layout.addWidget(self.radio_dip_from_strike)
        calc_layout.addWidget(self.radio_strike_from_dip)

        # Add help text
        # help_label = QLabel(
        #     self.tr("Note: Dip azimuth = Strike azimuth ± 90°\nThe tool will calculate the perpendicular direction.")
        # )
        # help_label.setStyleSheet("color: gray; font-style: italic;")
        # calc_layout.addWidget(help_label)

        layout.addWidget(calc_group)

        # Field selection group
        field_group = QGroupBox(self.tr("Field Selection"))
        field_layout = QFormLayout(field_group)

        self.input_field_combo = QComboBox()
        field_layout.addRow(QLabel(self.tr("Input Field:")), self.input_field_combo)

        # Output field selection
        self.output_field_combo = QComboBox()
        self.create_field_checkbox = QCheckBox(self.tr("Create new field"))
        self.new_field_name_edit = QLineEdit()
        self.new_field_name_edit.setPlaceholderText(self.tr("Enter new field name"))
        self.new_field_name_edit.setEnabled(False)

        self.create_field_checkbox.toggled.connect(self.on_create_field_toggled)

        field_layout.addRow(QLabel(self.tr("Output Field:")), self.output_field_combo)
        field_layout.addRow("", self.create_field_checkbox)
        field_layout.addRow(QLabel(self.tr("New Field Name:")), self.new_field_name_edit)

        layout.addWidget(field_group)

        # Rounding options group
        rounding_group = QGroupBox(self.tr("Calculation Options"))
        rounding_layout = QFormLayout(rounding_group)

        self.decimal_places_spinbox = QSpinBox()
        self.decimal_places_spinbox.setRange(0, 10)
        self.decimal_places_spinbox.setValue(2)  # Default to 2 decimal places
        self.decimal_places_spinbox.setSuffix(self.tr(" decimal places"))
        self.decimal_places_spinbox.valueChanged.connect(self.on_decimal_places_changed)

        rounding_layout.addRow(QLabel(self.tr("Round to:")), self.decimal_places_spinbox)

        layout.addWidget(rounding_group)

        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

    def populate_layers(self):
        """Populate the layer combo box with available vector layers and tables."""
        self.layer_combo.clear()
        self.layer_combo.addItem(self.tr("-- Select a layer --"), None)

        project = QgsProject.instance()
        if not project:
            return

        for layer_id, layer in project.mapLayers().items():
            if isinstance(layer, QgsVectorLayer) and layer.isValid():
                # Include all vector layers (point, line, polygon) and tables
                self.layer_combo.addItem(layer.name(), layer)

    def on_layer_changed(self):
        """Handle layer selection change."""
        current_layer = self.layer_combo.currentData()
        self.selected_layer = current_layer

        # Clear and populate field combos
        self.input_field_combo.clear()
        self.output_field_combo.clear()

        if current_layer is None:
            return

        # Populate input field combo with numeric fields
        self.input_field_combo.addItem(self.tr("-- Select input field --"), None)
        for field in current_layer.fields():
            if field.type() in [QVariant.Int, QVariant.Double]:
                self.input_field_combo.addItem(field.name(), field)

        # Populate output field combo with existing numeric fields
        self.output_field_combo.addItem(self.tr("-- Select output field --"), None)
        for field in current_layer.fields():
            if field.type() in [QVariant.Int, QVariant.Double]:
                self.output_field_combo.addItem(field.name(), field)

    def on_calculation_type_changed(self):
        """Handle calculation type change."""
        if self.radio_dip_from_strike.isChecked():
            self.calculation_type = "dip_from_strike"
        else:
            self.calculation_type = "strike_from_dip"

    def on_create_field_toggled(self, checked):
        """Handle create new field checkbox toggle."""
        self.create_new_field = checked
        self.new_field_name_edit.setEnabled(checked)
        self.output_field_combo.setEnabled(not checked)

        if checked:
            # Set a default field name based on calculation type
            if self.calculation_type == "dip_from_strike":
                self.new_field_name_edit.setText("dip_azimuth")
            else:
                self.new_field_name_edit.setText("strike_azimuth")

    def on_decimal_places_changed(self, value):
        """Handle decimal places change."""
        self.decimal_places = value

    def check_input_value_range(self):
        """Check if input field contains values outside 0-360° range.

        :return: Tuple of (has_invalid_values, invalid_count, total_count)
        :rtype: tuple[bool, int, int]
        """
        if not self.selected_layer or not self.input_field:
            return False, 0, 0

        input_field_name = self.input_field.name()
        input_field_idx = self.selected_layer.fields().indexFromName(input_field_name)

        if input_field_idx == -1:
            return False, 0, 0

        invalid_count = 0
        total_count = 0

        # Check all features for values outside 0-360 range
        for feature in self.selected_layer.getFeatures():
            input_value = feature.attribute(input_field_idx)

            # Skip null/empty values
            if input_value is None or input_value == "":
                continue

            try:
                value = float(input_value)
                total_count += 1
                if value < 0 or value >= 360:
                    invalid_count += 1
            except (ValueError, TypeError):
                # Invalid numeric values will be handled during calculation
                total_count += 1

        return invalid_count > 0, invalid_count, total_count

    def validate_inputs(self):
        """Validate user inputs before accepting the dialog."""
        if self.selected_layer is None:
            QMessageBox.warning(self, self.tr("Validation Error"), self.tr("Please select a layer."))
            return False

        if self.input_field_combo.currentData() is None:
            QMessageBox.warning(self, self.tr("Validation Error"), self.tr("Please select an input field."))
            return False

        if self.create_new_field:
            field_name = self.new_field_name_edit.text().strip()
            if not field_name:
                QMessageBox.warning(
                    self, self.tr("Validation Error"), self.tr("Please enter a name for the new field.")
                )
                return False

            # Check if field name already exists
            existing_names = [field.name().lower() for field in self.selected_layer.fields()]
            if field_name.lower() in existing_names:
                QMessageBox.warning(
                    self,
                    self.tr("Validation Error"),
                    self.tr("A field with the name '{}' already exists.").format(field_name),
                )
                return False

            self.new_field_name = field_name
        else:
            if self.output_field_combo.currentData() is None:
                QMessageBox.warning(
                    self, self.tr("Validation Error"), self.tr("Please select an output field or create a new one.")
                )
                return False

            self.output_field = self.output_field_combo.currentData()

        self.input_field = self.input_field_combo.currentData()

        # Check input value range if the input field is numeric
        if self.input_field_combo.currentData().type() in [QVariant.Int, QVariant.Double]:
            has_invalid_values, invalid_count, total_count = self.check_input_value_range()
            if has_invalid_values:
                reply = QMessageBox.warning(
                    self,
                    self.tr("Invalid Input Values"),
                    self.tr(
                        "The input field contains values outside the 0-360° range.\n"
                        "Invalid values: {invalid_count} out of {total_count} total values.\n\n"
                        "Do you want to continue with the calculation?",
                    ).format(invalid_count=invalid_count, total_count=total_count),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return False

        return True

    def accept(self):
        """Accept the dialog if inputs are valid."""
        if self.validate_inputs():
            super().accept()

    def get_calculation_config(self):
        """Get the calculation configuration.

        :return: Dictionary containing calculation configuration
        :rtype: dict
        """
        return {
            "layer": self.selected_layer,
            "calculation_type": self.calculation_type,
            "input_field": self.input_field,
            "output_field": self.output_field,
            "create_new_field": self.create_new_field,
            "new_field_name": self.new_field_name,
            "decimal_places": self.decimal_places,
        }

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)
