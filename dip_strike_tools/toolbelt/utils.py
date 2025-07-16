from functools import wraps

from ..toolbelt.log_handler import PlgLogger


def skip_file_not_found(func):
    """Decorator to catch FileNotFoundError exceptions."""

    @wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except FileNotFoundError as e:
            PlgLogger.log(f"File not found: {e}", log_level=1)

    return _wrapper
