# Plugin Settings and Customization

The Dip Strike Tools plugin provides comprehensive customization options through QGIS's integrated settings system. This page covers all available settings, customization options, and configuration workflows.

## Accessing Plugin Settings

The plugin settings are integrated into QGIS's main Options dialog for a seamless user experience.

### Opening Settings

Access plugin settings by going to `Settings` > `Options...` in QGIS menu, navigating to "Dip Strike Tools" in the left sidebar, or using direct access through the plugin's main menu.

### Settings Categories

The plugin organizes settings into logical groups including **General Options** for core plugin behavior settings, **Geological Types** for customizable classification system, **Display Options** for visual appearance and feedback settings, and **Advanced Settings** for technical configuration options.

## General Settings

### Debug Mode

Enable detailed logging for troubleshooting and development purposes.

:::{note}
**When to Enable**: Use debug mode when investigating plugin behavior issues, reporting bugs to developers, or understanding plugin operations in detail.
:::

**Effects**: Increases log output verbosity, may impact plugin performance slightly, and provides detailed error information.

**Usage**: Enable temporarily for troubleshooting, disable for normal daily use, and note that it's required for meaningful bug reports.

### Version Information

The settings dialog displays current plugin version information for reference and support purposes including current plugin version, last settings save timestamp, QGIS compatibility information, and installation status.

## Geological Types Management

The plugin provides a powerful system for managing geological classification types used in data collection and analysis.

### Default Geological Types

The plugin ships with standard geological classifications:

1. **Strata**: Sedimentary bedding planes and layered structures
2. **Foliation**: Metamorphic fabric and foliated textures
3. **Fault**: Fault planes and fracture surfaces
4. **Joint**: Joint sets and systematic fractures
5. **Cleavage**: Cleavage planes and penetrative fabrics

### Customizing Geological Types

#### Adding New Types

Access the geological types management table, click the "+" button to add a new type, provide a short unique code (numbers or letters), add a clear descriptive name, and apply settings to store the new type.

#### Editing Existing Types

Select the row for the type you want to modify, double-click to edit code or description, ensure codes remain unique, and apply settings to save changes to update the system.

#### Removing Types

Select the type to remove, click the "-" button or use Delete key, confirm the action when prompted, and save changes to apply settings making removal permanent.

:::{warning}
Removing geological types may affect existing data that uses those classifications.
:::

### Code and Description Guidelines

#### Code Best Practices

Keep codes short using 1-3 characters when possible, ensure each code is unique, use intuitive abbreviations to be memorable, and consider that codes affect display order.

**Examples**: Use `S` or `ST` for Strata, `F` or `FOL` for Foliation, `FT` for Fault, and `J` for Joint.

#### Description Best Practices

Be descriptive using clear, unambiguous terms, follow standards with accepted geological terminology, consider users making descriptions meaningful to your team, and include context with clarifying information if needed.

**Examples**: "Bedding (Sedimentary Strata)", "Schistosity (Metamorphic Foliation)", "Normal Fault Plane", "Systematic Joint Set".

### Resetting to Defaults

If your geological types become corrupted or you want to start fresh, use the "Reset to Defaults" button, confirm the action by acknowledging the warning dialog, review that default types are restored, and customize again by adding your custom types as needed.

:::{warning}
This action permanently removes all custom geological types and restores only the original five default types.
:::

### Geological Types in Data Collection

#### Selection Interface

When collecting data, geological types appear in dropdown lists in data entry dialogs, lookup tables in field mapping configurations, and validation rules in data quality checking.

#### Data Storage

Geological type information is stored as **codes** in layer attribute tables (space-efficient), **descriptions** in user interfaces (human-readable), and **mappings** in plugin configuration (linking codes to descriptions).

#### Migration and Compatibility

The system provides **forward compatibility** where new types work with existing data, **backward compatibility** where the plugin handles missing type definitions gracefully, and **data preservation** where existing data retains original type codes even if types are modified.

## Display and Interface Options

### Visual Feedback Settings

Control how the plugin provides visual feedback during data collection and editing.

#### Marker Display

- **Marker Style**: Choose from various marker symbols
- **Marker Size**: Adjust marker size for visibility
- **Marker Color**: Customize marker colors for different types
- **Transparency**: Set opacity levels for overlaid markers

#### Compass Dial Settings

- **Dial Size**: Adjust the compass dial dimensions
- **Precision**: Set the granularity of dial movements
- **Visual Style**: Choose between different dial appearances
- **Feedback Mode**: Configure how the dial responds to input

### Layer Visualization

#### Temporary Layer Opacity

Configure how temporary layers appear during data collection:

