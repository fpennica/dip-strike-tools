# {{ title }} - Documentation

> **Description:** {{ description }}  
> **Author and contributors:** {{ author }}  
> **Plugin version:** {{ version }}  
> **QGIS minimum version:** {{ qgis_version_min }}  
> **QGIS maximum version:** {{ qgis_version_max }}  
> **Source code:** {{ repo_url }}  
> **Last documentation update:** {{ date_update }}

----

**Overview**

Dip-Strike Tools is a QGIS plugin that aims to provide a set of tools for digitizing, managing, and analyzing plane orientation or attitude data (dip and strike) of planar geologic features. It currently provides basic tools to streamline the workflow for geologists working with structural geology datasets, enabling efficient dip and strike data capture and management within QGIS.

**Key Features**

- **Interactive Data Collection**: Point-and-click interface for recording dip/strike measurements directly on the map
- **True North Correction**: Automatic adjustment for grid convergence
- **Layer Management**: Automated creation and configuration of specialized geological data layers
- **Field Calculations**: Batch calculation tools for converting between strike and dip azimuths
- **Customizable Geology Types**: Configurable geological type classifications (strata, foliation, faults, etc.)
- **Multi-format Support**: Works with shapefiles, GeoPackages, and other vector formats

```{toctree}
---
caption: User Guide
maxdepth: 1
---
usage/overview
usage/installation
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
development/pyqt-compatibility
development/documentation
development/translation
development/packaging
development/testing
development/history
```

```{toctree}
---
caption: About
maxdepth: 1
---
license
```
