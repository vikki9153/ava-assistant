#define MyAppVersion "1.0.0"
[Setup]
AppName=Ava Assistant
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\Ava Assistant
DefaultGroupName=Ava Assistant
OutputBaseFilename=AvaAssistantInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\\AvaAssistant.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\Ava Assistant"; Filename: "{app}\\AvaAssistant.exe"
