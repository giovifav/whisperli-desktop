# -*- mode: python ; coding: utf-8 -*-
import os
import glob
import sys
from PyInstaller.utils.hooks import collect_data_files

# Impostazioni di debug
DEBUG = False

block_cipher = None

# Lista di moduli da escludere (solo moduli non utilizzati)
# Rimossi PyQt6, PyQt5, PySide2 per evitare conflitti con PySide6
excluded_imports = [
    # Qt - Rimossi moduli essenziali, mantenuti solo quelli specifici non utilizzati
    'PySide6.Qt3D*', 'PySide6.QtBluetooth',
    'PySide6.QtDataVisualization', 'PySide6.QtLocation', # PySide6.QtMultimedia rimane
    'PySide6.QtNetworkAuth', 'PySide6.QtPositioning',
    'PySide6.QtQuick', 'PySide6.QtRemoteObjects', 'PySide6.QtSensors',
    'PySide6.QtSerialPort', 'PySide6.QtSql',
    'PySide6.QtTest', 'PySide6.QtWebChannel', 'PySide6.QtWebSockets',
    'PySide6.QtXml', 'PySide6.QtXmlPatterns',
    
    # Librerie scientifiche non necessarie
    'numpy', 'pandas', 'scipy', 'matplotlib', 'scikit_learn', 'tensorflow', 'torch',
    
    # Interfacce grafiche non utilizzate
    'tkinter', 'tcl', 'tk', 'ttk', 'wx', 'kivy', 'pyglet', 'pygame',
    
    # Testing
    'test', 'unittest', 'pytest', 'nose', 'doctest',
    
    # Strumenti di sviluppo
    'distutils', 'setuptools', 'pip', 'wheel', 'virtualenv', 'venv',
    
    # Protocolli non necessari
    'email', 'http', 'xml', 'html', 'ftplib', 'poplib', 'smtplib', 'imaplib',
    'urllib3', 'requests', 'aiohttp', 'asyncio', 'twisted', 'websocket',
    
    # Concorrenza non necessaria
    'concurrent', 'multiprocessing', 'multiprocess', 'joblib',
    
    # Documentazione e debug
    'pdb', 'ipdb', 'pudb', 'pygments', 'sphinx', 'pydoc', 'pylint', 'flake8',
    
    # Database
    'sqlalchemy', 'sqlite3', 'pymysql', 'psycopg2', 'pymongo', 'redis',
    
    # Altro
    'notebook', 'jupyter', 'IPython', 'spyder'  # qtpy is not used in this app
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # Collect data files for qtawesome
    datas=[
        ('sounds', 'sounds'),
        ('sessions', 'sessions'),
        ('translations', 'translations'),
    ] + collect_data_files('qtawesome', subdir='fonts'),
    hiddenimports=[
        'PySide6.QtSvg', 'qtawesome',
        'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtCore',
        'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
    ],
    hookspath=[],
    hooksconfig={
        # Necessario per PySide6 per raccogliere tutti i moduli Qt
        'pyside6': [None],  # Ciò dovrebbe importare tutti i moduli PySide6 necessari
    },
    runtime_hooks=[],
    excludes=excluded_imports,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=2,  # Ottimizzazione a livello di bytecode
    upx=True,  # Abilita UPX per i file binari
    upx_dir=r'C:\Users\jo\Documents\upx-5.0.2-win64',
    upx_exclude=[],
    name='AmbientSoundMixer',
    upx_compress=True,
    upx_best=True
)

# Add any additional files needed
# a.datas += Tree('path/to/extra/files', prefix='extra_files')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AmbientSoundMixer',
    debug=False,
    bootloader_ignore_signals=True,
    strip=False,  # Disabilitato per evitare problemi con Qt/GUI
    upx=True,     # Abilita UPX per comprimere l'eseguibile
    upx_exclude=[],
    upx_compress=True,
    upx_best=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    optimize=0,  # Ottimizzazione disabilitata per maggiore stabilità
    no_archive=False,
    onefile=True
)

# For creating a single directory with all dependencies
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,  # Disabilitato per stabilità Qt
#     upx=False,    # UPX disabilitato per sicurezza
#     upx_exclude=[],
#     name='AmbientSoundMixer',
#     optimize=0  # Ottimizzazione ridotta per maggiore stabilità
# )

# Pulisci i file temporanei dopo la build
if not DEBUG:
    import shutil
    build_dir = os.path.join(os.getcwd(), 'build')
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)
