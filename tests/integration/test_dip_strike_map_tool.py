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

#! python3  # noqa: E265

"""
QGIS integration tests for DipStrikeMapTool.

These tests require a QGIS environment and use pytest-qgis.
"""

from unittest.mock import Mock, patch

import pytest

# Import pytest-qgis utilities
pytest_plugins = ["pytest_qgis"]


class TestDipStrikeMapToolQGIS:
    """QGIS integration tests for DipStrikeMapTool."""

    def test_map_tool_import(self):
        """Test that the map tool can be imported in QGIS environment."""
        try:
            from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

            assert DipStrikeMapTool is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")

    def test_map_tool_initialization(self, qgis_iface):
        """Test DipStrikeMapTool initialization in QGIS environment."""
        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        # Create the map tool with iface
        map_tool = DipStrikeMapTool(qgis_iface)

        # Test basic initialization
        assert map_tool._canvas == qgis_iface.mapCanvas()
        assert map_tool.iface == qgis_iface
        assert map_tool.highlighted_feature is None
        assert map_tool.current_highlight is None
        assert map_tool.feature_finder is not None

        # Test that it's a proper QgsMapToolEmitPoint
        from qgis.gui import QgsMapToolEmitPoint

        assert isinstance(map_tool, QgsMapToolEmitPoint)

    def test_map_tool_signals(self, qgis_iface):
        """Test that map tool signals are properly defined."""
        from qgis.PyQt.QtCore import pyqtSignal

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Test that signals exist and are pyqtSignal instances
        assert hasattr(map_tool, "canvasClicked")
        assert hasattr(map_tool, "featureClicked")
        assert isinstance(type(map_tool).canvasClicked, type(pyqtSignal()))
        assert isinstance(type(map_tool).featureClicked, type(pyqtSignal()))

    def test_cursor_setting(self, qgis_iface):
        """Test cursor setting functionality."""
        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Test setting valid cursor
        map_tool._set_safe_cursor("CrossCursor")
        # Should not raise exception

        # Test setting invalid cursor (should fallback)
        map_tool._set_safe_cursor("NonExistentCursor")
        # Should not raise exception

    def test_canvas_move_event_no_plugin(self, qgis_iface):
        """Test canvas move event when no plugin is set."""
        from qgis.core import QgsPointXY
        from qgis.gui import QgsMapMouseEvent

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a mock mouse event
        point = QgsPointXY(0, 0)
        event = Mock(spec=QgsMapMouseEvent)
        event.mapPoint.return_value = point

        # Should not raise exception
        map_tool.canvasMoveEvent(event)

    def test_canvas_move_event_with_plugin(self, qgis_iface):
        """Test canvas move event with feature finder."""
        from qgis.core import QgsPointXY

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Mock the feature_finder
        with patch.object(map_tool.feature_finder, "find_feature_at_point", return_value=None) as mock_find:
            # Create mock event
            point = QgsPointXY(0, 0)
            event = Mock()
            event.mapPoint.return_value = point

            # Should call feature finder method
            map_tool.canvasMoveEvent(event)
            mock_find.assert_called_once_with(point, tolerance_pixels=15)

    def test_canvas_release_event_signal_emission(self, qgis_iface):
        """Test that canvas release event emits signals."""
        from qgis.core import QgsPointXY

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Mock the feature_finder to return None
        with patch.object(map_tool.feature_finder, "find_feature_at_point", return_value=None):
            # Track signal emissions
            feature_clicked_signals = []
            canvas_clicked_signals = []

            def on_feature_clicked(*args):
                feature_clicked_signals.append(args)

            def on_canvas_clicked(*args):
                canvas_clicked_signals.append(args)

            map_tool.featureClicked.connect(on_feature_clicked)
            map_tool.canvasClicked["QgsPointXY"].connect(on_canvas_clicked)

        # Create mock event
        point = QgsPointXY(10, 20)
        event = Mock()
        event.mapPoint.return_value = point

        # Trigger event
        map_tool.canvasReleaseEvent(event)

        # Verify signals were emitted
        assert len(feature_clicked_signals) == 1
        assert len(canvas_clicked_signals) == 1
        assert feature_clicked_signals[0] == (point, None)
        assert canvas_clicked_signals[0] == (point,)

    def test_highlight_feature_with_qgs_highlight(self, qgis_iface):
        """Test feature highlighting with QgsHighlight."""
        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a test layer and feature
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        feature.setId(1)

        existing_feature = {"feature": feature, "layer": layer}

        # Test highlighting (should not raise exception)
        map_tool._highlight_feature(existing_feature)

        # Verify state was set
        assert map_tool.highlighted_feature == existing_feature
        assert map_tool.current_highlight is not None

    def test_clear_highlight(self, qgis_iface):
        """Test clearing highlight."""
        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a test layer and feature for highlighting
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        feature.setId(1)

        existing_feature = {"feature": feature, "layer": layer}

        # First highlight a feature
        map_tool._highlight_feature(existing_feature)
        assert map_tool.highlighted_feature is not None
        assert map_tool.current_highlight is not None

        # Then clear the highlight
        map_tool._clear_highlight()
        assert map_tool.highlighted_feature is None
        assert map_tool.current_highlight is None

    def test_activation_deactivation(self, qgis_iface):
        """Test map tool activation and deactivation."""
        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Test activation
        map_tool.activate()
        # Should not raise exception

        # Test deactivation
        map_tool.deactivate()
        # Should not raise exception

    def test_clean_up(self, qgis_iface):
        """Test map tool cleanup."""
        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a test layer and feature for highlighting
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        feature.setId(1)

        existing_feature = {"feature": feature, "layer": layer}

        # Highlight a feature
        map_tool._highlight_feature(existing_feature)
        assert map_tool.highlighted_feature is not None

        # Clean up
        map_tool.clean_up()
        assert map_tool.highlighted_feature is None
        assert map_tool.current_highlight is None

    def test_canvas_release_event_with_coordinate_transformation(self, qgis_iface):
        """Test canvas release event with coordinate transformation."""
        from unittest.mock import patch

        from qgis.core import QgsCoordinateReferenceSystem, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a test layer with different CRS
        layer = QgsVectorLayer("Point?crs=EPSG:3857", "test_layer", "memory")
        layer.setCrs(QgsCoordinateReferenceSystem("EPSG:3857"))

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1000000, 1000000)))
        feature.setId(1)

        existing_feature = {"feature": feature, "layer": layer}

        # Track signal emissions
        feature_clicked_signals = []

        def on_feature_clicked(*args):
            feature_clicked_signals.append(args)

        map_tool.featureClicked.connect(on_feature_clicked)

        # Create mock event
        point = QgsPointXY(10, 20)
        event = Mock()
        event.mapPoint.return_value = point

        # Set canvas CRS to WGS84
        qgis_iface.mapCanvas().mapSettings().setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        # Mock the feature_finder to return the feature
        with patch.object(map_tool.feature_finder, "find_feature_at_point", return_value=existing_feature):
            # Trigger event (should handle coordinate transformation)
            map_tool.canvasReleaseEvent(event)

        # Verify signal was emitted
        assert len(feature_clicked_signals) == 1
        emitted_point, emitted_feature = feature_clicked_signals[0]
        assert emitted_feature == existing_feature
        # Point should be transformed (different from original click point)
        assert isinstance(emitted_point, QgsPointXY)

    def test_highlight_same_feature_twice(self, qgis_iface):
        """Test highlighting the same feature twice should not recreate highlight."""
        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a test layer and feature
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        feature.setId(1)

        existing_feature = {"feature": feature, "layer": layer}

        # First highlight
        map_tool._highlight_feature(existing_feature)
        first_highlight = map_tool.current_highlight

        # Second highlight of same feature
        map_tool._highlight_feature(existing_feature)
        second_highlight = map_tool.current_highlight

        # Should be the same highlight object
        assert first_highlight == second_highlight

    def test_canvas_move_event_with_existing_feature(self, qgis_iface):
        """Test canvas move event highlighting an existing feature."""
        from unittest.mock import patch

        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a test layer and feature
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        feature.setId(1)

        existing_feature = {"feature": feature, "layer": layer}

        # Create mock event
        point = QgsPointXY(0, 0)
        event = Mock()
        event.mapPoint.return_value = point

        # Mock the feature_finder to return the feature
        with patch.object(map_tool.feature_finder, "find_feature_at_point", return_value=existing_feature):
            # Move event should highlight the feature
            map_tool.canvasMoveEvent(event)

        # Verify feature is highlighted
        assert map_tool.highlighted_feature == existing_feature
        assert map_tool.current_highlight is not None

    def test_map_tool_inheritance(self, qgis_iface):
        """Test that DipStrikeMapTool properly inherits from QgsMapToolEmitPoint."""
        from qgis.gui import QgsMapTool, QgsMapToolEmitPoint

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Test inheritance chain
        assert isinstance(map_tool, QgsMapToolEmitPoint)
        assert isinstance(map_tool, QgsMapTool)

        # Test that it has expected methods from parent classes
        assert hasattr(map_tool, "setCursor")
        assert callable(map_tool.setCursor)
        assert hasattr(map_tool, "activate")
        assert callable(map_tool.activate)
        assert hasattr(map_tool, "deactivate")
        assert callable(map_tool.deactivate)

    def test_canvas_release_event_coordinate_transformation_failure(self, qgis_iface):
        """Test canvas release event when coordinate transformation fails."""
        from unittest.mock import patch

        from qgis.core import QgsCoordinateReferenceSystem, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a test layer with different CRS
        layer = QgsVectorLayer("Point?crs=EPSG:3857", "test_layer", "memory")
        layer.setCrs(QgsCoordinateReferenceSystem("EPSG:3857"))

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1000000, 1000000)))
        feature.setId(1)

        existing_feature = {"feature": feature, "layer": layer}

        # Track signal emissions
        feature_clicked_signals = []

        def on_feature_clicked(*args):
            feature_clicked_signals.append(args)

        map_tool.featureClicked.connect(on_feature_clicked)

        # Create mock event
        point = QgsPointXY(10, 20)
        event = Mock()
        event.mapPoint.return_value = point

        # Set canvas CRS to different from layer CRS
        qgis_iface.mapCanvas().mapSettings().setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        # Mock coordinate transformation to fail
        with patch("qgis.core.QgsCoordinateTransform") as mock_transform_class:
            mock_transform = Mock()
            mock_transform.transform.side_effect = Exception("Transform failed")
            mock_transform_class.return_value = mock_transform

            # Mock the feature_finder to return the feature
            with patch.object(map_tool.feature_finder, "find_feature_at_point", return_value=existing_feature):
                # Trigger event (should handle transformation failure gracefully)
                map_tool.canvasReleaseEvent(event)

            # Should still emit signal with original point when transformation fails
            assert len(feature_clicked_signals) == 1
            emitted_point, emitted_feature = feature_clicked_signals[0]
            assert emitted_feature == existing_feature

    def test_highlight_feature_exception_without_plugin(self, qgis_iface):
        """Test highlighting when exception occurs and no plugin is set."""
        from unittest.mock import patch

        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a test layer and feature
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        feature.setId(1)

        existing_feature = {"feature": feature, "layer": layer}

        # Mock QgsHighlight to raise exception
        with patch("dip_strike_tools.core.dip_strike_map_tool.QgsHighlight") as mock_highlight_class:
            mock_highlight_class.side_effect = Exception("Highlight creation failed")

            # Should handle exception gracefully without plugin
            map_tool._highlight_feature(existing_feature)

            # Should still set highlighted_feature
            assert map_tool.highlighted_feature == existing_feature

    def test_clear_highlight_scene_removal_exception(self, qgis_iface):
        """Test clearing highlight when scene removal fails."""
        from unittest.mock import Mock

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create mock highlight that fails on scene removal
        mock_highlight = Mock()
        mock_scene = Mock()
        mock_scene.removeItem.side_effect = Exception("Scene removal failed")
        mock_highlight.scene.return_value = mock_scene
        mock_highlight.hide = Mock()

        map_tool.current_highlight = mock_highlight

        # Should handle scene removal exception gracefully
        map_tool._clear_highlight()

        # Should have tried fallback methods
        mock_highlight.hide.assert_called_once()
        assert map_tool.current_highlight is None
        assert map_tool.highlighted_feature is None

    def test_clear_highlight_canvas_refresh_exception(self, qgis_iface):
        """Test clearing highlight when canvas refresh fails."""
        from unittest.mock import Mock, patch

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create mock highlight
        mock_highlight = Mock()
        mock_scene = Mock()
        mock_highlight.scene.return_value = mock_scene
        map_tool.current_highlight = mock_highlight

        # Patch the canvas refresh method to fail
        with patch.object(map_tool._canvas, "refresh", side_effect=Exception("Canvas refresh failed")):
            # Should handle canvas refresh exception gracefully
            map_tool._clear_highlight()

        # Should still clear state
        assert map_tool.current_highlight is None
        assert map_tool.highlighted_feature is None

    def test_clear_highlight_hide_exception(self, qgis_iface):
        """Test clearing highlight when hide method fails."""
        from unittest.mock import Mock

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create mock highlight that fails on all methods
        mock_highlight = Mock()
        mock_highlight.scene.side_effect = Exception("Scene failed")
        mock_highlight.hide.side_effect = Exception("Hide failed")

        map_tool.current_highlight = mock_highlight

        # Should handle all exceptions gracefully
        map_tool._clear_highlight()

        # Should still clear state
        assert map_tool.current_highlight is None
        assert map_tool.highlighted_feature is None

    def test_canvas_release_event_with_different_crs_same_result(self, qgis_iface):
        """Test canvas release event with different CRS that are actually equal."""
        from unittest.mock import patch

        from qgis.core import QgsCoordinateReferenceSystem, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a test layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        layer.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 20)))
        feature.setId(1)

        existing_feature = {"feature": feature, "layer": layer}

        # Track signal emissions
        feature_clicked_signals = []

        def on_feature_clicked(*args):
            feature_clicked_signals.append(args)

        map_tool.featureClicked.connect(on_feature_clicked)

        # Create mock event
        click_point = QgsPointXY(5, 5)
        event = Mock()
        event.mapPoint.return_value = click_point

        # Set canvas CRS to same as layer CRS (should use centroid)
        qgis_iface.mapCanvas().mapSettings().setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        # Mock the feature_finder to return the feature
        with patch.object(map_tool.feature_finder, "find_feature_at_point", return_value=existing_feature):
            # Trigger event
            map_tool.canvasReleaseEvent(event)

        # Should use feature centroid since CRS are the same
        assert len(feature_clicked_signals) == 1
        emitted_point, emitted_feature = feature_clicked_signals[0]
        assert emitted_feature == existing_feature
        # The emitted point should be the feature's centroid, not the click point
        assert emitted_point != click_point

    def test_canvas_release_same_crs_using_centroid(self, qgis_iface):
        """Test canvas release event using feature centroid when CRS are the same."""
        from unittest.mock import patch

        from qgis.core import QgsCoordinateReferenceSystem, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

        from dip_strike_tools.core.dip_strike_map_tool import DipStrikeMapTool

        map_tool = DipStrikeMapTool(qgis_iface)

        # Create a test layer with specific CRS
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
        layer.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        # Create feature with specific geometry
        feature_point = QgsPointXY(100, 200)
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(feature_point))
        feature.setId(1)

        existing_feature = {"feature": feature, "layer": layer}

        # Track signal emissions
        feature_clicked_signals = []

        def on_feature_clicked(*args):
            feature_clicked_signals.append(args)

        map_tool.featureClicked.connect(on_feature_clicked)

        # Create mock event with different click point
        click_point = QgsPointXY(0, 0)  # Different from feature point
        event = Mock()
        event.mapPoint.return_value = click_point

        # Set canvas CRS to be exactly the same as layer CRS
        qgis_iface.mapCanvas().mapSettings().setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        # Mock the feature_finder to return the feature
        with patch.object(map_tool.feature_finder, "find_feature_at_point", return_value=existing_feature):
            # Trigger event
            map_tool.canvasReleaseEvent(event)

        # Should use feature centroid (not click point) since CRS are the same
        assert len(feature_clicked_signals) == 1
        emitted_point, emitted_feature = feature_clicked_signals[0]
        assert emitted_feature == existing_feature

        # The emitted point should be the feature's centroid
        assert emitted_point.x() == feature_point.x()
        assert emitted_point.y() == feature_point.y()
        assert emitted_point != click_point
