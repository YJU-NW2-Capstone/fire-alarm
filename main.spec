# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Fire_ui.py'],
    pathex=['.'],  # 현재 경로
    binaries=[],
    datas=[('source/*', 'source')],  # 리소스 파일 추가
    hiddenimports=[],
    hookspath=[],
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
    [],
    exclude_binaries=True,
    name='HotSpot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='source/icon.ico',  # 아이콘 설정
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HotSpot',  # 앱 이름 변경
)