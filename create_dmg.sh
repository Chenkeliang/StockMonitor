#!/bin/bash

# 安装必要的工具（如果没有安装）
if ! command -v create-dmg &> /dev/null; then
    echo "Installing create-dmg..."
    brew install create-dmg
fi

# 构建应用
echo "Building application..."
rm -rf build dist
python setup.py py2app

# 复制必要的库
echo "Copying libraries..."
python fix_libraries.py

# 创建临时目录
echo "Creating DMG..."
TMP_DMG="tmp_dmg"
rm -rf "$TMP_DMG"
mkdir "$TMP_DMG"

# 复制应用到临时目录
cp -r "dist/Stock Monitor.app" "$TMP_DMG/"

# 确保没有旧的挂载点
sudo hdiutil detach "/Volumes/Stock Monitor" 2>/dev/null || true

# 创建 DMG
create-dmg \
  --volname "Stock Monitor" \
  --volicon "icons/icon.icns" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "Stock Monitor.app" 175 190 \
  --hide-extension "Stock Monitor.app" \
  --app-drop-link 425 190 \
  --no-internet-enable \
  "Stock Monitor.dmg" \
  "$TMP_DMG"

# 安装应用（使用 sudo）
echo "Installing application..."
if [ -f "Stock Monitor.dmg" ]; then
    sudo hdiutil attach "Stock Monitor.dmg"
    sudo rm -rf "/Applications/Stock Monitor.app"
    sudo cp -R "/Volumes/Stock Monitor/Stock Monitor.app" /Applications/
    sudo chown -R $USER:staff "/Applications/Stock Monitor.app"
    sudo hdiutil detach "/Volumes/Stock Monitor"
    echo "应用已安装到 Applications 文件夹"
else
    echo "错误: DMG 文件未生成"
    exit 1
fi

# 清理临时文件
rm -rf "$TMP_DMG"

echo "DMG created and installed successfully!" 