# installer.iss
[Setup]
AppName=Web Shortcut Creator
AppVersion=1.1.1
DefaultDirName={pf}\WebShortcutCreator
DefaultGroupName=Web Shortcut Creator
OutputDir=dist
OutputBaseFilename=WebShortcutCreator_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\web_shortcut_creator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "asserts\*"; DestDir: "{app}\asserts"; Flags: ignoreversion recursesubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\Web Shortcut Creator"; Filename: "{app}\web_shortcut_creator.exe"
Name: "{commondesktop}\Web Shortcut Creator"; Filename: "{app}\web_shortcut_creator.exe"

[Run]
Filename: "{app}\web_shortcut_creator.exe"; Description: "Launch Web Shortcut Creator"; Flags: postinstall nowait

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := MsgBox(
    'Welcome to Web Shortcut Creator Installation' + #13#10 + #13#10 +
    'This application will:' + #13#10 +
    '1. Run in the background to manage your web shortcuts' + #13#10 +
    '2. Start automatically with Windows' + #13#10 +
    '3. Create global hotkeys (Ctrl+Alt+Key) for your shortcuts' + #13#10 +
    '4. Require administrator privileges for proper functionality' + #13#10 + #13#10 +
    'Do you agree to these terms and want to continue with the installation?',
    mbInformation,
    MB_YESNO
  ) = IDYES;
end;