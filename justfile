PLUGIN_SLUG := "dip_strike_tools"

# default recipe to display help information
default:
  @just --list

# create venv with uv on linux, automatically detecting system python version and qgis path
create-venv:
    #!/bin/bash
    set -euo pipefail

    # Detect system Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "Detected system Python version: $PYTHON_VERSION"

    # Try to find QGIS Python libraries in common locations
    QGIS_PYTHON_LIB_PATH=""
    for path in "/usr/lib/python${PYTHON_VERSION}/site-packages" "/usr/share/qgis/python" "/usr/local/lib/python${PYTHON_VERSION}/site-packages"; do
        if [ -d "$path/qgis" ]; then
            QGIS_PYTHON_LIB_PATH="$path"
            echo "Found QGIS libraries at: $QGIS_PYTHON_LIB_PATH"
            break
        fi
    done

    if [ -z "$QGIS_PYTHON_LIB_PATH" ]; then
        echo "Warning: Could not find QGIS Python libraries. Using default path."
        QGIS_PYTHON_LIB_PATH="/usr/lib/python${PYTHON_VERSION}/site-packages"
    fi

    # Create virtual environment
    rm -rf .venv
    uv venv --system-site-packages --python "$PYTHON_VERSION"
    echo "$QGIS_PYTHON_LIB_PATH" > .venv/lib/python${PYTHON_VERSION}/site-packages/qgis.pth
    uv sync --all-groups
    uv run qgis-plugin-ci changelog latest

# create venv with manual python version and qgis path (for special cases)
create-venv-manual PYTHON_VERSION QGIS_PYTHON_LIB_PATH:
    rm -rf .venv
    uv venv --system-site-packages --python "{{ PYTHON_VERSION }}"
    echo "{{ QGIS_PYTHON_LIB_PATH }}" > .venv/lib/python{{ PYTHON_VERSION }}/site-packages/qgis.pth
    uv sync --all-groups
    uv run qgis-plugin-ci changelog latest

# create symbolic links for development
dev-link QGIS_PLUGIN_PATH="~/.local/share/QGIS/QGIS3/profiles/default/python/plugins":
    #!/bin/bash
    # Ensure the target directory exists
    mkdir -p {{ QGIS_PLUGIN_PATH }}
    rm -rf {{ QGIS_PLUGIN_PATH }}/{{ PLUGIN_SLUG }}

    # Create a relative path symlink
    PLUGIN_SOURCE=$(pwd)/{{ PLUGIN_SLUG }}
    cd {{ QGIS_PLUGIN_PATH }}
    ln -sf $(python3 -c "import os; print(os.path.relpath('$PLUGIN_SOURCE', os.getcwd()))")
    cd -

    # Create symlinks for supporting files
    ln -sf $(pwd)/LICENSE $(pwd)/{{ PLUGIN_SLUG }}/LICENSE
    ln -sf $(pwd)/CREDITS.md $(pwd)/{{ PLUGIN_SLUG }}/CREDITS.md
    ln -sf $(pwd)/CHANGELOG.md $(pwd)/{{ PLUGIN_SLUG }}/CHANGELOG.md

    # Show success message
    echo "Plugin symlink created at {{ QGIS_PLUGIN_PATH }}/{{ PLUGIN_SLUG }}"

@bootstrap-dev: create-venv dev-link trans-compile

@update-deps:
    uv lock --upgrade

trans-update:
    uv run pylupdate5 -noobsolete -verbose ./{{ PLUGIN_SLUG }}/resources/i18n/plugin_translation.pro

