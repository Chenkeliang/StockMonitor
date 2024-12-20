#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

print_message() {
    echo -e "${GREEN}[安装程序]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 检查图标文件
if [ ! -f "icons/icon.icns" ]; then
    print_error "缺少图标文件 icons/icon.icns"
    exit 1
fi

# 清理旧文件
print_message "清理旧文件..."
rm -rf build dist *.spec venv

# 创建虚拟环境
print_message "创建虚拟环境..."
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
print_message "安装依赖..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

# 创建 spec 文件
print_message "创建打包配置..."
cat > stock_monitor.spec << EOL
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['stock_monitor/ui/menubar.py'],
    pathex=[],
    binaries=[],
    datas=[('icons/*', 'icons')],
    hiddenimports=['rumps', 'matplotlib', 'numpy', 'requests'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Stock Monitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Stock Monitor',
)

app = BUNDLE(
    coll,
    name='Stock Monitor.app',
    icon='icons/icon.icns',
    bundle_identifier='com.stockmonitor.app',
    info_plist={
        'LSUIElement': True,
        'CFBundleName': 'Stock Monitor',
        'CFBundleDisplayName': 'Stock Monitor',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSAppleEventsUsageDescription': '需要访问文件系统来保存配置',
        'NSDesktopFolderUsageDescription': '需要访问文件系统来保存配置',
        'NSDocumentsFolderUsageDescription': '需要访问文件系统来保存配置',
        'NSDownloadsFolderUsageDescription': '需要访问文件系统来保存配置',
        'NSHomeDirectoryUsageDescription': '需要访问用户目录来保存配置',
    }
)
EOL

# 构建应用
print_message "构建应用..."
pyinstaller --clean stock_monitor.spec

# 检查构建结果
if [ ! -d "dist/Stock Monitor.app" ]; then
    print_error "应用构建失败"
    exit 1
fi

# 修复权限和签名
print_message "修复权限和签名..."
chmod -R 755 "dist/Stock Monitor.app"
xattr -cr "dist/Stock Monitor.app"
codesign --force --deep --sign - "dist/Stock Monitor.app"

# 安装到应用程序文件夹
print_message "安装应用..."
sudo rm -rf "/Applications/Stock Monitor.app"
sudo cp -R "dist/Stock Monitor.app" /Applications/
sudo chown -R $USER:staff "/Applications/Stock Monitor.app"

print_message "安装完成！" 