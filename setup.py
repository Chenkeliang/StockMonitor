from setuptools import setup

APP = ['stock_menubar.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icons/icon.icns',
    'plist': {
        'LSUIElement': True,
        'CFBundleName': 'Stock Monitor',
        'CFBundleDisplayName': 'Stock Monitor',
        'CFBundleIdentifier': 'com.yourname.stockmonitor',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
    },
    'packages': ['rumps', 'requests'],
}

setup(
    app=APP,
    name='Stock Monitor',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 