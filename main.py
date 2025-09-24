#!/usr/bin/env python3
"""
Ambient Sound Mixer - Main Entry Point

A modular desktop application for creating relaxing ambient soundscapes
by layering .ogg sounds with volume control, loop behavior, and automation.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir, QTranslator, QLocale
from PySide6.QtGui import QIcon


# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

# Global variable to hold the translator
_translator = None


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Ambient Sound Mixer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Ambient Mixer")

    # Set up application style for touch-friendly interface
    app.setStyle('Fusion')

    # Initialize translator
    global _translator
    _translator = QTranslator()
    # Load default language (e.g., English)
    load_translator(app, QLocale.system().name())

    # Create and show main window
    window = MainWindow()
    window.show()

    return app.exec()


def load_translator(app: QApplication, locale: str):
    """Loads the translator for the given locale."""
    global _translator
    if _translator:
        app.removeTranslator(_translator)

    # Try to load the translation file for the given locale
    # Assuming translation files are in a 'translations' directory
    translations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations")
    if _translator.load(f"ambient_mixer_{locale}", translations_path):
        app.installTranslator(_translator)
        print(f"Loaded translation for locale: {locale}")
    else:
        print(f"Could not load translation for locale: {locale}")


if __name__ == '__main__':
    sys.exit(main())
