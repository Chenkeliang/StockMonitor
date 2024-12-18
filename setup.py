from setuptools import setup

APP = ["stock_menubar.py"]
DATA_FILES = [
    ("icons", ["icons/icon.icns", "icons/icon.png"]),
]
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "icons/icon.icns",
    "plist": {
        "LSUIElement": True,
        "CFBundleName": "Stock Monitor",
        "CFBundleDisplayName": "Stock Monitor",
        "CFBundleIdentifier": "com.yourname.stockmonitor",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        "CFBundleIconFile": "icon.icns",
        "CFBundlePackageType": "APPL",
    },
    "packages": [
        "rumps",
        "matplotlib",
        "numpy",
        "pandas",
        "flask",
        "plotly",
        "requests",
        "pkg_resources",
    ],
    "includes": [
        "packaging",
        "pkg_resources._vendor.packaging",
        "pkg_resources._vendor.pyparsing",
    ],
    "resources": ["icons/*"],
    "site_packages": True,
    "strip": False,
    "semi_standalone": False,
    "arch": "arm64",
    "frameworks": [],
    "prefer_ppc": False,
    "debug_modulegraph": False,
    "optimize": 0,
}

setup(
    name="Stock Monitor",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    install_requires=[
        "pyobjc-framework-Cocoa",
        "rumps",
        "matplotlib",
        "numpy",
        "pandas",
        "flask",
        "plotly",
        "requests",
    ],
)
