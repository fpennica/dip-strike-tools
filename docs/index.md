# {{ title }} - Documentation

> **Description:** {{ description }}  
> **Author and contributors:** {{ author }}  
> **Plugin version:** {{ version }}  
> **QGIS minimum version:** {{ qgis_version_min }}  
> **QGIS maximum version:** {{ qgis_version_max }}  
> **Source code:** {{ repo_url }}  
> **Last documentation update:** {{ date_update }}

----

## Overview

The Dip Strike Tools plugin provides comprehensive tools for geological field data collection, management, and analysis in QGIS. It enables geologists to efficiently record and visualize geological strike and dip measurements with interactive tools and automated calculations.

### Key Features

- **Interactive Data Collection**: Point-and-click interface for recording dip/strike measurements directly on the map
- **Layer Management**: Automated creation and configuration of specialized geological data layers
- **Field Calculations**: Batch calculation tools for converting between strike and dip azimuths
- **Customizable Geology Types**: Configurable geological type classifications (strata, foliation, faults, etc.)
- **Multi-format Support**: Works with shapefiles, GeoPackages, and other vector formats
- **True North Correction**: Automatic adjustment for magnetic declination and grid convergence

```{toctree}
---
caption: User Guide
maxdepth: 1
---
usage/installation
usage/overview
usage/layer-creation
usage/data-insertion
usage/calculate-values
usage/settings
```

```{toctree}
---
caption: Development
maxdepth: 1
---
development/contribute
development/environment
development/documentation
development/translation
development/packaging
development/testing
development/history
```
