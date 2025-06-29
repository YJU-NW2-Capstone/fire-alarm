# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Fire_ui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('source/찐메인.png', 'source'),
        ('source/image-removebg-preview.png', 'source'),
        ('source/main_sound.mp3', 'source'),
        ('source/floor3.png', 'source'),
    ],
    hiddenimports=[
        'win10toast',
        'plyer',
        'plyer.platforms.win.notification',  # plyer 알림이 필요한 경우
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Fire_ui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='source/icon.ico',  # 아이콘 파일이 있다면 추가
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Fire_ui',
)
