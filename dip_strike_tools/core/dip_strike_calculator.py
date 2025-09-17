#! python3  # noqa: E265

"""
Calculator for dip and strike values.
"""

from qgis.core import (
    QgsField,
    QgsVectorLayer,
    edit,
)

from ..toolbelt import PlgLogger, QVariant
from . import dip_strike_math


class DipStrikeCalculator:
    """Calculator for converting between dip and strike azimuths."""

    def __init__(self):
        """Initialize the calculator."""
        self.log = PlgLogger().log

    def calculate_dip_from_strike(self, strike_azimuth, decimal_places=2):
        """Calculate dip azimuth from strike azimuth.

        :param strike_azimuth: Strike azimuth in degrees
        :type strike_azimuth: float
        :param decimal_places: Number of decimal places to round to
        :type decimal_places: int
        :return: Dip azimuth in degrees
        :rtype: float
        """
        return dip_strike_math.calculate_dip_from_strike(strike_azimuth, decimal_places)

    def calculate_strike_from_dip(self, dip_azimuth, decimal_places=2):
        """Calculate strike azimuth from dip azimuth.

        :param dip_azimuth: Dip azimuth in degrees
        :type dip_azimuth: float
        :param decimal_places: Number of decimal places to round to
        :type decimal_places: int
        :return: Strike azimuth in degrees
        :rtype: float
        """
        return dip_strike_math.calculate_strike_from_dip(dip_azimuth, decimal_places)

    def process_layer(self, config):
        """Process a layer to calculate dip or strike values.

        :param config: Configuration dictionary containing:
            - layer: QgsVectorLayer to process
            - calculation_type: 'dip_from_strike' or 'strike_from_dip'
            - input_field: QgsField with input values
            - output_field: QgsField for output (if using existing field)
            - create_new_field: bool indicating if new field should be created
            - new_field_name: str name for new field (if creating)
            - decimal_places: int number of decimal places to round to (default: 2)
        :type config: dict
        :return: Success status and message
        :rtype: tuple[bool, str]
        """
        try:
            layer = config["layer"]
            calculation_type = config["calculation_type"]
            input_field = config["input_field"]
            create_new_field = config["create_new_field"]
            decimal_places = config.get("decimal_places", 2)  # Default to 2 if not provided

            if not isinstance(layer, QgsVectorLayer) or not layer.isValid():
                return False, "Invalid layer"

            # Determine output field
            if create_new_field:
                output_field_name = config["new_field_name"]
                # Create new field
                new_field = QgsField(output_field_name, QVariant.Double, "double", 10, 2)

                with edit(layer):
                    if not layer.addAttribute(new_field):
                        error_msg = f"Failed to add new field '{output_field_name}'"
                        self.log(message=error_msg, log_level=1, push=True)
                        return False, error_msg

                # Get the field index after adding
                output_field_idx = layer.fields().indexFromName(output_field_name)
                if output_field_idx == -1:
                    error_msg = f"Failed to find newly created field '{output_field_name}'"
                    self.log(message=error_msg, log_level=1, push=True)
                    return False, error_msg

                self.log(message=f"Created new field '{output_field_name}' for calculated values", log_level=3)
            else:
                output_field = config["output_field"]
                output_field_name = output_field.name()
                output_field_idx = layer.fields().indexFromName(output_field_name)
                if output_field_idx == -1:
                    return False, f"Output field '{output_field_name}' not found"

            # Get input field index
            input_field_name = input_field.name()
            input_field_idx = layer.fields().indexFromName(input_field_name)
            if input_field_idx == -1:
                return False, f"Input field '{input_field_name}' not found"

            # Process features
            processed_count = 0
            error_count = 0

            with edit(layer):
                features = layer.getFeatures()
                for feature in features:  # type: ignore
                    input_value = feature.attribute(input_field_idx)

                    if input_value is None or input_value == "":
                        continue  # Skip null/empty values

                    # Calculate output value
                    if calculation_type == "dip_from_strike":
                        output_value = self.calculate_dip_from_strike(input_value, decimal_places)
                    else:  # strike_from_dip
                        output_value = self.calculate_strike_from_dip(input_value, decimal_places)

                    if output_value is not None:
                        # Update the feature
                        if layer.changeAttributeValue(feature.id(), output_field_idx, output_value):
                            processed_count += 1
                        else:
                            error_count += 1
                            self.log(message=f"Failed to update feature {feature.id()}", log_level=2)
                    else:
                        error_count += 1
                        self.log(message=f"Invalid input value for feature {feature.id()}: {input_value}", log_level=2)

            # Log results
            self.log(
                message=f"Calculation completed. Processed: {processed_count}, Errors: {error_count}", log_level=3
            )

            if processed_count == 0:
                return False, "No features were processed. Check that input field contains valid numeric values."

            success_msg = f"Successfully calculated {processed_count} values"
            if error_count > 0:
                success_msg += f" ({error_count} errors)"

            return True, success_msg

        except Exception as e:
            error_msg = f"Error during calculation: {str(e)}"
            self.log(message=error_msg, log_level=1, push=True)
            return False, error_msg
