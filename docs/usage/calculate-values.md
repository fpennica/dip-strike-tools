# Calculate Dip/Strike Values

The Dip Strike Tools plugin includes a calculator tool that can compute dip azimuths from strike azimuths (and vice versa) in existing vector layers or tables.

## Overview

This tool is useful when you have geological data with either strike or dip azimuth values and need to calculate the corresponding perpendicular direction.

:::{note}
**Mathematical Relationship**:

- **Dip Azimuth** = Strike Azimuth + 90° (normalized to 0-360°)
- **Strike Azimuth** = Dip Azimuth - 90° (normalized to 0-360°)
:::

All calculations use the plugin's unified mathematical functions, ensuring consistency across all tools (including the interactive insert dialog and batch calculation features).

## Accessing the Tool

Open QGIS and ensure the Dip Strike Tools plugin is loaded, then click the **Calculate Dip/Strike Values** button in the toolbar (calculator icon), or access it through the plugin menu.

## Using the Calculator

### Step 1: Select a Layer

Choose any vector layer or table from your current QGIS project. The layer must be valid and loaded in the project, and both geometric layers (points, lines, polygons) and non-spatial tables are supported.

### Step 2: Choose Calculation Type

Select the type of calculation you want to perform:

**Calculate Dip Azimuth from Strike Azimuth**: Converts strike values to dip values

**Calculate Strike Azimuth from Dip Azimuth**: Converts dip values to strike values

### Step 3: Select Input Field

Choose the field containing the source azimuth values. Only numeric fields (integer or double) are available for selection, and values should be in degrees (0-360°).

### Step 4: Choose Output Destination

You have two options for storing the calculated values:

#### Option A: Use Existing Field

Select an existing numeric field from the dropdown. The calculated values will overwrite existing values in this field.

#### Option B: Create New Field

Check the "Create new field" checkbox, enter a name for the new field, and a new double-precision field will be added to the layer. Default names are suggested based on calculation type.

### Step 5: Set Calculation Options

- **Rounding**: Choose how many decimal places to round the results to
Default is 2 decimal places (e.g., 135.47°) with range from 0-10 decimal places. This affects the precision of the calculated values stored in the output field.

### Step 6: Execute Calculation

Click **OK** to start the calculation. The tool will process all features with valid input values, and progress and results are logged in the QGIS message log.

## Example Usage

### Converting Strike to Dip Azimuth

Consider this workflow: You have a point layer with geological measurements containing a field called `strike_azimuth` with values like 45°, 120°, etc. Select the layer in the calculator dialog, choose "Calculate Dip Azimuth from Strike Azimuth", select `strike_azimuth` as the input field, create a new field called `dip_azimuth`, set rounding to 1 decimal place for cleaner results, and execute the calculation.

**Result**: Strike 45° becomes Dip 135°, Strike 120° becomes Dip 210°, etc.

## Data Requirements

**Input values** must be numeric (integer or double). **Value range** should ideally be 0-360 degrees, though the tool will warn you if values are outside this range and you can choose to continue calculation or cancel to fix the data first. **Null values** in features with null or empty input values are skipped. **Invalid values** that are non-numeric are logged as errors and skipped.

## Error Handling

The tool handles various error conditions gracefully including **invalid layers** (tool validates layer selection), **missing fields** (verifies field selection before processing), **duplicate field names** (prevents creating fields with existing names), **data type errors** (skips features with invalid input values), and **layer editing** (handles layer edit mode automatically).

## Results and Feedback

After calculation, you'll see a **success message** showing number of processed features, **error reporting** for any features that couldn't be processed, **layer refresh** automatically displaying new values, and **message log** with detailed information available in QGIS message log.

## Tips

:::{tip}
**Best Practices**:

1. **Backup your data**: Always work on a copy of important datasets
2. **Check results**: Verify a few calculated values manually to ensure correctness
3. **Field naming**: Use descriptive names for new fields (e.g., "dip_azimuth_calc")
4. **Data validation**: The tool will warn you if input values are outside 0-360° range - review these before proceeding
5. **Range validation**: If you get a range warning, check your data for measurement errors or unit inconsistencies
6. **Layer symbology**: Consider updating your layer symbology to visualize the new calculated values
:::
