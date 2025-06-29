#! python3  # noqa: E265

"""
Core mathematical functions for dip and strike calculations.

This module provides unified calculation functions for converting between
dip and strike azimuths, with support for rounding and value validation.
"""

from typing import Any, Optional, Tuple, Union


def validate_azimuth_range(azimuth: Any) -> bool:
    """Validate that an azimuth value is within the valid 0-360° range.

    :param azimuth: Azimuth value to validate
    :type azimuth: Any
    :return: True if valid, False otherwise
    :rtype: bool
    """
    try:
        if azimuth is None:
            return False
        value = float(azimuth)
        return 0.0 <= value <= 360.0
    except (ValueError, TypeError):
        return False


def normalize_azimuth(azimuth: float) -> float:
    """Normalize an azimuth value to the 0-360° range.

    :param azimuth: Azimuth value to normalize
    :type azimuth: float
    :return: Normalized azimuth value
    :rtype: float
    """
    return azimuth % 360.0


def calculate_dip_from_strike(
    strike_azimuth: Union[float, int, str, None], decimal_places: int = 2
) -> Optional[float]:
    """Calculate dip azimuth from strike azimuth.

    Dip azimuth is perpendicular to strike azimuth.
    We add 90° and normalize to 0-360° range.

    :param strike_azimuth: Strike azimuth in degrees
    :type strike_azimuth: Union[float, int, str, None]
    :param decimal_places: Number of decimal places to round to
    :type decimal_places: int
    :return: Dip azimuth in degrees, or None if input is invalid
    :rtype: Optional[float]
    """
    if strike_azimuth is None:
        return None

    try:
        dip_azimuth = float(strike_azimuth) + 90.0
        # Normalize to 0-360 range
        normalized = normalize_azimuth(dip_azimuth)
        # Round to specified decimal places
        return round(normalized, decimal_places)
    except (ValueError, TypeError):
        return None


def calculate_strike_from_dip(dip_azimuth: Union[float, int, str, None], decimal_places: int = 2) -> Optional[float]:
    """Calculate strike azimuth from dip azimuth.

    Strike azimuth is perpendicular to dip azimuth.
    We subtract 90° and normalize to 0-360° range.

    :param dip_azimuth: Dip azimuth in degrees
    :type dip_azimuth: Union[float, int, str, None]
    :param decimal_places: Number of decimal places to round to
    :type decimal_places: int
    :return: Strike azimuth in degrees, or None if input is invalid
    :rtype: Optional[float]
    """
    if dip_azimuth is None:
        return None

    try:
        strike_azimuth = float(dip_azimuth) - 90.0
        # Normalize to 0-360 range
        normalized = normalize_azimuth(strike_azimuth)
        # Round to specified decimal places
        return round(normalized, decimal_places)
    except (ValueError, TypeError):
        return None


def convert_azimuth_with_true_north(azimuth: float, true_north_bearing: float, from_true_north: bool = False) -> float:
    """Convert azimuth between map/screen relative and true north relative values.

    :param azimuth: Input azimuth value
    :type azimuth: float
    :param true_north_bearing: True north bearing adjustment
    :type true_north_bearing: float
    :param from_true_north: If True, convert from true north to map relative.
                           If False, convert from map relative to true north.
    :type from_true_north: bool
    :return: Converted azimuth value
    :rtype: float
    """
    if from_true_north:
        # Convert from true north to map relative
        return normalize_azimuth(azimuth + true_north_bearing)
    else:
        # Convert from map relative to true north
        return normalize_azimuth(azimuth - true_north_bearing)


def get_strike_and_dip_from_azimuth(
    azimuth: float,
    is_strike_mode: bool = True,
    true_north_bearing: float = 0.0,
    apply_true_north: bool = False,
    decimal_places: int = 2,
) -> Tuple[float, float]:
    """Convert azimuth input to both strike and dip values.

    This function handles the conversion logic used in the insert dialog,
    where the user can input either strike or dip direction and get both values.

    :param azimuth: Input azimuth value
    :type azimuth: float
    :param is_strike_mode: True if azimuth represents strike, False if dip
    :type is_strike_mode: bool
    :param true_north_bearing: True north bearing for adjustment
    :type true_north_bearing: float
    :param apply_true_north: Whether to apply true north adjustment
    :type apply_true_north: bool
    :param decimal_places: Number of decimal places to round to
    :type decimal_places: int
    :return: Tuple of (strike_azimuth, dip_azimuth)
    :rtype: Tuple[float, float]
    """
    if is_strike_mode:
        # Azimuth represents strike direction - use directly
        strike_azimuth = azimuth
    else:
        # Azimuth represents dip direction - convert to strike (perpendicular)
        # Dip direction is 90° clockwise from strike direction
        # So strike direction is 90° counter-clockwise from dip direction
        strike_azimuth = normalize_azimuth(azimuth - 90)

    # Calculate dip from strike
    dip_azimuth = normalize_azimuth(strike_azimuth + 90)

    # Apply true north adjustment if enabled
    if apply_true_north:
        strike_azimuth = convert_azimuth_with_true_north(strike_azimuth, true_north_bearing, from_true_north=False)
        dip_azimuth = convert_azimuth_with_true_north(dip_azimuth, true_north_bearing, from_true_north=False)

    # Round to specified decimal places
    return (round(strike_azimuth, decimal_places), round(dip_azimuth, decimal_places))