- **Opacity Levels**: Set transparency for better base map visibility
- **Highlight Mode**: Choose how selected features are emphasized
- **Layer Ordering**: Control where temporary layers appear in layer stack

#### Symbol Configuration

- **Default Symbols**: Set default symbols for new dip/strike features
- **Type-based Styling**: Configure different symbols for geological types
- **Size Scaling**: Adjust symbol sizes based on map scale
- **Color Schemes**: Apply consistent color schemes across projects

## Advanced Configuration

### Technical Settings

#### Coordinate Precision

- **Display Precision**: Number of decimal places shown in coordinates
- **Storage Precision**: Precision maintained in data files
- **Calculation Precision**: Internal calculation accuracy
- **Rounding Behavior**: How values are rounded for display

#### Azimuth Calculation

- **Calculation Method**: Choose between different azimuth calculation approaches
- **True North Correction**: Enable/disable automatic magnetic declination correction
- **Angle Conventions**: Set preferred angle measurement conventions
- **Validation Tolerances**: Configure acceptable ranges for measurements

#### Performance Options

- **Cache Settings**: Configure how plugin caches layer information
- **Update Frequency**: Set how often interface elements refresh
- **Background Processing**: Enable/disable background calculations
- **Memory Management**: Control memory usage for large datasets

### File and Data Handling

#### Default File Locations

- **Export Directory**: Default location for exported data
- **Template Directory**: Location for layer templates
- **Backup Directory**: Automatic backup storage location
- **Log File Location**: Where diagnostic logs are stored

#### Data Format Preferences

- **Default Layer Format**: Preferred format for new layers (Shapefile, GeoPackage, etc.)
- **Field Name Conventions**: Standard field naming patterns
- **Metadata Standards**: Default metadata templates
- **Export Formats**: Preferred formats for data export

### Integration Settings

#### QGIS Integration

- **Menu Integration**: How plugin menus integrate with QGIS
- **Toolbar Customization**: Plugin toolbar appearance and behavior
- **Keyboard Shortcuts**: Custom keyboard shortcuts for plugin functions
- **Status Bar Integration**: Plugin status information display

#### External Tools

- **Calculator Integration**: Links to external calculation tools
- **Database Connections**: Default database connection settings
- **Web Service Access**: Configuration for online geological resources
- **Export Tool Integration**: Links to specialized export utilities

## Settings Management

### Saving and Loading Settings

#### Automatic Saving

- Settings are automatically saved when applying changes
- No manual save operation required
- Settings persist across QGIS sessions
- Backup copies maintained automatically

#### Settings Location

Settings are stored in QGIS's standard configuration system:

- **Windows**: User profile directory under QGIS settings
- **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/`
- **macOS**: User Library under QGIS application support

#### Export/Import Settings

While not directly supported by the plugin, QGIS settings can be:

- **Exported**: Using QGIS's settings export functionality
- **Imported**: Using QGIS's settings import functionality
- **Shared**: By copying configuration files between installations
- **Backed Up**: As part of QGIS profile backups

### Troubleshooting Settings

#### Corrupted Settings

If settings become corrupted:

1. **Reset to Defaults**: Use the reset functionality in each settings section
2. **Clear Cache**: Restart QGIS to clear cached settings
3. **Reinstall Plugin**: Remove and reinstall if problems persist
4. **Manual Cleanup**: Remove plugin settings from QGIS configuration (advanced)

#### Settings Not Persisting

If settings don't save properly:

1. **Check Permissions**: Ensure QGIS can write to configuration directory
2. **Verify Installation**: Confirm plugin is properly installed
3. **Restart QGIS**: Close and reopen QGIS completely
4. **Check Logs**: Review QGIS logs for error messages

#### Compatibility Issues

When upgrading plugin versions:

1. **Backup Settings**: Export current settings before upgrading
2. **Check Compatibility**: Review changelog for setting changes
3. **Migrate Settings**: Use any provided migration tools
4. **Reconfigure**: Manually reconfigure if automatic migration fails

## Best Practices

### Settings Configuration

- **Document Changes**: Keep notes about custom configurations
- **Test Settings**: Verify settings work as expected after changes
- **Regular Backups**: Include settings in project backup procedures
- **Team Coordination**: Standardize settings across team members

### Geological Types Best Practices

Plan ahead by designing type systems before starting major projects, be consistent using consistent naming conventions, conduct regular review by periodically cleaning up geological types, and maintain documentation of custom type definitions.

### Performance Optimization

Monitor performance by watching for performance impacts from settings changes, optimize display by adjusting settings for your hardware capabilities, conduct regular maintenance by periodically cleaning up temporary files and caches, and manage resources by configuring settings appropriate for your system capabilities.
