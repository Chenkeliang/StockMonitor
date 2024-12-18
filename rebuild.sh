#!/bin/bash

# 确保 Python 环境可用
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    echo "Error: Python3 not found"
    exit 1
fi

# 清理所有构建文件和缓存
rm -rf build dist *.pyc __pycache__ *.egg-info
rm -rf myenv/lib/python*/site-packages/*.dist-info

# 清理 Python 缓存
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# 重新创建虚拟环境
rm -rf myenv
$PYTHON_PATH -m venv myenv
source myenv/bin/activate || exit 1

# 确保 pip 可用
myenv/bin/pip3 install --upgrade pip

# 确保所有依赖都已安装
myenv/bin/pip3 install --no-cache-dir -r requirements.txt

# 构建应用
myenv/bin/python3 setup.py py2app --no-strip 

# 移除重复的 dist-info 目录
if [ -d "build" ]; then
    find build -name "*.dist-info" -type d -exec rm -rf {} +
fi

# 对应用进行签名
if [ -d "dist/Stock Monitor.app" ]; then
    codesign --force --deep --sign - "dist/Stock Monitor.app"
else
    echo "Error: Application bundle not found"
    exit 1
fi