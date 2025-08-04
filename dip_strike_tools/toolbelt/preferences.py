#! python3  # noqa: E265

"""
Plugin settings.
"""

# standard
from dataclasses import asdict, dataclass, fields

# PyQGIS
from qgis.core import QgsSettings

# package
import dip_strike_tools.toolbelt.log_handler as log_hdlr
from dip_strike_tools.__about__ import __title__, __version__
from dip_strike_tools.toolbelt.env_var_parser import EnvVarParser

# ############################################################################
# ########## Classes ###############
# ##################################

PREFIX_ENV_VARIABLE = "QGIS_DIP_STRIKE_TOOLS_"


@dataclass
class PlgEnvVariableSettings:
    """Plugin settings from environnement variable"""

    def env_variable_used(self, attribute: str, default_from_name: bool = True) -> str:
        """Get environnement variable used for environnement variable settings

        :param attribute: attribute to check
        :type attribute: str
        :param default_from_name: define default environnement value from attribute name PREFIX_ENV_VARIABLE_<upper case attribute>
        :type default_from_name: bool
        :return: environnement variable used
        :rtype: str
        """
        settings_env_variable = asdict(self)
        env_variable = settings_env_variable.get(attribute, "")
        if not env_variable and default_from_name:
            env_variable = f"{PREFIX_ENV_VARIABLE}{attribute}".upper()
        return env_variable


@dataclass
class PlgSettingsStructure:
    """Plugin settings structure and defaults values."""

    # global
    debug_mode: bool = False
    version: str = __version__

    # geological types configuration
    geological_types: str = "1:Strata,2:Foliation,3:Fault,4:Joint,5:Cleavage"
    geo_type_storage_mode: str = "code"  # "code" or "description"


class PlgOptionsManager:
    @staticmethod
    def get_plg_settings() -> PlgSettingsStructure:
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings
        :rtype: PlgSettingsStructure
        """
        # get dataclass fields definition
        settings_fields = fields(PlgSettingsStructure)
        env_variable_settings = PlgEnvVariableSettings()

        # retrieve settings from QGIS/Qt
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # map settings values to preferences object
        li_settings_values = []
        for i in settings_fields:
            try:
                value = settings.value(key=i.name, defaultValue=i.default, type=i.type)
                # If environnement variable used, get value from environnement variable
                env_variable = env_variable_settings.env_variable_used(i.name)
                if env_variable:
                    value = EnvVarParser.get_env_var(env_variable, value)
                li_settings_values.append(value)
            except TypeError:
                li_settings_values.append(settings.value(key=i.name, defaultValue=i.default))

        # instanciate new settings object
        options = PlgSettingsStructure(*li_settings_values)

        settings.endGroup()

        return options

    @staticmethod
    def get_value_from_key(key: str, default=None, exp_type=None):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        if not hasattr(PlgSettingsStructure, key):
            field_names = [field.name for field in fields(PlgSettingsStructure)]
            log_hdlr.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(",".join(field_names)),
                log_level=1,
            )
            return None

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            out_value = settings.value(key=key, defaultValue=default, type=exp_type)
        except Exception as err:
            log_hdlr.PlgLogger.log(message="Error occurred trying to get settings: {}.Trace: {}".format(key, err))
            out_value = None

        settings.endGroup()

        return out_value

    @classmethod
    def set_value_from_key(cls, key: str, value) -> bool:
        """Set plugin QSettings value using the key.

        :param key: QSettings key
        :type key: str
        :param value: value to set
        :type value: depending on the settings
        :return: operation status
        :rtype: bool
        """
        if not hasattr(PlgSettingsStructure, key):
            field_names = [field.name for field in fields(PlgSettingsStructure)]
            log_hdlr.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(",".join(field_names)),
                log_level=2,
            )
            return False

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            settings.setValue(key, value)
            out_value = True
        except Exception as err:
            log_hdlr.PlgLogger.log(message="Error occurred trying to set settings: {}.Trace: {}".format(key, err))
            out_value = False

        settings.endGroup()

        return out_value

    @classmethod
    def save_from_object(cls, plugin_settings_obj: PlgSettingsStructure):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        settings = QgsSettings()
        settings.beginGroup(__title__)

        for k, v in asdict(plugin_settings_obj).items():
            cls.set_value_from_key(k, v)

        settings.endGroup()

    @staticmethod
    def get_geological_types() -> dict:
        """Get geological types from settings as a dictionary.

        :return: Dictionary with code as key and description as value
        :rtype: dict
        """
        settings = PlgOptionsManager.get_plg_settings()
        geo_types_string = settings.geological_types

        geo_types = {}
        try:
            # Parse the string format "1:Strata,2:Foliation,3:Fault,..."
            for item in geo_types_string.split(","):
                if ":" in item:
                    code, description = item.strip().split(":", 1)
                    geo_types[code.strip()] = description.strip()
        except Exception:
            # Fallback to default if parsing fails
            geo_types = {"1": "Strata", "2": "Foliation", "3": "Fault", "4": "Joint", "5": "Cleavage"}

        return geo_types

    @staticmethod
    def get_geo_type_storage_mode() -> str:
        """Get the geological type storage mode (code or description).

        :return: Storage mode - "code" or "description"
        :rtype: str
        """
        settings = PlgOptionsManager.get_plg_settings()
        return settings.geo_type_storage_mode

    @staticmethod
    def set_geological_types(geo_types: dict) -> bool:
        """Set geological types in settings.

        :param geo_types: Dictionary with code as key and description as value
        :type geo_types: dict
        :return: True if successful, False otherwise
        :rtype: bool
        """
        # Convert dictionary to string format
        geo_types_string = ",".join([f"{code}:{desc}" for code, desc in geo_types.items()])
        return PlgOptionsManager.set_value_from_key("geological_types", geo_types_string)

    @staticmethod
    def set_geo_type_storage_mode(mode: str) -> bool:
        """Set the geological type storage mode.

        :param mode: Storage mode - "code" or "description"
        :type mode: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        if mode not in ["code", "description"]:
            mode = "code"  # Default fallback
        return PlgOptionsManager.set_value_from_key("geo_type_storage_mode", mode)
