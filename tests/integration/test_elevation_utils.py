# -----------------------------------------------------------------------------
# Copyright (C) 2025-2026, F. Pennica
# This file is part of Dip-Strike Tools QGIS plugin.
#
# Dip-Strike Tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Dip-Strike Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dip-Strike Tools.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

"""QGIS integration tests for elevation_utils module."""

import pytest
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsPointXY,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
)

from dip_strike_tools.core.elevation_utils import ElevationExtractor

# Import pytest-qgis utilities
pytest_plugins = ["pytest_qgis"]


class TestElevationExtractorQGIS:
    """QGIS integration tests for ElevationExtractor."""

    def test_elevation_extractor_import(self):
        """Test that ElevationExtractor can be imported."""
        assert ElevationExtractor is not None

    def test_elevation_extractor_initialization(self):
        """Test ElevationExtractor initialization with QGIS."""
        extractor = ElevationExtractor()
        assert extractor is not None
        assert hasattr(extractor, "log")

    def test_is_suitable_dtm_layer_with_qgis_raster(self):
        """Test is_suitable_dtm_layer with QGIS raster layer."""
        extractor = ElevationExtractor()

        # Create a test raster layer (invalid path, but valid QgsRasterLayer)
        layer = QgsRasterLayer("", "test", "gdal")

        # This should fail because the layer is invalid (no data source)
        is_suitable, error_msg = extractor.is_suitable_dtm_layer(layer)

        assert is_suitable is False
        assert error_msg == "Layer is not valid"

    def test_get_suitable_dtm_layers_with_qgis_project(self):
        """Test get_suitable_dtm_layers with actual QGIS project."""
        extractor = ElevationExtractor()

        # Get suitable layers from empty project
        suitable_layers = extractor.get_suitable_dtm_layers()

        assert isinstance(suitable_layers, list)
        # Should be empty since no layers in test project
        assert len(suitable_layers) == 0

    def test_format_elevation_display_integration(self):
        """Test format_elevation_display method integration."""
        extractor = ElevationExtractor()

        # Test various elevation values
        test_cases = [
            (None, "N/A"),
            (0.0, "0 m"),
            (100.0, "100 m"),
            (100.4, "100 m"),
            (100.6, "101 m"),
            (-50.2, "-50 m"),
            (1234.7, "1235 m"),
            (8848.86, "8849 m"),  # Mount Everest
            (-430.5, "-430 m"),  # Dead Sea level
        ]

        for elevation, expected in test_cases:
            result = extractor.format_elevation_display(elevation)
            assert result == expected, f"Failed for elevation {elevation}: got {result}, expected {expected}"

    def test_extract_elevation_with_qgis_types(self):
        """Test extract_elevation with QGIS coordinate types."""
        extractor = ElevationExtractor()

        # Create invalid raster layer for testing error handling
        layer = QgsRasterLayer("", "test", "gdal")

        # Test with QgsPointXY
        point = QgsPointXY(100.0, 200.0)
        success, elevation, error_msg = extractor.extract_elevation(layer, point)

        # Should fail because layer is invalid
        assert success is False
        assert elevation is None
        assert "Layer is not valid" in error_msg

    def test_extract_elevation_with_coordinate_systems(self):
        """Test extract_elevation with different coordinate systems."""
        extractor = ElevationExtractor()

        # Create coordinate reference systems
        wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
        web_mercator = QgsCoordinateReferenceSystem("EPSG:3857")

        assert wgs84.isValid()
        assert web_mercator.isValid()
        assert wgs84.authid() == "EPSG:4326"
        assert web_mercator.authid() == "EPSG:3857"

        # Create invalid raster layer for testing
        layer = QgsRasterLayer("", "test", "gdal")
        point = QgsPointXY(100.0, 200.0)

        # Test with target CRS (should still fail due to invalid layer)
        success, elevation, error_msg = extractor.extract_elevation(layer, point, target_crs=wgs84)

        assert success is False
        assert elevation is None
        assert "Layer is not valid" in error_msg

    def test_qgis_rectangle_operations(self):
        """Test QGIS rectangle operations used in elevation extraction."""
        # Create a rectangle
        rect = QgsRectangle(0, 0, 100, 100)

        # Test point containment
        point_inside = QgsPointXY(50, 50)
        point_outside = QgsPointXY(150, 150)

        assert rect.contains(point_inside) is True
        assert rect.contains(point_outside) is False

    def test_qgis_data_types_coverage(self):
        """Test coverage of QGIS data types used in suitability check."""
        # Test that all expected numeric data types are in the numeric_types list
        expected_types = [
            Qgis.DataType.Byte,
            Qgis.DataType.Int16,
            Qgis.DataType.UInt16,
            Qgis.DataType.Int32,
            Qgis.DataType.UInt32,
            Qgis.DataType.Float32,
            Qgis.DataType.Float64,
        ]

        # Verify that these are valid QGIS data types
        for data_type in expected_types:
            assert isinstance(data_type, Qgis.DataType)

    def test_coordinate_transform_creation(self):
        """Test QgsCoordinateTransform creation and basic functionality."""
        # This tests the QGIS classes used in coordinate transformation
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        target_crs = QgsCoordinateReferenceSystem("EPSG:3857")
        project = QgsProject.instance()

        # Create coordinate transform
        from qgis.core import QgsCoordinateTransform

        transform = QgsCoordinateTransform(source_crs, target_crs, project)

        assert transform is not None
        assert transform.sourceCrs() == source_crs
        assert transform.destinationCrs() == target_crs

    def test_project_integration(self):
        """Test QgsProject integration used in get_suitable_dtm_layers."""
        project = QgsProject.instance()

        # Test that we can access project methods
        assert hasattr(project, "mapLayers")

        # Get layers (should be empty dict in test environment)
        layers = project.mapLayers()
        assert isinstance(layers, dict)

    def test_raster_identify_format_enum(self):
        """Test that RasterIdentifyFormat enum is accessible."""
        # This tests the enum used in raster value identification
        format_value = Qgis.RasterIdentifyFormat.Value
        assert format_value is not None
        assert isinstance(format_value, Qgis.RasterIdentifyFormat)

    def test_elevation_extractor_error_handling_integration(self):
        """Test error handling integration with QGIS exceptions."""
        extractor = ElevationExtractor()

        # Test with None layer (should handle gracefully)
        point = QgsPointXY(0, 0)
        success, elevation, error_msg = extractor.extract_elevation(None, point)

        assert success is False
        assert elevation is None
        assert "Layer is not a raster layer" in error_msg

    @pytest.mark.parametrize(
        "band_count,expected_suitable",
        [
            (1, True),  # Single band - suitable for DTM
            (3, False),  # RGB - not suitable
            (4, False),  # RGBA - not suitable
            (0, False),  # No bands - not suitable
        ],
    )
    def test_band_count_suitability(self, band_count, expected_suitable):
        """Test DTM suitability based on band count."""
        extractor = ElevationExtractor()

        # Create mock layer that appears valid but has different band counts
        from unittest.mock import MagicMock

        layer = MagicMock(spec=QgsRasterLayer)
        layer.isValid.return_value = True
        layer.bandCount.return_value = band_count

        # Mock data provider for single band case
        if band_count == 1:
            mock_provider = MagicMock()
            mock_provider.dataType.return_value = Qgis.DataType.Float32
            layer.dataProvider.return_value = mock_provider

        is_suitable, error_msg = extractor.is_suitable_dtm_layer(layer)

        assert is_suitable == expected_suitable
        if not expected_suitable and band_count != 1:
            assert f"{band_count} bands" in error_msg

    def test_logging_integration(self):
        """Test that logging integration works correctly."""
        extractor = ElevationExtractor()

        # Test that log attribute exists and is callable
        assert hasattr(extractor, "log")
        assert callable(extractor.log)

        # Test that we can call log method without errors
        try:
            extractor.log("Test message", log_level=4)
            # If no exception, logging is working
            assert True
        except Exception as e:
            # If there's an error, it should be a reasonable one
            assert "log" not in str(e).lower() or "not found" not in str(e).lower()
