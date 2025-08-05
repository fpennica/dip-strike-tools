"""Unit tests for layer_utils module."""

from unittest.mock import MagicMock

import pytest

from dip_strike_tools.core.layer_utils import check_layer_editability


@pytest.mark.unit
class TestLayerUtils:
    """Tests for layer utility functions."""

    def test_check_layer_editability_editable_layer(self):
        """Test layer editability check with an editable layer."""
        # Mock an editable layer
        mock_layer = MagicMock()
        mock_data_provider = MagicMock()
        mock_data_provider.name.return_value = "ogr"  # Not delimited text
        mock_layer.dataProvider.return_value = mock_data_provider
        mock_layer.isEditable.return_value = False
        mock_layer.startEditing.return_value = True
        mock_layer.rollBack.return_value = True

        is_editable, message = check_layer_editability(mock_layer, "testing")

        assert is_editable is True
        assert message == ""
        mock_layer.startEditing.assert_called_once()
        mock_layer.rollBack.assert_called_once()

    def test_check_layer_editability_delimited_text_layer(self):
        """Test layer editability check with a delimited text layer."""
        # Mock a delimited text layer
        mock_layer = MagicMock()
        mock_data_provider = MagicMock()
        mock_data_provider.name.return_value = "delimitedtext"
        mock_layer.dataProvider.return_value = mock_data_provider

        is_editable, message = check_layer_editability(mock_layer, "testing")

        assert is_editable is False
        assert "delimited text layer" in message.lower()
        assert "read-only" in message.lower()
        assert "testing" in message

    def test_check_layer_editability_non_editable_layer(self):
        """Test layer editability check with a non-editable layer."""
        # Mock a non-editable layer
        mock_layer = MagicMock()
        mock_data_provider = MagicMock()
        mock_data_provider.name.return_value = "some_readonly_provider"
        mock_layer.dataProvider.return_value = mock_data_provider
        mock_layer.isEditable.return_value = False
        mock_layer.startEditing.return_value = False  # Cannot start editing

        is_editable, message = check_layer_editability(mock_layer, "testing")

        assert is_editable is False
        assert "cannot be edited" in message.lower()
        assert "testing" in message

    def test_check_layer_editability_none_layer(self):
        """Test layer editability check with None layer."""
        is_editable, message = check_layer_editability(None, "testing")

        assert is_editable is True
        assert message == ""

    def test_check_layer_editability_default_operation_context(self):
        """Test layer editability check with default operation context."""
        # Mock a delimited text layer
        mock_layer = MagicMock()
        mock_data_provider = MagicMock()
        mock_data_provider.name.return_value = "delimitedtext"
        mock_layer.dataProvider.return_value = mock_data_provider

        is_editable, message = check_layer_editability(mock_layer)

        assert is_editable is False
        assert "delimited text layer" in message.lower()
        assert "working with" in message  # Default context
