"""
Theme Manager for Ambient Sound Mixer

Handles application themes (light/dark) with styling and persistence.
"""

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication


class ThemeManager:
    """Manages application themes and styling."""

    LIGHT_THEME = "light"
    DARK_THEME = "dark"

    def __init__(self):
        self.settings = QSettings("Ambient Mixer", "Ambient Sound Mixer")
        self.current_theme = self.settings.value("theme", self.LIGHT_THEME)
        self._load_theme()

    def _load_theme(self):
        """Load and apply the current theme."""
        if self.current_theme == self.DARK_THEME:
            self._apply_dark_theme()
        else:
            self._apply_light_theme()

    def set_theme(self, theme):
        """Set the theme to light or dark."""
        if theme not in [self.LIGHT_THEME, self.DARK_THEME]:
            return

        self.current_theme = theme
        self.settings.setValue("theme", theme)
        self._load_theme()

    def toggle_theme(self):
        """Switch between light and dark themes."""
        new_theme = self.DARK_THEME if self.current_theme == self.LIGHT_THEME else self.LIGHT_THEME
        self.set_theme(new_theme)

    def get_current_theme(self):
        """Return the current theme."""
        return self.current_theme

    def is_dark(self):
        """Check if the current theme is dark."""
        return self.current_theme == self.DARK_THEME

    def apply_theme(self):
        """Apply the current theme to the application (legacy method)."""
        self._load_theme()

    def _apply_light_theme(self):
        """Apply the light theme stylesheet."""
        stylesheet = """
            QWidget {
                background-color: #ffffff;
                color: #000000;
                font-family: Arial, sans-serif;
                font-size: 12px;
            }

            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px 12px;
            }

            QPushButton:hover {
                background-color: #e0e0e0;
            }

            QPushButton:pressed {
                background-color: #d0d0d0;
            }

            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }

            QSlider::groove:horizontal {
                border: 1px solid #cccccc;
                height: 8px;
                background: #ffffff;
                margin: 2px 0;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: #cccccc;
                border: 1px solid #999999;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }

            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
                background-color: #ffffff;
            }

            QComboBox:hover {
                border-color: #999999;
            }

            QComboBox::drop-down {
                border: none;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666666;
                margin-right: 6px;
            }

            QSpinBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
                background-color: #ffffff;
            }

            QSpinBox:hover {
                border-color: #999999;
            }

            QCheckBox::indicator {
                width: 13px;
                height: 13px;
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }

            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }

            QTreeView {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }

            QTreeView::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }

            QMenuBar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #cccccc;
            }

            QMenuBar::item {
                padding: 4px 8px;
            }

            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }

            QStatusBar {
                background-color: #f0f0f0;
                border-top: 1px solid #cccccc;
            }
        """
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)

    def _apply_dark_theme(self):
        """Apply the dark theme stylesheet."""
        stylesheet = """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: Arial, sans-serif;
                font-size: 12px;
            }

            QPushButton {
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
            }

            QPushButton:hover {
                background-color: #505050;
            }

            QPushButton:pressed {
                background-color: #303030;
            }

            QGroupBox {
                font-weight: bold;
                border: 1px solid #606060;
                border-radius: 5px;
                margin-top: 1ex;
                color: #ffffff;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }

            QSlider::groove:horizontal {
                border: 1px solid #606060;
                height: 8px;
                background: #404040;
                margin: 2px 0;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: #606060;
                border: 1px solid #808080;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }

            QComboBox {
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 4px;
                background-color: #404040;
                color: #ffffff;
            }

            QComboBox:hover {
                border-color: #808080;
            }

            QComboBox::drop-down {
                border: none;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ffffff;
                margin-right: 6px;
            }

            QSpinBox {
                border: 1px solid #606060;
                border-radius: 4px;
                padding: 4px;
                background-color: #404040;
                color: #ffffff;
            }

            QSpinBox:hover {
                border-color: #808080;
            }

            QCheckBox::indicator {
                width: 13px;
                height: 13px;
                border: 1px solid #606060;
                background-color: #404040;
            }

            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }

            QTreeView {
                border: 1px solid #606060;
                background-color: #2b2b2b;
                color: #ffffff;
            }

            QTreeView::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }

            QMenuBar {
                background-color: #404040;
                border-bottom: 1px solid #606060;
                color: #ffffff;
            }

            QMenuBar::item {
                padding: 4px 8px;
            }

            QMenuBar::item:selected {
                background-color: #505050;
            }

            QStatusBar {
                background-color: #404040;
                border-top: 1px solid #606060;
                color: #ffffff;
            }
        """
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)