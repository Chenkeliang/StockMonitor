import os
import shutil
from pathlib import Path

def copy_dynamic_libraries():
    """复制必要的动态库到应用程序包中"""
    app_path = "dist/Stock Monitor.app"
    frameworks_path = f"{app_path}/Contents/Frameworks"
    resources_path = f"{app_path}/Contents/Resources"
    
    # 创建 Frameworks 目录
    os.makedirs(frameworks_path, exist_ok=True)
    
    # 复制 libffi
    libffi_path = os.popen('brew --prefix libffi').read().strip()
    if os.path.exists(f"{libffi_path}/lib/libffi.8.dylib"):
        shutil.copy2(f"{libffi_path}/lib/libffi.8.dylib", frameworks_path)
        
        # 创建符号链接
        os.system(f'install_name_tool -change "@rpath/libffi.8.dylib" "@executable_path/../Frameworks/libffi.8.dylib" "{resources_path}/lib/python3.11/lib-dynload/objc/_objc.so"')
    
    print("Dynamic libraries copied successfully!")

if __name__ == "__main__":
    copy_dynamic_libraries() 