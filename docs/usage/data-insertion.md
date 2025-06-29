# Data Insertion and Management

The Dip Strike Tools plugin provides powerful interactive tools for collecting and managing geological dip and strike measurements directly on your QGIS map. This page covers all aspects of data entry, editing, and management workflows.

## Interactive Point Tool

The plugin's primary data collection tool allows you to click anywhere on the map to insert new dip/strike measurements with precise geographic positioning.

### Using the Point Tool

1. **Access the Tool**: Click the plugin's main toolbar button or use the menu item
2. **Select Target Layer**: Choose an existing layer or create a new one
3. **Click on Map**: Click at any location where you want to record a measurement
4. **Enter Data**: The data entry dialog opens automatically with the clicked coordinates

:::{tip}
**Feature Highlighting**: When using the point tool, the plugin will automatically highlight existing point features that are close to your mouse cursor, even if they are from layers that don't have configured field mappings but are visible in the map. This helps you identify nearby measurements and avoid duplicate entries.
:::

### Data Entry Dialog Features

The interactive data entry dialog provides comprehensive input options:

#### Required Measurements

**Strike Azimuth**: Enter values from 0-360° using direct numeric input in the spin box, interactive compass dial (click and drag), or keyboard shortcuts (arrow keys for fine adjustment).

**Dip Value**: Enter dip angle from 0-90°.

**Dip Azimuth**: Automatically calculated from strike (or manually entered).

#### Coordinate Information

The dialog shows precise coordinates of the exact clicked location, displays current coordinate reference system information, and allows optional manual coordinate entry to modify the position.

#### Geological Classification

Select **Geological Type** from customizable categories including Strata (bedding planes), Foliation (metamorphic structures), Fault planes, Joint surfaces, Cleavage planes, and custom types that are configurable in settings.

#### Additional Data Fields

Additional fields include **Age** for geological age or formation name, **Lithology** for rock type description, and **Notes** for free-text field observations and comments.

### Compass Dial Interface

The interactive compass dial provides intuitive azimuth entry with **visual feedback** showing real-time needle position, **mouse interaction** for click and drag value setting, **keyboard control** using arrow keys for precise adjustment, and **automatic conversion** where strike and dip azimuths update automatically.

## Layer Management

### Target Layer Selection

The plugin works with any point vector layer that contains appropriate fields. **You don't need to create a new layer specifically for the plugin** - you can use any existing point layer, and the plugin will automatically check and configure field mappings as needed.

#### Compatible Layer Types

The plugin supports **Shapefiles** (`.shp`), **GeoPackage** layers (`.gpkg`), **PostGIS** tables, **Memory layers** (temporary), and other OGR-supported formats.

#### Required Fields

For existing layers, the plugin needs fields for strike azimuth (numeric, 0-360), dip azimuth (numeric, 0-360), and dip value (numeric, 0-90).

#### Optional Fields

Additional fields enhance data management and include geological type (text), age/formation (text), lithology (text), and notes (text).

### Field Mapping Configuration

When working with existing layers, the plugin automatically checks for compatible fields and suggests mappings. If automatic detection works well, you can start using the layer immediately. If not, use the field mapping tool to manually connect your layer's fields to the plugin's expected data structure.

#### Automatic Field Detection

The plugin automatically suggests field mappings based on **field names** (recognizes common naming patterns), **data types** (matches numeric fields to azimuth/dip values), and **field order** (considers typical field arrangements).

#### Manual Configuration

If automatic detection doesn't work, manually configure mappings by opening field configuration (click the gear icon next to layer selection), mapping required fields (set strike azimuth, dip azimuth, and dip value fields), mapping optional fields (configure geological type, age, lithology, and notes), validating configuration (the dialog shows validation status), and saving settings (mappings are stored with the layer).

#### Validation Features

The system provides **real-time feedback** with visual indicators showing mapping status, **duplicate detection** preventing multiple fields mapping to same purpose, **type checking** ensuring numeric fields for measurements, and **required field warnings** highlighting missing critical mappings.

## Editing Existing Features

The plugin supports comprehensive editing of existing dip/strike measurements.

### Edit Mode Access

Access edit mode through:
1. **Feature Selection**: Use QGIS selection tools to select features
2. **Plugin Menu**: Choose "Edit Selected Feature" from the plugin menu
3. **Direct Editing**: Double-click features with the plugin tool active

### Edit Dialog Features

The edit dialog includes all standard data entry features plus:

#### Feature Context
- **Layer Information**: Shows source layer name
- **Feature ID**: Displays unique feature identifier
- **Edit History**: Tracks modification timestamps (if available)

#### Coordinate Modification
- **Position Adjustment**: Modify feature coordinates if needed
- **CRS Conversion**: Automatic coordinate system handling
- **Precision Control**: Maintains original coordinate precision

