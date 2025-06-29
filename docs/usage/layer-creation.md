# Layer Creation

The **Create New Dip Strike Layer** tool provides an easy way to set up properly configured vector layers for geological data collection. This tool ensures that your layers have all the required fields and appropriate settings for strike and dip measurements.

:::{note}
Creating a new layer is not strictly required for using the plugin. You can work with any existing point vector layer, and the plugin will automatically check and configure field mappings when you select an existing layer. The layer creation tool is provided as a convenience for users who want optimally configured layers from the start.
:::

## Accessing the Tool

1. Click the **Create New Dip Strike Layer** button in the Dip Strike Tools toolbar
2. Or access it through the plugin menu in QGIS

## Layer Creation Dialog

The layer creation dialog allows you to configure all aspects of your new geological data layer:

### Basic Settings

#### Layer Name

Enter a descriptive name for your layer (e.g., "Structural_Measurements_2024"). The name will appear in the QGIS Layers panel.

#### Layer Type

Choose from three storage options:

**Memory Layer (Temporary)**: Fast creation and editing with data that exists only while QGIS is open. Ideal for quick analysis or temporary data collection, and can be saved later using QGIS "Export" functionality.

**Shapefile**: Traditional GIS format compatible with most GIS software. Field names are limited to 10 characters and the plugin automatically uses field mapping for compatibility.

**GeoPackage**: Modern SQLite-based format supporting longer field names and more data types in a single file that contains all data and styling. Recommended for new projects.

### Coordinate Reference System (CRS)

#### Current Project CRS

Uses the same coordinate system as your current QGIS project, ensuring compatibility with existing project data. This is **recommended** for most use cases.

#### Custom CRS

Select any coordinate reference system when working with specific regional grids. Both geographic (lat/lon) and projected coordinates are supported.

### Field Configuration

The plugin automatically creates the required fields for geological measurements:

#### Required Fields

The plugin creates three essential fields: **Strike Azimuth** for the direction of strike line (0-360°), **Dip Azimuth** for the direction of dip (strike + 90°), and **Dip Value** for the angle of dip from horizontal (0-90°).

#### Optional Fields

Enable optional fields based on your data collection needs. These include **Geological Type** for classification of the measured feature, **Age** for geological age or formation name, **Lithology** for rock type or lithological description, and **Notes** for additional comments or observations.

### Geological Type Configuration

When you enable the **Geological Type** field, you can choose the storage method:

#### Store Codes

Saves numerical codes (1, 2, 3, etc.) which results in smaller file size but requires reference to decode meanings and is used with lookup tables.

#### Store Descriptions

Saves full text descriptions ("Strata", "Foliation", etc.) which creates self-documenting data that is immediately readable but results in larger file size.

:::{tip}
The geological types are defined in the [plugin settings](settings.md) and can be customized for your specific workflow.
:::

### Symbology Options

#### Apply Default Symbology

Automatically applies geological strike/dip symbols using traditional structural geology conventions with strike lines and dip tick marks, and different colors for different geological types.

#### No Symbology

Creates layer with simple point symbols, allowing custom styling later and is useful when integrating with existing style schemes.

## Layer Creation Process

1. **Configure Settings**: Fill in all required settings in the dialog
2. **Click OK**: The plugin creates and configures the layer  
3. **Automatic Setup**: The layer is added to your QGIS project, configured with proper field mappings, marked as a dip/strike layer for the plugin, and styled (if symbology option selected)

## Working with Created Layers

### Field Mapping

The plugin automatically sets up field mappings that connect the physical field names to the plugin's requirements. This is especially important for shapefiles where field names are truncated.

### Layer Recognition

Created layers are automatically recognized by other plugin tools. The **Create Dip Strike Point** tool will prioritize these layers, field mapping dialogs are pre-configured, and data validation uses the correct field mappings.

### Integration with QGIS

Created layers work seamlessly with QGIS features including the **Attribute Table** for viewing and editing data, **Layer Properties** for modifying styling and labels, **Editing Tools** for adding and modifying features, and **Export** functionality for saving to different formats.

## Best Practices

### Naming Conventions

Use descriptive names that include location and date, avoiding spaces and special characters for better compatibility. Examples include `Structural_Site_A_2024` and `Foliation_Traverse_1`.

### CRS Selection

For **local projects**, use your country's national grid system. For **regional studies**, use UTM zones for the area. For **global analysis**, use appropriate global projections. For **field work**, consider GPS coordinate systems.

### Field Selection

For **minimal setup**, enable only required fields for quick data collection. For **comprehensive setup**, enable all optional fields for detailed documentation. For **custom needs**, use the field configuration dialog later to adjust mappings.

### File Management

Use **memory layers** for quick analysis, **GeoPackages** for comprehensive data management, **shapefiles** when sharing with other software, and implement regular backup procedures for your data files.

## Troubleshooting

### Common Issues

:::{warning}
**Layer creation failed**: Check that you have write permissions to the selected folder, ensure the file path doesn't contain invalid characters, and try creating in a different location.
:::

:::{warning}
**Invalid CRS selected**: Ensure the selected coordinate system is valid for your area, check that the CRS is properly defined in QGIS, and try using the project CRS instead.
:::

:::{warning}
**Symbology not applied**: Check that the QML files are present in the plugin resources, try applying symbology manually later, and restart QGIS if the issue persists.
:::

### Layer Configuration Issues

If a created layer doesn't work properly with other plugin tools:

1. **Check Layer Role**: Ensure the layer has the correct custom properties
2. **Verify Field Mappings**: Use the field configuration dialog to check mappings  
3. **Recreate Layer**: Sometimes it's easier to create a new layer with correct settings

## Next Steps

After creating your layer, you can **start data collection** using the [Create Dip Strike Point](data-insertion.md) tool, **import existing data** by copying features from other layers, **configure styling** to customize the appearance, and **set up your project** by adding base maps and other reference layers.

:::{seealso}
For advanced field mapping and configuration options, see the [Data Insertion documentation](data-insertion.md).
:::
