from pathlib import Path

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsBearingUtils,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsProject,
    QgsSettings,
)
from qgis.gui import QgisInterface, QgsMapCanvas, QgsMapToolPan
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtWidgets import QDial, QDialog, QDoubleSpinBox, QGraphicsScene, QGraphicsView, QMessageBox, QSizePolicy
from qgis.utils import iface

from ..core.layer_creator import DipStrikeLayerCreator, LayerCreationError
from ..core.rubber_band_marker import RubberBandMarker
from ..toolbelt import PlgLogger

FORM_CLASS, _ = uic.loadUiType(Path(__file__).parent / f"{Path(__file__).stem}.ui")


class DlgInsertDipStrike(QDialog, FORM_CLASS):
    def __init__(self, parent=None, clicked_point=None, existing_feature=None):
        super().__init__(parent)
        self.setupUi(self)

        self.iface: QgisInterface = iface  # type: ignore
        self.log = PlgLogger().log

        # Store existing feature data if provided
        self.existing_feature = existing_feature

        # Store clicked point for creating new features
        self._clicked_point = clicked_point

        # Set dialog title based on whether we're editing existing or creating new
        if self.existing_feature:
            layer_name = self.existing_feature["layer_name"]
            feature_id = self.existing_feature["feature"].id()
            self.setWindowTitle(f"Edit Dip/Strike Data - {layer_name} (Feature {feature_id})")
            # If editing an existing feature, disable the layer selection and new layer creation
            self.cbo_feature_layer.setEnabled(False)
            self.btn_new_layer.setEnabled(False)
        else:
            self.setWindowTitle("Insert New Dip/Strike Point")

        # Flag to prevent saving settings during initialization
        self._initializing = True

        # Store original layer opacity values for restoration on close
        self.original_layer_opacities = {}

        # Set filters for feature layer combobox to only show point layers
        self.cbo_feature_layer.setFilters(Qgis.LayerFilter.PointLayer)
        self.cbo_feature_layer.setLayer(None)
        self.cbo_feature_layer.layerChanged.connect(self.check_feature_layer)

        # Initially disable all optional fields since no layer is selected
        self._disable_all_optional_fields()

        # Layer tools buttons
        self.btn_configure_layer.clicked.connect(self.open_feature_layer_config_dialog)
        # self.btn_configure_layer.setText("⚙")
        self.btn_configure_layer.setIcon(QgsApplication.getThemeIcon("mActionEditTable.svg"))
        self.btn_configure_layer.setToolTip("Configure field mappings for this layer")
        self.btn_configure_layer.setEnabled(False)  # Initially disabled
        self.btn_new_layer.clicked.connect(self.create_new_feature_layer)
        # self.btn_new_layer.setText("+")
        self.btn_new_layer.setIcon(QgsApplication.getThemeIcon("mIconModelInput.svg"))
        self.btn_new_layer.setToolTip("Create a new layer for dip/strike features")

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
        self.rdio_strike.toggled.connect(self._save_ui_settings)
        self.rdio_dip.toggled.connect(self._save_ui_settings)

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
        # self.grp_preview.layout().addWidget(self.map_canvas_widget)
        layout = self.grp_preview.layout()
        layout.insertWidget(0, self.map_canvas_widget)

        self.map_canvas_widget.enableAntiAliasing(True)
        self.map_canvas_widget.setLayers(self.iface.mapCanvas().layers())  # type: ignore
        self.map_canvas_widget.setExtent(self.iface.mapCanvas().extent())  # type: ignore

        # Store original opacity values for all layers
        self.store_original_layer_opacities()

        if clicked_point:
            self.map_canvas_widget.setCenter(clicked_point)
        else:
            self.map_canvas_widget.setCenter(self.map_canvas_widget.extent().center())

        # Zoom in to get a closer view
        self.map_canvas_widget.zoomByFactor(0.25)  # 0.25 = zoom in 4x, 0.1 = zoom in 10x

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
        self.chk_true_north.toggled.connect(self._save_ui_settings)

        # Set icon for opacity label using setPixmap
        icon = QgsApplication.getThemeIcon("mActionIncreaseContrast.svg")
        pixmap = icon.pixmap(16, 16)  # 16x16 pixel size
        self.label_opacity.setPixmap(pixmap)
        self.label_opacity.setToolTip("Layer Opacity")

        # Connect opacity widget to update all layers opacity
        # self.opacity_widget.opacityChanged.connect(self.update_all_layers_opacity)
        self.opacity_slider.valueChanged.connect(self.update_all_layers_opacity)

        # self.grp_optional.setCollapsed(True)
        self._initial_collapse_state = True
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.setMinimumSize(0, 0)
        self.grp_optional.collapsedStateChanged.connect(self._on_optional_group_collapsed)
        self.grp_optional.collapsedStateChanged.connect(self._save_ui_settings)

        # Connect dialog signals to handle cleanup when dialog is closed
        self.accepted.connect(self.cleanup_on_close)
        self.rejected.connect(self.cleanup_on_close)

        # Customize dialog buttons
        self._setup_dialog_buttons()

        # Populate geological types combo box
        self._populate_geological_types()

        # Restore the last used feature layer and UI settings
        self._restore_last_feature_layer()
        self._restore_ui_settings()

        # Initialization complete - now UI settings changes should be saved
        self._initializing = False

        # Load existing feature data if provided
        if self.existing_feature:
            self._load_existing_feature_data()

    def showEvent(self, event):
        """Override showEvent to set initial collapsed state when dialog is shown."""
        super().showEvent(event)

        # Set collapsed state on first show
        if hasattr(self, "_initial_collapse_state") and self._initial_collapse_state is not None:
            self.grp_optional.setCollapsed(self._initial_collapse_state)
            self._initial_collapse_state = None  # Only do this once

            # Force resize after the dialog has been shown
            from qgis.PyQt.QtCore import QTimer

            QTimer.singleShot(100, self.adjustSize)

    def _on_optional_group_collapsed(self, collapsed):
        """Handle QgsCollapsibleGroupBox collapse/expand to resize dialog."""
        from qgis.PyQt.QtCore import QTimer

        # Use a timer to delay the resize until after the animation completes
        QTimer.singleShot(10, self._resize_dialog_after_collapse)

    def _resize_dialog_after_collapse(self):
        """Resize the dialog after group box collapse/expand animation."""
        # Force layout update first
        self.layout().invalidate()
        self.layout().update()

        # Then resize to fit content
        self.adjustSize()

        # Optionally set a minimum height to prevent it from becoming too small
        # if self.grp_optional.isCollapsed():
        #     # When collapsed, ensure minimum reasonable height
        #     min_height = self.sizeHint().height()
        #     if self.height() < min_height:
        #         self.resize(self.width(), min_height)

    def check_feature_layer(self):
        """Check if a feature layer is selected and enable/disable controls accordingly"""
        required_fields = ["strike_azimuth", "dip_azimuth", "dip_value"]
        optional_fields = ["geo_type", "age", "lithology", "notes"]
        layer = self.cbo_feature_layer.currentLayer()

        if layer and layer.isValid():
            # Enable the configure button when a valid layer is selected
            self.btn_configure_layer.setEnabled(True)

            self.log(
                message=f"Selected feature layer: {layer.name()}",
                log_level=4,
            )
            # Check if this is a shapefile first
            is_shapefile = layer.dataProvider().name() == "ogr" and layer.source().lower().endswith(".shp")

            # For shapefiles, check if field mappings are correct regardless of layer role
            if is_shapefile:
                # Check if all required field mappings exist and are valid
                required_fields = ["strike_azimuth", "dip_azimuth", "dip_value"]
                missing_mappings = []

                for field_key in required_fields:
                    mapped_field = layer.customProperty(f"dip_strike_tools/{field_key}", "")
                    if not mapped_field or layer.fields().lookupField(mapped_field) == -1:
                        missing_mappings.append(field_key)

                if missing_mappings:
                    self.log(
                        message=f"Shapefile '{layer.name()}' has missing or invalid field mappings: {', '.join(missing_mappings)}",
                        log_level=4,
                    )
                    self.log(
                        message="Opening field configuration dialog for shapefile",
                        log_level=4,
                    )
                    # Open field config dialog directly for shapefiles (no confirmation needed)
                    from .dlg_field_config import DlgFieldConfig

                    config_dialog = DlgFieldConfig(layer, self)
                    if config_dialog.exec() == DlgFieldConfig.DialogCode.Accepted:
                        self.log(
                            message=f"Field configuration completed for shapefile: {layer.name()}",
                            log_level=3,
                        )
                        # Refresh the geological types combo box in case storage mode changed
                        self._populate_geological_types()
                        # Refresh the layer check to update UI state
                        self.check_feature_layer()
                    else:
                        self.log(
                            message=f"Field configuration cancelled for shapefile: {layer.name()}",
                            log_level=4,
                        )
                    return  # Exit early since we handled the shapefile

            # check if layer is already configured (for non-shapefiles or properly configured shapefiles)
            if not layer.customProperty("dip_strike_tools/layer_role") == "dip_strike_feature_layer":
                self.log(
                    message=f"Layer '{layer.name()}' is not configured for dip/strike features",
                    log_level=4,
                )

                # For non-shapefiles, use original logic
                missing_required_fields = [
                    field for field in required_fields if layer.fields().lookupField(field) == -1
                ]
                present_optional_fields = [
                    field for field in optional_fields if layer.fields().lookupField(field) != -1
                ]

                if not missing_required_fields:
                    # Set custom property to mark layer as configured
                    layer.setCustomProperty("dip_strike_tools/layer_role", "dip_strike_feature_layer")
                    self.log(
                        message=f"Layer '{layer.name()}' configured for dip/strike features",
                        log_level=4,
                    )
                    # Set custom properties to map the fields
                    for field in required_fields:
                        layer.setCustomProperty(f"dip_strike_tools/{field}", field)
                    for field in present_optional_fields:
                        layer.setCustomProperty(f"dip_strike_tools/{field}", field)
                else:
                    self.log(
                        message=f"Layer '{layer.name()}' is missing required fields: {', '.join(missing_required_fields)}",
                        log_level=1,
                    )
                    self.log(
                        message=f"Optional fields present: {', '.join(present_optional_fields)}",
                        log_level=4,
                    )
                    # Automatically open the field mapping dialog if missing required fields
                    self._auto_open_field_config_dialog(layer, missing_required_fields)

            else:
                self.log(
                    message=f"Layer '{layer.name()}' is already configured for dip/strike features",
                    log_level=4,
                )
                # Verify the configuration is still valid
                mapped_fields = []
                for field_key in required_fields + optional_fields:
                    mapped_field = layer.customProperty(f"dip_strike_tools/{field_key}", "")
                    if mapped_field and layer.fields().lookupField(mapped_field) != -1:
                        mapped_fields.append(f"{field_key} → {mapped_field}")

                if mapped_fields:
                    self.log(
                        message=f"Current field mappings: {', '.join(mapped_fields)}",
                        log_level=4,
                    )

            # Update state of optional fields based on mapping configuration
            self._update_optional_fields_state(layer)

        else:
            # Disable the configure button when no layer is selected
            self.btn_configure_layer.setEnabled(False)

            # Disable all optional fields when no layer is selected
            self._disable_all_optional_fields()

            self.log(
                message="No valid feature layer selected",
                log_level=4,
            )

        # Update Save button state based on layer configuration
        current_layer = self.cbo_feature_layer.currentLayer()

        # Save the current layer selection for future use
        self._save_last_feature_layer(current_layer)

        self._update_save_button_state(current_layer)

    def _update_optional_fields_state(self, layer):
        """Update state of optional fields based on layer field mappings.

        :param layer: The layer to check for field mappings
        :type layer: QgsVectorLayer
        """
        # Define mapping between field keys and UI widgets
        field_widgets = {
            "geo_type": self.cbo_geo_type,
            "age": self.line_age,
            "lithology": self.text_litho,
            "notes": self.text_notes,
        }

        enabled_count = 0

        for field_key, widget in field_widgets.items():
            # Check if this optional field is mapped for the current layer
            mapped_field = layer.customProperty(f"dip_strike_tools/{field_key}", "")
            is_mapped = bool(mapped_field and layer.fields().lookupField(mapped_field) != -1)

            # Enable/disable the widget based on mapping status
            widget.setEnabled(is_mapped)

            if is_mapped:
                enabled_count += 1
                # Clear placeholder text for enabled fields
                if hasattr(widget, "setPlaceholderText"):
                    widget.setPlaceholderText("")
                elif hasattr(widget, "setPlainText") and not widget.toPlainText():
                    # For QTextEdit, clear if empty
                    widget.setPlainText("")
                elif widget == self.cbo_geo_type:
                    # For combo box, ensure it's populated normally
                    pass  # TODO: Handle combo box population

                self.log(
                    message=f"Enabled optional field: {field_key} (mapped to '{mapped_field}')",
                    log_level=4,
                )
            else:
                # Set placeholder text for disabled fields
                placeholder_text = "Field not configured for feature layer"
                if hasattr(widget, "setPlaceholderText"):
                    widget.setPlaceholderText(placeholder_text)
                elif hasattr(widget, "setPlainText"):
                    # For QTextEdit, clear content when disabled
                    widget.setPlainText("")
                elif widget == self.cbo_geo_type:
                    # For combo box, clear items and add placeholder item
                    widget.clear()
                    widget.addItem(placeholder_text)

                self.log(
                    message=f"Disabled optional field: {field_key} (not mapped)",
                    log_level=4,
                )

        # The Optional Data group box remains always visible
        # self.groupBox_3.setVisible(True)

        self.log(
            message=f"Optional Data section: {enabled_count} field(s) enabled, {len(field_widgets) - enabled_count} disabled",
            log_level=4,
        )

    def _load_existing_feature_data(self):
        """Load data from existing feature into the dialog controls.

        Populates the azimuth, dip, and optional fields with values from the
        existing feature if field mappings are configured properly.
        """
        if not self.existing_feature:
            return

        feature = self.existing_feature["feature"]
        layer = self.existing_feature["layer"]

        self.log(
            message=f"Loading existing feature data from layer '{layer.name()}' (Feature ID: {feature.id()})",
            log_level=3,
        )

        try:
            # Get field mappings from layer custom properties
            strike_azimuth_field = layer.customProperty("dip_strike_tools/strike_azimuth", "")
            dip_azimuth_field = layer.customProperty("dip_strike_tools/dip_azimuth", "")
            dip_value_field = layer.customProperty("dip_strike_tools/dip_value", "")

            # Optional fields
            geo_type_field = layer.customProperty("dip_strike_tools/geo_type", "")
            age_field = layer.customProperty("dip_strike_tools/age", "")
            lithology_field = layer.customProperty("dip_strike_tools/lithology", "")
            notes_field = layer.customProperty("dip_strike_tools/notes", "")

            # First, set the layer in the combo box to enable proper field mapping
            self.cbo_feature_layer.setLayer(layer)

            # Load strike azimuth value
            if strike_azimuth_field and layer.fields().lookupField(strike_azimuth_field) != -1:
                strike_value = feature[strike_azimuth_field]
                if strike_value is not None:
                    try:
                        strike_azimuth = float(strike_value)
                        # Set radio button to strike mode
                        self.rdio_strike.setChecked(True)
                        # Set the azimuth value (this will trigger dial and spinbox updates)
                        self.azimuth_spinbox.setValue(strike_azimuth)
                        self.log(message=f"Loaded strike azimuth: {strike_azimuth}°", log_level=4)
                    except (ValueError, TypeError) as e:
                        self.log(message=f"Error parsing strike azimuth value '{strike_value}': {e}", log_level=2)

            # Load dip azimuth value (alternative to strike)
            elif dip_azimuth_field and layer.fields().lookupField(dip_azimuth_field) != -1:
                dip_azimuth_value = feature[dip_azimuth_field]
                if dip_azimuth_value is not None:
                    try:
                        dip_azimuth = float(dip_azimuth_value)
                        # Set radio button to dip mode
                        self.rdio_dip.setChecked(True)
                        # Set the azimuth value (this will trigger dial and spinbox updates)
                        self.azimuth_spinbox.setValue(dip_azimuth)
                        self.log(message=f"Loaded dip azimuth: {dip_azimuth}°", log_level=4)
                    except (ValueError, TypeError) as e:
                        self.log(message=f"Error parsing dip azimuth value '{dip_azimuth_value}': {e}", log_level=2)

            # Load dip value
            if dip_value_field and layer.fields().lookupField(dip_value_field) != -1:
                dip_val = feature[dip_value_field]
                if dip_val is not None:
                    try:
                        dip_value = float(dip_val)
                        self.spin_dip.setValue(dip_value)
                        self.log(message=f"Loaded dip value: {dip_value}°", log_level=4)
                    except (ValueError, TypeError) as e:
                        self.log(message=f"Error parsing dip value '{dip_val}': {e}", log_level=2)

            # Load optional fields if they exist and are mapped
            # Geological Type
            if geo_type_field and layer.fields().lookupField(geo_type_field) != -1 and hasattr(self, "cbo_geo_type"):
                geo_type_value = feature[geo_type_field]
                if geo_type_value:
                    # Try to find the item by data first (for code values)
                    index = -1
                    for i in range(self.cbo_geo_type.count()):
                        if self.cbo_geo_type.itemData(i) == str(geo_type_value):
                            index = i
                            break

                    # If not found by data, try by text (for description values)
                    if index == -1:
                        index = self.cbo_geo_type.findText(str(geo_type_value))

                    if index >= 0:
                        self.cbo_geo_type.setCurrentIndex(index)
                        self.log(message=f"Loaded geological type: {geo_type_value}", log_level=4)
                    else:
                        # Add the value if it's not in the list (fallback for custom values)
                        self.cbo_geo_type.addItem(str(geo_type_value), str(geo_type_value))
                        self.cbo_geo_type.setCurrentText(str(geo_type_value))

            # Age
            if age_field and layer.fields().lookupField(age_field) != -1 and hasattr(self, "line_age"):
                age_value = feature[age_field]
                if age_value:
                    self.line_age.setText(str(age_value))
                    self.log(message=f"Loaded age: {age_value}", log_level=4)

            # Lithology
            if lithology_field and layer.fields().lookupField(lithology_field) != -1 and hasattr(self, "text_litho"):
                lithology_value = feature[lithology_field]
                if lithology_value:
                    self.text_litho.setPlainText(str(lithology_value))
                    self.log(message=f"Loaded lithology: {lithology_value}", log_level=4)

            # Notes
            if notes_field and layer.fields().lookupField(notes_field) != -1 and hasattr(self, "text_notes"):
                notes_value = feature[notes_field]
                if notes_value:
                    self.text_notes.setPlainText(str(notes_value))
                    self.log(
                        message=f"Loaded notes: {str(notes_value)[:50]}{'...' if len(str(notes_value)) > 50 else ''}",
                        log_level=4,
                    )

            # Update the map display with the loaded values
            self.on_strike_dip_mode_changed()

            # Show user feedback that existing data was loaded
            self.log(message=f"Successfully loaded existing feature data from '{layer.name()}'", log_level=3)

        except Exception as e:
            self.log(message=f"Error loading existing feature data: {e}", log_level=1)

    def _disable_all_optional_fields(self):
        """Disable all optional fields and show placeholder text."""
        # Define all optional field widgets
        field_widgets = {
            "geo_type": self.cbo_geo_type,
            "age": self.line_age,
            "lithology": self.text_litho,
            "notes": self.text_notes,
        }

        # Disable all widgets and set placeholder text
        for field_key, widget in field_widgets.items():
            widget.setEnabled(False)
            placeholder_text = "No layer selected"

            if hasattr(widget, "setPlaceholderText"):
                widget.setPlaceholderText(placeholder_text)
            elif hasattr(widget, "setPlainText"):
                # For QTextEdit, clear content
                widget.setPlainText("")
            elif widget == self.cbo_geo_type:
                # For combo box, clear and add placeholder item
                widget.clear()
                widget.addItem(placeholder_text)

        # Keep the Optional Data group box visible for consistent layout
        # self.groupBox_3.setVisible(True)

        self.log(
            message="All optional fields disabled (no layer selected)",
            log_level=4,
        )

    def _setup_dialog_buttons(self):
        """Setup dialog buttons with custom text and initial state."""
        # Get reference to OK button and rename it based on whether editing existing feature
        self.save_button = self.buttonBox.button(self.buttonBox.StandardButton.Ok)
        if self.save_button:
            if self.existing_feature:
                self.save_button.setText("Update")
                self.save_button.setToolTip("Update existing dip/strike data in the selected feature layer")
            else:
                self.save_button.setText("Save")
                self.save_button.setToolTip("Save dip/strike data to the selected feature layer")
            # Initially disable the Save button since no layer is configured
            self.save_button.setEnabled(False)
            self.log(
                message="Save button initialized and disabled (no layer configured)",
                log_level=4,
            )

        # Get reference to Cancel button for consistency
        self.cancel_button = self.buttonBox.button(self.buttonBox.StandardButton.Cancel)
        if self.cancel_button:
            self.cancel_button.setToolTip("Cancel and close dialog without saving")

    def _save_last_feature_layer(self, layer):
        """Save the currently selected feature layer to settings for future use.

        :param layer: The layer to remember
        :type layer: QgsVectorLayer or None
        """
        settings = QgsSettings()
        settings.beginGroup("dip_strike_tools")

        # Get the currently saved layer ID to avoid unnecessary writes
        current_saved_id = settings.value("last_feature_layer_id", "")

        if layer and layer.isValid():
            # Only save if the layer has actually changed
            if layer.id() != current_saved_id:
                # Save both layer ID and name for better recovery
                settings.setValue("last_feature_layer_id", layer.id())
                settings.setValue("last_feature_layer_name", layer.name())

                self.log(
                    message=f"Saved last used feature layer: {layer.name()} (ID: {layer.id()})",
                    log_level=4,
                )
        else:
            # Clear the saved layer if None is selected (only if something was saved before)
            if current_saved_id:
                settings.remove("last_feature_layer_id")
                settings.remove("last_feature_layer_name")

                self.log(
                    message="Cleared saved feature layer (no layer selected)",
                    log_level=4,
                )

        settings.endGroup()

    def _restore_last_feature_layer(self):
        """Restore the last used feature layer from settings if it still exists."""
        settings = QgsSettings()
        settings.beginGroup("dip_strike_tools")

        last_layer_id = settings.value("last_feature_layer_id", "")
        last_layer_name = settings.value("last_feature_layer_name", "")

        settings.endGroup()

        if not last_layer_id:
            self.log(
                message="No previously used feature layer found in settings",
                log_level=4,
            )
            return

        # Try to find the layer by ID first (most reliable)
        project = QgsProject.instance()
        if not project:
            self.log(
                message="No QGIS project instance available",
                log_level=2,
            )
            return

        all_layers = project.mapLayers()
        target_layer = None

        # First try to find by exact ID match
        if last_layer_id in all_layers:
            layer = all_layers[last_layer_id]
            # Verify it's still a point layer
            if layer.geometryType() == 0:  # Point geometry
                target_layer = layer
                self.log(
                    message=f"Found last used layer by ID: {layer.name()} (ID: {layer.id()})",
                    log_level=4,
                )

        # If not found by ID, try to find by name as fallback
        if not target_layer and last_layer_name:
            for layer_id, layer in all_layers.items():
                if layer.name() == last_layer_name and layer.geometryType() == 0:  # Point geometry
                    target_layer = layer
                    self.log(
                        message=f"Found last used layer by name: {layer.name()} (ID: {layer.id()})",
                        log_level=4,
                    )
                    break

        if target_layer:
            # Set the layer in the combo box
            self.cbo_feature_layer.setLayer(target_layer)
            self.log(
                message=f"Restored last used feature layer: {target_layer.name()}",
                log_level=3,
            )
        else:
            self.log(
                message=f"Last used feature layer '{last_layer_name}' (ID: {last_layer_id}) no longer exists",
                log_level=4,
            )
            # Clear the saved settings since the layer no longer exists
            self._save_last_feature_layer(None)

    def _save_ui_settings(self):
        """Save UI settings to QSettings for future use."""
        # Don't save settings during initialization
        if getattr(self, "_initializing", True):
            return

        settings = QgsSettings()
        settings.beginGroup("dip_strike_tools")

        # Save the true north checkbox state
        settings.setValue("true_north_enabled", self.chk_true_north.isChecked())

        # Save the optional group box collapsed state
        settings.setValue("optional_group_collapsed", self.grp_optional.isCollapsed())

        # Save the strike/dip mode selection
        settings.setValue("strike_mode_selected", self.rdio_strike.isChecked())

        settings.endGroup()

        self.log(
            message=f"Saved UI settings - True North: {self.chk_true_north.isChecked()}, Optional Group Collapsed: {self.grp_optional.isCollapsed()}, Strike Mode: {self.rdio_strike.isChecked()}",
            log_level=4,
        )

    def _restore_ui_settings(self):
        """Restore UI settings from QSettings."""
        settings = QgsSettings()
        settings.beginGroup("dip_strike_tools")

        # Restore the true north checkbox state (default to True if not found)
        true_north_enabled = settings.value("true_north_enabled", True, type=bool)

        # Restore the optional group box collapsed state (default to True if not found)
        optional_group_collapsed = settings.value("optional_group_collapsed", True, type=bool)

        # Restore the strike/dip mode selection (default to strike mode if not found)
        strike_mode_selected = settings.value("strike_mode_selected", True, type=bool)

        # Clean up old settings that are no longer saved
        old_settings = ["last_azimuth_value", "last_dip_value"]
        for old_setting in old_settings:
            if settings.contains(old_setting):
                settings.remove(old_setting)
                self.log(
                    message=f"Removed old UI setting: {old_setting}",
                    log_level=4,
                )

        settings.endGroup()

        # Temporarily disconnect signals to avoid triggering update events during restoration
        self.chk_true_north.toggled.disconnect()
        self.rdio_strike.toggled.disconnect()
        self.rdio_dip.toggled.disconnect()

        # Restore the true north checkbox value
        self.chk_true_north.setChecked(true_north_enabled)

        # Restore the strike/dip mode selection
        self.rdio_strike.setChecked(strike_mode_selected)
        self.rdio_dip.setChecked(not strike_mode_selected)

        # Store the collapsed state to be applied in showEvent
        self._initial_collapse_state = optional_group_collapsed

        # Reconnect the signals
        self.chk_true_north.toggled.connect(self.update_marker_azimuth)
        self.chk_true_north.toggled.connect(self._save_ui_settings)
        self.rdio_strike.toggled.connect(self.on_strike_dip_mode_changed)
        self.rdio_dip.toggled.connect(self.on_strike_dip_mode_changed)
        self.rdio_strike.toggled.connect(self._save_ui_settings)
        self.rdio_dip.toggled.connect(self._save_ui_settings)

        # Update the marker to reflect the restored strike/dip mode
        self.update_marker_azimuth()

        self.log(
            message=f"Restored UI settings - True North: {true_north_enabled}, Optional Group Collapsed: {optional_group_collapsed}, Strike Mode: {strike_mode_selected}",
            log_level=4,
        )

    def _update_save_button_state(self, layer):
        """Update the save button state based on layer configuration.

        :param layer: The layer to check
        :type layer: QgsVectorLayer or None
        """
        if not hasattr(self, "save_button") or not self.save_button:
            return

        if not layer or not layer.isValid():
            self.save_button.setEnabled(False)
            self.log(
                message="Save button disabled (no valid layer selected)",
                log_level=4,
            )
            return

        # Check if layer is configured for dip/strike tools
        is_configured = layer.customProperty("dip_strike_tools/layer_role") == "dip_strike_feature_layer"

        if is_configured:
            # Verify required field mappings exist
            required_fields = ["strike_azimuth", "dip_azimuth", "dip_value"]
            all_required_mapped = True

            for field_key in required_fields:
                field_name = layer.customProperty(f"dip_strike_tools/{field_key}", "")
                if not field_name or layer.fields().lookupField(field_name) == -1:
                    all_required_mapped = False
                    break

            if all_required_mapped:
                self.save_button.setEnabled(True)
                self.log(
                    message=f"Save button enabled (layer '{layer.name()}' is properly configured)",
                    log_level=4,
                )
            else:
                self.save_button.setEnabled(False)
                self.log(
                    message=f"Save button disabled (layer '{layer.name()}' missing required field mappings)",
                    log_level=4,
                )
        else:
            self.save_button.setEnabled(False)
            self.log(
                message=f"Save button disabled (layer '{layer.name()}' not configured for dip/strike tools)",
                log_level=4,
            )

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
            self.lbl_strike_dir.setText(f"{adjusted_strike_azimuth:.2f}°")
            self.lbl_dip_dir.setText(f"{adjusted_dip_azimuth:.2f}°")
            msg_true_north = self.tr("* Azimuth value relative to true North")
            msg_top_map = self.tr("* Azimuth value relative to top of the map/screen")
            self.label_true_north_relative.setText(
                f"{msg_true_north if is_true_north_adjust_enabled else msg_top_map}"
            )

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

    def cleanup_on_close(self):
        """Handle cleanup when dialog is closed via OK/Cancel buttons"""
        self.log(message="Dialog closed via OK/Cancel - performing cleanup", log_level=4)
        try:
            # Restore original layer opacities before closing
            self.restore_original_layer_opacities()

            # Clean up the marker
            if hasattr(self, "dip_strike_item") and self.dip_strike_item:
                self.dip_strike_item.cleanup()
                self.log(message="Marker cleaned up on dialog close", log_level=4)
        except Exception as e:
            self.log(message=f"Error during dialog cleanup: {e}", log_level=1)

    def closeEvent(self, event):
        """Handle dialog close event (when closed via window close button)"""
        self.log(message="Dialog closed via window close button - performing cleanup", log_level=4)
        self.cleanup_on_close()
        super().closeEvent(event)

    def store_original_layer_opacities(self):
        """Store the original opacity values of all layers for restoration on close"""
        try:
            layers = self.map_canvas_widget.layers()
            if not layers:
                self.log(
                    message="No layers found to store opacity values for",
                    log_level=4,
                )
                return

            for layer in layers:
                if hasattr(layer, "opacity"):
                    layer_id = layer.id()
                    original_opacity = layer.opacity()
                    self.original_layer_opacities[layer_id] = original_opacity
                    self.log(
                        message=f"Stored original opacity for layer '{layer.name()}': {original_opacity * 100:.1f}%",
                        log_level=4,
                    )

            self.log(
                message=f"Stored original opacity values for {len(self.original_layer_opacities)} layers",
                log_level=4,
            )
        except Exception as e:
            self.log(
                message=f"Error storing original layer opacities: {e}",
                log_level=1,
            )

    def restore_original_layer_opacities(self):
        """Restore the original opacity values of all layers"""
        try:
            if not self.original_layer_opacities:
                self.log(
                    message="No original opacity values stored, skipping restoration",
                    log_level=4,
                )
                return

            layers = self.map_canvas_widget.layers()
            restored_count = 0

            for layer in layers:
                if hasattr(layer, "setOpacity") and hasattr(layer, "id"):
                    layer_id = layer.id()
                    if layer_id in self.original_layer_opacities:
                        original_opacity = self.original_layer_opacities[layer_id]
                        layer.setOpacity(original_opacity)
                        restored_count += 1
                        self.log(
                            message=f"Restored opacity for layer '{layer.name()}' to {original_opacity * 100:.1f}%",
                            log_level=4,
                        )

            if restored_count > 0:
                # Refresh the canvas to show the changes
                self.map_canvas_widget.refresh()
                self.log(
                    message=f"Restored original opacity values for {restored_count} layers",
                    log_level=4,
                )
        except Exception as e:
            self.log(
                message=f"Error restoring original layer opacities: {e}",
                log_level=1,
            )

    def update_all_layers_opacity(self, opacity_value):
        """Update opacity for all layers in the map canvas"""
        opacity_value = opacity_value / 100.0  # Convert from percentage (0-100) to 0-1 range
        try:
            # Get all layers from the map canvas
            layers = self.map_canvas_widget.layers()

            # Update opacity for each layer
            for layer in layers:
                if hasattr(layer, "setOpacity"):
                    layer.setOpacity(opacity_value)  # Use the original value (0-1 range)

            # Refresh the canvas to show the changes
            self.map_canvas_widget.refresh()

        except Exception as e:
            self.log(
                message=f"Error updating layer opacity: {e}",
                log_level=1,
            )

    def open_feature_layer_config_dialog(self):
        """Open a dialog to configure the selected feature layer.

        This method opens a field configuration dialog that allows users to map
        the layer's actual field names to the required and optional fields needed
        for dip/strike features:

        Required fields:
        - strike_azimuth: Field containing strike azimuth values
        - dip_azimuth: Field containing dip azimuth values
        - dip_value: Field containing dip angle values

        Optional fields:
        - geo_type: Geological type information
        - age: Age/period information
        - lithology: Rock type/lithology information
        - notes: Additional notes or comments

        The configuration is saved as custom properties on the layer.
        """
        layer = self.cbo_feature_layer.currentLayer()
        if not layer or not layer.isValid():
            self.log(
                message="No valid feature layer selected for configuration",
                log_level=1,
            )
            return

        # Import the field configuration dialog
        from .dlg_field_config import DlgFieldConfig

        # Open the configuration dialog
        config_dialog = DlgFieldConfig(layer, self)
        if config_dialog.exec() == DlgFieldConfig.DialogCode.Accepted:
            self.log(
                message=f"Field configuration saved for layer: {layer.name()}",
                log_level=3,
            )
            # Refresh the geological types combo box in case storage mode changed
            self._populate_geological_types()
            # Refresh the layer check to update UI state and field visibility
            self.check_feature_layer()
        else:
            self.log(
                message="Field configuration cancelled",
                log_level=4,
            )

    def _auto_open_field_config_dialog(self, layer, missing_fields):
        """Automatically open field configuration dialog for layers missing required fields.

        :param layer: The layer that needs configuration
        :type layer: QgsVectorLayer
        :param missing_fields: List of missing required field names
        :type missing_fields: list
        """
        # Show informative message to user about why the dialog is opening
        reply = QMessageBox.question(
            self,
            "Layer Configuration Required",
            f"The selected layer '{layer.name()}' is missing required fields for dip/strike data:\n\n"
            f"Missing fields: {', '.join(missing_fields)}\n\n"
            f"Would you like to configure field mappings now?\n\n"
            f"This will allow you to map existing layer fields to the required dip/strike fields.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.Yes:
            self.log(
                message=f"Auto-opening field configuration dialog for layer: {layer.name()}",
                log_level=3,
            )

            # Import and open the field configuration dialog
            from .dlg_field_config import DlgFieldConfig

            config_dialog = DlgFieldConfig(layer, self)
            if config_dialog.exec() == DlgFieldConfig.DialogCode.Accepted:
                self.log(
                    message=f"Auto-configuration completed for layer: {layer.name()}",
                    log_level=3,
                )
                # Refresh the geological types combo box in case storage mode changed
                self._populate_geological_types()
                # Refresh the layer check to update UI state and field visibility after configuration
                self.check_feature_layer()
            else:
                self.log(
                    message=f"Auto-configuration cancelled for layer: {layer.name()}",
                    log_level=4,
                )
        else:
            self.log(
                message=f"User declined auto-configuration for layer: {layer.name()}",
                log_level=4,
            )

    def create_new_feature_layer(self):
        """Create a new feature layer for dip/strike features using the layer creation dialog."""
        self.log(
            message="Opening layer creation dialog",
            log_level=4,
        )

        # Import the layer creation dialog
        from .dlg_create_layer import DlgCreateLayer

        # Open the layer creation dialog
        create_dialog = DlgCreateLayer(self)
        if create_dialog.exec() != DlgCreateLayer.DialogCode.Accepted:
            self.log(
                message="Layer creation cancelled by user",
                log_level=4,
            )
            return

        # Get the layer configuration from the dialog
        config = create_dialog.get_layer_config()

        try:
            # Get the CRS from the configuration (selected in the dialog)
            crs = config.get("crs")
            if not crs or not crs.isValid():
                # Fallback to map canvas CRS if no valid CRS in config
                crs = self.iface.mapCanvas().mapSettings().destinationCrs()
                self.log(
                    message="No valid CRS in config, using map canvas CRS as fallback",
                    log_level=2,
                )

            # Create the layer using the layer creator with full configuration support
            layer_creator = DipStrikeLayerCreator()
            layer = layer_creator.create_dip_strike_layer(config, crs)

            if layer is None or not layer.isValid():
                raise LayerCreationError("Failed to create layer")

            # Note: Layer is already added to project and configured by create_dip_strike_layer

            # Select the new layer in the combo box
            self.cbo_feature_layer.setLayer(layer)

            # Refresh the geological types combo box
            self._populate_geological_types()

            # Save this layer as the last used layer
            self._save_last_feature_layer(layer)

            # Check the layer to update UI state
            self.check_feature_layer()

            self.log(
                message=f"Successfully created and configured layer: {layer.name()}",
                log_level=3,
            )

        except LayerCreationError as e:
            self.log(
                message=f"Layer creation error: {e}",
                log_level=1,
            )
            QMessageBox.critical(self, "Error", f"Failed to create layer:\n{str(e)}")
        except Exception as e:
            self.log(
                message=f"Unexpected error creating feature layer: {e}",
                log_level=1,
            )
            QMessageBox.critical(self, "Error", f"Unexpected error creating layer:\n{str(e)}")

    def accept(self):
        """Handle save/update button click - save feature data to the selected layer."""
        try:
            # Get the selected layer
            layer = self.cbo_feature_layer.currentLayer()
            if not layer or not layer.isValid():
                self.log(message="No valid layer selected for saving", log_level=1)
                return

            # Log layer information for debugging multi-layer GeoPackage issues
            self.log(
                message=f"Using layer for feature insertion: '{layer.name()}' (ID: {layer.id()}, Source: {layer.source()})",
                log_level=4,
            )

            # Get field mappings from layer custom properties
            strike_azimuth_field = layer.customProperty("dip_strike_tools/strike_azimuth", "")
            dip_azimuth_field = layer.customProperty("dip_strike_tools/dip_azimuth", "")
            dip_value_field = layer.customProperty("dip_strike_tools/dip_value", "")

            # Optional fields
            geo_type_field = layer.customProperty("dip_strike_tools/geo_type", "")
            age_field = layer.customProperty("dip_strike_tools/age", "")
            lithology_field = layer.customProperty("dip_strike_tools/lithology", "")
            notes_field = layer.customProperty("dip_strike_tools/notes", "")

            # Check if required fields are mapped
            required_fields = ["strike_azimuth", "dip_azimuth", "dip_value"]
            missing_required = []
            for field_key in required_fields:
                field_name = layer.customProperty(f"dip_strike_tools/{field_key}", "")
                if not field_name or layer.fields().lookupField(field_name) == -1:
                    missing_required.append(field_key)

            if missing_required:
                self.log(
                    message=f"Cannot save: layer '{layer.name()}' is missing required field mappings: {', '.join(missing_required)}",
                    log_level=1,
                )
                return

            # Get values from UI controls
            raw_azimuth_value = self.azimuth_spinbox.value()
            dip_value = self.spin_dip.value()

            # Get adjusted azimuth values (accounting for true north bearing)
            adjusted_strike_azimuth, adjusted_dip_azimuth = self.get_adjusted_azimuth_values()

            self.log(
                message=f"Saving values - Raw azimuth: {raw_azimuth_value}°, Adjusted strike: {adjusted_strike_azimuth:.2f}°, Adjusted dip: {adjusted_dip_azimuth:.2f}°, Dip value: {dip_value}°",
                log_level=4,
            )

            # Get optional field values
            geo_type_value = None
            if geo_type_field and hasattr(self, "cbo_geo_type"):
                # Use currentData() to get the stored value (code or description based on storage mode)
                geo_type_value = self.cbo_geo_type.currentData()
                if (
                    geo_type_value == "Field not configured for feature layer"
                    or not geo_type_value
                    or not str(geo_type_value).strip()
                ):
                    geo_type_value = None

            age_value = None
            if age_field and hasattr(self, "line_age"):
                age_value = self.line_age.text().strip()
                if not age_value:
                    age_value = None

            lithology_value = None
            if lithology_field and hasattr(self, "text_litho"):
                lithology_value = self.text_litho.toPlainText().strip()
                if not lithology_value:
                    lithology_value = None

            notes_value = None
            if notes_field and hasattr(self, "text_notes"):
                notes_value = self.text_notes.toPlainText().strip()
                if not notes_value:
                    notes_value = None

            # Start editing the layer
            if not layer.isEditable():
                layer.startEditing()

            if self.existing_feature:
                # Update existing feature
                feature = self.existing_feature["feature"]
                feature_id = feature.id()

                self.log(message=f"Updating existing feature {feature_id} in layer '{layer.name()}'", log_level=3)

                # Update field values
                changes = {}

                # Save both azimuth values regardless of mode
                if strike_azimuth_field:
                    field_idx = layer.fields().lookupField(strike_azimuth_field)
                    if field_idx != -1:
                        changes[field_idx] = adjusted_strike_azimuth

                if dip_azimuth_field:
                    field_idx = layer.fields().lookupField(dip_azimuth_field)
                    if field_idx != -1:
                        changes[field_idx] = adjusted_dip_azimuth

                # Set dip value
                if dip_value_field:
                    field_idx = layer.fields().lookupField(dip_value_field)
                    if field_idx != -1:
                        changes[field_idx] = dip_value

                # Set optional fields
                if geo_type_field and geo_type_value is not None:
                    field_idx = layer.fields().lookupField(geo_type_field)
                    if field_idx != -1:
                        changes[field_idx] = geo_type_value

                if age_field and age_value is not None:
                    field_idx = layer.fields().lookupField(age_field)
                    if field_idx != -1:
                        changes[field_idx] = age_value

                if lithology_field and lithology_value is not None:
                    field_idx = layer.fields().lookupField(lithology_field)
                    if field_idx != -1:
                        changes[field_idx] = lithology_value

                if notes_field and notes_value is not None:
                    field_idx = layer.fields().lookupField(notes_field)
                    if field_idx != -1:
                        changes[field_idx] = notes_value

                # Apply changes
                if changes:
                    success = layer.changeAttributeValues(feature_id, changes)
                    if success:
                        self.log(
                            message=f"Successfully updated feature {feature_id} with {len(changes)} field changes. Strike: {adjusted_strike_azimuth:.2f}°, Dip azimuth: {adjusted_dip_azimuth:.2f}°, Dip value: {dip_value}°",
                            log_level=3,
                        )
                    else:
                        self.log(message=f"Failed to update feature {feature_id}", log_level=1)
                        return

            else:
                # Create new feature
                from qgis.core import QgsCoordinateTransform, QgsFeature, QgsGeometry

                # Get the clicked point (should be stored from when dialog was created)
                if hasattr(self, "_clicked_point") and self._clicked_point:
                    point_to_use = self._clicked_point
                    # Get map canvas CRS
                    canvas_crs = self.iface.mapCanvas().mapSettings().destinationCrs()
                    layer_crs = layer.crs()

                    # Transform point to layer CRS if needed
                    if canvas_crs != layer_crs:
                        project = QgsProject.instance()
                        transform = QgsCoordinateTransform(canvas_crs, layer_crs, project)
                        try:
                            point_to_use = transform.transform(self._clicked_point)
                            self.log(
                                message=f"Transformed new feature point from {canvas_crs.authid()} to {layer_crs.authid()}: {self._clicked_point} -> {point_to_use}",
                                log_level=4,
                            )
                        except Exception as e:
                            self.log(message=f"Error transforming coordinates for new feature: {e}", log_level=2)
                            return

                    geometry = QgsGeometry.fromPointXY(point_to_use)
                else:
                    # Fallback to map canvas center if no clicked point
                    center = self.map_canvas_widget.center()
                    geometry = QgsGeometry.fromPointXY(center)

                self.log(
                    message=f"Creating new feature in layer '{layer.name()}' (ID: {layer.id()}) at {geometry.asPoint()}",
                    log_level=3,
                )

                # Create new feature
                feature = QgsFeature(layer.fields())
                feature.setGeometry(geometry)

                # Set field values - save both azimuth values regardless of mode
                if strike_azimuth_field:
                    field_idx = layer.fields().lookupField(strike_azimuth_field)
                    if field_idx != -1:
                        feature.setAttribute(field_idx, adjusted_strike_azimuth)

                if dip_azimuth_field:
                    field_idx = layer.fields().lookupField(dip_azimuth_field)
                    if field_idx != -1:
                        feature.setAttribute(field_idx, adjusted_dip_azimuth)

                # Set dip value
                if dip_value_field:
                    field_idx = layer.fields().lookupField(dip_value_field)
                    if field_idx != -1:
                        feature.setAttribute(field_idx, dip_value)

                # Set optional fields
                if geo_type_field and geo_type_value is not None:
                    field_idx = layer.fields().lookupField(geo_type_field)
                    if field_idx != -1:
                        feature.setAttribute(field_idx, geo_type_value)

                if age_field and age_value is not None:
                    field_idx = layer.fields().lookupField(age_field)
                    if field_idx != -1:
                        feature.setAttribute(field_idx, age_value)

                if lithology_field and lithology_value is not None:
                    field_idx = layer.fields().lookupField(lithology_field)
                    if field_idx != -1:
                        feature.setAttribute(field_idx, lithology_value)

                if notes_field and notes_value is not None:
                    field_idx = layer.fields().lookupField(notes_field)
                    if field_idx != -1:
                        feature.setAttribute(field_idx, notes_value)

                # Add feature to layer
                success = layer.addFeature(feature)
                if success:
                    self.log(
                        message=f"Successfully created new feature in layer '{layer.name()}'. Strike: {adjusted_strike_azimuth:.2f}°, Dip azimuth: {adjusted_dip_azimuth:.2f}°, Dip value: {dip_value}°",
                        log_level=3,
                    )
                else:
                    self.log(message=f"Failed to create new feature in layer '{layer.name()}'", log_level=1)
                    return

            # Commit changes and refresh
            if layer.isEditable():
                layer.commitChanges()

            # Refresh the layer
            layer.triggerRepaint()

            # Update map canvas
            self.iface.mapCanvas().refresh()

            # Call parent accept to close dialog
            super().accept()

        except Exception as e:
            self.log(message=f"Error saving feature data: {e}", log_level=1)

    def get_adjusted_azimuth_values(self):
        """Get the current azimuth values adjusted for true north bearing.

        Returns:
            tuple: (strike_azimuth, dip_azimuth) both adjusted for true north if enabled
        """
        azimuth = self.get_azimuth_value()
        is_strike_mode = self.rdio_strike.isChecked()

        if is_strike_mode:
            # Azimuth represents strike direction - use directly
            strike_azimuth = azimuth
        else:
            # Azimuth represents dip direction - convert to strike (perpendicular)
            # Dip direction is 90° clockwise from strike direction
            # So strike direction is 90° counter-clockwise from dip direction
            strike_azimuth = (azimuth - 90) % 360

        # Apply true north adjustment if enabled
        is_true_north_adjust_enabled = self.chk_true_north.isChecked()
        adjusted_strike_azimuth = (
            strike_azimuth if not is_true_north_adjust_enabled else (strike_azimuth - self._true_north_bearing) % 360
        )
        adjusted_dip_azimuth = (
            (strike_azimuth + 90) % 360
            if not is_true_north_adjust_enabled
            else (strike_azimuth + 90 - self._true_north_bearing) % 360
        )

        return adjusted_strike_azimuth, adjusted_dip_azimuth

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def _populate_geological_types(self):
        """Populate the geological types combo box with values from preferences."""
        try:
            from ..toolbelt.preferences import PlgOptionsManager

            # Get geological types from preferences
            geo_types = PlgOptionsManager.get_geological_types()
            storage_mode = PlgOptionsManager.get_geo_type_storage_mode()

            # Clear existing items
            if hasattr(self, "cbo_geo_type"):
                self.cbo_geo_type.clear()

                # Add empty item first
                self.cbo_geo_type.addItem("", "")  # Empty option

                # Add geological types based on storage mode
                for code, description in geo_types.items():
                    if storage_mode == "code":
                        # Display description but store code
                        self.cbo_geo_type.addItem(description, code)
                    else:
                        # Display and store description
                        self.cbo_geo_type.addItem(description, description)

                self.log(
                    f"Populated geological types combo box with {len(geo_types)} items (mode: {storage_mode})",
                    log_level=4,
                )

        except Exception as e:
            self.log(f"Error populating geological types: {e}", log_level=1)
            # Fallback to default items if there's an error
            if hasattr(self, "cbo_geo_type"):
                self.cbo_geo_type.clear()
                self.cbo_geo_type.addItem("", "")
                self.cbo_geo_type.addItem("Strata", "1")
                self.cbo_geo_type.addItem("Foliation", "2")
                self.cbo_geo_type.addItem("Fault", "3")
                self.cbo_geo_type.addItem("Joint", "4")
                self.cbo_geo_type.addItem("Cleavage", "5")
