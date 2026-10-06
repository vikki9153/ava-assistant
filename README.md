# Personal Voice Assistant

This is a Windows desktop personal assistant inspired by Alexa and Siri. It listens for a wake word, understands Hindi and English commands, opens apps, performs quick actions, and responds in a more natural assistant tone.

## Features

- Wake phrase: "Hey assistant" or "Namaste assistant"
- Hindi + English recognition
- Open apps such as WhatsApp, Teams, Chrome, VS Code, Notepad, Calculator
- Quick search in Google
- Time and date responses
- Study mode and work mode shortcuts
- Natural spoken replies with a female voice preference when available

## Install

1. Install Python 3.12 from Python.org or winget.
2. Open a terminal in this folder.
3. Run:

```bash
py -m pip install -r requirements.txt
```

If `pyaudio` fails to install, use:

```bash
py -m pip install pipwin
py -m pipwin install pyaudio
```

## Run

```bash
py voice_assistant.py
```

## Build a Windows executable

Run the bundled PowerShell script to install PyInstaller (if needed) and build a single-file executable:

```powershell
cd /d "e:\new project"
.\build_app.ps1
```
cd /d "e:\new project"
.\build_app.ps1
The built exe will be at `dist\AvaAssistant.exe`.

## CI build + release (auto-deploy)

You can set up GitHub Actions to build and publish the Windows exe automatically when you push a tag.

1. Create a new public or private GitHub repository and push this project to it.
2. Add any repository secrets if needed (not required for the default workflow).
3. Create a release by pushing a tag (for example `git tag v1.0 && git push --tags`) or trigger the workflow via the Actions tab.
4. The workflow builds `AvaAssistant.exe` and attaches it to a GitHub Release; you can then download the exe from the release page and run it on your laptop.

Notes:
- GitHub Actions runs on GitHub's Windows runners; the produced exe is ready for download from the Release assets.
- For private repos, ensure you have permissions to download release assets from the repository.

## Example commands

- "Hey assistant"
- "Open WhatsApp"
- "Open Teams"
- "Open Chrome"
- "Open VS Code"
- "Study mode"
- "Work mode"
- "What time is it?"
- "Search Python tutorials"
- "Bye"

## Notes

This is a lightweight local assistant designed for personal use on Windows. It runs fully on your laptop and does not require a cloud service for the main command actions.
