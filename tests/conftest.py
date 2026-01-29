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

import importlib
import os
import traceback
from unittest.mock import MagicMock

import pytest

# Set QGIS prefix path from environment variable if defined
# if os.environ.get("QGIS_PREFIX_PATH"):
#     from qgis.core import QgsApplication

#     QgsApplication.setPrefixPath(os.environ.get("QGIS_PREFIX_PATH"), True)


GUI_TIMEOUT_DEFAULT = 2000  # milliseconds


@pytest.fixture(scope="session")
def gui_timeout(pytestconfig):
    """
    Determine timeout in milliseconds for GUI tests based on environment settings and pytest options.
    """
    is_gui_disabled = pytestconfig.getoption("qgis_disable_gui") or os.environ.get("QT_QPA_PLATFORM") == "offscreen"
    timeout_secs = os.environ.get("GUI_TIMEOUT")
    if timeout_secs is not None:
        try:
            timeout_secs = int(timeout_secs)
        except (TypeError, ValueError):
            timeout_secs = None

    return 0 if is_gui_disabled else (timeout_secs * 1000 if timeout_secs is not None else GUI_TIMEOUT_DEFAULT)


@pytest.fixture(autouse=True)
def patch_qgis_error_dialogs(monkeypatch):
    """
    Patch QGIS error dialogs to prevent modal dialogs from appearing during tests.

    This fixture is automatically applied to all tests and patches qgis.utils functions
    to print exceptions to console instead of showing modal dialogs.
    Based on: https://github.com/qgis/QGIS/blob/master/.docker/qgis_resources/test_runner/qgis_startup.py
    """
    try:
        from qgis import utils
        from qgis.core import Qgis

        def _showException(type, value, tb, msg, messagebar=False, level=Qgis.MessageLevel.Warning):  # type: ignore
            """Print exception instead of showing a dialog."""
            print(msg)
            logmessage = ""
            for s in traceback.format_exception(type, value, tb):
                # Handle both str (Python 3) and bytes (potential legacy)
                logmessage += s.decode("utf-8", "replace") if hasattr(s, "decode") else s  # type: ignore
            print(logmessage)

        def _open_stack_dialog(type, value, tb, msg, pop_error=True):  # type: ignore
            """Print exception instead of opening stack trace dialog."""
            print(msg)

        monkeypatch.setattr(utils, "showException", _showException)
        monkeypatch.setattr(utils, "open_stack_dialog", _open_stack_dialog)
    except ImportError:
        # QGIS not available, skip patching
        pass


@pytest.fixture()
def plugin(qgis_iface, monkeypatch):
    """Fixture that imports the plugin main class lazily and returns the class."""
    # mock qgis_iface.projectRead signal
    monkeypatch.setattr(qgis_iface, "projectRead", MagicMock(), raising=False)
    mod = importlib.import_module("dip_strike_tools.plugin_main")
    return mod.DipStrikeToolsPlugin


def pytest_collection_modifyitems(session, config, items):
    """Modify the order of collected tests to run unit tests first, then integration, then e2e.

    This hook reorders test items based on their location in the test directory structure:
    - tests/unit/ → executed first
    - tests/integration/ → executed second
    - tests/e2e/ → executed last

    Also applies appropriate markers to each test based on its location.
    """
    unit = []
    integration = []
    e2e = []
    other = []

    for item in items:
        # Use the normalized path string to determine test category
        test_path = str(item.fspath).replace("\\", "/")

        if "/tests/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
            unit.append(item)
        elif "/tests/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
            integration.append(item)
        elif "/tests/e2e/" in test_path:
            item.add_marker(pytest.mark.e2e)
            e2e.append(item)
        else:
            other.append(item)

    # Reorder: unit first, then integration, then e2e, then any other tests
    items[:] = unit + integration + e2e + other
