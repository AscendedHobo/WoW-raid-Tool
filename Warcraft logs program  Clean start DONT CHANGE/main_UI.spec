# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import tkinterdnd2

block_cipher = None

# Get tkinterdnd2 location
tkdnd_path = Path(tkinterdnd2.__file__).parent

a = Analysis(
    ['main_UI.py'],
    pathex=[],
    binaries=[],
    datas=[
        (str(tkdnd_path), 'tkinterdnd2'),
    ],
    hiddenimports=[],
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
    name='Combat_Visualizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
) 