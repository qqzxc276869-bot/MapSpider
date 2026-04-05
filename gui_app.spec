# -*- mode: python ; coding: utf-8 -*-


import os
import customtkinter

# Find customtkinter directory to bundle theme assets
ctk_path = os.path.dirname(customtkinter.__file__)

a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[(ctk_path, 'customtkinter')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'torchvision', 'torchaudio', 'pygame', 'scipy', 'matplotlib', 'cryptography', 'IPython', 'PIL', 'tk', 'tcl'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LeadMagnetPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
)
