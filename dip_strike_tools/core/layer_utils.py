"""
Utilities for working with QGIS layers.

This module provides common functionality for layer operations that are shared
across multiple parts of the plugin.
"""

from qgis.PyQt.QtCore import QCoreApplication


def check_layer_editability(layer, operation_context="working with"):
    """Check if a layer can be edited and return status message.

    :param layer: Layer to check
    :type layer: QgsVectorLayer
    :param operation_context: Context description for error messages (e.g., "calculating values", "inserting features")
    :type operation_context: str
    :return: Tuple of (is_editable, message)
    :rtype: tuple[bool, str]
    """
    if layer is None:
        return True, ""

    # Check if layer supports editing by trying to detect read-only layers
    provider_type = layer.dataProvider().name()

    if provider_type.lower() == "delimitedtext":
        return False, QCoreApplication.translate(
            "LayerUtils",
            "This is a delimited text layer which is read-only. "
            "Please save the layer to an editable format (e.g., Shapefile, GeoPackage) "
            "using 'Export > Save Features As...' before {operation_context}.",
        ).format(operation_context=operation_context)

    # Try to check if layer can be edited by attempting to start edit mode
    if not layer.isEditable():
        can_edit = layer.startEditing()
        if not can_edit:
            return False, QCoreApplication.translate(
                "LayerUtils",
                "This layer cannot be edited. Please save the layer to an editable format before {operation_context}.",
            ).format(operation_context=operation_context)
        # If we successfully started editing, rollback since we don't want to keep it in edit mode yet
        layer.rollBack()

    return True, ""
