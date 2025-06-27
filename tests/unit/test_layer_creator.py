"""
Tests for the DipStrikeLayerCreator class.
"""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
class TestDipStrikeLayerCreator:
    """Test class for DipStrikeLayerCreator."""

    def test_layer_creator_import(self):
        """Test that the layer creator can be imported."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator, LayerCreationError

            assert DipStrikeLayerCreator is not None
            assert LayerCreationError is not None
        except ImportError as e:
            pytest.skip(f"QGIS modules not available: {e}")

    def test_layer_creator_initialization(self):
        """Test basic layer creator initialization."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        creator = DipStrikeLayerCreator()

        # Check basic initialization
        assert hasattr(creator, "log")
        assert callable(creator.log)

    def test_get_dip_strike_fields(self):
        """Test getting standard field definitions."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        creator = DipStrikeLayerCreator()
        required_fields, optional_fields = creator.get_dip_strike_fields()

        # Check that we get the expected fields
        assert isinstance(required_fields, list)
        assert isinstance(optional_fields, list)
        assert len(required_fields) > 0
        assert len(optional_fields) > 0

        # Check that required fields include the key dip/strike fields
        field_names = [field.name() for field in required_fields]
        assert "strike_azimuth" in field_names
        assert "dip_azimuth" in field_names
        assert "dip_value" in field_names

    def test_get_shapefile_field_mapping(self):
        """Test getting field mapping for shapefiles."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        creator = DipStrikeLayerCreator()
        mapping = creator.get_shapefile_field_mapping()

        # Check that we get a valid mapping
        assert isinstance(mapping, dict)
        assert len(mapping) > 0

        # Check for expected field mappings
        assert "strike_azimuth" in mapping
        assert "dip_azimuth" in mapping
        assert "dip_value" in mapping

    def test_translation_method(self):
        """Test translation method."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        creator = DipStrikeLayerCreator()

        # Test translation method
        test_string = "Test String"
        result = creator.tr(test_string)
        assert isinstance(result, str)
        assert result == test_string  # Default implementation returns as-is

    def test_create_memory_layer(self):
        """Test memory layer creation."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_crs = Mock()
        mock_crs.authid.return_value = "EPSG:4326"

        mock_layer = Mock()
        mock_layer.isValid.return_value = True

        with patch("dip_strike_tools.core.layer_creator.QgsVectorLayer", return_value=mock_layer):
            creator = DipStrikeLayerCreator()

            layer = creator.create_memory_layer("Test Layer", mock_crs)

            assert layer is not None
            assert layer.isValid()

    def test_layer_creation_error(self):
        """Test LayerCreationError exception."""
        try:
            from dip_strike_tools.core.layer_creator import LayerCreationError
        except ImportError:
            pytest.skip("QGIS modules not available")

        # Test that the exception can be raised and caught
        with pytest.raises(LayerCreationError):
            raise LayerCreationError("Test error message")

    def test_configure_layer_properties_methods(self):
        """Test layer property configuration methods."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        creator = DipStrikeLayerCreator()

        # Check that configuration methods exist
        assert hasattr(creator, "configure_layer_properties")
        assert hasattr(creator, "configure_layer_properties_for_existing")
        assert callable(creator.configure_layer_properties)
        assert callable(creator.configure_layer_properties_for_existing)

    def test_symbology_methods(self):
        """Test symbology application methods."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        creator = DipStrikeLayerCreator()

        # Check that symbology methods exist
        assert hasattr(creator, "apply_symbology")
        assert hasattr(creator, "apply_symbology_to_existing_layer")
        assert callable(creator.apply_symbology)
        assert callable(creator.apply_symbology_to_existing_layer)

    def test_layer_config_creation(self):
        """Test layer configuration creation."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        creator = DipStrikeLayerCreator()

        # Test that create_layer_config method exists
        assert hasattr(creator, "create_layer_config")
        assert callable(creator.create_layer_config)

    def test_file_layer_creation(self):
        """Test file layer creation method."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        creator = DipStrikeLayerCreator()

        # Test that file layer creation method exists
        assert hasattr(creator, "create_file_layer")
        assert callable(creator.create_file_layer)

    def test_geopackage_methods(self):
        """Test GeoPackage-specific methods."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        creator = DipStrikeLayerCreator()

        # Test that GeoPackage methods exist
        assert hasattr(creator, "check_geopackage_layer_exists")
        assert callable(creator.check_geopackage_layer_exists)


@pytest.mark.unit
class TestLayerCreatorIntegration:
    """Integration tests for layer creator with mocked QGIS components."""

    def test_create_dip_strike_layer_memory(self):
        """Test creating a memory layer through the main interface."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_crs = Mock()
        mock_crs.authid.return_value = "EPSG:4326"
        mock_crs.isValid.return_value = True

        mock_layer = Mock()
        mock_layer.isValid.return_value = True
        mock_layer.id.return_value = "test_layer_id"

        config = {
            "name": "Test Layer",
            "format": "memory",
            "output_path": "",  # Memory layers don't need a path
            "format_info": {"driver": "memory", "extension": "", "description": "Memory layer"},
            "symbology": {"apply": False},
            "crs": mock_crs,
        }

        with (
            patch("dip_strike_tools.core.layer_creator.QgsVectorLayer", return_value=mock_layer),
            patch("dip_strike_tools.core.layer_creator.QgsProject"),
        ):
            creator = DipStrikeLayerCreator()
            layer = creator.create_dip_strike_layer(config, mock_crs)

            assert layer is not None
            assert layer.isValid()

    def test_create_dip_strike_layer_with_symbology(self):
        """Test creating a layer with symbology application."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_crs = Mock()
        mock_crs.authid.return_value = "EPSG:4326"
        mock_crs.isValid.return_value = True

        mock_layer = Mock()
        mock_layer.isValid.return_value = True
        mock_layer.id.return_value = "test_layer_id"

        config = {
            "name": "Test Layer",
            "format": "memory",
            "output_path": "",  # Memory layers don't need a path
            "format_info": {"driver": "memory", "extension": "", "description": "Memory layer"},
            "symbology": {"apply": True},
            "crs": mock_crs,
        }

        with (
            patch("dip_strike_tools.core.layer_creator.QgsVectorLayer", return_value=mock_layer),
            patch("dip_strike_tools.core.layer_creator.QgsProject"),
            patch.object(DipStrikeLayerCreator, "apply_symbology", return_value=True),
        ):
            creator = DipStrikeLayerCreator()
            layer = creator.create_dip_strike_layer(config, mock_crs)

            assert layer is not None
            assert layer.isValid()

    def test_error_handling_invalid_layer(self):
        """Test error handling when layer creation fails."""
        try:
            from dip_strike_tools.core.layer_creator import DipStrikeLayerCreator, LayerCreationError
        except ImportError:
            pytest.skip("QGIS modules not available")

        mock_crs = Mock()
        mock_crs.authid.return_value = "EPSG:4326"
        mock_crs.isValid.return_value = True

        mock_layer = Mock()
        mock_layer.isValid.return_value = False  # Invalid layer

        config = {
            "name": "Test Layer",
            "format": "memory",
            "output_path": "",  # Memory layers don't need a path
            "format_info": {"driver": "memory", "extension": "", "description": "Memory layer"},
            "symbology": {"apply": False},
            "crs": mock_crs,
        }

        with (
            patch("dip_strike_tools.core.layer_creator.QgsVectorLayer", return_value=mock_layer),
            patch("dip_strike_tools.core.layer_creator.QgsProject"),
        ):
            creator = DipStrikeLayerCreator()

            with pytest.raises(LayerCreationError):
                creator.create_dip_strike_layer(config, mock_crs)
