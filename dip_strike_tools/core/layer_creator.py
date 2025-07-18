#! python3  # noqa: E265

"""
Layer creation utilities for dip/strike features.
"""

import os
import sqlite3
import tempfile

from qgis.core import (
    QgsField,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QMetaType

from ..toolbelt import PlgLogger


class LayerCreationError(Exception):
    """Custom exception for layer creation errors."""

    pass


class DipStrikeLayerCreator:
    """Utility class for creating dip/strike feature layers."""

    def __init__(self):
        """Initialize the layer creator."""
        self.log = PlgLogger().log

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: String to translate
        :type message: str

        :returns: Translated string
        :rtype: str
        """
        # Note: This is a utility class, errors are typically handled by calling code
        return message  # For now, return the message as-is since this is a utility class

    def get_dip_strike_fields(self):
        """Get the standard field definitions for dip/strike layers.

        :returns: Tuple of (required_fields, optional_fields)
        :rtype: tuple
        """
        # Create required fields using modern constructor
        strike_azimuth_field = QgsField()
        strike_azimuth_field.setName("strike_azimuth")
        strike_azimuth_field.setType(QMetaType.Type.Double)
        strike_azimuth_field.setLength(10)
        strike_azimuth_field.setPrecision(2)

        dip_azimuth_field = QgsField()
        dip_azimuth_field.setName("dip_azimuth")
        dip_azimuth_field.setType(QMetaType.Type.Double)
        dip_azimuth_field.setLength(10)
        dip_azimuth_field.setPrecision(2)

        dip_value_field = QgsField()
        dip_value_field.setName("dip_value")
        dip_value_field.setType(QMetaType.Type.Double)
        dip_value_field.setLength(10)
        dip_value_field.setPrecision(2)

        required_fields = [strike_azimuth_field, dip_azimuth_field, dip_value_field]

        # Create optional fields using modern constructor
        geo_type_field = QgsField()
        geo_type_field.setName("geo_type")
        geo_type_field.setType(QMetaType.Type.QString)
        geo_type_field.setLength(50)

        age_field = QgsField()
        age_field.setName("age")
        age_field.setType(QMetaType.Type.QString)
        age_field.setLength(50)

        lithology_field = QgsField()
        lithology_field.setName("lithology")
        lithology_field.setType(QMetaType.Type.QString)
        lithology_field.setLength(100)

        notes_field = QgsField()
        notes_field.setName("notes")
        notes_field.setType(QMetaType.Type.QString)
        notes_field.setLength(255)

        z_value_field = QgsField()
        z_value_field.setName("z_value")
        z_value_field.setType(QMetaType.Type.Int)
        z_value_field.setLength(10)

        optional_fields = [geo_type_field, age_field, lithology_field, notes_field, z_value_field]

        return required_fields, optional_fields

    def get_shapefile_field_mapping(self):
        """Get field name mapping for shapefile format (max 10 characters).

        :returns: Dictionary mapping original field names to shortened versions
        :rtype: dict
        """
        return {
            "strike_azimuth": "strike_azi",
            "dip_azimuth": "dip_azi",
            "dip_value": "dip_val",
            "geo_type": "geo_type",
            "age": "age",
            "lithology": "lithology",
            "notes": "notes",
        }

    def get_mapped_field_name(self, layer, original_field_name):
        """Get the actual field name in the layer for a given original field name.

        This method handles the mapping between original field names and the actual
        field names in the layer, which may be different (e.g., shortened for shapefiles).

        :param layer: The layer to check
        :type layer: QgsVectorLayer
        :param original_field_name: The original field name (e.g., 'strike_azimuth')
        :type original_field_name: str
        :returns: The actual field name in the layer, or None if not found
        :rtype: str or None
        """
        # First check if the original field name exists directly
        if layer.fields().lookupField(original_field_name) != -1:
            return original_field_name

        # Check if a mapped field name exists in custom properties
        mapped_name = layer.customProperty(f"dip_strike_tools/{original_field_name}")
        if mapped_name and layer.fields().lookupField(mapped_name) != -1:
            return mapped_name

        # For shapefiles, try the shortened name
        shapefile_mapping = self.get_shapefile_field_mapping()
        if original_field_name in shapefile_mapping:
            shortened_name = shapefile_mapping[original_field_name]
            if layer.fields().lookupField(shortened_name) != -1:
                return shortened_name

        return None

    def apply_symbology(self, layer):
        """Apply default single symbol symbology to a dip/strike layer.

        :param layer: The layer to apply symbology to
        :type layer: QgsVectorLayer
        :returns: True if symbology was applied successfully, False otherwise
        :rtype: bool
        """
        try:
            return self._apply_single_symbol_symbology(layer)
        except Exception as e:
            self.log(f"Error applying symbology: {e}", log_level=1)
            return False

    def _apply_single_symbol_symbology(self, layer):
        """Apply single symbol symbology with rotation based on strike and dip value labels.

        :param layer: The layer to apply symbology to
        :type layer: QgsVectorLayer
        :returns: True if successful, False otherwise
        :rtype: bool
        """
        try:
            # Get the path to the single symbol QML file
            qml_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "resources", "qml", "single_symbol.qml"
            )

            if not os.path.exists(qml_path):
                self.log(f"Single symbol QML file not found: {qml_path}", log_level=1)
                return False

            # Get mapped field names
            strike_field = self.get_mapped_field_name(layer, "strike_azimuth")
            dip_value_field = self.get_mapped_field_name(layer, "dip_value")

            if not strike_field:
                self.log("Strike azimuth field not found in layer", log_level=1)
                return False

            if not dip_value_field:
                self.log("Dip value field not found in layer", log_level=1)
                return False

            self.log(f"Field mapping: strike_azimuth -> {strike_field}, dip_value -> {dip_value_field}", log_level=4)

            # Always update field references to ensure correct mapping
            # The QML file expects 'strike_azimuth' for rotation and 'dip' for labeling
            self.log(
                f"Applying symbology with field mapping - rotation: {strike_field}, labels: {dip_value_field}",
                log_level=3,
            )

            qml_content = self._update_qml_field_references(
                qml_path,
                {
                    "strike_azimuth": strike_field,
                    "dip": dip_value_field,  # Map the label field 'dip' to our 'dip_value' field
                },
            )
            success = self._apply_qml_content(layer, qml_content)

            if success:
                self.log(f"Applied single symbol symbology to layer: {layer.name()}", log_level=3)

                # Verify the symbology was applied correctly
                verification = self.verify_symbology_fields(layer)
                if not verification["strike_field_found"] or not verification["dip_field_found"]:
                    self.log("Warning: Required fields for symbology not found after application", log_level=2)
                else:
                    self.log(
                        f"Symbology fields verified: strike={verification['strike_field_name']}, dip={verification['dip_field_name']}",
                        log_level=4,
                    )

                # Check if labeling is enabled
                if hasattr(layer, "labelsEnabled") and layer.labelsEnabled():
                    self.log(f"Labels are enabled for layer {layer.name()}", log_level=4)
                else:
                    self.log(f"Labels are NOT enabled for layer {layer.name()}", log_level=2)
            else:
                self.log(f"Failed to apply single symbol symbology to layer: {layer.name()}", log_level=1)

            return success

        except Exception as e:
            self.log(f"Error applying single symbol symbology: {e}", log_level=1)
            return False

    def _update_qml_field_references(self, qml_path, field_mapping):
        """Read QML file and update field references based on mapping.

        :param qml_path: Path to the QML file
        :type qml_path: str
        :param field_mapping: Dictionary mapping original field names to actual field names
        :type field_mapping: dict
        :returns: Updated QML content as string
        :rtype: str
        """
        try:
            with open(qml_path, "r", encoding="utf-8") as f:
                qml_content = f.read()

            # Replace field references in the QML content
            for original_field, actual_field in field_mapping.items():
                if actual_field != original_field:
                    # Count replacements for debugging
                    before_count = qml_content.count(original_field)

                    # Log what we're looking for
                    self.log(
                        f"Looking for field references to '{original_field}' to replace with '{actual_field}'",
                        log_level=4,
                    )
                    self.log(f'Searching for pattern: fieldName="{original_field}"', log_level=4)

                    # Replace field references in various QML contexts
                    # Handle different field reference patterns in QML
                    qml_content = qml_content.replace(
                        f'field" value="{original_field}"', f'field" value="{actual_field}"'
                    )
                    qml_content = qml_content.replace(f'attr="{original_field}"', f'attr="{actual_field}"')
                    qml_content = qml_content.replace(f'fieldName="{original_field}"', f'fieldName="{actual_field}"')
                    qml_content = qml_content.replace(f"&quot;{original_field}&quot;", f"&quot;{actual_field}&quot;")
                    # Also handle expression-based field references
                    qml_content = qml_content.replace(f'"{original_field}"', f'"{actual_field}"')

                    after_count = qml_content.count(original_field)
                    replaced_count = before_count - after_count
                    self.log(
                        f"Updated QML field reference: {original_field} -> {actual_field} ({replaced_count} replacements)",
                        log_level=4,
                    )
                else:
                    self.log(f"No replacement needed for field: {original_field} (already matches)", log_level=4)

            return qml_content

        except Exception as e:
            self.log(f"Error updating QML field references: {e}", log_level=1)
            raise

    def _apply_qml_content(self, layer, qml_content):
        """Apply QML content to a layer.

        :param layer: The layer to apply symbology to
        :type layer: QgsVectorLayer
        :param qml_content: QML content as string
        :type qml_content: str
        :returns: True if successful, False otherwise
        :rtype: bool
        """
        try:
            # Write QML content to a temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".qml", delete=False, encoding="utf-8") as temp_file:
                temp_file.write(qml_content)
                temp_qml_path = temp_file.name  # Load the style from the temporary file
            self.log(f"Loading QML style from temporary file: {temp_qml_path}", log_level=4)
            result, error_msg = layer.loadNamedStyle(temp_qml_path)

            self.log(f"QML loading result: {result}, error_msg: '{error_msg}'", log_level=4)

            # Clean up temporary file
            try:
                os.unlink(temp_qml_path)
            except Exception:
                pass  # Ignore cleanup errors

            # Check if the result explicitly indicates failure
            # Sometimes loadNamedStyle returns strange values, so we check for explicit failure indicators
            if result is False or (isinstance(error_msg, str) and error_msg.lower() in ["false", "failed", "error"]):
                self.log(f"QML style loading failed: {error_msg}", log_level=2)
                return False
            else:
                # Assume success if no explicit failure indication
                self.log(f"QML style loaded successfully for layer: {layer.name()}", log_level=4)

            # Trigger layer repaint
            layer.triggerRepaint()

            # Ensure labeling is explicitly enabled
            self.ensure_labeling_enabled(layer)

            return True

        except Exception as e:
            self.log(f"Error applying QML content: {e}", log_level=1)
            return False

    def create_memory_layer(self, layer_name, crs, optional_fields_config=None):
        """Create a memory layer for dip/strike features.

        :param layer_name: Name for the layer
        :type layer_name: str
        :param crs: Coordinate reference system
        :type crs: QgsCoordinateReferenceSystem
        :param optional_fields_config: Configuration for optional fields to include
        :type optional_fields_config: dict or None
        :returns: Created memory layer
        :rtype: QgsVectorLayer
        :raises: LayerCreationError if layer creation fails
        """
        self.log(f"Creating memory layer: {layer_name}", log_level=4)

        # Create memory layer
        layer = QgsVectorLayer(f"Point?crs={crs.authid()}&index=yes", layer_name, "memory")

        if not layer.isValid():
            raise LayerCreationError(f"Failed to create memory layer: {layer_name}")

        # Add fields to memory layer based on configuration
        selected_fields = self.get_selected_fields(optional_fields_config)

        layer.startEditing()
        layer.dataProvider().addAttributes(selected_fields)
        layer.updateFields()
        layer.commitChanges()

        self.log(f"Successfully created memory layer: {layer_name}", log_level=4)
        return layer

    def create_file_layer(self, layer_name, output_path, format_info, crs, optional_fields_config=None):
        """Create a file-based layer for dip/strike features.

        :param layer_name: Name for the layer
        :type layer_name: str
        :param output_path: Path to output file
        :type output_path: str
        :param format_info: Format information dictionary
        :type format_info: dict
        :param crs: Coordinate reference system
        :type crs: QgsCoordinateReferenceSystem
        :param optional_fields_config: Configuration for optional fields to include
        :type optional_fields_config: dict or None
        :returns: Created file layer
        :rtype: QgsVectorLayer
        :raises: LayerCreationError if layer creation fails
        """
        # Validate input parameters
        if not output_path:
            raise LayerCreationError(
                f"output_path is required for file layer creation (driver: {format_info.get('driver', 'unknown')})"
            )

        self.log(f"Creating {format_info['driver']} layer: {layer_name} at {output_path}", log_level=4)

        # Get field definitions based on configuration
        selected_fields = self.get_selected_fields(optional_fields_config)

        # Create temporary memory layer to define the structure
        temp_layer = QgsVectorLayer(f"Point?crs={crs.authid()}", "temp", "memory")
        temp_layer.startEditing()

        # For shapefiles, create fields with already shortened names to avoid mapping issues
        if format_info["driver"] == "ESRI Shapefile":
            shapefile_mapping = self.get_shapefile_field_mapping()
            shapefile_fields = []

            for field in selected_fields:
                original_name = field.name()
                if original_name in shapefile_mapping:
                    # Create a new field with the shortened name
                    shapefile_field = QgsField()
                    shapefile_field.setName(shapefile_mapping[original_name])
                    shapefile_field.setType(field.type())
                    shapefile_field.setLength(field.length())
                    shapefile_field.setPrecision(field.precision())
                    shapefile_fields.append(shapefile_field)
                else:
                    # Use original field but truncate name if needed
                    truncated_field = QgsField()
                    truncated_field.setName(original_name[:10])
                    truncated_field.setType(field.type())
                    truncated_field.setLength(field.length())
                    truncated_field.setPrecision(field.precision())
                    shapefile_fields.append(truncated_field)

            temp_layer.dataProvider().addAttributes(shapefile_fields)
        else:
            # For other formats, use original field names
            temp_layer.dataProvider().addAttributes(selected_fields)

        temp_layer.updateFields()
        temp_layer.commitChanges()

        # Set up writer options
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = format_info["driver"]
        save_options.fileEncoding = "UTF-8"

        # For GeoPackage, set the layer name to avoid conflicts
        if format_info["driver"] == "GPKG":
            save_options.layerName = layer_name
            self.log(f"Setting GeoPackage layer name to: {layer_name}", log_level=4)

            # Check if the GeoPackage file already exists
            if os.path.exists(output_path):
                # Check if a layer with the same name already exists
                if self.check_geopackage_layer_exists(output_path, layer_name):
                    self.log(
                        f"Warning: Layer '{layer_name}' already exists in GeoPackage, it will be overwritten",
                        log_level=2,
                    )

                # For existing GeoPackages, we need to append the new layer
                save_options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteLayer
                self.log(f"GeoPackage exists, will add layer '{layer_name}' to existing file", log_level=4)
            else:
                # For new GeoPackages, create the file
                save_options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
                self.log(f"Creating new GeoPackage file with layer '{layer_name}'", log_level=4)

        # Write the layer
        self.log(f"Writing {format_info['driver']} file to: {output_path}", log_level=4)

        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            temp_layer, output_path, temp_layer.transformContext(), save_options
        )

        if error[0] != 0:  # 0 indicates no error
            error_msg = error[1] if len(error) > 1 and error[1] else "Unknown error"
            self.log(f"Failed to create {format_info['driver']} file: {error_msg}", log_level=1)
            raise LayerCreationError(f"Failed to create {format_info['driver']} file: {error_msg}")

        self.log(f"Successfully created {format_info['driver']} file: {output_path}", log_level=4)

        # Load the created file as a layer
        # For GeoPackage, specify the layer name to ensure we load the correct layer
        if format_info["driver"] == "GPKG":
            # Use the format: "path|layername=layername" for GeoPackages
            layer_source = f"{output_path}|layername={layer_name}"
            self.log(f"Loading GeoPackage layer with source: {layer_source}", log_level=4)
        else:
            layer_source = output_path

        layer = QgsVectorLayer(layer_source, layer_name, "ogr")

        if not layer.isValid():
            self.log(f"Failed to load created {format_info['driver']} file as layer: {output_path}", log_level=1)
            raise LayerCreationError(f"Failed to load created {format_info['driver']} file as layer")

        # For shapefiles, log the actual field names that were created to debug field mapping issues
        if format_info["driver"] == "ESRI Shapefile":
            actual_field_names = [field.name() for field in layer.fields()]
            self.log(f"Shapefile created with actual field names: {actual_field_names}", log_level=4)

        # Verify the layer source is correct for GeoPackages
        if format_info["driver"] == "GPKG":
            self.log(f"Loaded GeoPackage layer '{layer_name}' with final source: {layer.source()}", log_level=4)

        return layer

    def configure_layer_properties(self, layer, format_info):
        """Configure layer properties for dip/strike tools.

        :param layer: The layer to configure
        :type layer: QgsVectorLayer
        :param format_info: Format information dictionary
        :type format_info: dict
        """
        # Configure layer properties for dip/strike tools
        layer.setCustomProperty("dip_strike_tools/layer_role", "dip_strike_feature_layer")

        # Map fields to themselves (direct mapping since we created them with correct names)
        # For shapefiles, we need to handle the shortened field names
        if format_info["driver"] == "ESRI Shapefile":
            # Create mapping for shortened field names in shapefiles
            field_mapping = self.get_shapefile_field_mapping()

            for original_name, actual_field_name in field_mapping.items():
                # Check if the field actually exists in the layer
                if layer.fields().lookupField(actual_field_name) != -1:
                    layer.setCustomProperty(f"dip_strike_tools/{original_name}", actual_field_name)
                    self.log(f"Mapped {original_name} -> {actual_field_name} for shapefile", log_level=4)
        else:
            # For other formats, use direct mapping
            required_fields, optional_fields = self.get_dip_strike_fields()
            all_fields = required_fields + optional_fields

            for field in all_fields:
                field_name = field.name()
                if layer.fields().lookupField(field_name) != -1:
                    layer.setCustomProperty(f"dip_strike_tools/{field_name}", field_name)

    def configure_layer_properties_for_existing(self, layer):
        """Configure layer properties for dip/strike tools on an existing layer.

        This method is used when the layer was created externally (e.g., via QgsNewVectorLayerDialog)
        and we need to configure it for dip/strike tools.

        :param layer: The existing layer to configure
        :type layer: QgsVectorLayer
        """
        # Configure layer properties for dip/strike tools
        layer.setCustomProperty("dip_strike_tools/layer_role", "dip_strike_feature_layer")

        # Detect if this is a shapefile by checking the data provider or source
        is_shapefile = layer.dataProvider().name() == "ogr" and layer.source().lower().endswith(".shp")

        if is_shapefile:
            # Handle shapefile field mapping (shortened field names)
            field_mapping = self.get_shapefile_field_mapping()

            for original_name, shortened_name in field_mapping.items():
                # Check if the shortened field name exists in the layer
                if layer.fields().lookupField(shortened_name) != -1:
                    layer.setCustomProperty(f"dip_strike_tools/{original_name}", shortened_name)
                    self.log(f"Mapped shapefile field: {original_name} -> {shortened_name}", log_level=4)
                else:
                    # Also check for the original name (in case it wasn't shortened)
                    if layer.fields().lookupField(original_name) != -1:
                        layer.setCustomProperty(f"dip_strike_tools/{original_name}", original_name)
                        self.log(f"Mapped shapefile field (original): {original_name}", log_level=4)
        else:
            # For other formats, use direct mapping
            required_fields, optional_fields = self.get_dip_strike_fields()
            all_fields = required_fields + optional_fields

            for field in all_fields:
                field_name = field.name()
                if layer.fields().lookupField(field_name) != -1:
                    layer.setCustomProperty(f"dip_strike_tools/{field_name}", field_name)
                    self.log(f"Mapped field: {field_name}", log_level=4)

        self.log(f"Configured existing layer for dip/strike tools: {layer.name()}", log_level=4)

    def create_dip_strike_layer(self, config, crs):
        """Create a new dip/strike layer based on configuration.

        :param config: Layer configuration dictionary
        :type config: dict
        :param crs: Coordinate reference system
        :type crs: QgsCoordinateReferenceSystem
        :returns: Created and configured layer
        :rtype: QgsVectorLayer
        :raises: LayerCreationError if layer creation fails
        """
        layer_name = config["name"]
        layer_format = config["format"]
        output_path = config["output_path"]
        format_info = config["format_info"]

        # Extract optional fields configuration
        optional_fields_config = config.get("optional_fields", None)

        # Extract symbology configuration
        symbology_config = config.get("symbology", {})
        apply_symbology = symbology_config.get("apply", False)

        self.log(
            f"Creating layer: {layer_name}, apply_symbology: {apply_symbology}, optional_fields: {optional_fields_config}",
            log_level=4,
        )

        # Debug: Log the layer format
        self.log(f"Layer format: '{layer_format}' (type: {type(layer_format)})", log_level=4)

        try:
            if layer_format == "memory":
                self.log("Taking memory layer creation path", log_level=4)
                layer = self.create_memory_layer(layer_name, crs, optional_fields_config)
            else:
                self.log("Taking file layer creation path", log_level=4)
                layer = self.create_file_layer(layer_name, output_path, format_info, crs, optional_fields_config)

            # Configure layer properties
            self.configure_layer_properties(layer, format_info)

            # Apply symbology if requested
            if apply_symbology:
                self._apply_symbology_to_layer(layer)

            # Add layer to project
            QgsProject.instance().addMapLayer(layer)

            format_info_str = (
                f" ({format_info.get('display_name', layer_format)})" if layer_format != "memory" else " (Memory)"
            )
            location_info = f" at {output_path}" if output_path else ""
            symbology_info = " with single symbol symbology" if apply_symbology else ""

            self.log(
                f"Successfully created and configured layer: {layer_name}{format_info_str}{location_info}{symbology_info}",
                log_level=3,
            )

            return layer

        except Exception as e:
            self.log(f"Error creating dip/strike layer: {e}", log_level=1)
            raise LayerCreationError(f"Failed to create layer: {str(e)}")

    def _apply_symbology_to_layer(self, layer):
        """Apply symbology to a layer.

        :param layer: The layer to apply symbology to
        :type layer: QgsVectorLayer
        """
        try:
            self.log(f"Applying single symbol symbology to layer: {layer.name()}", log_level=3)

            success = self._apply_single_symbol_symbology(layer)

            if not success:
                self.log(
                    f"Symbology application reported failure for layer {layer.name()}, but style may still be applied",
                    log_level=2,
                )
            else:
                self.log(f"Successfully applied symbology to layer {layer.name()}", log_level=3)
        except Exception as e:
            self.log(f"Error applying symbology to layer: {e}", log_level=1)

    def apply_symbology_to_existing_layer(self, layer):
        """Apply symbology to an existing dip/strike layer.

        This method can be used to apply symbology to layers that were not created
        through the create_dip_strike_layer method, or to change the symbology of
        existing layers. Only single symbol symbology is supported.

        :param layer: The layer to apply symbology to
        :type layer: QgsVectorLayer
        :returns: True if symbology was applied successfully, False otherwise
        :rtype: bool
        """
        try:
            # Ensure the layer is configured for dip/strike tools
            self.configure_layer_properties_for_existing(layer)

            # Apply single symbol symbology
            return self._apply_single_symbol_symbology(layer)

        except Exception as e:
            self.log(f"Error applying symbology to existing layer: {e}", log_level=1)
            return False

    def check_geopackage_layer_exists(self, gpkg_path, layer_name):
        """Check if a layer with the given name already exists in a GeoPackage.

        :param gpkg_path: Path to the GeoPackage file
        :type gpkg_path: str
        :param layer_name: Name of the layer to check
        :type layer_name: str
        :returns: True if layer exists, False otherwise
        :rtype: bool
        """
        if not os.path.exists(gpkg_path):
            return False

        try:
            conn = sqlite3.connect(gpkg_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM gpkg_contents WHERE table_name = ? AND data_type = 'features'", (layer_name,)
            )
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception as e:
            self.log(f"Error checking GeoPackage layers: {e}", log_level=2)
            return False

    def create_layer_config(
        self,
        layer_name,
        layer_format="memory",
        output_path=None,
        apply_symbology=False,
        optional_fields_config=None,
    ):
        """Create a properly formatted configuration dictionary for layer creation.

        :param layer_name: Name for the layer
        :type layer_name: str
        :param layer_format: Format for the layer ('memory', 'gpkg', 'shapefile')
        :type layer_format: str
        :param output_path: Path for file-based layers (required for non-memory layers)
        :type output_path: str or None
        :param apply_symbology: Whether to apply default symbology to the layer
        :type apply_symbology: bool
        :param optional_fields_config: Configuration for optional fields to include
        :type optional_fields_config: dict or None
        :returns: Configuration dictionary ready for create_dip_strike_layer
        :rtype: dict
        """
        # Format information mapping using internal keys
        format_mapping = {
            "memory": {"driver": "memory", "extension": "", "display_name": "Memory Layer"},
            "shapefile": {"driver": "ESRI Shapefile", "extension": "shp", "display_name": "ESRI Shapefile"},
            "gpkg": {"driver": "GPKG", "extension": "gpkg", "display_name": "GeoPackage"},
        }

        if layer_format not in format_mapping:
            raise ValueError(
                f"Unsupported layer format: {layer_format}. Supported formats: {list(format_mapping.keys())}"
            )

        if layer_format != "memory" and not output_path:
            raise ValueError(f"output_path is required for {layer_format} layers")

        config = {
            "name": layer_name,
            "format": layer_format,
            "output_path": output_path,
            "format_info": format_mapping[layer_format],
            "symbology": {"apply": apply_symbology},
            "optional_fields": optional_fields_config,
        }

        return config

    def create_memory_layer_with_symbology(self, layer_name, crs):
        """Convenience method to create a memory layer with symbology applied.

        :param layer_name: Name for the layer
        :type layer_name: str
        :param crs: Coordinate reference system
        :type crs: QgsCoordinateReferenceSystem
        :returns: Created layer with symbology applied
        :rtype: QgsVectorLayer
        """
        config = self.create_layer_config(
            layer_name=layer_name,
            layer_format="memory",
            apply_symbology=True,
        )

        return self.create_dip_strike_layer(config, crs)

    def create_memory_layer_without_symbology(self, layer_name, crs):
        """Convenience method to create a memory layer without symbology.

        :param layer_name: Name for the layer
        :type layer_name: str
        :param crs: Coordinate reference system
        :type crs: QgsCoordinateReferenceSystem
        :returns: Created layer without symbology
        :rtype: QgsVectorLayer
        """
        config = self.create_layer_config(layer_name=layer_name, layer_format="memory", apply_symbology=False)

        return self.create_dip_strike_layer(config, crs)

    def create_file_layer_with_symbology(self, layer_name, output_path, layer_format, crs):
        """Convenience method to create a file-based layer with symbology applied.

        :param layer_name: Name for the layer
        :type layer_name: str
        :param output_path: Path to output file
        :type output_path: str
        :param layer_format: Format for the layer ('GeoPackage', 'ESRI Shapefile', etc.)
        :type layer_format: str
        :param crs: Coordinate reference system
        :type crs: QgsCoordinateReferenceSystem
        :returns: Created layer with symbology applied
        :rtype: QgsVectorLayer
        """
        config = self.create_layer_config(
            layer_name=layer_name,
            layer_format=layer_format,
            output_path=output_path,
            apply_symbology=True,
        )

        return self.create_dip_strike_layer(config, crs)

    def create_file_layer_without_symbology(self, layer_name, output_path, layer_format, crs):
        """Convenience method to create a file-based layer without symbology.

        :param layer_name: Name for the layer
        :type layer_name: str
        :param output_path: Path to output file
        :type output_path: str
        :param layer_format: Format for the layer ('GeoPackage', 'ESRI Shapefile', etc.)
        :type layer_format: str
        :param crs: Coordinate reference system
        :type crs: QgsCoordinateReferenceSystem
        :returns: Created layer without symbology
        :rtype: QgsVectorLayer
        """
        config = self.create_layer_config(
            layer_name=layer_name, layer_format=layer_format, output_path=output_path, apply_symbology=False
        )

        return self.create_dip_strike_layer(config, crs)

    def verify_symbology_fields(self, layer):
        """Verify that the layer has the correct fields for symbology and they are properly mapped.

        :param layer: The layer to verify
        :type layer: QgsVectorLayer
        :returns: Dictionary with verification results
        :rtype: dict
        """
        verification = {
            "strike_field_found": False,
            "dip_field_found": False,
            "strike_field_name": None,
            "dip_field_name": None,
            "has_features": False,
            "sample_values": {},
        }

        # Check field mapping
        strike_field = self.get_mapped_field_name(layer, "strike_azimuth")
        dip_field = self.get_mapped_field_name(layer, "dip_value")

        verification["strike_field_found"] = strike_field is not None
        verification["dip_field_found"] = dip_field is not None
        verification["strike_field_name"] = strike_field
        verification["dip_field_name"] = dip_field

        # Check if layer has features and get sample values
        if layer.featureCount() > 0:
            verification["has_features"] = True
            # Get first feature as sample
            feature = next(layer.getFeatures())
            if strike_field:
                verification["sample_values"]["strike"] = feature[strike_field]
            if dip_field:
                verification["sample_values"]["dip"] = feature[dip_field]

        self.log(f"Symbology verification for {layer.name()}: {verification}", log_level=4)
        return verification

    def ensure_labeling_enabled(self, layer):
        """Ensure that labeling is explicitly enabled for the layer.

        :param layer: The layer to enable labeling for
        :type layer: QgsVectorLayer
        """
        try:
            # Get the labeling settings
            labeling = layer.labeling()
            if labeling is not None:
                # Labeling is configured, ensure it's enabled
                self.log(f"Labeling is configured for layer {layer.name()}", log_level=4)
                # Force enable the labeling
                layer.setLabelsEnabled(True)
                self.log(f"Explicitly enabled labeling for layer {layer.name()}", log_level=4)
            else:
                self.log(f"No labeling configuration found for layer {layer.name()}", log_level=2)
        except Exception as e:
            self.log(f"Error ensuring labeling is enabled: {e}", log_level=2)

    def get_selected_fields(self, optional_fields_config=None):
        """Get the field definitions based on optional fields configuration.

        :param optional_fields_config: Dictionary indicating which optional fields to include
        :type optional_fields_config: dict or None
        :returns: List of fields to include in the layer
        :rtype: list
        """
        required_fields, optional_fields = self.get_dip_strike_fields()

        # Always include required fields
        selected_fields = required_fields.copy()

        # Add optional fields based on configuration
        if optional_fields_config is not None:
            for field in optional_fields:
                field_name = field.name()
                if optional_fields_config.get(field_name, False):
                    selected_fields.append(field)
                    self.log(f"Including optional field: {field_name}", log_level=4)
        else:
            # If no configuration provided, include all optional fields
            selected_fields.extend(optional_fields)
            self.log("No optional fields configuration provided, including all optional fields", log_level=4)

        self.log(f"Selected fields: {[f.name() for f in selected_fields]}", log_level=4)
        return selected_fields
