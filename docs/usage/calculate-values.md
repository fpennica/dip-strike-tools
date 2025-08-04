# Calculate Dip/Strike Values

The Dip-Strike Tools plugin includes a **calculator tool** that can compute dip azimuths from strike azimuths (and vice versa) in existing vector layers or tables.

This tool is useful when you have geological data with either strike or dip azimuth values and need to calculate the corresponding perpendicular direction.

:::{note}

- **Dip Azimuth** = Strike Azimuth + 90° (normalized to 0-360°)
- **Strike Azimuth** = Dip Azimuth - 90° (normalized to 0-360°)

:::

## Using the Tool

Open QGIS and ensure the Dip Strike Tools plugin is loaded, then click the **Calculate Dip/Strike Values** button in the toolbar, or access it through the plugin menu.

```{figure} ../static/field_calculator.png
:align: center
:width: 450px

Field calculator tool
```

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

- Select an **existing numeric field** from the dropdown. The calculated values will overwrite existing values in this field.
- Check the "Create new field" checkbox, enter a name for the new field, and a new double-precision field will be added to the layer.

### Step 5: Set Calculation Options

- **Rounding**: Choose how many decimal places to round the results to
Default is 2 decimal places. This affects the precision of the calculated values stored in the output field.

### Step 6: Execute Calculation

Click **OK** to start the calculation. The tool will process all features with valid input values, and progress and results are logged in the QGIS message log.
