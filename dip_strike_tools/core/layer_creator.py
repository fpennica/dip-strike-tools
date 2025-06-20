#! python3  # noqa: E265

"""
Layer creation utilities for dip/strike features.
"""

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

        optional_fields = [geo_type_field, age_field, lithology_field, notes_field]

        return required_fields, optional_fields

    def get_shapefile_field_mapping(self):
        """Get field name mapping for shapefile format (max 10 characters).

        :returns: Dictionary mapping original field names to shortened versions
        :rtype: dict
        """
        return {
            "strike_azimuth": "strike_az",
            "dip_azimuth": "dip_az",
            "dip_value": "dip_val",
            "geo_type": "geo_type",
            "age": "age",
            "lithology": "lithology",
            "notes": "notes",
        }

    def create_memory_layer(self, layer_name, crs):
        """Create a memory layer for dip/strike features.

        :param layer_name: Name for the layer
        :type layer_name: str
        :param crs: Coordinate reference system
        :type crs: QgsCoordinateReferenceSystem
        :returns: Created memory layer
        :rtype: QgsVectorLayer
        :raises: LayerCreationError if layer creation fails
        """
        self.log(f"Creating memory layer: {layer_name}", log_level=4)

        # Create memory layer
        layer = QgsVectorLayer(f"Point?crs={crs.authid()}&index=yes", layer_name, "memory")

        if not layer.isValid():
            raise LayerCreationError(f"Failed to create memory layer: {layer_name}")

        # Add fields to memory layer
        required_fields, optional_fields = self.get_dip_strike_fields()
        all_fields = required_fields + optional_fields

        layer.startEditing()
        layer.dataProvider().addAttributes(all_fields)
        layer.updateFields()
        layer.commitChanges()

        self.log(f"Successfully created memory layer: {layer_name}", log_level=4)
        return layer

    def create_file_layer(self, layer_name, output_path, format_info, crs):
        """Create a file-based layer for dip/strike features.

        :param layer_name: Name for the layer
        :type layer_name: str
        :param output_path: Path to output file
        :type output_path: str
        :param format_info: Format information dictionary
        :type format_info: dict
        :param crs: Coordinate reference system
        :type crs: QgsCoordinateReferenceSystem
        :returns: Created file layer
        :rtype: QgsVectorLayer
        :raises: LayerCreationError if layer creation fails
        """
        self.log(f"Creating {format_info['driver']} layer: {layer_name} at {output_path}", log_level=4)

        # Get field definitions
        required_fields, optional_fields = self.get_dip_strike_fields()
        all_fields = required_fields + optional_fields

        # Create temporary memory layer to define the structure
        temp_layer = QgsVectorLayer(f"Point?crs={crs.authid()}", "temp", "memory")
        temp_layer.startEditing()
        temp_layer.dataProvider().addAttributes(all_fields)
        temp_layer.updateFields()
        temp_layer.commitChanges()

        # Set up writer options
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = format_info["driver"]
        save_options.fileEncoding = "UTF-8"

        # Special handling for shapefiles
        if format_info["driver"] == "ESRI Shapefile":
            field_name_mapping = {}
            shapefile_mapping = self.get_shapefile_field_mapping()

            for field in all_fields:
                original_name = field.name()
                if original_name in shapefile_mapping:
                    short_name = shapefile_mapping[original_name]
                    field_name_mapping[original_name] = short_name
                else:
                    # Fallback for any unmapped fields
                    field_name_mapping[original_name] = original_name[:10]

            # Apply field name mapping
            if field_name_mapping:
                save_options.attributesExportNames = field_name_mapping
                self.log(f"Applied shapefile field mapping: {field_name_mapping}", log_level=4)

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
        layer = QgsVectorLayer(output_path, layer_name, "ogr")

        if not layer.isValid():
            self.log(f"Failed to load created {format_info['driver']} file as layer: {output_path}", log_level=1)
            raise LayerCreationError(f"Failed to load created {format_info['driver']} file as layer")

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

        try:
            if layer_format == "Memory Layer":
                layer = self.create_memory_layer(layer_name, crs)
            else:
                layer = self.create_file_layer(layer_name, output_path, format_info, crs)

            # Configure layer properties
            self.configure_layer_properties(layer, format_info)

            # Add layer to project
            QgsProject.instance().addMapLayer(layer)

            format_info_str = f" ({layer_format})" if layer_format != "Memory Layer" else " (Memory)"
            location_info = f" at {output_path}" if output_path else ""

            self.log(
                f"Successfully created and configured layer: {layer_name}{format_info_str}{location_info}",
                log_level=3,
            )

            return layer

        except Exception as e:
            self.log(f"Error creating dip/strike layer: {e}", log_level=1)
            raise LayerCreationError(f"Failed to create layer: {str(e)}")
