[Setup]
AppName=Devops God Mode
AppVersion=1.0
DefaultDirName={pf}\DevopsGodMode
DefaultGroupName=Devops God Mode
OutputDir=dist
OutputBaseFilename=GodModeSetup
Compression=lzma
SolidCompression=yes
SetupIconFile=favicon.ico

[Files]
Source: "dist\launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "backend\*"; DestDir: "{app}\backend"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\Devops God Mode"; Filename: "{app}\launcher.exe"
Name: "{commondesktop}\Devops God Mode"; Filename: "{app}\launcher.exe"

[Run]
Filename: "{app}\launcher.exe"; Description: "Start God Mode"; Flags: nowait postinstall skipifsilent
