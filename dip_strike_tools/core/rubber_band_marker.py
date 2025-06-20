import math

from qgis.core import Qgis, QgsPointXY
from qgis.gui import QgsRubberBand
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtGui import QColor

from ..toolbelt import PlgLogger


class RubberBandMarker(QObject):
    def __init__(self, canvas):
        super().__init__()
        self.log = PlgLogger().log
        self._canvas = canvas

        # Create separate rubber bands for different parts of the marker
        self._strike_band = QgsRubberBand(canvas, Qgis.GeometryType.Line)
        self._dip_band = QgsRubberBand(canvas, Qgis.GeometryType.Line)
        self._arrow_band1 = QgsRubberBand(canvas, Qgis.GeometryType.Line)  # First dip arrow line
        self._arrow_band2 = QgsRubberBand(canvas, Qgis.GeometryType.Line)  # Second dip arrow line
        self._strike_arrow_band1 = QgsRubberBand(canvas, Qgis.GeometryType.Line)  # First strike arrow line
        self._strike_arrow_band2 = QgsRubberBand(canvas, Qgis.GeometryType.Line)  # Second strike arrow line
        self._center_band = QgsRubberBand(canvas, Qgis.GeometryType.Point)

        # Set colors and styles
        self._strike_band.setColor(QColor(255, 0, 0))  # Red for strike
        self._strike_band.setWidth(3)

        self._dip_band.setColor(QColor(0, 0, 255))  # Blue for dip
        self._dip_band.setWidth(2)

        self._arrow_band1.setColor(QColor(0, 0, 255))  # Blue for dip arrow (same as dip)
        self._arrow_band1.setWidth(2)

        self._arrow_band2.setColor(QColor(0, 0, 255))  # Blue for dip arrow (same as dip)
        self._arrow_band2.setWidth(2)

        self._strike_arrow_band1.setColor(QColor(255, 0, 0))  # Red for strike arrow (same as strike)
        self._strike_arrow_band1.setWidth(2)

        self._strike_arrow_band2.setColor(QColor(255, 0, 0))  # Red for strike arrow (same as strike)
        self._strike_arrow_band2.setWidth(2)

        self._center_band.setColor(QColor(0, 0, 0))  # Black for center point
        self._center_band.setWidth(4)

        # Marker properties
        self._center = QgsPointXY(0, 0)
        self._size = 100  # Size in pixels
        self._azimuth = 0.0  # Azimuth in degrees (0 = North)
        self._dip = 45.0  # Dip angle in degrees
        self._show_strike = True
        self._show_dip = True
        self._visible = True

        # Connect to canvas extent changes to maintain fixed pixel size
        self._canvas.extentsChanged.connect(self._on_canvas_changed)
        # Connect to CRS changes using the correct QGIS API
        self._canvas.destinationCrsChanged.connect(self._on_canvas_changed)

        self.log(message="RubberBandMarker initialized", log_level=4)

        # Initialize geometry with current settings
        # If center is at (0,0), use canvas center as default
        if self._center.x() == 0 and self._center.y() == 0:
            canvas_center = self._canvas.extent().center()
            self._center = canvas_center
            self.log(message=f"Using canvas center as default: {canvas_center}", log_level=4)

        self._update_geometry()

    def setCenter(self, center):
        """Set the center point of the marker"""
        self._center = center
        self._update_geometry()
        # self.log(message=f"Marker center set to: {center}", log_level=4)

    def center(self):
        """Get the center point of the marker"""
        return self._center

    def setSize(self, size):
        """Set the size of the marker in pixels"""
        self._size = size
        self._update_geometry()

    def size(self):
        """Get the size of the marker in pixels"""
        return self._size

    def setAzimuth(self, azimuth):
        """Set the azimuth in degrees (0 = North, 90 = East)"""
        self._azimuth = azimuth % 360
        self._update_geometry()
        # self.log(message=f"Marker azimuth set to: {self._azimuth}°", log_level=4)

    def azimuth(self):
        """Get the azimuth in degrees"""
        return self._azimuth

    def setDip(self, dip):
        """Set the dip angle in degrees"""
        self._dip = max(0, min(90, dip))
        self._update_geometry()

    def dip(self):
        """Get the dip angle in degrees"""
        return self._dip

    def setShowStrike(self, show):
        """Set whether to show the strike line"""
        self._show_strike = show
        self._update_visibility()

    def setShowDip(self, show):
        """Set whether to show the dip line"""
        self._show_dip = show
        self._update_visibility()

    def setVisible(self, visible):
        """Set marker visibility"""
        self._visible = visible
        self._update_visibility()
        # self.log(message=f"Marker visibility set to: {visible}", log_level=4)

    def isVisible(self):
        """Get marker visibility"""
        return self._visible

    def show(self):
        """Show the marker"""
        self.setVisible(True)

    def hide(self):
        """Hide the marker"""
        self.setVisible(False)

    def refresh(self):
        """Refresh the marker geometry (useful after canvas changes)"""
        self._update_geometry()

    def _on_canvas_changed(self):
        """Handle canvas changes (zoom, extent, CRS) to maintain fixed pixel size"""
        self._update_geometry()

    def _update_geometry(self):
        """Update the geometry of all rubber bands"""
        if (
            not self._canvas
            or not self._strike_band
            or not self._dip_band
            or not self._arrow_band1
            or not self._arrow_band2
            or not self._center_band
        ):
            return

        try:
            # Clear existing geometries
            self._strike_band.reset()
            self._dip_band.reset()
            self._arrow_band1.reset()
            self._arrow_band2.reset()
            self._strike_arrow_band1.reset()
            self._strike_arrow_band2.reset()
            self._center_band.reset()

            # Calculate line length in map units
            # Convert pixel size to map units (recalculated each time for fixed pixel size)
            pixel_to_map = self._canvas.mapUnitsPerPixel()
            line_length_map = (self._size / 2) * pixel_to_map

            # self.log(
            #     message=f"Updating geometry: pixel_to_map={pixel_to_map:.6f}, "
            #     f"size={self._size}px, line_length_map={line_length_map:.6f}",
            #     log_level=4,
            # )

            # Create strike line geometry
            if self._show_strike:
                # Convert geological azimuth to mathematical angle
                # Geological: 0° = North, 90° = East (clockwise)
                # Mathematical: 0° = East, 90° = North (counter-clockwise)
                math_angle = math.radians(90 - self._azimuth)

                # Calculate strike line endpoints
                dx = line_length_map * math.cos(math_angle)
                dy = line_length_map * math.sin(math_angle)

                start_point = QgsPointXY(self._center.x() - dx, self._center.y() - dy)
                end_point = QgsPointXY(self._center.x() + dx, self._center.y() + dy)

                self._strike_band.addPoint(start_point)
                self._strike_band.addPoint(end_point)

                # Create arrowhead on the north side of the strike line (end_point side)
                arrow_size_map = (8 / 2) * pixel_to_map  # 8 pixels arrow size converted to map units

                # Calculate arrowhead points (two lines forming arrow tip)
                # Arrow points backwards from the end_point along the strike line
                strike_arrow_angle = math_angle + math.pi  # Reverse direction for arrowhead

                strike_arrow_x1 = end_point.x() + arrow_size_map * math.cos(strike_arrow_angle - math.pi / 6)
                strike_arrow_y1 = end_point.y() + arrow_size_map * math.sin(strike_arrow_angle - math.pi / 6)
                strike_arrow_x2 = end_point.x() + arrow_size_map * math.cos(strike_arrow_angle + math.pi / 6)
                strike_arrow_y2 = end_point.y() + arrow_size_map * math.sin(strike_arrow_angle + math.pi / 6)

                strike_arrow_point1 = QgsPointXY(strike_arrow_x1, strike_arrow_y1)
                strike_arrow_point2 = QgsPointXY(strike_arrow_x2, strike_arrow_y2)

                # Add strike arrow lines
                self._strike_arrow_band1.addPoint(end_point)
                self._strike_arrow_band1.addPoint(strike_arrow_point1)

                self._strike_arrow_band2.addPoint(end_point)
                self._strike_arrow_band2.addPoint(strike_arrow_point2)

                # self.log(message=f"Strike line: {start_point} to {end_point}, azimuth: {self._azimuth}°", log_level=4)

            # Create dip line geometry
            if self._show_dip:
                # Dip direction is perpendicular to strike (90° clockwise from strike azimuth)
                dip_azimuth = (self._azimuth + 90) % 360
                math_angle_dip = math.radians(90 - dip_azimuth)

                # Use fixed dip line length (60% of strike line length)
                dip_line_length = line_length_map * 0.6

                # Calculate dip line endpoint (only show in dip direction, not bidirectional)
                dx_dip = dip_line_length * math.cos(math_angle_dip)
                dy_dip = dip_line_length * math.sin(math_angle_dip)

                dip_end_point = QgsPointXY(self._center.x() + dx_dip, self._center.y() + dy_dip)

                self._dip_band.addPoint(self._center)
                self._dip_band.addPoint(dip_end_point)

                # Create arrowhead on dip line to show direction
                arrow_size_map = (8 / 2) * pixel_to_map  # 8 pixels arrow size converted to map units
                arrow_angle = math_angle_dip

                # Calculate arrowhead points (two lines forming arrow tip)
                arrow_x1 = dip_end_point.x() - arrow_size_map * math.cos(arrow_angle - math.pi / 6)
                arrow_y1 = dip_end_point.y() - arrow_size_map * math.sin(arrow_angle - math.pi / 6)
                arrow_x2 = dip_end_point.x() - arrow_size_map * math.cos(arrow_angle + math.pi / 6)
                arrow_y2 = dip_end_point.y() - arrow_size_map * math.sin(arrow_angle + math.pi / 6)

                arrow_point1 = QgsPointXY(arrow_x1, arrow_y1)
                arrow_point2 = QgsPointXY(arrow_x2, arrow_y2)

                # Add arrow lines to separate arrow bands for better control
                # First arrow line: from tip to arrow_point1
                self._arrow_band1.addPoint(dip_end_point)
                self._arrow_band1.addPoint(arrow_point1)

                # Second arrow line: from tip to arrow_point2
                self._arrow_band2.addPoint(dip_end_point)
                self._arrow_band2.addPoint(arrow_point2)

                # self.log(message=f"Dip line: {self._center} to {dip_end_point}, dip: {self._dip}°", log_level=4)
                # self.log(message=f"Arrow points: {arrow_point1}, {arrow_point2}", log_level=4)

            # Create center point geometry
            self._center_band.addPoint(self._center)

            # Update visibility
            self._update_visibility()

        except Exception as e:
            self.log(message=f"Error updating marker geometry: {e}", log_level=1)

    def _update_visibility(self):
        """Update visibility of all rubber bands"""
        if (
            not self._strike_band
            or not self._dip_band
            or not self._arrow_band1
            or not self._arrow_band2
            or not self._strike_arrow_band1
            or not self._strike_arrow_band2
            or not self._center_band
        ):
            return

        try:
            # Show/hide based on overall visibility and individual component settings
            self._strike_band.setVisible(self._visible and self._show_strike)
            self._dip_band.setVisible(self._visible and self._show_dip)
            self._arrow_band1.setVisible(self._visible and self._show_dip)  # Dip arrow visibility follows dip
            self._arrow_band2.setVisible(self._visible and self._show_dip)  # Dip arrow visibility follows dip
            self._strike_arrow_band1.setVisible(
                self._visible and self._show_strike
            )  # Strike arrow visibility follows strike
            self._strike_arrow_band2.setVisible(
                self._visible and self._show_strike
            )  # Strike arrow visibility follows strike
            self._center_band.setVisible(self._visible)

            # self.log(
            #     message=f"Visibility updated - Strike: {self._visible and self._show_strike}, "
            #     f"Dip: {self._visible and self._show_dip}, Arrow: {self._visible and self._show_dip}, "
            #     f"Center: {self._visible}",
            #     log_level=4,
            # )

        except Exception as e:
            self.log(message=f"Error updating marker visibility: {e}", log_level=1)

    def cleanup(self):
        """Clean up rubber bands when marker is no longer needed"""
        try:
            # Disconnect canvas signals
            if self._canvas:
                try:
                    self._canvas.extentsChanged.disconnect(self._on_canvas_changed)
                    self._canvas.destinationCrsChanged.disconnect(self._on_canvas_changed)
                except TypeError:
                    # Signals may not be connected
                    pass

            if self._strike_band:
                self._strike_band.reset()
                self._strike_band = None

            if self._dip_band:
                self._dip_band.reset()
                self._dip_band = None

            if self._arrow_band1:
                self._arrow_band1.reset()
                self._arrow_band1 = None

            if self._arrow_band2:
                self._arrow_band2.reset()
                self._arrow_band2 = None

            if self._strike_arrow_band1:
                self._strike_arrow_band1.reset()
                self._strike_arrow_band1 = None

            if self._strike_arrow_band2:
                self._strike_arrow_band2.reset()
                self._strike_arrow_band2 = None

            if self._center_band:
                self._center_band.reset()
                self._center_band = None

            self.log(message="RubberBandMarker cleaned up", log_level=4)

        except Exception as e:
            self.log(message=f"Error cleaning up marker: {e}", log_level=1)
