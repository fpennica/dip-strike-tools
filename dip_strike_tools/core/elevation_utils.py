"""Utility functions for elevation extraction from raster layers."""

from qgis.core import (
    Qgis,
    QgsCoordinateTransform,
    QgsProject,
    QgsRasterLayer,
)

from ..toolbelt.log_handler import PlgLogger


class ElevationExtractor:
    """Utility class for extracting elevation values from raster layers."""

    def __init__(self):
        """Initialize the elevation extractor."""
        self.log = PlgLogger().log

    def is_suitable_dtm_layer(self, layer):
        """Check if a raster layer is suitable for elevation extraction.

        :param layer: The raster layer to check
        :type layer: QgsRasterLayer
        :return: True if suitable, error message if not
        :rtype: tuple(bool, str)
        """
        if not layer or not isinstance(layer, QgsRasterLayer):
            return False, "Layer is not a raster layer"

        if not layer.isValid():
            return False, "Layer is not valid"

        # Check if it's a single band raster (typical for DTM/DEM)
        if layer.bandCount() != 1:
            return False, f"Layer has {layer.bandCount()} bands, expected single band for DTM"

        # Check if the band has numeric data type
        data_type = layer.dataProvider().dataType(1)  # Band 1
        numeric_types = [
            Qgis.DataType.Byte,
            Qgis.DataType.Int16,
            Qgis.DataType.UInt16,
            Qgis.DataType.Int32,
            Qgis.DataType.UInt32,
            Qgis.DataType.Float32,
            Qgis.DataType.Float64,
        ]

        if data_type not in numeric_types:
            return False, f"Layer data type {data_type} is not suitable for elevation data"

        return True, ""

    def extract_elevation(self, dtm_layer, point, target_crs=None):
        """Extract elevation value from DTM at the given point.

        :param dtm_layer: The DTM raster layer
        :type dtm_layer: QgsRasterLayer
        :param point: The point to extract elevation for
        :type point: QgsPointXY
        :param target_crs: CRS of the input point (if different from DTM CRS)
        :type target_crs: QgsCoordinateReferenceSystem or None
        :return: Tuple of (success, elevation_value, error_message)
        :rtype: tuple(bool, float or None, str)
        """
        try:
            # Check if the layer is suitable
            is_suitable, error_msg = self.is_suitable_dtm_layer(dtm_layer)
            if not is_suitable:
                return False, None, error_msg

            # Get DTM CRS
            dtm_crs = dtm_layer.crs()
            self.log(f"DTM CRS: {dtm_crs.authid()}", log_level=4)

            # Transform point if necessary
            query_point = point
            if target_crs and target_crs != dtm_crs:
                self.log(
                    f"Transforming point from {target_crs.authid()} to {dtm_crs.authid()}",
                    log_level=4,
                )
                transform = QgsCoordinateTransform(target_crs, dtm_crs, QgsProject.instance())
                try:
                    query_point = transform.transform(point)
                    self.log(
                        f"Transformed point: {point.x():.4f}, {point.y():.4f} → {query_point.x():.4f}, {query_point.y():.4f}",
                        log_level=4,
                    )
                except Exception as e:
                    return False, None, f"Failed to transform coordinates: {str(e)}"

            # Check if point is within DTM extent
            dtm_extent = dtm_layer.extent()
            if not dtm_extent.contains(query_point):
                return (
                    False,
                    None,
                    f"Point ({query_point.x():.4f}, {query_point.y():.4f}) is outside DTM extent",
                )

            # Sample the raster at the point
            data_provider = dtm_layer.dataProvider()
            result = data_provider.identify(query_point, Qgis.RasterIdentifyFormat.Value)

            if not result.isValid():
                return False, None, "Failed to identify raster value at point"

            results = result.results()
            if 1 not in results:  # Band 1
                return False, None, "No elevation data available at this point"

            elevation = results[1]

            # Check for nodata values
            if elevation is None:
                return False, None, "No elevation data available at this point (nodata)"

            # Convert to float and check for special values
            try:
                elevation_float = float(elevation)

                # Check for common nodata values
                nodata_value = data_provider.sourceNoDataValue(1)
                if nodata_value is not None and abs(elevation_float - nodata_value) < 1e-10:
                    return False, None, "No elevation data available at this point (nodata value)"

                # Check for unreasonable values (basic sanity check)
                if elevation_float < -12000 or elevation_float > 9000:  # Below Dead Sea to above Everest
                    self.log(
                        f"Warning: Elevation value {elevation_float} seems unreasonable",
                        log_level=2,
                    )

                self.log(f"Extracted elevation: {elevation_float} m", log_level=4)
                return True, elevation_float, ""

            except (ValueError, TypeError) as e:
                return False, None, f"Invalid elevation value: {str(e)}"

        except Exception as e:
            return False, None, f"Unexpected error during elevation extraction: {str(e)}"

    def get_suitable_dtm_layers(self):
        """Get all raster layers in the project suitable for DTM.

        :return: List of suitable DTM layers
        :rtype: list[QgsRasterLayer]
        """
        suitable_layers = []
        project = QgsProject.instance()

        for layer_id, layer in project.mapLayers().items():
            if isinstance(layer, QgsRasterLayer):
                is_suitable, _ = self.is_suitable_dtm_layer(layer)
                if is_suitable:
                    suitable_layers.append(layer)

        return suitable_layers

    def format_elevation_display(self, elevation):
        """Format elevation value for display.

        :param elevation: Elevation value in meters
        :type elevation: float
        :return: Formatted elevation string
        :rtype: str
        """
        if elevation is None:
            return "N/A"

        # Round to nearest integer for display
        return f"{int(round(elevation))} m"
