from pathlib import Path

from qgis.core import Qgis, QgsBearingUtils, QgsCoordinateReferenceSystem, QgsCoordinateTransformContext
from qgis.gui import QgsMapCanvas, QgsMapToolPan
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtWidgets import QDial, QDialog, QDoubleSpinBox, QGraphicsScene, QGraphicsView
from qgis.utils import iface

from ..core.rubber_band_marker import RubberBandMarker
from ..toolbelt import PlgLogger

FORM_CLASS, _ = uic.loadUiType(Path(__file__).parent / f"{Path(__file__).stem}.ui")


class DlgInsertDipStrike(QDialog, FORM_CLASS):
    def __init__(self, parent=None, clicked_point=None):
        super().__init__(parent)
        self.setupUi(self)

        self.iface = iface
        self.log = PlgLogger().log

        # Set filters for feature layer combobox to only show point layers
        self.cbo_feature_layer.setFilters(Qgis.LayerFilter.PointLayer)

        self.dial_azimuth = QDial()

        self.dial_azimuth.setFixedHeight(80)
        self.dial_azimuth.setFixedWidth(80)

        # adapt QDial to be used for inserting azimuth values
        self.dial_azimuth.setWrapping(True)
        self.dial_azimuth.setNotchesVisible(True)
        self.dial_azimuth.setPageStep(90)
        self.dial_azimuth.setSingleStep(45)
        self.dial_azimuth.setMinimum(0)
        self.dial_azimuth.setMaximum(359)  # 0-359 to avoid 360 showing as 0

        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.graphics_item = self.scene.addWidget(self.dial_azimuth)
        if self.graphics_item:
            self.graphics_item.setRotation(180)

        # Make the QGraphicsView invisible
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setFixedHeight(self.dial_azimuth.height())
        self.view.setFixedWidth(self.dial_azimuth.width())
        self.view.setStyleSheet("border: 0px")

        # self.azimuth_label = QLabel("Azimuth (°):")
        # self.azimuth_hlayout.addWidget(self.azimuth_label)
        self.azimuth_hlayout.addWidget(self.view)

        # Add synchronized decimal degree spinbox
        self.azimuth_spinbox = QDoubleSpinBox()

        # Configure the spinbox
        self.azimuth_spinbox.setFixedWidth(80)
        self.azimuth_spinbox.setMinimum(0.0)
        self.azimuth_spinbox.setMaximum(360.0)
        self.azimuth_spinbox.setDecimals(2)  # Allow 2 decimal places
        self.azimuth_spinbox.setSingleStep(1)
        self.azimuth_spinbox.setValue(0.0)
        self.azimuth_spinbox.setSuffix("°")
        self.azimuth_spinbox.setToolTip(
            QCoreApplication.translate(
                "DlgInsertDipStrike", "Enter azimuth value in decimal degrees from North (0.00-360.00°)"
            )
        )

        # Add spinbox and label to layout
        self.azimuth_hlayout.addWidget(self.azimuth_spinbox)

        # Connect signals for synchronization
        self.dial_azimuth.valueChanged.connect(self.update_spinbox_from_dial)
        self.azimuth_spinbox.valueChanged.connect(self.update_dial_from_spinbox)

        # Connect radio buttons for strike/dip mode
        self.rdio_strike.toggled.connect(self.on_strike_dip_mode_changed)
        self.rdio_dip.toggled.connect(self.on_strike_dip_mode_changed)

        # map canvas
        self.map_canvas_widget = QgsMapCanvas(self)
        # set crs to match the current map canvas
        destination_crs: QgsCoordinateReferenceSystem = self.iface.mapCanvas().mapSettings().destinationCrs()  # type: ignore
        self.lbl_crs.setText(destination_crs.authid())
        self.log(
            message=f"Setting map canvas CRS to: {destination_crs.authid()}",
            log_level=4,
        )
        self.map_canvas_widget.setDestinationCrs(destination_crs)
        self.grp_preview.layout().addWidget(self.map_canvas_widget)

        self.map_canvas_widget.enableAntiAliasing(True)
        self.map_canvas_widget.setLayers(self.iface.mapCanvas().layers())  # type: ignore
        self.map_canvas_widget.setExtent(self.iface.mapCanvas().extent())  # type: ignore

        if clicked_point:
            self.map_canvas_widget.setCenter(clicked_point)
        else:
            self.map_canvas_widget.setCenter(self.map_canvas_widget.extent().center())

        self.map_canvas_widget.setWheelFactor(1.2)
        self.toolPan = QgsMapToolPan(self.map_canvas_widget)
        self.map_canvas_widget.setMapTool(self.toolPan)
        # self.map_canvas_widget.setWheelAction(QgsMapCanvas.WheelNothing)
        self.map_canvas_widget.refresh()

        # dip-strike symbol using RubberBand
        self.dip_strike_item = RubberBandMarker(self.map_canvas_widget)

        # Set the marker center to the clicked point or canvas center
        if clicked_point:
            self.dip_strike_item.setCenter(clicked_point)
            self.log(
                message=f"Setting dip-strike marker center to clicked point: {clicked_point}",
                log_level=4,
            )
            self._true_north_bearing = QgsBearingUtils.bearingTrueNorth(
                destination_crs, QgsCoordinateTransformContext(), clicked_point
            )
            self.log(f"North bearing: {self._true_north_bearing}", log_level=4)
            crs_type = destination_crs.type()
            if crs_type == Qgis.CrsType.Projected:
                self.lbl_coord_x.setText(f"X: {clicked_point.x():.2f}")
                self.lbl_coord_y.setText(f"Y: {clicked_point.y():.2f}")
            else:
                self.lbl_coord_x.setText(f"Lon: {clicked_point.x():.4f}")
                self.lbl_coord_y.setText(f"Lat: {clicked_point.y():.4f}")
            self.lbl_north_bearing.setText(f"{self._true_north_bearing:.2f}°")
        else:
            canvas_center = self.map_canvas_widget.extent().center()
            self.dip_strike_item.setCenter(canvas_center)
            self.log(
                message=f"Setting dip-strike marker center to canvas center: {canvas_center}",
                log_level=4,
            )
            self._true_north_bearing = QgsBearingUtils.bearingTrueNorth(
                destination_crs, QgsCoordinateTransformContext(), canvas_center
            )
            self.log(f"North bearing: {self._true_north_bearing}", log_level=4)
            crs_type = destination_crs.type()
            if crs_type == Qgis.CrsType.Projected:
                self.lbl_coord_x.setText(f"X: {canvas_center.x():.2f}")
                self.lbl_coord_y.setText(f"Y: {canvas_center.y():.2f}")
            else:
                self.lbl_coord_x.setText(f"Lon: {canvas_center.x():.4f}")
                self.lbl_coord_y.setText(f"Lat: {canvas_center.y():.4f}")
            self.lbl_north_bearing.setText(f"{self._true_north_bearing:.2f}°")

        # Ensure the marker is visible and force updates
        self.dip_strike_item.setVisible(True)
        self.dip_strike_item.show()  # Explicitly show the item

        # Force immediate canvas refresh to trigger rendering
        self.map_canvas_widget.refresh()
        self.map_canvas_widget.refreshAllLayers()

        # Connect azimuth controls to marker
        self.update_marker_azimuth()

        # Force another refresh after marker setup
        self.map_canvas_widget.refresh()

        # Connect azimuth controls to marker
        self.update_marker_azimuth()

        self.chk_true_north.toggled.connect(self.update_marker_azimuth)

    def update_spinbox_from_dial(self, dial_value):
        """Update the spinbox when dial value changes"""
        azimuth_value = float(dial_value)

        # Temporarily disconnect to avoid circular updates
        self.azimuth_spinbox.valueChanged.disconnect()
        self.azimuth_spinbox.setValue(azimuth_value)
        self.azimuth_spinbox.valueChanged.connect(self.update_dial_from_spinbox)

        # Update the marker
        self.update_marker_azimuth()

    def update_dial_from_spinbox(self, azimuth_value):
        """Update the dial when spinbox value changes"""
        dial_value = int(round(azimuth_value))

        # Temporarily disconnect to avoid circular updates
        self.dial_azimuth.valueChanged.disconnect()
        self.dial_azimuth.setValue(dial_value)
        self.dial_azimuth.valueChanged.connect(self.update_spinbox_from_dial)

        # Update the marker
        self.update_marker_azimuth()

    def on_strike_dip_mode_changed(self):
        """Handle changes in strike/dip radio button selection"""
        self.update_marker_azimuth()

        # Update tooltip and label text based on mode
        if self.rdio_strike.isChecked():
            tooltip_text = "Enter strike azimuth in decimal degrees from North (0.00-360.00°)"
        else:
            tooltip_text = "Enter dip azimuth in decimal degrees from North (0.00-360.00°)"

        self.azimuth_spinbox.setToolTip(QCoreApplication.translate("DlgInsertDipStrike", tooltip_text))

    def update_marker_azimuth(self):
        """Update the marker with current azimuth value"""
        if hasattr(self, "dip_strike_item"):
            azimuth = self.get_azimuth_value()

            # Determine if we're in strike or dip mode
            is_strike_mode = self.rdio_strike.isChecked()

            if is_strike_mode:
                # Azimuth represents strike direction - use directly
                strike_azimuth = azimuth
            else:
                # Azimuth represents dip direction - convert to strike (perpendicular)
                # Dip direction is 90° clockwise from strike direction
                # So strike direction is 90° counter-clockwise from dip direction
                strike_azimuth = (azimuth - 90) % 360

            self.dip_strike_item.setAzimuth(strike_azimuth)
            self.dip_strike_item.setShowStrike(True)
            self.dip_strike_item.setShowDip(True)

            # Refresh the canvas to show changes
            self.map_canvas_widget.refresh()

            is_true_north_adjust_enabled = self.chk_true_north.isChecked()
            adjusted_strike_azimuth = (
                strike_azimuth
                if not is_true_north_adjust_enabled
                else (strike_azimuth - self._true_north_bearing) % 360
            )
            adjusted_dip_azimuth = (
                (strike_azimuth + 90) % 360
                if not is_true_north_adjust_enabled
                else (strike_azimuth + 90 - self._true_north_bearing) % 360
            )
            self.line_strike.setText(f"{adjusted_strike_azimuth:.2f}")
            self.line_dip.setText(f"{adjusted_dip_azimuth:.2f}")

            # self.log(
            #     f"Adjusted azimuth relative to true North: {strike_azimuth - self._true_north_bearing}°", log_level=4
            # )

    def get_azimuth_value(self):
        """Get the current azimuth value as a float"""
        return self.azimuth_spinbox.value()

    def set_azimuth_value(self, value):
        """Set the azimuth value programmatically"""
        value = max(0.0, min(360.0, float(value)))  # Clamp to valid range
        self.azimuth_spinbox.setValue(value)
        # Direct mapping: azimuth value maps directly to dial value
        dial_value = int(round(value))
        self.dial_azimuth.setValue(dial_value)
        self.update_marker_azimuth()

    def update_marker_display(self):
        """Update marker based on current settings"""
        if hasattr(self, "dip_strike_item"):
            # Update azimuth
            self.update_marker_azimuth()

            # Update dip if there's a dip control
            if hasattr(self, "dip_spinbox"):
                dip_value = self.dip_spinbox.value()
                self.dip_strike_item.setDip(dip_value)

            # Force canvas refresh
            self.map_canvas_widget.refresh()

    def closeEvent(self, event):
        """Handle dialog close event to clean up marker"""
        try:
            if hasattr(self, "dip_strike_item") and self.dip_strike_item:
                self.dip_strike_item.cleanup()
                self.log(message="Marker cleaned up on dialog close", log_level=4)
        except Exception as e:
            self.log(message=f"Error cleaning up marker: {e}", log_level=1)

        super().closeEvent(event)

    # def showEvent(self, e):
    #     pass
