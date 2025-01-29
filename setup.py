import PyInstaller.__main__

PyInstaller.__main__.run([
    'web_shortcut_creator.py',
    '--onefile',
    '--windowed',
    '--add-data=asserts;asserts',
    '--icon=asserts/tray_icon.ico',
    '--hidden-import=win32timezone',
    '--name=web_shortcut_creator'
])