#### Data Validation
- **Range Checking**: Ensures azimuth values stay within 0-360°
- **Dip Validation**: Confirms dip values are within 0-90°
- **Consistency Checks**: Validates strike/dip azimuth relationships

### Batch Editing

For multiple features, use QGIS's standard editing tools combined with the plugin's calculation features:

1. **Select Multiple Features**: Use QGIS selection tools
2. **Open Attribute Table**: Access the layer's attribute table
3. **Enable Editing**: Toggle layer editing mode
4. **Use Field Calculator**: Apply plugin calculations to selected features
5. **Validate Results**: Check calculations using the plugin's validation tools

## Data Quality and Validation

### Input Validation

The plugin provides comprehensive validation during data entry:

#### Azimuth Validation
- **Range Checks**: Ensures values are within 0-360°
- **Automatic Normalization**: Converts negative values and values >360°
- **Consistency Checking**: Validates strike/dip azimuth relationships

#### Dip Validation
- **Angle Range**: Ensures dip values are within 0-90°
- **Physical Constraints**: Prevents impossible dip angles
- **Measurement Units**: Assumes degrees (most common geological convention)

#### Coordinate Validation
- **CRS Checking**: Validates coordinates within layer's coordinate system
- **Precision Maintenance**: Preserves coordinate precision from source
- **Boundary Checking**: Warns if coordinates fall outside expected ranges

### Data Consistency

#### Strike-Dip Relationships
The plugin ensures mathematical consistency between strike and dip azimuths:
- **Perpendicular Rule**: Dip azimuth = strike azimuth ± 90°
- **Automatic Calculation**: Calculates missing values when possible
- **Conflict Resolution**: Warns when manual entries conflict

#### Geological Logic
- **Formation Consistency**: Validates geological type selections
- **Age Relationships**: Checks for logical age assignments (if configured)
- **Lithology Matching**: Validates rock type consistency (if configured)

## Workflow Examples

### Field Data Collection Workflow

1. **Setup**:
   - Load base maps and reference layers
   - Configure geological type categories
   - Create or select target layer

2. **Data Collection**:
   - Navigate to measurement location
   - Click to insert new point
   - Enter strike and dip measurements
   - Add geological classification
   - Include field notes

3. **Quality Control**:
   - Review entered data
   - Check azimuth calculations
   - Validate geological classifications
   - Add supplementary information

4. **Documentation**:
   - Export data for reporting
   - Generate map products
   - Archive with project data

### Data Import and Validation Workflow

1. **Import Existing Data**:
   - Load external dip/strike datasets
   - Configure field mappings
   - Validate data integrity

2. **Standardization**:
   - Use calculation tools to fill missing values
   - Standardize geological type classifications
   - Normalize azimuth measurements

3. **Enhancement**:
   - Add missing geological information
   - Include location descriptions
   - Link to reference materials

4. **Integration**:
   - Merge with other geological datasets
   - Create composite layers
   - Generate analysis products

## Best Practices

### Data Entry Best Practices

- **Consistent Units**: Always use degrees for azimuth measurements
- **Measurement Conventions**: Follow standard geological strike/dip conventions
- **Field Validation**: Validate measurements in the field when possible
- **Documentation**: Include comprehensive notes for each measurement

### Layer Management Best Practices

- **Naming Conventions**: Use clear, descriptive layer names
- **Field Naming**: Use standard field names for compatibility
- **Backup Strategy**: Regular backups of valuable field data
- **Version Control**: Track changes to important datasets

### Quality Assurance Best Practices

- **Regular Validation**: Periodically check data consistency
- **Peer Review**: Have colleagues review critical measurements
- **Cross-Reference**: Compare with existing geological maps
- **Statistical Analysis**: Use statistical tools to identify outliers

## Troubleshooting

### Common Issues

#### Layer Compatibility
- **Missing Fields**: Use field mapping to connect existing fields
- **Type Mismatches**: Ensure numeric fields for azimuth/dip values
- **Encoding Issues**: Check character encoding for text fields

#### Data Entry Problems
- **Coordinate Issues**: Verify coordinate reference system settings
- **Azimuth Conflicts**: Check strike/dip azimuth relationship calculations
- **Validation Errors**: Review input ranges and data types

#### Performance Issues
- **Large Datasets**: Consider using spatial indexing for large layers
- **Complex Geometries**: Simplify base maps if needed
- **Memory Usage**: Close unnecessary layers and applications

### Getting Help

- **Plugin Documentation**: Refer to this comprehensive guide
- **QGIS Community**: Use QGIS forums and community resources
- **Issue Reporting**: Report bugs through the plugin's issue tracker
- **Feature Requests**: Suggest improvements through appropriate channels
