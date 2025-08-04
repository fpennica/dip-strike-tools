def classFactory(iface):
    """Load the plugin class.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .plugin_main import DipStrikeToolsPlugin

    return DipStrikeToolsPlugin(iface)