trans-compile:
    uv run lrelease ./{{ PLUGIN_SLUG }}/resources/i18n/*.ts

docs-autobuild:
    uv sync --group docs
    uv run sphinx-autobuild -b html docs/ docs/_build --port 8000

docs-build-html:
    uv sync --group docs
    uv run sphinx-build -b html -j auto -d docs/_build/cache -q docs docs/_build/html

docs-build-pdf:
    #!/bin/bash
    set -e
    uv sync --group docs
    uv run sphinx-build -b latex -j auto -d docs/_build/cache -q docs docs/_build/latex
    pushd docs/_build/latex
    latexmk -pdf -dvi- -ps- -interaction=nonstopmode -halt-on-error dipstriketools.tex
    popd

# Run tests with pytest and coverage info
test:
    uv sync --no-group ci
    uv sync --group testing
    uv run pytest -v --cov={{ PLUGIN_SLUG }} --cov-report=term-missing

@package VERSION:
    #!/bin/bash
    uv sync --group ci
    cp --remove-destination LICENSE {{ PLUGIN_SLUG }}/
    cp --remove-destination CHANGELOG.md {{ PLUGIN_SLUG }}/
    cp --remove-destination CREDITS.md {{ PLUGIN_SLUG }}/
    # remove rule for compiled translations from .gitignore
    sed -i "s|^\*\.qm|# \*\.qm|" .gitignore
    git add .
    uv run qgis-plugin-ci package -c {{ VERSION }}
    just dev-link
    # add compiled translations to gitignore
    sed -i "s|^# \*\.qm|\*\.qm|" .gitignore
    git reset

@release-test VERSION:
    #!/bin/bash
    uv sync --group ci
    cp --remove-destination LICENSE {{ PLUGIN_SLUG }}/
    cp --remove-destination CHANGELOG.md {{ PLUGIN_SLUG }}/
    cp --remove-destination CREDITS.md {{ PLUGIN_SLUG }}/
    sed -i "s|^\*\.qm|# \*\.qm|" .gitignore
    git add .
    # run qgis-plugin-ci release without github token and osgeo auth
    uv run qgis-plugin-ci release -c {{ VERSION }}
    just dev-link
    sed -i "s|^# \*\.qm|\*\.qm|" .gitignore
    git reset

qgis-ltr-pull:
    docker pull qgis/qgis:ltr

# start latest QGIS LTR version with docker on Linux
qgis-docker VERSION="ltr" QGIS_PYTHON_PATH=".local/share/QGIS/QGIS3/profiles/default/python":
    #!/bin/bash
    # Allow local X server connections
    xhost +local:

    # Define paths and variables
    USER_ID=$(id -u)
    GROUP_ID=$(id -g)

    # Create necessary directories with correct permissions
    TEMP_DIR=$(mktemp -d)
    mkdir -p ${TEMP_DIR}/certificates
    mkdir -p ${TEMP_DIR}/qgis_config/{processing,profile,cache,data/expressions}
    mkdir -p ${TEMP_DIR}/qgis_config/python/expressions

    # Copy and set permissions for certificates
    cp -L /etc/ssl/certs/ca-certificates.crt ${TEMP_DIR}/certificates/
    chmod 644 ${TEMP_DIR}/certificates/ca-certificates.crt

    # Set permissions for QGIS config directories
    chmod -R 777 ${TEMP_DIR}/qgis_config

    # Create an empty qgis.db file that QGIS can write to
    touch ${TEMP_DIR}/qgis_config/data/qgis.db
    chmod 666 ${TEMP_DIR}/qgis_config/data/qgis.db

    # Ensure plugin directory exists in host
    mkdir -p ${HOME}/{{ QGIS_PYTHON_PATH }}/plugins

    # Run QGIS in container with proper mounts and environment
    docker run --rm --name qgis_ltr \
        -it \
        -e DISPLAY=unix$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        -v ${HOME}/{{ QGIS_PYTHON_PATH }}/plugins:/home/qgis/.local/share/QGIS/QGIS3/profiles/default/python/plugins \
        -v $(pwd)/{{ PLUGIN_SLUG }}:/home/qgis/.local/share/QGIS/QGIS3/profiles/default/python/plugins/{{ PLUGIN_SLUG }} \
        -v ${HOME}:/home/host \
        -v ${TEMP_DIR}/certificates:/etc/ssl/certs:ro \
        -v ${TEMP_DIR}/qgis_config/processing:/home/qgis/.local/share/QGIS/QGIS3/profiles/default/processing \
        -v ${TEMP_DIR}/qgis_config/profile:/home/qgis/.config/QGIS \
        -v ${TEMP_DIR}/qgis_config/cache:/home/qgis/.cache/QGIS \
        -v ${TEMP_DIR}/qgis_config/data:/home/qgis/.local/share/QGIS/QGIS3/profiles/default \
        -v ${TEMP_DIR}/qgis_config/python/expressions:/home/qgis/.local/share/QGIS/QGIS3/profiles/default/python/expressions \
        -e HOME=/home/qgis \
        -e QT_X11_NO_MITSHM=1 \
        -e SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
        -e PYTHONHOME= \
        --user ${USER_ID}:${GROUP_ID} \
        qgis/qgis:{{ VERSION }} qgis

    # Clean up temporary directory
    rm -rf ${TEMP_DIR}

# run pyqt6 migration script: https://github.com/qgis/QGIS/wiki/Plugin-migration-to-be-compatible-with-Qt5-and-Qt6
pyqt5-to-pyqt6:
    #!/bin/bash
    # no way to ignore files, so edits to toolbelt/qt_compat.py must be discarded
    docker run --rm -v "$(pwd):/home/pyqgisdev/" registry.gitlab.com/oslandia/qgis/pyqgis-4-checker/pyqgis-qt-checker:latest pyqt5_to_pyqt6.py --logfile /home/pyqgisdev/pyqt6_checker.log .
