# -*- mode: python ; coding: utf-8 -*-
import os
project_root = os.path.abspath('.')

from PyInstaller.utils.hooks import collect_submodules
hiddenimports = collect_submodules('client')

a = Analysis(
    ['client/main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('client/agent/proxy/mitmproxy.exe', 'client/agent/proxy/mitmproxy.exe'),
        ('client/agent/proxy/block_domain.py', 'client/agent/proxy/block_domain.py'),
        ('client/agent/proxy/mitmproxy-ca-cert.pem', 'client/agent/proxy/mitmproxy-ca-cert.pem'),
    ],



    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='surfshield',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 改为 True 可看运行日志窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,  # ✅ 保持管理员启动，防证书安装失败
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='surfshield'
)
