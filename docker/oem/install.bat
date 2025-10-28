@echo off
setlocal

REM Set installer URL and local path
set "QGIS_URL=https://qgis.org/downloads/QGIS-OSGeo4W-3.40.11-1.msi"
set "QGIS_MSI=%SystemDrive%\OEM\QGIS-OSGeo4W-3.40.11-1.msi"

REM Download QGIS installer if not already present
if not exist "%QGIS_MSI%" (
    curl.exe -L -o "%QGIS_MSI%" "%QGIS_URL%"
)

REM Install QGIS silently
msiexec /i "%QGIS_MSI%" /qn /norestart
REM del "%QGIS_MSI%"

REM map network drive for shared folder
net use Z: \\host.lan\Data

REM create plugin symbolic link inside QGIS default profile
if not exist "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\" (
    mkdir "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins"
)
mklink /D "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\dip_strike_tools" "Z:\GIT\dip-strike-tools\dip_strike_tools"
endlocal
