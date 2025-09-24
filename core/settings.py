"""
Settings Manager for Ambient Sound Mixer

Handles application settings persistence (themes, language, future settings).
"""

from PySide6.QtCore import QSettings, QLocale
from PySide6.QtWidgets import QApplication


class SettingsManager:
    """Manages application settings persistence."""

    LIGHT_THEME = "light"
    DARK_THEME = "dark"

    def __init__(self):
        self.settings = QSettings("Ambient Mixer", "Ambient Sound Mixer")

    def get_theme(self) -> str:
        """Get the saved theme, defaulting to light."""
        return self.settings.value("theme", self.LIGHT_THEME)

    def set_theme(self, theme: str):
        """Save the theme setting."""
        if theme in [self.LIGHT_THEME, self.DARK_THEME]:
            self.settings.setValue("theme", theme)

    def get_language(self) -> str:
        """Get the saved language, defaulting to system locale."""
        default_locale = QLocale.system().name()
        return self.settings.value("language", default_locale)

    def set_language(self, locale: str):
        """Save the language setting."""
        self.settings.setValue("language", locale)

    def is_dark_theme(self) -> bool:
        """Check if current theme is dark."""
        return self.get_theme() == self.DARK_THEME
