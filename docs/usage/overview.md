# Plugin Overview

The Dip Strike Tools plugin is designed to streamline geological field data collection and analysis within QGIS. It provides an integrated workflow for recording, managing, and analyzing geological strike and dip measurements.

## What are Strike and Dip?

**Strike** and **dip** are fundamental measurements in structural geology that describe the orientation of planar geological features such as rock layers, fault planes, and fractures.

:::{note}
**Key Definitions**:

- **Strike**: The compass direction of a horizontal line on an inclined plane (0-360°)
- **Dip**: The angle of inclination of a plane from horizontal (0-90°)
- **Dip Azimuth**: The compass direction of the steepest descent down the plane (strike + 90°)
:::

## Plugin Architecture

The plugin uses a unified mathematical engine that ensures consistency across all tools. All calculations use the same mathematical functions, strike and dip azimuths are automatically normalized to 0-360° range, true north corrections are applied consistently, and robust input validation prevents data entry errors.

## Available Tools

The plugin provides four main tools accessible from the QGIS toolbar:

### 1. Create New Dip Strike Layer

Creates and configures new vector layers specifically designed for geological data collection. Supports multiple output formats and automatically sets up required fields.

[→ Learn more about Layer Creation](layer-creation.md)

### 2. Create Dip Strike Point

Interactive map tool for collecting geological measurements. Click anywhere on the map to record strike/dip data with visual preview and validation.

[→ Learn more about Data Insertion](data-insertion.md)

### 3. Calculate Dip/Strike Values

Batch calculation tool for converting between strike and dip azimuths in existing datasets. Includes input validation and rounding options.

[→ Learn more about Field Calculations](calculate-values.md)

### 4. Plugin Settings

Configure plugin behavior and customize geological type classifications for your specific workflow.

[→ Learn more about Settings](settings.md)

## Workflow Examples

### Typical Field Data Collection Workflow

**Setup**: Create a new dip/strike layer or configure an existing layer.

**Collection**: Use the interactive map tool to record measurements at field locations.

**Analysis**: Use the calculator tool to compute derived values (e.g., convert all strikes to dips).

**Visualization**: Apply symbology to visualize structural trends.

### Working with Existing Data

**Import**: Load existing geological data into QGIS.

**Configure**: Map existing fields to dip/strike structure using the field configuration dialog.

**Calculate**: Use the calculator tool to fill missing values or convert between formats.

**Validate**: Check data quality with built-in range validation.

## Data Storage Formats

The plugin supports multiple vector formats including **memory layers** for temporary layers for quick analysis, **shapefiles** for traditional GIS format with field mapping support, **GeoPackages** for modern format with extended field names and attributes, and **PostGIS** for enterprise database storage with spatial indexing.

## Quality Assurance Features

The plugin provides **input validation** with automatic checking of azimuth values (0-360° range), **user warnings** with alerts for potentially invalid data and option to continue, **consistent calculations** where all tools use the same mathematical engine, and **data integrity** with required field validation preventing incomplete records.

## Integration with QGIS

The plugin integrates seamlessly with QGIS through **native UI** following QGIS design patterns and conventions, **settings integration** with configuration panel in QGIS preferences, **layer management** working with QGIS layer tree and styling, **coordinate systems** with automatic CRS handling and transformations, and **undo/redo** with full support for QGIS editing history.

## Next Steps

:::{tip}
**Getting Started**:

- **Installation**: [Install the plugin](installation.md) from the QGIS Plugin Repository
- **First Use**: Start with [creating a new layer](layer-creation.md) for your project
- **Data Collection**: Learn the [interactive data insertion](data-insertion.md) workflow
- **Customization**: Configure [plugin settings](settings.md) for your specific needs
:::

For developers interested in contributing or understanding the plugin architecture, see the [development documentation](../development/contribute.md).
