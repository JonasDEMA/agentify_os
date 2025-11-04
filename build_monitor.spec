# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for CPA Monitor executable."""

block_cipher = None


a = Analysis(
    ['agents/desktop_rpa/ui/run_monitor.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env', '.'),
    ],
    hiddenimports=[
        'agents.desktop_rpa.cognitive.cognitive_executor',
        'agents.desktop_rpa.cognitive.llm_wrapper',
        'agents.desktop_rpa.cognitive.models',
        'agents.desktop_rpa.config.settings',
        'openai',
        'pydantic',
        'pyautogui',
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
    name='CPA_Monitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)

