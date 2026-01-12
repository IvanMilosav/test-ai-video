# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Video Analyzer GUI
Packages the application into a standalone executable
"""

block_cipher = None

a = Analysis(
    ['video_analyzer_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('master_clip_ontology.txt', '.'),
        ('script_clip_brain.txt', '.'),
        ('DATA_LOCATION_GUIDE.txt', '.'),
        ('icon.png', '.'),
        ('icon.ico', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinterdnd2',
        'google.generativeai',
        'dotenv',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

# For macOS app bundle
app = BUNDLE(
    exe,
    name='VideoAnalyzer.app',
    icon='icon.ico',
    bundle_identifier='com.videoanalyzer.app',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.0.0',
    },
)
