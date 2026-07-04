# -*- mode: python ; coding: utf-8 -*-
# Windowed onedir build of the GUI. Build from the repo root:
#     pyinstaller --noconfirm packaging/psarc2feedpak.spec
# The vgmstream/ffmpeg binaries are NOT bundled here; the release workflow drops
# them into the dist folder next to the .exe, where audio.find() looks for them.

import os
root = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    [os.path.join(SPECPATH, 'entry_gui.py')],
    pathex=[root],
    binaries=[],
    datas=[],
    hiddenimports=['construct', 'cryptography'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='psarc2feedpak',
    console=False,
    disable_windowed_traceback=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='psarc2feedpak',
)
