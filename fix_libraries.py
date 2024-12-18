import os
import shutil
import subprocess
from pathlib import Path


def copy_dynamic_libraries():
    """复制必要的动态库到应用程序包中"""
    app_path = "dist/Stock Monitor.app"
    frameworks_path = f"{app_path}/Contents/Frameworks"
    resources_path = f"{app_path}/Contents/Resources"

    try:
        # 创建 Frameworks 目录并设置权限
        os.makedirs(frameworks_path, exist_ok=True)
        os.chmod(frameworks_path, 0o755)

        # 复制 Python framework
        python_version = "3.11"
        python_framework = (
            f"/Library/Frameworks/Python.framework/Versions/{python_version}/Python"
        )
        if os.path.exists(python_framework):
            dest_path = os.path.join(frameworks_path, "Python")
            shutil.copy2(python_framework, dest_path)
            os.chmod(dest_path, 0o755)

            # 修复 Python framework 的链接
            subprocess.run(
                [
                    "install_name_tool",
                    "-id",
                    "@executable_path/../Frameworks/Python",
                    dest_path,
                ]
            )

        # 复制 libffi
        libffi_path = os.popen("brew --prefix libffi").read().strip()
        if os.path.exists(f"{libffi_path}/lib/libffi.8.dylib"):
            dest_path = os.path.join(frameworks_path, "libffi.8.dylib")
            shutil.copy2(f"{libffi_path}/lib/libffi.8.dylib", dest_path)
            os.chmod(dest_path, 0o755)

            # 修改动态库链接
            objc_path = (
                f"{resources_path}/lib/python{python_version}/lib-dynload/objc/_objc.so"
            )
            if os.path.exists(objc_path):
                subprocess.run(
                    [
                        "install_name_tool",
                        "-change",
                        "@rpath/libffi.8.dylib",
                        "@executable_path/../Frameworks/libffi.8.dylib",
                        objc_path,
                    ]
                )

        print("Dynamic libraries copied successfully!")
    except Exception as e:
        print(f"Error copying libraries: {str(e)}")


if __name__ == "__main__":
    copy_dynamic_libraries()
