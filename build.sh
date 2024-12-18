#!/bin/bash

# 确保 Python 3.11 环境可用
PYTHON_PATH=$(which python3.11)
if [ -z "$PYTHON_PATH" ]; then
    echo "Error: Python 3.11 not found"
    echo "Please install Python 3.11: brew install python@3.11"
    exit 1
fi

# 创建缓存目录
CACHE_DIR="$HOME/.pip_cache"
mkdir -p "$CACHE_DIR"

# 完全清理所有构建文件和缓存
rm -rf build dist *.pyc __pycache__ *.egg-info venv
rm -rf "$HOME/Library/Caches/com.apple.python/Applications"

# 清理 Python 缓存
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# 创建新的虚拟环境
$PYTHON_PATH -m venv venv
source venv/bin/activate

# 升级基础包
python -m pip install --upgrade pip setuptools wheel

# 安装构建工具
python -m pip install py2app

# 安装依赖
python -m pip install -r requirements.txt

# 构建应用
python setup.py py2app --no-strip

# 复制必要的库
python fix_libraries.py

# 修复权限和签名
if [ -d "dist/Stock Monitor.app" ]; then
    chmod -R 755 "dist/Stock Monitor.app"
    xattr -cr "dist/Stock Monitor.app"
    codesign --force --deep --sign - "dist/Stock Monitor.app"
    echo "应用构建成功！"
else
    echo "Error: Application bundle not found"
    exit 1
fi 