#!/bin/bash

echo "开始重新打包安装..."

# 1. 卸载旧应用
echo "正在卸载旧应用..."
rm -rf "/Applications/Stock Monitor.app"
rm -f *."Stock Monitor.dmg"

# 2. 清理构建文件
echo "清理构建文件..."
rm -rf build dist
rm -rf tmp_dmg

# 3. 清理系统图标缓存
echo "清理系统缓存..."
sudo rm -rf /Library/Caches/com.apple.iconservices.store
killall Dock
killall Finder

# 4. 重新生成图标
echo "重新生成图标..."
python convert_icon.py

# 5. 检查必要的工具
if ! command -v create-dmg &> /dev/null; then
    echo "安装 create-dmg..."
    brew install create-dmg
fi

# 6. 构建应用
echo "构建应用..."
python setup.py py2app

# 7. 复制必要的库
echo "复制必要的库..."
python fix_libraries.py

# 8. 创建 DMG
echo "创建 DMG..."
./create_dmg.sh

# 9. 安装应用
echo "安装应用..."
if [ -f "Stock Monitor.dmg" ]; then
    hdiutil attach "Stock Monitor.dmg"
    cp -r "/Volumes/Stock Monitor/Stock Monitor.app" /Applications/
    hdiutil detach "/Volumes/Stock Monitor"
    echo "应用已安装到 Applications 文件夹"
else
    echo "错误: DMG 文件未生成"
    exit 1
fi

echo "重新打包安装完成!" 