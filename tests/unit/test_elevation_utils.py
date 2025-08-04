"""Tests for elevation_utils module."""

from unittest.mock import MagicMock, patch

from qgis.core import Qgis, QgsPointXY

from dip_strike_tools.core.elevation_utils import ElevationExtractor


class TestElevationExtractor:
    """Tests for ElevationExtractor class."""

    def test_elevation_extractor_initialization(self):
        """Test ElevationExtractor initialization."""
        extractor = ElevationExtractor()
        assert extractor is not None
        assert hasattr(extractor, "log")

    def test_is_suitable_dtm_layer_none_layer(self):
        """Test is_suitable_dtm_layer with None layer."""
        extractor = ElevationExtractor()
        is_suitable, error_msg = extractor.is_suitable_dtm_layer(None)

        assert is_suitable is False
        assert error_msg == "Layer is not a raster layer"

    def test_is_suitable_dtm_layer_non_raster(self):
        """Test is_suitable_dtm_layer with non-raster layer."""
        extractor = ElevationExtractor()
        mock_layer = MagicMock()

        is_suitable, error_msg = extractor.is_suitable_dtm_layer(mock_layer)

        assert is_suitable is False
        assert error_msg == "Layer is not a raster layer"

    def test_is_suitable_dtm_layer_invalid_layer(self):
        """Test is_suitable_dtm_layer with invalid raster layer."""
        from qgis.core import QgsRasterLayer

        extractor = ElevationExtractor()
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = False

        is_suitable, error_msg = extractor.is_suitable_dtm_layer(mock_layer)

        assert is_suitable is False
        assert error_msg == "Layer is not valid"

    def test_is_suitable_dtm_layer_multiple_bands(self):
        """Test is_suitable_dtm_layer with multi-band raster."""
        from qgis.core import QgsRasterLayer

        extractor = ElevationExtractor()
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 3  # RGB image

        is_suitable, error_msg = extractor.is_suitable_dtm_layer(mock_layer)

        assert is_suitable is False
        assert "3 bands, expected single band" in error_msg

    def test_is_suitable_dtm_layer_non_numeric_data(self):
        """Test is_suitable_dtm_layer with non-numeric data type."""
        from qgis.core import QgsRasterLayer

        extractor = ElevationExtractor()
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1

        # Mock data provider with string data type
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.ARGB32  # Non-numeric
        mock_layer.dataProvider.return_value = mock_provider

        is_suitable, error_msg = extractor.is_suitable_dtm_layer(mock_layer)

        assert is_suitable is False
        assert "not suitable for elevation data" in error_msg

    def test_is_suitable_dtm_layer_valid_float32(self):
        """Test is_suitable_dtm_layer with valid Float32 DTM."""
        from qgis.core import QgsRasterLayer

        extractor = ElevationExtractor()
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1

        # Mock data provider with float32 data type
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_layer.dataProvider.return_value = mock_provider

        is_suitable, error_msg = extractor.is_suitable_dtm_layer(mock_layer)

        assert is_suitable is True
        assert error_msg == ""

    def test_is_suitable_dtm_layer_valid_int16(self):
        """Test is_suitable_dtm_layer with valid Int16 DTM."""
        from qgis.core import QgsRasterLayer

        extractor = ElevationExtractor()
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1

        # Mock data provider with int16 data type
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Int16
        mock_layer.dataProvider.return_value = mock_provider

        is_suitable, error_msg = extractor.is_suitable_dtm_layer(mock_layer)

        assert is_suitable is True
        assert error_msg == ""

    def test_extract_elevation_unsuitable_layer(self):
        """Test extract_elevation with unsuitable layer."""
        from qgis.core import QgsRasterLayer

        extractor = ElevationExtractor()
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = False

        point = QgsPointXY(100, 200)
        success, elevation, error_msg = extractor.extract_elevation(mock_layer, point)

        assert success is False
        assert elevation is None
        assert error_msg == "Layer is not valid"

    @patch("dip_strike_tools.core.elevation_utils.QgsProject")
    def test_extract_elevation_coordinate_transform_failure(self, mock_project):
        """Test extract_elevation with coordinate transformation failure."""
        from qgis.core import QgsCoordinateReferenceSystem, QgsRasterLayer

        extractor = ElevationExtractor()

        # Mock suitable layer
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_layer.dataProvider.return_value = mock_provider

        # Mock CRS
        mock_layer_crs = MagicMock(spec=QgsCoordinateReferenceSystem)
        mock_layer_crs.authid.return_value = "EPSG:3857"
        mock_layer.crs.return_value = mock_layer_crs

        mock_target_crs = MagicMock(spec=QgsCoordinateReferenceSystem)
        mock_target_crs.authid.return_value = "EPSG:4326"

        # Mock coordinate transform that fails
        with patch("dip_strike_tools.core.elevation_utils.QgsCoordinateTransform") as mock_transform_class:
            mock_transform = MagicMock()
            mock_transform.transform.side_effect = Exception("Transform failed")
            mock_transform_class.return_value = mock_transform

            point = QgsPointXY(100, 200)
            success, elevation, error_msg = extractor.extract_elevation(mock_layer, point, target_crs=mock_target_crs)

        assert success is False
        assert elevation is None
        assert "Failed to transform coordinates" in error_msg

    def test_extract_elevation_point_outside_extent(self):
        """Test extract_elevation with point outside DTM extent."""
        from qgis.core import QgsRasterLayer, QgsRectangle

        extractor = ElevationExtractor()

        # Mock suitable layer
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_layer.dataProvider.return_value = mock_provider

        # Mock CRS
        mock_layer_crs = MagicMock()
        mock_layer_crs.authid.return_value = "EPSG:3857"
        mock_layer.crs.return_value = mock_layer_crs

        # Mock extent that doesn't contain the point
        mock_extent = MagicMock(spec=QgsRectangle)
        mock_extent.contains.return_value = False
        mock_layer.extent.return_value = mock_extent

        point = QgsPointXY(1000000, 2000000)  # Point outside extent
        success, elevation, error_msg = extractor.extract_elevation(mock_layer, point)

        assert success is False
        assert elevation is None
        assert "outside DTM extent" in error_msg

    def test_extract_elevation_invalid_raster_identify(self):
        """Test extract_elevation with invalid raster identify result."""
        from qgis.core import QgsRasterLayer, QgsRectangle

        extractor = ElevationExtractor()

        # Mock suitable layer
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_layer.dataProvider.return_value = mock_provider

        # Mock CRS
        mock_layer_crs = MagicMock()
        mock_layer_crs.authid.return_value = "EPSG:3857"
        mock_layer.crs.return_value = mock_layer_crs

        # Mock extent that contains the point
        mock_extent = MagicMock(spec=QgsRectangle)
        mock_extent.contains.return_value = True
        mock_layer.extent.return_value = mock_extent

        # Mock invalid identify result
        mock_result = MagicMock()
        mock_result.isValid.return_value = False
        mock_provider.identify.return_value = mock_result

        point = QgsPointXY(100, 200)
        success, elevation, error_msg = extractor.extract_elevation(mock_layer, point)

        assert success is False
        assert elevation is None
        assert "Failed to identify raster value" in error_msg

    def test_extract_elevation_no_band_data(self):
        """Test extract_elevation with no data for band 1."""
        from qgis.core import QgsRasterLayer, QgsRectangle

        extractor = ElevationExtractor()

        # Mock suitable layer
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_layer.dataProvider.return_value = mock_provider

        # Mock CRS
        mock_layer_crs = MagicMock()
        mock_layer_crs.authid.return_value = "EPSG:3857"
        mock_layer.crs.return_value = mock_layer_crs

        # Mock extent that contains the point
        mock_extent = MagicMock(spec=QgsRectangle)
        mock_extent.contains.return_value = True
        mock_layer.extent.return_value = mock_extent

        # Mock identify result with no band 1 data
        mock_result = MagicMock()
        mock_result.isValid.return_value = True
        mock_result.results.return_value = {}  # No band 1 data
        mock_provider.identify.return_value = mock_result

        point = QgsPointXY(100, 200)
        success, elevation, error_msg = extractor.extract_elevation(mock_layer, point)

        assert success is False
        assert elevation is None
        assert "No elevation data available at this point" in error_msg

    def test_extract_elevation_none_value(self):
        """Test extract_elevation with None elevation value."""
        from qgis.core import QgsRasterLayer, QgsRectangle

        extractor = ElevationExtractor()

        # Mock suitable layer
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_layer.dataProvider.return_value = mock_provider

        # Mock CRS
        mock_layer_crs = MagicMock()
        mock_layer_crs.authid.return_value = "EPSG:3857"
        mock_layer.crs.return_value = mock_layer_crs

        # Mock extent that contains the point
        mock_extent = MagicMock(spec=QgsRectangle)
        mock_extent.contains.return_value = True
        mock_layer.extent.return_value = mock_extent

        # Mock identify result with None value
        mock_result = MagicMock()
        mock_result.isValid.return_value = True
        mock_result.results.return_value = {1: None}  # None elevation
        mock_provider.identify.return_value = mock_result

        point = QgsPointXY(100, 200)
        success, elevation, error_msg = extractor.extract_elevation(mock_layer, point)

        assert success is False
        assert elevation is None
        assert "No elevation data available at this point (nodata)" in error_msg

    def test_extract_elevation_nodata_value(self):
        """Test extract_elevation with nodata value."""
        from qgis.core import QgsRasterLayer, QgsRectangle

        extractor = ElevationExtractor()

        # Mock suitable layer
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_provider.sourceNoDataValue.return_value = -9999.0
        mock_layer.dataProvider.return_value = mock_provider

        # Mock CRS
        mock_layer_crs = MagicMock()
        mock_layer_crs.authid.return_value = "EPSG:3857"
        mock_layer.crs.return_value = mock_layer_crs

        # Mock extent that contains the point
        mock_extent = MagicMock(spec=QgsRectangle)
        mock_extent.contains.return_value = True
        mock_layer.extent.return_value = mock_extent

        # Mock identify result with nodata value
        mock_result = MagicMock()
        mock_result.isValid.return_value = True
        mock_result.results.return_value = {1: -9999.0}  # Nodata value
        mock_provider.identify.return_value = mock_result

        point = QgsPointXY(100, 200)
        success, elevation, error_msg = extractor.extract_elevation(mock_layer, point)

        assert success is False
        assert elevation is None
        assert "No elevation data available at this point (nodata value)" in error_msg

    def test_extract_elevation_success(self):
        """Test successful elevation extraction."""
        from qgis.core import QgsRasterLayer, QgsRectangle

        extractor = ElevationExtractor()

        # Mock suitable layer
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_provider.sourceNoDataValue.return_value = -9999.0
        mock_layer.dataProvider.return_value = mock_provider

        # Mock CRS
        mock_layer_crs = MagicMock()
        mock_layer_crs.authid.return_value = "EPSG:3857"
        mock_layer.crs.return_value = mock_layer_crs

        # Mock extent that contains the point
        mock_extent = MagicMock(spec=QgsRectangle)
        mock_extent.contains.return_value = True
        mock_layer.extent.return_value = mock_extent

        # Mock identify result with valid elevation
        mock_result = MagicMock()
        mock_result.isValid.return_value = True
        mock_result.results.return_value = {1: 1234.5}  # Valid elevation
        mock_provider.identify.return_value = mock_result

        point = QgsPointXY(100, 200)
        success, elevation, error_msg = extractor.extract_elevation(mock_layer, point)

        assert success is True
        assert elevation == 1234.5
        assert error_msg == ""

    def test_extract_elevation_unreasonable_value_low(self):
        """Test elevation extraction with unreasonably low value."""
        from qgis.core import QgsRasterLayer, QgsRectangle

        extractor = ElevationExtractor()

        # Mock suitable layer
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_provider.sourceNoDataValue.return_value = -9999.0
        mock_layer.dataProvider.return_value = mock_provider

        # Mock CRS
        mock_layer_crs = MagicMock()
        mock_layer_crs.authid.return_value = "EPSG:3857"
        mock_layer.crs.return_value = mock_layer_crs

        # Mock extent that contains the point
        mock_extent = MagicMock(spec=QgsRectangle)
        mock_extent.contains.return_value = True
        mock_layer.extent.return_value = mock_extent

        # Mock identify result with unreasonably low elevation
        mock_result = MagicMock()
        mock_result.isValid.return_value = True
        mock_result.results.return_value = {1: -600.0}  # Below Dead Sea (-430m)
        mock_provider.identify.return_value = mock_result

        point = QgsPointXY(100, 200)
        success, elevation, error_msg = extractor.extract_elevation(mock_layer, point)

        # Should still succeed but log warning
        assert success is True
        assert elevation == -600.0
        assert error_msg == ""

    def test_extract_elevation_invalid_value_type(self):
        """Test elevation extraction with invalid value type."""
        from qgis.core import QgsRasterLayer, QgsRectangle

        extractor = ElevationExtractor()

        # Mock suitable layer
        mock_layer = MagicMock(spec=QgsRasterLayer)
        mock_layer.isValid.return_value = True
        mock_layer.bandCount.return_value = 1
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_provider.sourceNoDataValue.return_value = -9999.0
        mock_layer.dataProvider.return_value = mock_provider

        # Mock CRS
        mock_layer_crs = MagicMock()
        mock_layer_crs.authid.return_value = "EPSG:3857"
        mock_layer.crs.return_value = mock_layer_crs

        # Mock extent that contains the point
        mock_extent = MagicMock(spec=QgsRectangle)
        mock_extent.contains.return_value = True
        mock_layer.extent.return_value = mock_extent

        # Mock identify result with non-numeric value
        mock_result = MagicMock()
        mock_result.isValid.return_value = True
        mock_result.results.return_value = {1: "invalid"}  # String value
        mock_provider.identify.return_value = mock_result

        point = QgsPointXY(100, 200)
        success, elevation, error_msg = extractor.extract_elevation(mock_layer, point)

        assert success is False
        assert elevation is None
        assert "Invalid elevation value" in error_msg

    @patch("dip_strike_tools.core.elevation_utils.QgsProject")
    def test_get_suitable_dtm_layers_empty(self, mock_project):
        """Test get_suitable_dtm_layers with no suitable layers."""
        extractor = ElevationExtractor()

        # Mock project with no layers
        mock_project_instance = MagicMock()
        mock_project_instance.mapLayers.return_value = {}
        mock_project.instance.return_value = mock_project_instance

        suitable_layers = extractor.get_suitable_dtm_layers()

        assert suitable_layers == []

    @patch("dip_strike_tools.core.elevation_utils.QgsProject")
    def test_get_suitable_dtm_layers_with_suitable(self, mock_project):
        """Test get_suitable_dtm_layers with suitable layers."""
        from qgis.core import QgsRasterLayer, QgsVectorLayer

        extractor = ElevationExtractor()

        # Mock suitable raster layer
        mock_raster = MagicMock(spec=QgsRasterLayer)
        mock_raster.isValid.return_value = True
        mock_raster.bandCount.return_value = 1
        mock_provider = MagicMock()
        mock_provider.dataType.return_value = Qgis.DataType.Float32
        mock_raster.dataProvider.return_value = mock_provider

        # Mock unsuitable vector layer
        mock_vector = MagicMock(spec=QgsVectorLayer)

        # Mock project with mixed layers
        mock_project_instance = MagicMock()
        mock_project_instance.mapLayers.return_value = {
            "layer1": mock_raster,
            "layer2": mock_vector,
        }
        mock_project.instance.return_value = mock_project_instance

        suitable_layers = extractor.get_suitable_dtm_layers()

        assert len(suitable_layers) == 1
        assert suitable_layers[0] == mock_raster

    def test_format_elevation_display_none(self):
        """Test format_elevation_display with None value."""
        extractor = ElevationExtractor()

        result = extractor.format_elevation_display(None)

        assert result == "N/A"

    def test_format_elevation_display_positive(self):
        """Test format_elevation_display with positive value."""
        extractor = ElevationExtractor()

        result = extractor.format_elevation_display(1234.7)

        assert result == "1235 m"

    def test_format_elevation_display_negative(self):
        """Test format_elevation_display with negative value."""
        extractor = ElevationExtractor()

        result = extractor.format_elevation_display(-123.4)

        assert result == "-123 m"

    def test_format_elevation_display_zero(self):
        """Test format_elevation_display with zero value."""
        extractor = ElevationExtractor()

        result = extractor.format_elevation_display(0.0)

        assert result == "0 m"

    def test_format_elevation_display_rounding(self):
        """Test format_elevation_display rounding behavior."""
        extractor = ElevationExtractor()

        # Test rounding up
        result1 = extractor.format_elevation_display(123.6)
        assert result1 == "124 m"

        # Test rounding down
        result2 = extractor.format_elevation_display(123.4)
        assert result2 == "123 m"

        # Test exact half (should round to nearest even)
        result3 = extractor.format_elevation_display(123.5)
        assert result3 == "124 m"
