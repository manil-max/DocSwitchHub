# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for DocSwitch Hub

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys

block_cipher = None

# Collect all data files from packages
datas = [
    ('static', 'static'),
    ('templates', 'templates'),
]

# Collect data files from dependencies
datas += collect_data_files('flask')
datas += collect_data_files('werkzeug')
datas += collect_data_files('jinja2')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'flask',
        'werkzeug',
        'jinja2',
        'PIL',
        'pypdf',
        'fitz',
        'pymupdf',
        'pdf2docx',
        'docx2pdf',
        'rembg',
        'yt_dlp',
        'scanner',
        'security_auditor',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
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
    name='DocSwitch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='docswitch_hub.ico',  # Add icon
)
