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

#! python3  # noqa E265

"""
QGIS integration tests for feature_finder module.

These tests require a QGIS environment and use pytest-qgis.
"""

from unittest.mock import Mock, patch

# Import pytest-qgis utilities
pytest_plugins = ["pytest_qgis"]


class TestFeatureFinderQGIS:
    """QGIS integration tests for FeatureFinder."""

    def test_feature_finder_import(self):
        """Test FeatureFinder can be imported."""
        from dip_strike_tools.core.feature_finder import FeatureFinder

        assert FeatureFinder is not None

    def test_feature_finder_initialization(self, qgis_iface):
        """Test FeatureFinder initialization."""
        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Verify basic attributes
        assert finder.iface == qgis_iface
        assert hasattr(finder, "log")

    @patch("dip_strike_tools.core.feature_finder.QgsProject")
    def test_find_feature_at_point_no_layers(self, mock_project, qgis_iface):
        """Test feature finding when no layers exist."""
        from qgis.core import QgsPointXY

        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Mock project with no layers
        mock_project_instance = Mock()
        mock_project_instance.mapLayers.return_value = {}
        mock_project.instance.return_value = mock_project_instance

        test_point = QgsPointXY(100, 200)
        result = finder.find_feature_at_point(test_point)

        assert result is None

    @patch("dip_strike_tools.core.feature_finder.QgsProject")
    def test_find_feature_at_point_with_configured_layer(self, mock_project, qgis_iface):
        """Test feature finding with a configured layer containing features."""
        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Create a mock layer with configured dip/strike properties
        mock_layer = Mock(spec=QgsVectorLayer)
        mock_layer.geometryType.return_value = 0  # Point geometry
        mock_layer.isValid.return_value = True
        mock_layer.customProperty.return_value = "dip_strike_feature_layer"
        mock_layer.crs.return_value = Mock()
        mock_layer.name.return_value = "Test Dip Strike Layer"
        mock_layer.id.return_value = "layer_1"
        mock_layer.hasSpatialIndex.return_value = True

        # Create a mock feature
        mock_feature = Mock(spec=QgsFeature)
        mock_feature.geometry.return_value = Mock(spec=QgsGeometry)
        mock_feature.geometry.return_value.intersects.return_value = True

        # Mock the layer's getFeatures method to return our mock feature
        mock_layer.getFeatures.return_value = [mock_feature]

        # Mock project
        mock_project_instance = Mock()
        mock_project_instance.mapLayers.return_value = {"layer_1": mock_layer}

        # Mock layer tree
        mock_layer_tree_layer = Mock()
        mock_layer_tree_layer.isVisible.return_value = True
        mock_root = Mock()
        mock_root.findLayer.return_value = mock_layer_tree_layer
        mock_project_instance.layerTreeRoot.return_value = mock_root

        mock_project.instance.return_value = mock_project_instance

        # Mock canvas
        mock_canvas = Mock()
        mock_canvas.mapUnitsPerPixel.return_value = 1.0
        mock_canvas_settings = Mock()
        mock_canvas_settings.destinationCrs.return_value = mock_layer.crs.return_value
        mock_canvas.mapSettings.return_value = mock_canvas_settings

        with patch.object(qgis_iface, "mapCanvas", return_value=mock_canvas):
            test_point = QgsPointXY(100, 200)
            result = finder.find_feature_at_point(test_point)

            # Should return the feature
            assert result is not None
            assert result["feature"] == mock_feature
            assert result["layer"] == mock_layer
            assert result["layer_name"] == "Test Dip Strike Layer"
            assert result["is_configured"] is True

    @patch("dip_strike_tools.core.feature_finder.QgsProject")
    def test_find_feature_early_returns(self, mock_project, qgis_iface):
        """Test feature finding method's early return conditions."""
        from qgis.core import QgsPointXY

        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)
        test_point = QgsPointXY(100, 200)

        # Test when project is None
        mock_project.instance.return_value = None
        result = finder.find_feature_at_point(test_point)
        assert result is None

        # Test when layer tree root is None
        mock_project_instance = Mock()
        mock_project_instance.layerTreeRoot.return_value = None
        mock_project.instance.return_value = mock_project_instance
        result = finder.find_feature_at_point(test_point)
        assert result is None

    @patch("dip_strike_tools.core.feature_finder.QgsProject")
    def test_find_feature_coordinate_transform_error(self, mock_project, qgis_iface):
        """Test feature finding when coordinate transformation fails."""
        from qgis.core import QgsPointXY

        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Mock layer with different CRS that causes transform error
        mock_layer = Mock()
        mock_layer.geometryType.return_value = 0  # Point geometry
        mock_layer.isValid.return_value = True
        mock_layer.customProperty.return_value = "dip_strike_feature_layer"
        mock_layer.crs.return_value = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.id.return_value = "layer_1"

        # Mock project
        mock_project_instance = Mock()
        mock_project_instance.mapLayers.return_value = {"layer_1": mock_layer}

        # Mock layer tree
        mock_layer_tree_layer = Mock()
        mock_layer_tree_layer.isVisible.return_value = True
        mock_root = Mock()
        mock_root.findLayer.return_value = mock_layer_tree_layer
        mock_project_instance.layerTreeRoot.return_value = mock_root

        mock_project.instance.return_value = mock_project_instance

        # Mock canvas with different CRS than layer
        mock_canvas = Mock()
        mock_canvas.mapUnitsPerPixel.return_value = 1.0
        mock_canvas_settings = Mock()
        mock_canvas_crs = Mock()
        mock_canvas_settings.destinationCrs.return_value = mock_canvas_crs
        mock_canvas.mapSettings.return_value = mock_canvas_settings

        # Make layer CRS different from canvas CRS
        mock_layer_crs = Mock()
        mock_layer.crs.return_value = mock_layer_crs
        mock_canvas_crs.__ne__ = Mock(return_value=True)  # Different CRS

        with patch.object(qgis_iface, "mapCanvas", return_value=mock_canvas):
            test_point = QgsPointXY(100, 200)

            with patch("dip_strike_tools.core.feature_finder.QgsCoordinateTransform") as mock_transform_class:
                mock_transform_instance = Mock()
                mock_transform_instance.transform.side_effect = Exception("Transform error")
                mock_transform_class.return_value = mock_transform_instance

                result = finder.find_feature_at_point(test_point)

                # Should return None due to transform error
                assert result is None

    @patch("dip_strike_tools.core.feature_finder.QgsProject")
    def test_find_feature_layer_processing_error(self, mock_project, qgis_iface):
        """Test feature finding when layer processing encounters an error."""
        from qgis.core import QgsPointXY

        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Mock layer that will cause an error during processing
        mock_layer = Mock()
        mock_layer.geometryType.return_value = 0  # Point geometry
        mock_layer.isValid.return_value = True
        mock_layer.customProperty.return_value = "other_layer"
        mock_layer.crs.side_effect = Exception("Layer error")  # This will cause an error
        mock_layer.name.return_value = "Test Layer"
        mock_layer.id.return_value = "layer_1"

        # Mock project
        mock_project_instance = Mock()
        mock_project_instance.mapLayers.return_value = {"layer_1": mock_layer}

        # Mock layer tree
        mock_layer_tree_layer = Mock()
        mock_layer_tree_layer.isVisible.return_value = True
        mock_root = Mock()
        mock_root.findLayer.return_value = mock_layer_tree_layer
        mock_project_instance.layerTreeRoot.return_value = mock_root

        mock_project.instance.return_value = mock_project_instance

        # Mock canvas
        mock_canvas = Mock()
        mock_canvas.mapUnitsPerPixel.return_value = 1.0
        mock_canvas_settings = Mock()
        mock_canvas_settings.destinationCrs.return_value = Mock()
        mock_canvas.mapSettings.return_value = mock_canvas_settings

        with patch.object(qgis_iface, "mapCanvas", return_value=mock_canvas):
            test_point = QgsPointXY(100, 200)

            result = finder.find_feature_at_point(test_point)

            # Should return None due to layer processing error
            assert result is None

    @patch("dip_strike_tools.core.feature_finder.QgsProject")
    def test_find_feature_with_visible_non_configured_layer(self, mock_project, qgis_iface):
        """Test feature finding with a visible non-configured layer."""
        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Create a mock layer that is NOT configured for dip/strike
        mock_layer = Mock(spec=QgsVectorLayer)
        mock_layer.geometryType.return_value = 0  # Point geometry
        mock_layer.isValid.return_value = True
        mock_layer.customProperty.return_value = "other_layer"  # Not a dip/strike layer
        mock_layer.crs.return_value = Mock()
        mock_layer.name.return_value = "Regular Point Layer"
        mock_layer.id.return_value = "layer_1"
        mock_layer.hasSpatialIndex.return_value = False

        # Create a mock feature
        mock_feature = Mock(spec=QgsFeature)
        mock_feature.geometry.return_value = Mock(spec=QgsGeometry)
        mock_feature.geometry.return_value.intersects.return_value = True

        # Mock the layer's getFeatures method to return our mock feature
        mock_layer.getFeatures.return_value = [mock_feature]

        # Mock project
        mock_project_instance = Mock()
        mock_project_instance.mapLayers.return_value = {"layer_1": mock_layer}

        # Mock layer tree - this layer is visible
        mock_layer_tree_layer = Mock()
        mock_layer_tree_layer.isVisible.return_value = True
        mock_root = Mock()
        mock_root.findLayer.return_value = mock_layer_tree_layer
        mock_project_instance.layerTreeRoot.return_value = mock_root

        mock_project.instance.return_value = mock_project_instance

        # Mock canvas
        mock_canvas = Mock()
        mock_canvas.mapUnitsPerPixel.return_value = 1.0
        mock_canvas_settings = Mock()
        mock_canvas_settings.destinationCrs.return_value = mock_layer.crs.return_value
        mock_canvas.mapSettings.return_value = mock_canvas_settings

        with patch.object(qgis_iface, "mapCanvas", return_value=mock_canvas):
            test_point = QgsPointXY(100, 200)
            result = finder.find_feature_at_point(test_point)

            # Should return the feature from the non-configured layer
            assert result is not None
            assert result["feature"] == mock_feature
            assert result["layer"] == mock_layer
            assert result["layer_name"] == "Regular Point Layer"
            assert result["is_configured"] is False

    def test_get_searchable_point_layers_basic(self, qgis_iface):
        """Test _get_searchable_point_layers method basic functionality."""
        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Test that method exists and is callable
        assert hasattr(finder, "_get_searchable_point_layers")
        assert callable(finder._get_searchable_point_layers)

    def test_prioritize_layers_basic(self, qgis_iface):
        """Test _prioritize_layers method basic functionality."""
        from qgis.core import QgsVectorLayer

        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Create mock layers with proper spec
        configured_layer = Mock(spec=QgsVectorLayer)
        configured_layer.customProperty.return_value = "dip_strike_feature_layer"

        other_layer = Mock(spec=QgsVectorLayer)
        other_layer.customProperty.return_value = "other_type"

        point_layers = [configured_layer, other_layer]

        # Test prioritization
        configured, others = finder._prioritize_layers(point_layers)  # type: ignore

        assert configured_layer in configured
        assert other_layer in others
        assert len(configured) == 1
        assert len(others) == 1

    def test_search_layer_basic(self, qgis_iface):
        """Test _search_layer method basic functionality."""
        from qgis.core import QgsGeometry, QgsPointXY

        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Create mock layer
        mock_layer = Mock()
        mock_layer.crs.return_value = Mock()
        mock_layer.hasSpatialIndex.return_value = True
        mock_layer.name.return_value = "Test Layer"

        # Create mock search geometry
        search_geometry = QgsGeometry.fromPointXY(QgsPointXY(0, 0)).buffer(10, 8)

        # Mock canvas CRS
        mock_crs = Mock()

        # Test that method exists and handles the call
        result = finder._search_layer(mock_layer, search_geometry, mock_crs)

        # Should not crash and return None or a result
        assert result is None or isinstance(result, dict)

    def test_create_feature_dict(self, qgis_iface):
        """Test _create_feature_dict method."""
        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Create mock feature and layer
        mock_feature = Mock()
        mock_layer = Mock()
        mock_layer.name.return_value = "Test Layer"
        mock_layer.customProperty.return_value = "dip_strike_feature_layer"

        # Test feature dict creation
        result = finder._create_feature_dict(mock_feature, mock_layer)

        # Verify the structure
        assert isinstance(result, dict)
        assert result["feature"] == mock_feature
        assert result["layer"] == mock_layer
        assert result["layer_name"] == "Test Layer"
        assert result["is_configured"] is True

    def test_create_feature_dict_non_configured(self, qgis_iface):
        """Test _create_feature_dict method with non-configured layer."""
        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Create mock feature and non-configured layer
        mock_feature = Mock()
        mock_layer = Mock()
        mock_layer.name.return_value = "Regular Layer"
        mock_layer.customProperty.return_value = "other_type"

        # Test feature dict creation
        result = finder._create_feature_dict(mock_feature, mock_layer)

        # Verify the structure
        assert isinstance(result, dict)
        assert result["feature"] == mock_feature
        assert result["layer"] == mock_layer
        assert result["layer_name"] == "Regular Layer"
        assert result["is_configured"] is False

    def test_search_methods_exist(self, qgis_iface):
        """Test that search helper methods exist."""
        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Verify helper methods exist
        assert hasattr(finder, "_search_layer_features")
        assert callable(finder._search_layer_features)

    def test_tolerance_parameter(self, qgis_iface):
        """Test that tolerance parameter is handled correctly."""
        from qgis.core import QgsPointXY

        from dip_strike_tools.core.feature_finder import FeatureFinder

        finder = FeatureFinder(qgis_iface)

        # Mock canvas
        mock_canvas = Mock()
        mock_canvas.mapUnitsPerPixel.return_value = 1.0
        mock_canvas_settings = Mock()
        mock_canvas_settings.destinationCrs.return_value = Mock()
        mock_canvas.mapSettings.return_value = mock_canvas_settings

        with patch.object(qgis_iface, "mapCanvas", return_value=mock_canvas):
            with patch("dip_strike_tools.core.feature_finder.QgsProject"):
                # Test with different tolerance values
                test_point = QgsPointXY(100, 200)

                # Should not crash with different tolerance values
                finder.find_feature_at_point(test_point, tolerance_pixels=5)
                finder.find_feature_at_point(test_point, tolerance_pixels=15)
                finder.find_feature_at_point(test_point, tolerance_pixels=20)
