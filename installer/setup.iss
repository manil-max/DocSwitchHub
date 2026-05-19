; DocSwitch Hub - Inno Setup Script (Updated)
; Creates a professional Windows installer
; Includes LibreOffice automatic installation and bundled .exe

#define MyAppName "DocSwitch Hub"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "manil-max"
#define MyAppURL "https://github.com/manil-max/DocSwitchHub"
#define MyAppExeName "DocSwitch.exe"

[Setup]
AppId={{D0C5W1TC-H4UB-2026-B3ST-SUiT3F0R3V3R}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\DocSwitchHub
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=Output
OutputBaseFilename=DocSwitchHub_Setup_v{#MyAppVersion}
SetupIconFile=..\docswitch_hub.ico
UninstallDisplayIcon={app}\docswitch_hub.ico
Compression=lzma2/ultra
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
DisableProgramGroupPage=no
UsePreviousTasks=yes
AlwaysShowDirOnReadyPage=yes
CloseApplications=yes
RestartIfNeededByRun=yes
Uninstallable=yes
ShowLanguageDialog=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunch"; Description: "Add to Quick Launch"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "install_libreoffice"; Description: "Download and install LibreOffice (required for conversions)"; GroupDescription: "Dependencies"; Flags: checked

[Files]
; Bundled PyInstaller executable and data
Source: "AppFiles\DocSwitch.exe"; DestDir: "{app}"; Flags: ignoreversion; Permissions: everyone-read
Source: "AppFiles\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

; Documentation
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

; LibreOffice offline installer (optional - downloaded during install if task selected)
; Source: "LibreOfficePortable.exe"; DestDir: "{tmp}"; Flags: external

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\docswitch_hub.ico"; Comment: "Document converter and media tool"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\docswitch_hub.ico"; Tasks: desktopicon; Comment: "Document converter and media tool"
Name: "{autoquicklaunch}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\docswitch_hub.ico"; Tasks: quicklaunch; Comment: "Document converter and media tool"

[Run]
; LibreOffice download and install if task selected
Filename: "https://www.libreoffice.org/download/download/"; Description: "Download LibreOffice (if not installed)"; Flags: shellexec skipifsilent; Tasks: install_libreoffice
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: postinstall nowait skipifsilent shellexec

[Registry]
; Add to Windows Search/Start Menu
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\DocSwitchHub"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\DocSwitchHub"; ValueType: string; ValueName: "Path"; ValueData: "{app}"; Flags: uninsdeletekey

[UninstallDelete]
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{localappdata}\DocSwitch"
Type: files; Name: "{app}\DocSwitch.log"

[Code]
const
  LIBREOFFICE_DOWNLOAD_URL = 'https://www.libreoffice.org/download/download/';

function IsLibreOfficeInstalled: Boolean;
begin
  Result := FileExists('C:\Program Files\LibreOffice\program\soffice.exe') or
            FileExists('C:\Program Files (x86)\LibreOffice\program\soffice.exe');
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    if not IsLibreOfficeInstalled then
    begin
      if MsgBox('LibreOffice is not installed. Document conversions require LibreOffice.' + #13 +
                'Would you like to download it now?', mbQuestion, MB_YESNO) = mrYes then
      begin
        ShellExecute('open', LIBREOFFICE_DOWNLOAD_URL, '', '', SW_SHOW);
      end;
    end;
  end;
end;

procedure DeinitializeSetup();
begin
  if IsTaskSelected('install_libreoffice') and not IsLibreOfficeInstalled then
  begin
    MsgBox('LibreOffice installation will open in your browser.' + #13 +
           'Please install the latest version and run DocSwitch Hub again.', mbInformation, MB_OK);
  end;
end;
