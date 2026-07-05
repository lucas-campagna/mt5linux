import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

datas = [
    ('mt5linux', 'mt5linux'),
]

hiddenimports = [
    'rpyc',
    'rpyc.cli',
    'rpyc.cli.rpyc_classic',
    'rpyc.core',
    'rpyc.core.service',
    'rpyc.core.channel',
    'rpyc.lib',
    'rpyc.utils',
    'rpyc.utils.classic',
    'mt5linux',
    'mt5linux.metatrader5',
    'mt5linux.constants',
    'ctypes',
    'socket',
    'threading',
    'time',
    'datetime',
    'struct',
    'collections',
    'inspect',
    'weakref',
    'copy',
    'functools',
    'typing',
    'numpy',
    'plumbum',
    'pyparsing',
]

a = Analysis(
    ['mt5linux/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='mt5server',
    debug=False,
    bootloader_warning=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
