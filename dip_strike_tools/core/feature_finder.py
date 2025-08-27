#! python3  # noqa: E265

"""Feature finder utility for dip strike tools."""

from typing import Dict, List, Optional

from qgis.core import (
    QgsCoordinateTransform,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
)

from dip_strike_tools.toolbelt import PlgLogger


class FeatureFinder:
    """Utility class for finding features near clicked points."""

    def __init__(self, iface):
        """Initialize the feature finder.

        :param iface: QGIS interface instance
        :type iface: QgsInterface
        """
        self.iface = iface
        self.log = PlgLogger().log

    def find_feature_at_point(self, clicked_point: QgsPointXY, tolerance_pixels: int = 10) -> Optional[Dict]:
        """Find existing dip/strike features near the clicked point.

        :param clicked_point: The point where user clicked (in map canvas CRS)
        :type clicked_point: QgsPointXY
        :param tolerance_pixels: Search tolerance in pixels
        :type tolerance_pixels: int
        :return: Dictionary with feature info or None if no feature found
        :rtype: dict or None
        """
        # Convert pixel tolerance to map units and create search geometry in canvas CRS
        canvas = self.iface.mapCanvas()
        tolerance_map_units = tolerance_pixels * canvas.mapUnitsPerPixel()
        canvas_crs = canvas.mapSettings().destinationCrs()

        # Create search geometry (circle around clicked point in canvas CRS)
        search_geometry_canvas = QgsGeometry.fromPointXY(clicked_point).buffer(tolerance_map_units, 8)

        # Get relevant point layers
        point_layers = self._get_searchable_point_layers()
        if not point_layers:
            return None

        # Search in configured layers first, then others
        configured_layers, other_layers = self._prioritize_layers(point_layers)

        for layer in configured_layers + other_layers:
            feature = self._search_layer(layer, search_geometry_canvas, canvas_crs)
            if feature:
                return feature

        return None

    def _get_searchable_point_layers(self) -> List[QgsVectorLayer]:
        """Get all searchable point layers from the project.

        :return: List of searchable point layers
        :rtype: List[QgsVectorLayer]
        """
        project = QgsProject.instance()
        if not project:
            return []

        # Get the layer tree root to check visibility
        root = project.layerTreeRoot()
        if not root:
            return []

        point_layers = []
        for layer in project.mapLayers().values():
            if not isinstance(layer, QgsVectorLayer):
                continue

            if (
                layer.geometryType() == 0  # Point geometry type
                and layer.isValid()
            ):
                # Always include configured dip/strike layers, even if not visible
                is_configured_layer = layer.customProperty("dip_strike_tools/layer_role") == "dip_strike_feature_layer"

                if is_configured_layer:
                    point_layers.append(layer)
                else:
                    # For other layers, check if they are visible using layer tree
                    layer_tree_layer = root.findLayer(layer.id())
                    if layer_tree_layer and layer_tree_layer.isVisible():
                        point_layers.append(layer)

        return point_layers

    def _prioritize_layers(
        self, point_layers: List[QgsVectorLayer]
    ) -> tuple[List[QgsVectorLayer], List[QgsVectorLayer]]:
        """Separate configured dip/strike layers from other layers.

        :param point_layers: List of all point layers
        :type point_layers: List[QgsVectorLayer]
        :return: Tuple of (configured_layers, other_layers)
        :rtype: tuple[List[QgsVectorLayer], List[QgsVectorLayer]]
        """
        configured_layers = []
        other_layers = []

        for layer in point_layers:
            # Check if layer is configured for dip/strike tools
            if layer.customProperty("dip_strike_tools/layer_role") == "dip_strike_feature_layer":
                configured_layers.append(layer)
            else:
                other_layers.append(layer)

        return configured_layers, other_layers

    def _search_layer(self, layer: QgsVectorLayer, search_geometry_canvas: QgsGeometry, canvas_crs) -> Optional[Dict]:
        """Search for features in a specific layer.

        :param layer: Vector layer to search
        :type layer: QgsVectorLayer
        :param search_geometry_canvas: Search geometry in canvas CRS
        :type search_geometry_canvas: QgsGeometry
        :param canvas_crs: Canvas coordinate reference system
        :return: Feature dictionary or None
        :rtype: Optional[Dict]
        """
        try:
            # Transform search geometry to layer CRS if needed
            layer_crs = layer.crs()
            if canvas_crs != layer_crs:
                project = QgsProject.instance()
                transform = QgsCoordinateTransform(canvas_crs, layer_crs, project)
                search_geometry_layer = QgsGeometry(search_geometry_canvas)
                search_geometry_layer.transform(transform)
            else:
                search_geometry_layer = search_geometry_canvas

            # Search layer using bounding box filter (spatial index is used automatically by QGIS)
            return self._search_layer_features(layer, search_geometry_layer)

        except Exception as e:
            # Log error and skip layers with errors
            self.log(message=f"Error searching layer '{layer.name()}': {e}", log_level=2)
            return None

    def _search_layer_features(self, layer: QgsVectorLayer, search_geometry: QgsGeometry) -> Optional[Dict]:
        """Search layer using bounding box filter with automatic spatial index optimization.

        :param layer: Vector layer to search
        :type layer: QgsVectorLayer
        :param search_geometry: Search geometry in layer CRS
        :type search_geometry: QgsGeometry
        :return: Feature dictionary or None
        :rtype: Optional[Dict]
        """
        # Use bounding box filter - QGIS automatically uses spatial index when available
        request = QgsFeatureRequest()
        request.setFilterRect(search_geometry.boundingBox())

        # Get features that intersect with search geometry
        for feature in layer.getFeatures(request):  # type: ignore
            if feature.geometry() and feature.geometry().intersects(search_geometry):
                return self._create_feature_dict(feature, layer)

        return None

    def _create_feature_dict(self, feature, layer: QgsVectorLayer) -> Dict:
        """Create a standardized feature dictionary.

        :param feature: The found feature
        :param layer: The layer containing the feature
        :type layer: QgsVectorLayer
        :return: Standardized feature dictionary
        :rtype: Dict
        """
        return {
            "feature": feature,
            "layer": layer,
            "layer_name": layer.name(),
            "is_configured": layer.customProperty("dip_strike_tools/layer_role") == "dip_strike_feature_layer",
        }
