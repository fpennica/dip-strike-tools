# Data Insertion and Management

The plugin's primary data collection tool allows you to click anywhere on the map to insert or edit dip/strike measurements.

## Interactive Point Tool

1. **Access the Tool**: Click the plugin's main toolbar button or use the menu item
2. **Click on Map**: Click at any location where you want to record a measurement
3. **Enter Data**: The data entry dialog opens automatically with the clicked coordinates
4. **Target Layer Selection**: The plugin automatically selects the most appropriate target layer - either the last used layer, or the layer containing an existing point near your click location. If the selected layer lacks proper field configuration, the plugin will prompt you to configure it.

:::{tip}
**Feature Highlighting**: When using the point tool, the plugin will automatically highlight existing point features that are close to your mouse cursor, even if they are from layers that don't have configured field mappings but are visible in the map. This helps you identify nearby measurements and avoid duplicate entries.
:::

## Data Entry Dialog Features

The interactive data entry dialog provides comprehensive input options:

```{figure} ../static/insert_point.png
:align: center

Inserting a new dip/strike feature
```

### Embedded Map

The dialog's embedded map offers a preview of the point feature at the clicked location. The feature is represented by a graphical marker with strike and dip lines that automatically update based on the azimuth values you enter.

:::{Note}
It is not possible to modify the point location (coordinates) within the dialog. To change the location, close the dialog and use the interactive point tool again, clicking on the new location on the QGIS map canvas. To move an already existing point, use the standard QGIS editing tools.
:::

The embedded map displays a portion of the QGIS map around the point location. The layers shown are the same as those displayed on the main QGIS map when using the point tool. To modify the embedded map background, simply adjust the QGIS map by enabling the desired layers, applying symbology, etc., before using the tool.

:::{tip}
You can interact with the map using the mouse scroll wheel to zoom in and out, and by clicking and dragging with the left mouse button to pan.
:::

The slider at the bottom of the map controls the transparency of the embedded map background. This feature helps provide a better view of the point marker against the underlying background.

### Required Input

**Strike or Dip Azimuth**: Enter the azimuth value from 0-360° using either direct numeric input in the spin box or the interactive compass dial (click and drag to set value).

The entered azimuth value can represent either **Strike** or **Dip** direction - select the appropriate mode using the radio buttons. When you change between dip and strike modes, the orientation marker on the embedded map updates automatically to reflect your selection.

**True North Correction**: Use this checkbox to automatically apply true north correction to your input azimuth values, compensating for grid convergence at your location (see [→ Overview](overview.md) for more).

**Dip Value**: Enter the dip angle from 0-90° (where 0° is horizontal and 90° is vertical).

**Corrected Dip and Strike Azimuth**: The final calculated dip and strike values that will be saved to the layer's attribute table are displayed here, with any selected corrections applied.

### Optional Data

#### DTM elevation value extraction

**Automatic Elevation Extraction**: When a suitable raster DTM (Digital Terrain Model) layer is loaded in your QGIS project, you can select it from the dropdown to automatically extract elevation values at point locations. The extracted elevation will be saved to the configured elevation field in your target layer.

**Coordinate System Handling**: The tool automatically handles coordinate transformations between the map canvas CRS and the DTM layer CRS, ensuring accurate elevation sampling regardless of coordinate system differences.

**Manual Entry Option**: If no DTM layer is selected or available, you can manually enter elevation values directly into the elevation field.

#### Additional Data Fields

Select **Geological Type** from customizable categories. Custom types are configurable in settings.

Additional fields include **Age** for geological age or formation name, **Lithology** for rock type description, and **Notes** for free-text field observations and comments.

## Layer Management

### Target Layer Selection

The plugin works with any point vector layer that contains appropriate fields (see [→ Layer Creation](layer-creation.md) for more).

#### Field Mapping Configuration

When working with existing layers, the plugin automatically checks for compatible fields and suggests mappings. If automatic detection works well, you can start using the layer immediately. If not, use the field mapping tool to manually connect your layer's fields to the plugin's expected data structure.

#### Automatic Field Detection

The plugin automatically suggests field mappings based on **field names** (recognizes common naming patterns), **data types** (matches numeric fields to azimuth/dip values), and **field order** (considers typical field arrangements).

#### Manual Configuration

If automatic detection doesn't work, manually configure mappings by opening field configuration (click the gear icon next to layer selection), mapping required fields (set strike azimuth, dip azimuth, and dip value fields), mapping optional fields (configure elevation, geological type, age, lithology, and notes), validating configuration (the dialog shows validation status), and saving settings (mappings are stored with the layer).
