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

"""Dip Strike Map Tool module."""

# PyQGIS
from qgis.gui import QgsHighlight, QgsMapTool, QgsMapToolEmitPoint
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor

from dip_strike_tools.core.feature_finder import FeatureFinder
from dip_strike_tools.toolbelt import PlgLogger, get_cursor_shape


class DipStrikeMapTool(QgsMapToolEmitPoint):
    """Custom map tool to handle click events for inserting dip strike points."""

    canvasClicked = pyqtSignal([int], ["QgsPointXY"])
    featureClicked = pyqtSignal(object, object)  # (point, existing_feature_dict_or_None)

    def __init__(self, iface):
        super(QgsMapTool, self).__init__(iface.mapCanvas())
        self._canvas = iface.mapCanvas()  # Store canvas reference
        self.iface = iface
        self.highlighted_feature = None
        self.current_highlight = None
        self.feature_finder = FeatureFinder(iface)
        self.log = PlgLogger().log

    def _set_safe_cursor(self, cursor_name):
        """Safely set cursor with fallback to ArrowCursor."""
        try:
            cursor_type = get_cursor_shape(cursor_name)
            self.setCursor(QCursor(cursor_type))
        except Exception as e:
            # Ultimate fallback: create a basic arrow cursor
            self.log(message=f"Cursor setting failed, using default: {e}", log_level=4)
            try:
                self.setCursor(QCursor())  # Default cursor
            except Exception:
                pass  # If even this fails, just continue without cursor change

    def canvasMoveEvent(self, event):
        """Handle mouse move to highlight features under cursor."""
        # Get point under cursor
        point_canvas_crs = event.mapPoint()

        # Search for existing feature (without excessive logging)
        existing_feature = self.feature_finder.find_feature_at_point(point_canvas_crs, tolerance_pixels=15)

        if existing_feature:
            self._highlight_feature(existing_feature)
        else:
            self._clear_highlight()

    def canvasReleaseEvent(self, event):
        """Handle canvas press event to open the dip strike dialog."""
        point_canvas_crs = event.mapPoint()

        # Check if there's an existing feature at the clicked point
        existing_feature = self.feature_finder.find_feature_at_point(point_canvas_crs, tolerance_pixels=15)
        if existing_feature:
            # If we found an existing feature, use its geometry center as the point
            feature_geom = existing_feature["feature"].geometry()
            if feature_geom and not feature_geom.isEmpty():
                # Get the centroid of the feature geometry
                centroid = feature_geom.centroid().asPoint()

                # Transform centroid from layer CRS to canvas CRS if needed
                from qgis.core import QgsCoordinateTransform, QgsProject

                if self._canvas:
                    canvas_crs = self._canvas.mapSettings().destinationCrs()
                    layer_crs = existing_feature["layer"].crs()

                    if canvas_crs != layer_crs:
                        try:
                            transform = QgsCoordinateTransform(layer_crs, canvas_crs, QgsProject.instance())
                            point_canvas_crs = transform.transform(centroid)
                        except Exception:
                            # If transformation fails, keep the original clicked point
                            pass
                    else:
                        point_canvas_crs = centroid

        # Emit the enhanced signal with both point and existing feature info
        self.featureClicked.emit(point_canvas_crs, existing_feature)

        # Also emit the legacy signal for backward compatibility
        self.canvasClicked["QgsPointXY"].emit(point_canvas_crs)

    def _highlight_feature(self, existing_feature):
        """Highlight a feature on the map canvas using QgsHighlight.

        :param existing_feature: Dictionary containing feature info
        :type existing_feature: dict
        """
        if not existing_feature:
            return

        feature = existing_feature["feature"]
        layer = existing_feature["layer"]

        # Only highlight if it's a different feature
        if (
            self.highlighted_feature
            and self.highlighted_feature.get("feature")
            and self.highlighted_feature["feature"].id() == feature.id()
            and self.highlighted_feature.get("layer")
            and self.highlighted_feature["layer"].id() == layer.id()
        ):
            return

        # Clear previous highlight
        self._clear_highlight()

        try:
            # Create QgsHighlight for the feature
            # Use the stored canvas reference
            self.current_highlight = QgsHighlight(self._canvas, feature.geometry(), layer)

            # Configure highlight appearance
            highlight_color = QColor(255, 0, 0, 128)  # Semi-transparent red
            self.current_highlight.setColor(highlight_color)
            self.current_highlight.setFillColor(QColor(255, 0, 0, 50))  # Light red fill
            self.current_highlight.setWidth(3)

            # Show the highlight
            self.current_highlight.show()

            # Set cursor to indicate feature is detected
            self._set_safe_cursor("PointingHandCursor")
            self.highlighted_feature = existing_feature

        except Exception as e:
            # Fallback: just provide cursor feedback if highlighting fails
            self.log(message=f"Highlight failed, using cursor only: {e}", log_level=2)
            self._set_safe_cursor("PointingHandCursor")
            self.highlighted_feature = existing_feature

    def _clear_highlight(self):
        """Clear any feature highlight."""
        # Clear QgsHighlight properly
        if self.current_highlight:
            try:
                # Method 1: Remove from scene (preferred)
                scene = self.current_highlight.scene()
                if scene:
                    scene.removeItem(self.current_highlight)

                # Clean up the object
                self.current_highlight = None
            except Exception:
                # Method 2: Fallback to hide and delete
                try:
                    if self.current_highlight:
                        self.current_highlight.hide()
                        # Force deletion by setting to None
                        self.current_highlight = None
                except Exception:
                    self.current_highlight = None

            # Method 3: Force canvas refresh to ensure cleanup
            try:
                if self._canvas:
                    self._canvas.refresh()
            except Exception:
                pass

        # Reset cursor
        self._set_safe_cursor("CrossCursor")
        self.highlighted_feature = None

    def activate(self):
        """Called when the tool is set as the active map tool."""
        super().activate()
        # Set initial cursor
        self._set_safe_cursor("CrossCursor")
        # Ensure mouse tracking is enabled for mouse move events
        if self._canvas:
            self._canvas.setMouseTracking(True)

    def deactivate(self):
        """Called when the tool is deactivated."""
        # Clear any highlights when tool is deactivated
        self._clear_highlight()
        super().deactivate()

    def clean_up(self):
        """Clean up resources when tool is no longer needed."""
        self._clear_highlight()
