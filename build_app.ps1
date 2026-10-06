# Build script for Ava voice assistant (Windows)
# Usage: run this script from PowerShell in the project root

Write-Output "Installing PyInstaller (if missing)..."
py -m pip install --upgrade pip
py -m pip install pyinstaller

Write-Output "Running PyInstaller to build single-file executable..."
# Include settings and custom commands if present (Windows uses ';' as path separator in --add-data)
pyinstaller --onefile --noconsole --name "AvaAssistant" --add-data "va_settings.json;." --add-data "custom_commands.json;." voice_assistant.py

Write-Output "Build finished. See the 'dist' folder for AvaAssistant.exe"
